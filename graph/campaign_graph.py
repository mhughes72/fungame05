"""
Campaign mode turn graphs — same pre/post split as game_graph.py.

Pre-turn:  run_economy_drift → select_campaign_crisis_node → generate_situation_briefing
Post-turn: apply_base_effects → classify_faction_reactions → compute_final_effects →
           check_threshold_events → generate_narrative → update_campaign_flags_node →
           save_turn_history

The extra post-turn step (update_campaign_flags_node) reads flag_effects from the
chosen option and merges them into campaign_flags. Path determination happens inside
select_campaign_crisis_node at turn 8.
"""

from langgraph.graph import StateGraph, END

from game.campaign import _determine_path, select_campaign_crisis
from game.state import GameState
from graph.nodes import (
    apply_base_effects_node,
    check_threshold_events_node,
    classify_faction_reactions,
    compute_final_effects,
    generate_narrative,
    generate_situation_briefing,
    run_economy_drift,
    save_turn_history,
)
import cli.debug as dbg


# ── Campaign-specific nodes ───────────────────────────────────────────────────

def select_campaign_crisis_node(state: GameState) -> dict:
    dbg.node_enter("select_campaign_crisis")
    flags = dict(state.get("campaign_flags") or {})
    turn  = state["current_turn"]

    # Determine path once, at the start of act 3
    if turn >= 8 and "path" not in flags:
        flags["path"] = _determine_path(flags)
        from cli.debug import _enabled
        if _enabled():
            from rich.console import Console
            Console(stderr=True, style="dim").print(
                f"  [dim]Campaign path determined:[/dim] [bold]{flags['path']}[/bold]"
            )

    crisis = select_campaign_crisis({**state, "campaign_flags": flags})

    from cli.debug import _enabled
    if _enabled():
        from rich.console import Console
        c = Console(stderr=True, style="dim")
        c.print(f"  [dim]Campaign crisis (turn {turn}):[/dim] [bold]{crisis['crisis_id']}[/bold] — {crisis['title']}")

    result = {
        "active_crisis": crisis,
        "campaign_flags": flags,
        "used_crisis_ids": state["used_crisis_ids"] + [crisis["crisis_id"]],
        "player_choice_index": None,
        "base_stat_effects":    None,
        "base_economy_effects": None,
        "base_faction_effects": None,
        "ai_reactions":         None,
        "ai_modifiers":         None,
        "final_stat_effects":   None,
        "final_economy_effects": None,
        "final_faction_effects": None,
        "triggered_events":     [],
        "situation_briefing":   None,
        "advisor_reactions":    None,
        "faction_narrative":    None,
        "headlines":            None,
        "faction_event_flags":  {fid: [] for fid in state["faction_support"]},
    }
    dbg.node_exit("select_campaign_crisis", result)
    return result


def update_campaign_flags_node(state: GameState) -> dict:
    """Merge flag_effects from the chosen option into campaign_flags."""
    dbg.node_enter("update_campaign_flags")
    flags  = dict(state.get("campaign_flags") or {})
    option = state["active_crisis"]["options"][state["player_choice_index"]]
    new_flags = option.get("flag_effects", {})
    flags.update(new_flags)

    from cli.debug import _enabled
    if _enabled() and new_flags:
        from rich.console import Console
        c = Console(stderr=True, style="dim")
        c.print(f"  [dim]Campaign flags updated:[/dim] {new_flags}")
        c.print(f"  [dim]Full campaign_flags:[/dim] {flags}")

    result = {"campaign_flags": flags}
    dbg.node_exit("update_campaign_flags", result)
    return result


# ── Graph builders ────────────────────────────────────────────────────────────

def build_pre_campaign_graph():
    g = StateGraph(GameState)
    g.add_node("run_economy_drift",            run_economy_drift)
    g.add_node("select_campaign_crisis",       select_campaign_crisis_node)
    g.add_node("generate_situation_briefing",  generate_situation_briefing)
    g.set_entry_point("run_economy_drift")
    g.add_edge("run_economy_drift",            "select_campaign_crisis")
    g.add_edge("select_campaign_crisis",       "generate_situation_briefing")
    g.add_edge("generate_situation_briefing",  END)
    return g.compile()


def build_post_campaign_graph():
    g = StateGraph(GameState)
    g.add_node("apply_base_effects",          apply_base_effects_node)
    g.add_node("classify_faction_reactions",  classify_faction_reactions)
    g.add_node("compute_final_effects",       compute_final_effects)
    g.add_node("check_threshold_events",      check_threshold_events_node)
    g.add_node("generate_narrative",          generate_narrative)
    g.add_node("update_campaign_flags",       update_campaign_flags_node)
    g.add_node("save_turn_history",           save_turn_history)
    g.set_entry_point("apply_base_effects")
    g.add_edge("apply_base_effects",          "classify_faction_reactions")
    g.add_edge("classify_faction_reactions",  "compute_final_effects")
    g.add_edge("compute_final_effects",       "check_threshold_events")
    g.add_edge("check_threshold_events",      "generate_narrative")
    g.add_edge("generate_narrative",          "update_campaign_flags")
    g.add_edge("update_campaign_flags",       "save_turn_history")
    g.add_edge("save_turn_history",           END)
    return g.compile()


pre_campaign_graph  = build_pre_campaign_graph()
post_campaign_graph = build_post_campaign_graph()
