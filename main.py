"""
Entry point. Outer game loop — win/loss checks live here.
The turn graph handles one complete turn per invocation.
"""

import sys
import game.config as cfg

# ── CLI flags ─────────────────────────────────────────────────────────────────

if "--debug" in sys.argv:
    cfg.DEBUG = True

if "--list-scenarios" in sys.argv:
    from game.scenarios import list_scenarios
    list_scenarios()
    sys.exit(0)

if "--scenario" in sys.argv:
    idx = sys.argv.index("--scenario")
    if idx + 1 >= len(sys.argv) or sys.argv[idx + 1].startswith("--"):
        print("Error: --scenario requires a name. Use --list-scenarios to see options.")
        sys.exit(1)
    from game.scenarios import apply_scenario
    apply_scenario(sys.argv[idx + 1])

if "--graph" in sys.argv:
    from graph.game_graph import save_graph_image
    idx = sys.argv.index("--graph")
    output = (
        sys.argv[idx + 1]
        if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("--")
        else "graph.png"
    )
    save_graph_image(output)
    sys.exit(0)

# ── Imports (after scenario patch, before game starts) ────────────────────────

from dotenv import load_dotenv
load_dotenv()

from cli.display import (
    console,
    display_consequences,
    display_end_screen,
    display_loss_screen,
    display_start_screen,
)
from game.engine import check_loss, determine_end_state
from game.scenarios import get_active_scenario
from graph.game_graph import turn_graph
from graph.nodes import generate_end_summary, initialize_game


# ── Game loop ─────────────────────────────────────────────────────────────────

def run_game() -> None:
    display_start_screen(scenario=get_active_scenario())
    input("  [Press Enter to begin your tenure...]\n")

    state = initialize_game({})

    while state["game_status"] == "active":
        state = turn_graph.invoke(state)

        display_consequences(state)

        lost, reason = check_loss(
            state["national_stats"],
            state["faction_support"],
            state.get("economy_stats"),
        )
        if lost:
            state["game_status"] = "lost"
            state["loss_reason"]  = reason
            break

        if state["current_turn"] > state["max_turns"]:
            state["game_status"] = "won"
            end_state, _ = determine_end_state(
                state["national_stats"],
                state["faction_support"],
                state.get("economy_stats"),
            )
            state["end_state"] = end_state
            break

    state = generate_end_summary(state)

    if state["game_status"] == "lost":
        display_loss_screen(state)

    display_end_screen(state)

    console.print("\n  Thanks for playing. Veridia endures.\n")


if __name__ == "__main__":
    run_game()
