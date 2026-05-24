"""
Freeform mode node functions.

The LLM generates crises from history and evaluates free-text player decisions.
Numerical effects are still validated and clamped by the engine.

Reused from nodes.py:
  - run_economy_drift
  - check_threshold_events_node
  - generate_end_summary

New nodes defined here:
  - generate_crisis_node
  - get_player_freeform_input
  - evaluate_decision_node
  - generate_freeform_narrative
  - save_freeform_turn_history
"""

import json
from typing import Any

from game.config import (
    MAX_ECONOMY_EFFECT_PER_TURN,
    MAX_EFFECT_PER_TURN,
    STARTING_ECONOMY_STATS,
    STARTING_FACTION_SUPPORT,
    STARTING_NATIONAL_STATS,
)
from game.economy import apply_economy_effects
from game.engine import apply_base_effects, update_recent_events
from game.state import GameState
from llm.client import get_llm
from llm.freeform_prompts import (
    evaluate_decision_prompt,
    evaluate_decision_retry_prompt,
    freeform_advisor_reactions_prompt,
    freeform_faction_narrative_prompt,
    freeform_headlines_prompt,
    generate_crisis_prompt,
)
import cli.debug as dbg


# ── LLM helpers ───────────────────────────────────────────────────────────────

def _build_lc_messages(messages: list[dict]) -> list:
    lc = []
    for m in messages:
        if m["role"] == "system":
            from langchain_core.messages import SystemMessage
            lc.append(SystemMessage(content=m["content"]))
        elif m["role"] == "assistant":
            from langchain_core.messages import AIMessage
            lc.append(AIMessage(content=m["content"]))
        else:
            from langchain_core.messages import HumanMessage
            lc.append(HumanMessage(content=m["content"]))
    return lc


def _call_llm_raw(label: str, messages: list[dict]) -> str:
    """Call the LLM and return raw text. Never raises — returns '' on failure."""
    dbg.llm_prompt(label, messages)
    try:
        response = get_llm().invoke(_build_lc_messages(messages))
        return response.content.strip()
    except Exception as e:
        dbg.llm_fallback(label, str(e))
        return ""


def _extract_json(text: str) -> Any:
    """
    Try multiple strategies to extract a JSON object from LLM output.
    Returns parsed object or None.

    Strategy order:
      1. Parse the whole string directly
      2. Strip a markdown code fence and parse
      3. Find the outermost { ... } and parse that substring
    """
    # Strategy 1: clean parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: strip markdown code fence
    stripped = text
    if "```" in text:
        parts = text.split("```")
        # Parts[1] is the content inside the first pair of fences
        if len(parts) >= 2:
            inner = parts[1]
            if inner.startswith("json"):
                inner = inner[4:]
            stripped = inner.strip()
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass

    # Strategy 3: find outermost { ... }
    start = text.find("{")
    end   = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            pass

    return None


def _call_llm_json(label: str, messages: list[dict]) -> Any:
    """Call the LLM, extract JSON robustly. Returns (parsed_result, raw_text)."""
    raw_text = _call_llm_raw(label, messages)
    if not raw_text:
        return None, ""
    result = _extract_json(raw_text)
    if result is not None:
        dbg.llm_response(label, result)
    else:
        dbg.llm_fallback(label, f"JSON extraction failed. Raw: {raw_text[:200]}")
    return result, raw_text


# ── Effect validation ──────────────────────────────────────────────────────────

def _validate_effects(raw: Any) -> tuple[dict | None, str]:
    """
    Validate and clamp LLM decision output.
    Returns (cleaned_dict, error_reason). error_reason is "" on success.
    """
    if not isinstance(raw, dict):
        return None, "response is not a JSON object"

    for key in ("interpretation", "stat_effects", "economy_effects", "faction_effects"):
        if key not in raw:
            return None, f"missing required key '{key}'"

    interpretation = raw.get("interpretation", "")
    if not isinstance(interpretation, str) or not interpretation.strip():
        return None, "interpretation must be a non-empty string"

    stat_fx: dict[str, int] = {}
    for key in STARTING_NATIONAL_STATS:
        val = raw["stat_effects"].get(key, 0)
        if not isinstance(val, (int, float)):
            return None, f"stat_effects.{key} is not a number"
        stat_fx[key] = max(-MAX_EFFECT_PER_TURN, min(MAX_EFFECT_PER_TURN, int(val)))

    eco_fx: dict[str, int] = {}
    for key in STARTING_ECONOMY_STATS:
        val = raw["economy_effects"].get(key, 0)
        if not isinstance(val, (int, float)):
            return None, f"economy_effects.{key} is not a number"
        eco_fx[key] = max(-MAX_ECONOMY_EFFECT_PER_TURN, min(MAX_ECONOMY_EFFECT_PER_TURN, int(val)))

    fac_fx: dict[str, int] = {}
    for key in STARTING_FACTION_SUPPORT:
        val = raw["faction_effects"].get(key, 0)
        if not isinstance(val, (int, float)):
            return None, f"faction_effects.{key} is not a number"
        fac_fx[key] = max(-MAX_EFFECT_PER_TURN, min(MAX_EFFECT_PER_TURN, int(val)))

    return {
        "interpretation": interpretation.strip(),
        "stat_effects":     stat_fx,
        "economy_effects":  eco_fx,
        "faction_effects":  fac_fx,
    }, ""


