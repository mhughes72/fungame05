"""
LangGraph turn graph.

Each invocation of turn_graph.invoke(state) runs one complete turn:
  select_crisis → generate_briefing → get_player_choice →
  apply_base_effects → classify_reactions → compute_final_effects →
  check_thresholds → generate_narrative → save_turn_history

The outer game loop (win/loss checks, turn advancement) lives in main.py.
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
    get_player_choice,
    save_turn_history,
    select_crisis,
)


def build_turn_graph() -> StateGraph:
    g = StateGraph(GameState)

    g.add_node("select_crisis",              select_crisis)
    g.add_node("generate_situation_briefing", generate_situation_briefing)
    g.add_node("get_player_choice",          get_player_choice)
    g.add_node("apply_base_effects",         apply_base_effects_node)
    g.add_node("classify_faction_reactions", classify_faction_reactions)
    g.add_node("compute_final_effects",      compute_final_effects)
    g.add_node("check_threshold_events",     check_threshold_events_node)
    g.add_node("generate_narrative",         generate_narrative)
    g.add_node("save_turn_history",          save_turn_history)

    g.set_entry_point("select_crisis")
    g.add_edge("select_crisis",              "generate_situation_briefing")
    g.add_edge("generate_situation_briefing", "get_player_choice")
    g.add_edge("get_player_choice",          "apply_base_effects")
    g.add_edge("apply_base_effects",         "classify_faction_reactions")
    g.add_edge("classify_faction_reactions", "compute_final_effects")
    g.add_edge("compute_final_effects",      "check_threshold_events")
    g.add_edge("check_threshold_events",     "generate_narrative")
    g.add_edge("generate_narrative",         "save_turn_history")
    g.add_edge("save_turn_history",          END)

    return g.compile()


turn_graph = build_turn_graph()


def save_graph_image(output_path: str = "graph.png") -> None:
    """Render the turn graph as a PNG using the Mermaid.ink API."""
    png_bytes = turn_graph.get_graph().draw_mermaid_png()
    with open(output_path, "wb") as f:
        f.write(png_bytes)
    print(f"Graph saved to {output_path}")
