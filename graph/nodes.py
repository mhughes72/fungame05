"""
LangGraph node functions. Each node receives the full GameState and returns
a partial dict that LangGraph merges back into the state.
"""

import json
import random
import uuid
from typing import Any

from game.config import (
    MAX_TURNS,
    STARTING_ECONOMY_STATS,
    STARTING_FACTION_SUPPORT,
    STARTING_NATIONAL_STATS,
)
from game.crises import CRISIS_TEMPLATES
from game.economy import (
    apply_economy_effects,
    compute_economy_drift,
    compute_faction_pressure,
    get_crisis_weights,
)
from game.engine import (
    apply_ai_modifiers,
    apply_base_effects,
    apply_threshold_effects,
    check_loss,
    check_thresholds,
    compute_ai_modifiers,
    determine_end_state,
    update_recent_events,
    validate_ai_reactions,
)
from game.factions import FACTION_PERSONAS
from game.state import GameState
from llm.client import get_llm
from llm.prompts import (
    advisor_reactions_prompt,
    build_faction_context,
    end_summary_prompt,
    faction_narrative_prompt,
    headlines_prompt,
    reaction_classification_prompt,
    situation_briefing_prompt,
)
import cli.debug as dbg


# ── LLM helpers ───────────────────────────────────────────────────────────────

def _call_llm_json(label: str, messages: list[dict]) -> Any:
    """Call the LLM and parse JSON. Returns None on failure."""
    dbg.llm_prompt(label, messages)
    llm = get_llm()
    lc_messages = []
    for m in messages:
        if m["role"] == "system":
            from langchain_core.messages import SystemMessage
            lc_messages.append(SystemMessage(content=m["content"]))
        else:
            from langchain_core.messages import HumanMessage
            lc_messages.append(HumanMessage(content=m["content"]))
    try:
        response = llm.invoke(lc_messages)
        text = response.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        result = json.loads(text)
        dbg.llm_response(label, result)
        return result
    except Exception as e:
        dbg.llm_fallback(label, str(e))
        return None


def _call_llm_text(label: str, messages: list[dict]) -> str:
    """Call the LLM and return plain text. Returns fallback string on failure."""
    dbg.llm_prompt(label, messages)
    llm = get_llm()
    lc_messages = []
    for m in messages:
        if m["role"] == "system":
            from langchain_core.messages import SystemMessage
            lc_messages.append(SystemMessage(content=m["content"]))
        else:
            from langchain_core.messages import HumanMessage
            lc_messages.append(HumanMessage(content=m["content"]))
    try:
        response = llm.invoke(lc_messages)
        result = response.content.strip()
        dbg.llm_response(label, result)
        return result
    except Exception as e:
        dbg.llm_fallback(label, str(e))
        return "Veridia endures. Somehow."


# ── Node: initialize_game ──────────────────────────────────────────────────────

def initialize_game(_state: GameState) -> dict:
    import copy
    dbg.node_enter("initialize_game")
    personas = copy.deepcopy(FACTION_PERSONAS)
    result = {
        "game_id": str(uuid.uuid4())[:8],
        "current_turn": 1,
        "max_turns": MAX_TURNS,
        "game_status": "active",
        "end_state": None,
        "loss_reason": None,
        "national_stats": dict(STARTING_NATIONAL_STATS),
        "economy_stats": dict(STARTING_ECONOMY_STATS),
        "faction_support": dict(STARTING_FACTION_SUPPORT),
        "faction_personas": personas,
        "faction_event_flags": {fid: [] for fid in STARTING_FACTION_SUPPORT},
        "active_crisis": None,
        "used_crisis_ids": [],
        "player_choice_index": None,
        "player_input": None,
        "decision_interpretation": None,
        "base_stat_effects": None,
        "base_economy_effects": None,
        "base_faction_effects": None,
        "ai_reactions": None,
        "ai_modifiers": None,
        "final_stat_effects": None,
        "final_economy_effects": None,
        "final_faction_effects": None,
        "triggered_events": [],
        "economy_drift_descriptions": [],
        "faction_pressure_descriptions": [],
        "situation_briefing": None,
        "advisor_reactions": None,
        "faction_narrative": None,
        "headlines": None,
        "end_summary": None,
        "recent_events": [],
        "turn_history": [],
    }
    dbg.state_snapshot("after init", result, [
        "game_id", "current_turn", "max_turns", "national_stats", "economy_stats", "faction_support"
    ])
    dbg.node_exit("initialize_game", result)
    return result


# ── Node: run_economy_drift ────────────────────────────────────────────────────