def _safe_fallback_effects() -> dict:
    """Used when both LLM attempts fail — indecision has a small cost."""
    return {
        "interpretation": "The response was unclear. The situation drifts unresolved.",
        "stat_effects":    {k: 0 for k in STARTING_NATIONAL_STATS},
        "economy_effects": {k: 0 for k in STARTING_ECONOMY_STATS},
        "faction_effects": {k: -1 for k in STARTING_FACTION_SUPPORT},
    }


# ── Node: generate_crisis_node ────────────────────────────────────────────────

def generate_crisis_node(state: GameState) -> dict:
    dbg.node_enter("generate_crisis")

    messages = generate_crisis_prompt(
        turn=state["current_turn"],
        max_turns=state["max_turns"],
        national_stats=state["national_stats"],
        economy_stats=state["economy_stats"],
        faction_support=state["faction_support"],
        recent_events=state["recent_events"],
        turn_history=state["turn_history"],
    )

    raw, _ = _call_llm_json("generate_crisis", messages)

    if raw and isinstance(raw, dict) and "title" in raw and "description" in raw:
        crisis = {
            "crisis_id":   f"generated_{state['current_turn']}",
            "title":       raw["title"],
            "description": raw["description"],
            "options":     [],   # no authored options in freeform mode
        }
        if dbg._enabled() and raw.get("continuity_note"):
            from rich.console import Console
            Console(stderr=True, style="dim").print(
                f"  [dim]Continuity:[/dim] {raw['continuity_note']}"
            )
    else:
        # Fallback crisis if LLM fails
        crisis = {
            "crisis_id":   f"generated_{state['current_turn']}",
            "title":       "The Situation Deteriorates",
            "description": (
                "Something has gone wrong — the details are unclear, "
                "but the pressure is real and a response is required."
            ),
            "options": [],
        }

    result = {
        "active_crisis":          crisis,
        "player_choice_index":    None,
        "player_input":           None,
        "decision_interpretation": None,
        "base_stat_effects":      None,
        "base_economy_effects":   None,
        "base_faction_effects":   None,
        "ai_reactions":           None,
        "ai_modifiers":           None,
        "final_stat_effects":     None,
        "final_economy_effects":  None,
        "final_faction_effects":  None,
        "triggered_events":       [],
        "situation_briefing":     None,
        "advisor_reactions":      None,
        "faction_narrative":      None,
        "headlines":              None,
        "faction_event_flags":    {fid: [] for fid in state["faction_support"]},
    }
    dbg.node_exit("generate_crisis", result)
    return result


# ── Node: get_player_freeform_input ───────────────────────────────────────────

def get_player_freeform_input(state: GameState) -> dict:
    dbg.node_enter("get_player_freeform_input")
    from cli.display import display_freeform_turn_screen
    display_freeform_turn_screen(state)

    print()
    while True:
        raw = input("  Your response: ").strip()
        if raw:
            result = {"player_input": raw}
            if dbg._enabled():
                from rich.console import Console
                Console(stderr=True, style="dim").print(
                    f"  [dim]Player input:[/dim] \"{raw}\""
                )
            dbg.node_exit("get_player_freeform_input", result)
            return result
        print("  Please enter a response.")


# ── Node: evaluate_decision_node ──────────────────────────────────────────────

