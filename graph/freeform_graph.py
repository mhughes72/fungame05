"""
Freeform mode turn graphs — split at the player input point.

Pre-turn  (runs before the player sees the crisis):
  run_economy_drift → generate_crisis

Post-turn (runs after player_input is set in state):
  evaluate_decision → check_threshold_events → generate_freeform_narrative →
  save_freeform_turn_history

The CLI main.py chains these with a blocking input() call between them.
The web API stores state between the two invocations.
"""

from langgraph.graph import StateGraph, END

from game.state import GameState
from graph.nodes import (
    check_threshold_events_node,
    run_economy_drift,
)
from graph.freeform_nodes import (
    evaluate_decision_node,
    generate_crisis_node,
    generate_freeform_narrative,
    save_freeform_turn_history,
)


def build_pre_freeform_graph():
    g = StateGraph(GameState)
    g.add_node("run_economy_drift", run_economy_drift)
    g.add_node("generate_crisis",   generate_crisis_node)
    g.set_entry_point("run_economy_drift")
    g.add_edge("run_economy_drift", "generate_crisis")
    g.add_edge("generate_crisis",   END)
    return g.compile()


def build_post_freeform_graph():
    g = StateGraph(GameState)
    g.add_node("evaluate_decision",           evaluate_decision_node)
    g.add_node("check_threshold_events",      check_threshold_events_node)
    g.add_node("generate_freeform_narrative", generate_freeform_narrative)
    g.add_node("save_freeform_turn_history",  save_freeform_turn_history)
    g.set_entry_point("evaluate_decision")
    g.add_edge("evaluate_decision",           "check_threshold_events")
    g.add_edge("check_threshold_events",      "generate_freeform_narrative")
    g.add_edge("generate_freeform_narrative", "save_freeform_turn_history")
    g.add_edge("save_freeform_turn_history",  END)
    return g.compile()


pre_freeform_graph  = build_pre_freeform_graph()
post_freeform_graph = build_post_freeform_graph()