def run_economy_drift(state: GameState) -> dict:
    dbg.node_enter("run_economy_drift")
    new_economy, drift_descriptions = compute_economy_drift(
        state["economy_stats"],
        state["national_stats"],
    )
    new_factions, pressure_descriptions = compute_faction_pressure(
        new_economy,
        state["faction_support"],
    )

    from cli.debug import _enabled
    if _enabled():
        from rich.console import Console
        c = Console(stderr=True, style="dim")
        if drift_descriptions:
            c.print("  [dim]Economy drift triggers:[/dim]")
            for d in drift_descriptions:
                c.print(f"    • {d}")
        else:
            c.print("  [dim]Economy drift: no rules triggered[/dim]")
        if pressure_descriptions:
            c.print("  [dim]Faction pressure triggers:[/dim]")
            for d in pressure_descriptions:
                c.print(f"    • {d}")

    result = {
        "economy_stats": new_economy,
        "faction_support": new_factions,
        "economy_drift_descriptions": drift_descriptions,
        "faction_pressure_descriptions": pressure_descriptions,
    }
    dbg.node_exit("run_economy_drift", result)
    return result


# ── Node: select_crisis ────────────────────────────────────────────────────────

def select_crisis(state: GameState) -> dict:
    dbg.node_enter("select_crisis")
    used = set(state["used_crisis_ids"])
    available = [c for c in CRISIS_TEMPLATES if c["crisis_id"] not in used]
    if not available:
        available = list(CRISIS_TEMPLATES)

    weights = get_crisis_weights(state["economy_stats"], state["national_stats"], available)
    crisis = random.choices(available, weights=weights, k=1)[0]

    result = {
        "active_crisis": crisis,
        "used_crisis_ids": state["used_crisis_ids"] + [crisis["crisis_id"]],
        "player_choice_index": None,
        "base_stat_effects": None,
        "base_economy_effects": None,
        "base_faction_effects": None,
        "ai_reactions": None,
        "ai_modifiers": None,
        "final_stat_effects": None,
        "final_economy_effects": None,
        "final_faction_effects": None,
        "triggered_events": [],
        "situation_briefing": None,
        "advisor_reactions": None,
        "faction_narrative": None,
        "headlines": None,
        "faction_event_flags": {fid: [] for fid in state["faction_support"]},
    }

    from cli.debug import _enabled
    if _enabled():
        from rich.console import Console
        c = Console(stderr=True, style="dim")
        c.print(f"  [dim]Selected crisis:[/dim] [bold]{crisis['crisis_id']}[/bold] — {crisis['title']}")
        c.print(f"  [dim]Remaining pool:[/dim] {len(available) - 1} unused")
        boosted = [available[i]["crisis_id"] for i, w in enumerate(weights) if w > 1]
        if boosted:
            c.print(f"  [dim]Boosted by economy:[/dim] {', '.join(boosted)}")

    dbg.node_exit("select_crisis", result)
    return result


# ── Node: generate_situation_briefing ─────────────────────────────────────────

def generate_situation_briefing(state: GameState) -> dict:
    dbg.node_enter("generate_situation_briefing")
    messages = situation_briefing_prompt(
        turn=state["current_turn"],
        max_turns=state["max_turns"],
        national_stats=state["national_stats"],
        economy_stats=state["economy_stats"],
        faction_support=state["faction_support"],
        recent_events=state["recent_events"],
    )
    briefing = _call_llm_text("situation_briefing", messages)
    result = {"situation_briefing": briefing}
    dbg.node_exit("generate_situation_briefing", result)
    return result


# ── Node: get_player_choice ────────────────────────────────────────────────────

