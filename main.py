"""
Entry point. Outer game loop — win/loss checks live here.
The turn graph handles one complete turn per invocation.
"""

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
from graph.game_graph import turn_graph
from graph.nodes import generate_end_summary, initialize_game


def run_game() -> None:
    display_start_screen()
    input("  [Press Enter to begin your tenure...]\n")

    # Initialize state
    state = initialize_game({})

    # Game loop — one turn per iteration
    while state["game_status"] == "active":
        # Run one full turn through the LangGraph
        state = turn_graph.invoke(state)

        # Display consequences after the turn completes
        display_consequences(state)

        # Check loss conditions
        lost, reason = check_loss(state["national_stats"], state["faction_support"])
        if lost:
            state["game_status"] = "lost"
            state["loss_reason"]  = reason
            break

        # Check win condition
        if state["current_turn"] > state["max_turns"]:
            state["game_status"] = "won"
            end_state, _ = determine_end_state(state["national_stats"], state["faction_support"])
            state["end_state"] = end_state
            break

    # Generate and display end summary
    state = generate_end_summary(state)

    if state["game_status"] == "lost":
        display_loss_screen(state)

    display_end_screen(state)

    console.print("\n  Thanks for playing. Veridia endures.\n")


if __name__ == "__main__":
    import sys
    import game.config as cfg

    if "--debug" in sys.argv:
        cfg.DEBUG = True

    if "--graph" in sys.argv:
        from graph.game_graph import save_graph_image
        idx = sys.argv.index("--graph")
        output = (
            sys.argv[idx + 1]
            if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("--")
            else "graph.png"
        )
        save_graph_image(output)
    else:
        run_game()
