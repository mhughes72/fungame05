"""LangGraph state definition. Everything the graph nodes read and write."""

from typing import Any, Optional
from typing_extensions import TypedDict


class GameState(TypedDict):
    # ── Meta ──────────────────────────────────────────────────────────────────
    game_id: str
    current_turn: int       # 1-based
    max_turns: int
    game_status: str        # "active" | "won" | "lost"
    end_state: Optional[str]
    loss_reason: Optional[str]

    # ── Core game data ────────────────────────────────────────────────────────
    national_stats: dict[str, int]
    faction_support: dict[str, int]
    faction_personas: dict[str, dict[str, Any]]
    # Option C hybrid mood: one-turn event flags appended per turn, reset each turn
    faction_event_flags: dict[str, list[str]]

    # ── Turn data ─────────────────────────────────────────────────────────────
    active_crisis: Optional[dict[str, Any]]
    used_crisis_ids: list[str]
    player_choice_index: Optional[int]   # 0-based index into active_crisis["options"]

    # ── Effects computed during a turn ────────────────────────────────────────
    base_stat_effects: Optional[dict[str, int]]
    base_faction_effects: Optional[dict[str, int]]
    ai_reactions: Optional[dict[str, dict[str, str]]]   # {faction_id: {reaction, confidence, reason}}
    ai_modifiers: Optional[dict[str, int]]              # {faction_id: bounded delta}
    final_stat_effects: Optional[dict[str, int]]
    final_faction_effects: Optional[dict[str, int]]
    triggered_events: list[str]        # threshold event keys triggered this turn

    # ── LLM narrative outputs (display only, never alter state) ───────────────
    situation_briefing: Optional[str]
    advisor_reactions: Optional[list[dict[str, str]]]   # [{name, reaction}]
    faction_narrative: Optional[dict[str, str]]         # {faction_id: reaction_text}
    headlines: Optional[list[str]]
    end_summary: Optional[str]

    # ── History ───────────────────────────────────────────────────────────────
    recent_events: list[str]    # rolling window for LLM context
    turn_history: list[dict[str, Any]]