def get_player_choice(state: GameState) -> dict:
    dbg.node_enter("get_player_choice")
    from cli.display import display_turn_screen
    display_turn_screen(state)

    crisis = state["active_crisis"]
    options = crisis["options"]
    while True:
        raw = input(f"\n  Your choice [1–{len(options)}]: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            choice = int(raw) - 1
            result = {"player_choice_index": choice}
            from cli.debug import _enabled
            if _enabled():
                from rich.console import Console
                Console(stderr=True, style="dim").print(
                    f"  [dim]Player chose option {choice + 1}:[/dim] {options[choice]['label']}"
                )
            dbg.node_exit("get_player_choice", result)
            return result
        print(f"  Please enter a number between 1 and {len(options)}.")


# ── Node: apply_base_effects ───────────────────────────────────────────────────

def apply_base_effects_node(state: GameState) -> dict:
    dbg.node_enter("apply_base_effects")
    option = state["active_crisis"]["options"][state["player_choice_index"]]
    new_stats, new_factions = apply_base_effects(
        state["national_stats"],
        state["faction_support"],
        option["stat_effects"],
        option["faction_effects"],
    )
    economy_fx = option.get("economy_effects", {})
    new_economy = apply_economy_effects(state["economy_stats"], economy_fx)
    event_flags = option.get("event_flags", {})

    dbg.base_effects(option["stat_effects"], option["faction_effects"])

    from cli.debug import _enabled
    if _enabled() and economy_fx:
        from rich.console import Console
        c = Console(stderr=True, style="dim")
        c.print(f"  [dim]Base economy effects:[/dim] {economy_fx}")

    result = {
        "base_stat_effects":    option["stat_effects"],
        "base_economy_effects": economy_fx,
        "base_faction_effects": option["faction_effects"],
        "national_stats":       new_stats,
        "economy_stats":        new_economy,
        "faction_support":      new_factions,
        "faction_event_flags":  event_flags,
    }
    dbg.node_exit("apply_base_effects", result)
    return result


# ── Node: classify_faction_reactions ──────────────────────────────────────────

def classify_faction_reactions(state: GameState) -> dict:
    dbg.node_enter("classify_faction_reactions")
    option = state["active_crisis"]["options"][state["player_choice_index"]]
    affected = option["affected_factions"]

    support_before = dict(state["faction_support"])

    faction_contexts = [
        build_faction_context(
            fid,
            state["faction_personas"][fid],
            state["faction_support"][fid],
            state["faction_event_flags"],
        )
        for fid in affected
        if fid in state["faction_personas"]
    ]

    messages = reaction_classification_prompt(
        crisis_title=state["active_crisis"]["title"],
        selected_option_label=option["label"],
        selected_option_description=option["description"],
        policy_tags=option["policy_tags"],
        affected_factions=affected,
        faction_contexts=faction_contexts,
        national_stats=state["national_stats"],
        economy_stats=state["economy_stats"],
        recent_events=state["recent_events"],
    )

    raw = _call_llm_json("faction_reactions", messages)
    validated = validate_ai_reactions(raw, affected) if raw else None

    if validated:
        modifiers = compute_ai_modifiers(validated)
        new_factions = apply_ai_modifiers(state["faction_support"], modifiers)
        dbg.ai_modifier_pipeline(raw, validated, modifiers, support_before, new_factions)
        result = {
            "ai_reactions":    validated,
            "ai_modifiers":    modifiers,
            "faction_support": new_factions,
        }
    else:
        dbg.ai_modifier_pipeline(raw, None, {}, support_before, state["faction_support"])
        result = {
            "ai_reactions": None,
            "ai_modifiers": {},
        }

    dbg.node_exit("classify_faction_reactions", result)
    return result


# ── Node: compute_final_effects ────────────────────────────────────────────────

def compute_final_effects(state: GameState) -> dict:
    dbg.node_enter("compute_final_effects")
    option = state["active_crisis"]["options"][state["player_choice_index"]]
    base_stat = option["stat_effects"]
    base_eco  = option.get("economy_effects", {})
    base_fac  = option["faction_effects"]
    mods      = state.get("ai_modifiers") or {}

    final_fac = {
        k: base_fac.get(k, 0) + mods.get(k, 0)
        for k in set(list(base_fac.keys()) + list(mods.keys()))
    }

    from cli.debug import _enabled
    if _enabled():
        from rich.console import Console
        c = Console(stderr=True, style="dim")
        c.print("  [dim]Final faction effect breakdown (base + AI modifier):[/dim]")
        for fid in final_fac:
            b = base_fac.get(fid, 0)
            m = mods.get(fid, 0)
            total = b + m
            c.print(f"    {fid}: {b:+d} base  {m:+d} AI  = [bold]{total:+d}[/bold]")

    result = {
        "final_stat_effects":     base_stat,
        "final_economy_effects":  base_eco,
        "final_faction_effects":  final_fac,
    }
    dbg.node_exit("compute_final_effects", result)
    return result


# ── Node: check_threshold_events ──────────────────────────────────────────────

def check_threshold_events_node(state: GameState) -> dict:
    dbg.node_enter("check_threshold_events")
    already = set(
        e for t in state["turn_history"] for e in (t.get("triggered_events") or [])
    )
    new_triggers = check_thresholds(
        state["national_stats"],
        state["faction_support"],
        already,
        state["economy_stats"],
    )

    dbg.threshold_checks_clean(state["national_stats"], state["faction_support"], new_triggers)

    new_stats    = dict(state["national_stats"])
    new_factions = dict(state["faction_support"])
    new_economy  = dict(state["economy_stats"])
    event_descriptions = []

    for event_key in new_triggers:
        new_stats, new_factions, new_economy = apply_threshold_effects(
            event_key, new_stats, new_factions, new_economy
        )
        from game.config import THRESHOLD_EVENTS
        event_descriptions.append(THRESHOLD_EVENTS[event_key]["description"])

    result = {
        "triggered_events": new_triggers,
        "national_stats":   new_stats,
        "economy_stats":    new_economy,
        "faction_support":  new_factions,
        "recent_events":    update_recent_events(state["recent_events"], event_descriptions),
    }
    dbg.node_exit("check_threshold_events", result)
    return result


# ── Node: generate_narrative ──────────────────────────────────────────────────

def generate_narrative(state: GameState) -> dict:
    dbg.node_enter("generate_narrative")
    option    = state["active_crisis"]["options"][state["player_choice_index"]]
    validated = state.get("ai_reactions") or {}

    adv_messages = advisor_reactions_prompt(
        crisis_title=state["active_crisis"]["title"],
        selected_option_label=option["label"],
        final_stat_effects=state["final_stat_effects"] or {},
        final_faction_effects=state["final_faction_effects"] or {},
        national_stats=state["national_stats"],
    )
    advisors_raw = _call_llm_json("advisor_reactions", adv_messages)
    advisors = advisors_raw if isinstance(advisors_raw, list) else [
        {"name": "Finance Minister", "reaction": "No comment at this time."},
    ]

    faction_narr: dict[str, str] = {}
    if validated:
        fn_messages = faction_narrative_prompt(
            crisis_title=state["active_crisis"]["title"],
            selected_option_label=option["label"],
            validated_reactions=validated,
            faction_personas=state["faction_personas"],
            final_faction_effects=state["final_faction_effects"] or {},
        )
        fn_raw = _call_llm_json("faction_narrative", fn_messages)
        faction_narr = fn_raw if isinstance(fn_raw, dict) else {}

    hl_messages = headlines_prompt(
        crisis_title=state["active_crisis"]["title"],
        selected_option_label=option["label"],
        final_stat_effects=state["final_stat_effects"] or {},
        final_faction_effects=state["final_faction_effects"] or {},
        triggered_events=state["triggered_events"],
    )
    hl_raw = _call_llm_json("headlines", hl_messages)
    headlines = hl_raw if isinstance(hl_raw, list) else []

    result = {
        "advisor_reactions": advisors,
        "faction_narrative": faction_narr,
        "headlines":         headlines,
    }
    dbg.node_exit("generate_narrative", result)
    return result


# ── Node: save_turn_history ────────────────────────────────────────────────────

def save_turn_history(state: GameState) -> dict:
    dbg.node_enter("save_turn_history")
    option = state["active_crisis"]["options"][state["player_choice_index"]]
    record = {
        "turn_number":          state["current_turn"],
        "crisis_id":            state["active_crisis"]["crisis_id"],
        "crisis_title":         state["active_crisis"]["title"],
        "selected_option":      option["label"],
        "base_stat_effects":    state["base_stat_effects"],
        "base_economy_effects": state["base_economy_effects"],
        "base_fac_effects":     state["base_faction_effects"],
        "ai_reactions":         state["ai_reactions"],
        "ai_modifiers":         state["ai_modifiers"],
        "final_stat_effects":   state["final_stat_effects"],
        "final_economy_effects": state["final_economy_effects"],
        "final_fac_effects":    state["final_faction_effects"],
        "triggered_events":     state["triggered_events"],
        "economy_snapshot":     dict(state["economy_stats"]),
    }
    result = {
        "turn_history": state["turn_history"] + [record],
        "current_turn": state["current_turn"] + 1,
    }

    dbg.turn_summary({**state, **result})
    dbg.node_exit("save_turn_history", result)
    return result


# ── Node: generate_end_summary ────────────────────────────────────────────────

def generate_end_summary(state: GameState) -> dict:
    dbg.node_enter("generate_end_summary")
    won       = state["game_status"] == "won"
    end_state = state.get("end_state") or "Failed Democrat"
    flavour   = ""
    from game.config import END_STATE_RULES
    for name, _, flv in END_STATE_RULES:
        if name == end_state:
            flavour = flv
            break

    messages = end_summary_prompt(
        end_state=end_state,
        end_state_flavour=flavour,
        final_stats=state["national_stats"],
        final_factions=state["faction_support"],
        turn_history=state["turn_history"],
        won=won,
    )
    summary = _call_llm_text("end_summary", messages)
    result  = {"end_summary": summary}
    dbg.node_exit("generate_end_summary", result)
    return result
