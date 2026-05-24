"""
Classic mode turn graphs — split at the player input point.

Pre-turn  (runs before the player sees the crisis):
  run_economy_drift → select_crisis → generate_situation_briefing

Post-turn (runs after player_choice_index is set in state):
  apply_base_effects → classify_faction_reactions → compute_final_effects →
  check_threshold_events → generate_narrative → save_turn_history

The CLI main.py chains these with a blocking input() call between them.
The web API stores state between the two invocations.
"""

from langgraph.graph import StateGraph, END

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
    select_crisis,
)


def build_pre_classic_graph():
    g = StateGraph(GameState)
    g.add_node("run_economy_drift",           run_economy_drift)
    g.add_node("select_crisis",               select_crisis)
    g.add_node("generate_situation_briefing", generate_situation_briefing)
    g.set_entry_point("run_economy_drift")
    g.add_edge("run_economy_drift",           "select_crisis")
    g.add_edge("select_crisis",               "generate_situation_briefing")
    g.add_edge("generate_situation_briefing", END)
    return g.compile()


def build_post_classic_graph():
    g = StateGraph(GameState)
    g.add_node("apply_base_effects",         apply_base_effects_node)
    g.add_node("classify_faction_reactions", classify_faction_reactions)
    g.add_node("compute_final_effects",      compute_final_effects)
    g.add_node("check_threshold_events",     check_threshold_events_node)
    g.add_node("generate_narrative",         generate_narrative)
    g.add_node("save_turn_history",          save_turn_history)
    g.set_entry_point("apply_base_effects")
    g.add_edge("apply_base_effects",         "classify_faction_reactions")
    g.add_edge("classify_faction_reactions", "compute_final_effects")
    g.add_edge("compute_final_effects",      "check_threshold_events")
    g.add_edge("check_threshold_events",     "generate_narrative")
    g.add_edge("generate_narrative",         "save_turn_history")
    g.add_edge("save_turn_history",          END)
    return g.compile()


pre_classic_graph  = build_pre_classic_graph()
post_classic_graph = build_post_classic_graph()


def save_graph_image(output_path: str = "graph.png") -> None:
    """Render the pre-turn graph as a PNG using the Mermaid.ink API."""
    png_bytes = pre_classic_graph.get_graph().draw_mermaid_png()
    with open(output_path, "wb") as f:
        f.write(png_bytes)
    print(f"Graph saved to {output_path}")