def evaluate_decision_node(state: GameState) -> dict:
    dbg.node_enter("evaluate_decision")

    crisis = state["active_crisis"]
    player_input = state["player_input"] or ""

    messages = evaluate_decision_prompt(
        crisis_title=crisis["title"],
        crisis_description=crisis["description"],
        player_input=player_input,
        national_stats=state["national_stats"],
        economy_stats=state["economy_stats"],
        faction_support=state["faction_support"],
        faction_personas=state["faction_personas"],
        recent_events=state["recent_events"],
    )

    # First attempt — capture raw text so retry has something concrete to correct
    raw, raw_text = _call_llm_json("evaluate_decision", messages)
    validated, error = _validate_effects(raw)

    # Retry once if validation failed, passing the actual raw response
    if validated is None:
        dbg.llm_fallback("evaluate_decision_retry", f"First attempt failed: {error}")
        retry_messages = evaluate_decision_retry_prompt(messages, raw_text or "(no response)", error)
        raw2, _ = _call_llm_json("evaluate_decision_retry", retry_messages)
        validated, error2 = _validate_effects(raw2)

        if validated is None:
            dbg.llm_fallback("evaluate_decision_fallback", f"Retry failed: {error2}. Using fallback.")
            validated = _safe_fallback_effects()

    # Apply effects to state
    stat_fx  = validated["stat_effects"]
    eco_fx   = validated["economy_effects"]
    fac_fx   = validated["faction_effects"]
    interp   = validated["interpretation"]

    from game.config import STAT_MIN, STAT_MAX
    new_stats = {
        k: max(STAT_MIN, min(STAT_MAX, v + stat_fx.get(k, 0)))
        for k, v in state["national_stats"].items()
    }
    new_economy = apply_economy_effects(state["economy_stats"], eco_fx)
    new_factions = {
        k: max(STAT_MIN, min(STAT_MAX, v + fac_fx.get(k, 0)))
        for k, v in state["faction_support"].items()
    }

    if dbg._enabled():
        from rich.console import Console
        c = Console(stderr=True, style="dim")
        c.print(f"  [dim]Interpretation:[/dim] {interp}")
        c.print(f"  [dim]Stat effects:[/dim] {stat_fx}")
        c.print(f"  [dim]Economy effects:[/dim] {eco_fx}")
        c.print(f"  [dim]Faction effects:[/dim] {fac_fx}")

    result = {
        "decision_interpretation": interp,
        "national_stats":          new_stats,
        "economy_stats":           new_economy,
        "faction_support":         new_factions,
        "base_stat_effects":       stat_fx,
        "base_economy_effects":    eco_fx,
        "base_faction_effects":    fac_fx,
        "final_stat_effects":      stat_fx,
        "final_economy_effects":   eco_fx,
        "final_faction_effects":   fac_fx,
    }
    dbg.node_exit("evaluate_decision", result)
    return result


# ── Node: generate_freeform_narrative ────────────────────────────────────────

def generate_freeform_narrative(state: GameState) -> dict:
    dbg.node_enter("generate_freeform_narrative")

    interpretation = state.get("decision_interpretation") or "The president acted."
    crisis_title   = state["active_crisis"]["title"]

    adv_messages = freeform_advisor_reactions_prompt(
        crisis_title=crisis_title,
        decision_interpretation=interpretation,
        final_stat_effects=state["final_stat_effects"] or {},
        final_faction_effects=state["final_faction_effects"] or {},
        national_stats=state["national_stats"],
    )
    advisors_raw, _ = _call_llm_json("advisor_reactions", adv_messages)
    advisors = advisors_raw if isinstance(advisors_raw, list) else [
        {"name": "Finance Minister", "reaction": "No comment at this time."},
    ]

    fn_messages = freeform_faction_narrative_prompt(
        crisis_title=crisis_title,
        decision_interpretation=interpretation,
        faction_effects=state["final_faction_effects"] or {},
        faction_personas=state["faction_personas"],
    )
    fn_raw, _ = _call_llm_json("faction_narrative", fn_messages)
    faction_narr = fn_raw if isinstance(fn_raw, dict) else {}

    hl_messages = freeform_headlines_prompt(
        crisis_title=crisis_title,
        decision_interpretation=interpretation,
        final_stat_effects=state["final_stat_effects"] or {},
        final_faction_effects=state["final_faction_effects"] or {},
        triggered_events=state["triggered_events"],
    )
    hl_raw, _ = _call_llm_json("headlines", hl_messages)
    headlines = hl_raw if isinstance(hl_raw, list) else []

    result = {
        "advisor_reactions": advisors,
        "faction_narrative": faction_narr,
        "headlines":         headlines,
    }
    dbg.node_exit("generate_freeform_narrative", result)
    return result


# ── Node: save_freeform_turn_history ──────────────────────────────────────────

def save_freeform_turn_history(state: GameState) -> dict:
    dbg.node_enter("save_freeform_turn_history")
    record = {
        "turn_number":           state["current_turn"],
        "crisis_id":             state["active_crisis"]["crisis_id"],
        "crisis_title":          state["active_crisis"]["title"],
        "player_input":          state.get("player_input"),
        "decision_interpretation": state.get("decision_interpretation"),
        "final_stat_effects":    state["final_stat_effects"],
        "final_economy_effects": state["final_economy_effects"],
        "final_fac_effects":     state["final_faction_effects"],
        "triggered_events":      state["triggered_events"],
        "economy_snapshot":      dict(state["economy_stats"]),
    }
    result = {
        "turn_history": state["turn_history"] + [record],
        "current_turn": state["current_turn"] + 1,
    }
    dbg.turn_summary({**state, **result})
    dbg.node_exit("save_freeform_turn_history", result)
    return result
