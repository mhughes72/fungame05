"""
API route handlers.

Endpoints:
  GET  /api/health                  — health check
  POST /api/game                    — start new game, returns first crisis
  POST /api/game/{id}/resolve       — submit player choice/text, returns consequences + next crisis
  GET  /api/game/{id}               — get current state
  DELETE /api/game/{id}             — clean up session
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.session import create_session, delete_session, get_session, update_session_state
from game.engine import check_loss, determine_end_state
from graph.freeform_graph import post_freeform_graph, pre_freeform_graph
from graph.game_graph import post_classic_graph, pre_classic_graph
from graph.nodes import generate_end_summary, initialize_game

router = APIRouter()


# ── Request models ─────────────────────────────────────────────────────────────

class StartRequest(BaseModel):
    mode: str = "classic"


class ResolveRequest(BaseModel):
    choice_index: Optional[int] = None   # classic mode
    player_input: Optional[str] = None   # freeform mode


# ── Serializers ────────────────────────────────────────────────────────────────

def _extract_consequences(state: dict, mode: str) -> dict:
    """
    Capture consequence data from the post-turn state before the next pre-turn
    clears fields like active_crisis, advisor_reactions, headlines etc.
    """
    option_label = None
    if mode == "classic":
        crisis = state.get("active_crisis") or {}
        options = crisis.get("options", [])
        idx = state.get("player_choice_index")
        if idx is not None and 0 <= idx < len(options):
            option_label = options[idx]["label"]

    return {
        "selected_option_label":  option_label,
        "decision_interpretation": state.get("decision_interpretation"),
        "player_input":           state.get("player_input"),
        "final_stat_effects":     state.get("final_stat_effects") or {},
        "final_economy_effects":  state.get("final_economy_effects") or {},
        "final_faction_effects":  state.get("final_faction_effects") or {},
        "triggered_events":       state.get("triggered_events") or [],
        "advisor_reactions":      state.get("advisor_reactions") or [],
        "faction_narrative":      state.get("faction_narrative") or {},
        "headlines":              state.get("headlines") or [],
    }


def _serialize(
    state: dict,
    mode: str,
    consequences: Optional[dict] = None,
) -> dict:
    """Build an API response from game state. Excludes large internal fields."""
    crisis = state.get("active_crisis")
    crisis_data = None
    if crisis:
        options = [
            {"label": o["label"], "description": o["description"]}
            for o in crisis.get("options", [])
        ]
        crisis_data = {
            "crisis_id":   crisis["crisis_id"],
            "title":       crisis["title"],
            "description": crisis["description"],
            "options":     options,
        }

    return {
        "game_id":     state["game_id"],
        "mode":        mode,
        "current_turn": state["current_turn"],
        "max_turns":   state["max_turns"],
        "game_status": state["game_status"],
        "national_stats":  state["national_stats"],
        "economy_stats":   state["economy_stats"],
        "faction_support": state["faction_support"],
        "economy_drift_descriptions":   state.get("economy_drift_descriptions") or [],
        "faction_pressure_descriptions": state.get("faction_pressure_descriptions") or [],
        "active_crisis":      crisis_data,
        "situation_briefing": state.get("situation_briefing"),
        "end_state":    state.get("end_state"),
        "end_summary":  state.get("end_summary"),
        "loss_reason":  state.get("loss_reason"),
        "consequences": consequences,
    }


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/game")
async def start_game(body: StartRequest):
    if body.mode not in ("classic", "freeform"):
        raise HTTPException(
            status_code=400,
            detail=f"Unknown mode {body.mode!r}. Use 'classic' or 'freeform'.",
        )

    state = initialize_game({})

    if body.mode == "freeform":
        state = pre_freeform_graph.invoke(state)
    else:
        state = pre_classic_graph.invoke(state)

    create_session(state["game_id"], body.mode, state)
    return _serialize(state, body.mode)


@router.post("/game/{game_id}/resolve")
async def resolve_turn(game_id: str, body: ResolveRequest):
    session = get_session(game_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game not found.")

    state = dict(session.state)  # shallow copy so we don't mutate stored state
    mode  = session.mode

    # ── Apply player decision ──────────────────────────────────────────────────
    if mode == "classic":
        if body.choice_index is None:
            raise HTTPException(status_code=400, detail="choice_index required for classic mode.")
        crisis   = state.get("active_crisis") or {}
        n_opts   = len(crisis.get("options", []))
        if not (0 <= body.choice_index < n_opts):
            raise HTTPException(
                status_code=400,
                detail=f"choice_index must be 0–{n_opts - 1}.",
            )
        state["player_choice_index"] = body.choice_index
        state = post_classic_graph.invoke(state)
    else:
        if not body.player_input or not body.player_input.strip():
            raise HTTPException(status_code=400, detail="player_input required for freeform mode.")
        state["player_input"] = body.player_input.strip()
        state = post_freeform_graph.invoke(state)

    # ── Capture consequences before pre-turn clears fields ─────────────────────
    consequences = _extract_consequences(state, mode)

    # ── Win / loss check ───────────────────────────────────────────────────────
    # current_turn was incremented by save_turn_history / save_freeform_turn_history
    lost, reason = check_loss(
        state["national_stats"],
        state["faction_support"],
        state.get("economy_stats"),
    )
    if lost:
        state["game_status"] = "lost"
        state["loss_reason"]  = reason
    elif state["current_turn"] > state["max_turns"]:
        state["game_status"] = "won"
        end_state, _ = determine_end_state(
            state["national_stats"],
            state["faction_support"],
            state.get("economy_stats"),
        )
        state["end_state"] = end_state

    # ── Game over ──────────────────────────────────────────────────────────────
    if state["game_status"] != "active":
        # generate_end_summary returns a partial dict; merge into full state
        state = {**state, **generate_end_summary(state)}
        update_session_state(game_id, state)
        return _serialize(state, mode, consequences)

    # ── Next turn pre-phase ────────────────────────────────────────────────────
    if mode == "freeform":
        state = pre_freeform_graph.invoke(state)
    else:
        state = pre_classic_graph.invoke(state)

    update_session_state(game_id, state)
    return _serialize(state, mode, consequences)


@router.get("/game/{game_id}")
async def get_game_state(game_id: str):
    session = get_session(game_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Game not found.")
    return _serialize(session.state, session.mode)


@router.delete("/game/{game_id}")
async def delete_game(game_id: str):
    if not delete_session(game_id):
        raise HTTPException(status_code=404, detail="Game not found.")
    return {"ok": True}
