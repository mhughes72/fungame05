"""
Deterministic rules engine: base effects, AI modifier application,
threshold event checks, loss/win evaluation.
"""

import operator
from typing import Any

from game.config import (
    AI_MODIFIER_TABLE,
    ALLOWED_CONFIDENCE,
    ALLOWED_REACTIONS,
    END_STATE_RULES,
    LOSS_CONDITIONS,
    MAX_AI_MODIFIER,
    MIN_AI_MODIFIER,
    RECENT_EVENTS_WINDOW,
    STAT_MAX,
    STAT_MIN,
    THRESHOLD_EVENTS,
)

# ── Helpers ────────────────────────────────────────────────────────────────────

_OPS = {
    "<":  operator.lt,
    ">":  operator.gt,
    "==": operator.eq,
    "<=": operator.le,
    ">=": operator.ge,
}


def _clamp(value: int) -> int:
    return max(STAT_MIN, min(STAT_MAX, value))


def _check_condition(
    key: str,
    op: str,
    threshold: int,
    national_stats: dict[str, int],
    faction_support: dict[str, int],
) -> bool:
    value = national_stats.get(key) if key in national_stats else faction_support.get(key, 0)
    return _OPS[op](value, threshold)


# ── Base effects ───────────────────────────────────────────────────────────────

def apply_base_effects(
    national_stats: dict[str, int],
    faction_support: dict[str, int],
    stat_effects: dict[str, int],
    faction_effects: dict[str, int],
) -> tuple[dict[str, int], dict[str, int]]:
    """Return new stats and faction support after deterministic base effects."""
    new_stats = {k: _clamp(v + stat_effects.get(k, 0)) for k, v in national_stats.items()}
    new_factions = {k: _clamp(v + faction_effects.get(k, 0)) for k, v in faction_support.items()}
    return new_stats, new_factions


# ── AI modifier validation & application ──────────────────────────────────────

def validate_ai_reactions(
    raw: Any,
    affected_factions: list[str],
) -> dict[str, dict[str, str]] | None:
    """
    Validate LLM reaction output.
    Returns cleaned dict or None if invalid (triggers no-modifier fallback).
    """
    if not isinstance(raw, dict):
        return None

    cleaned: dict[str, dict[str, str]] = {}
    for faction_id in affected_factions:
        entry = raw.get(faction_id)
        if not isinstance(entry, dict):
            return None
        reaction   = entry.get("reaction", "").lower().strip()
        confidence = entry.get("confidence", "").lower().strip()
        reason     = entry.get("reason", "")

        if reaction not in ALLOWED_REACTIONS:
            return None
        if confidence not in ALLOWED_CONFIDENCE:
            return None
        if not isinstance(reason, str) or not reason:
            return None
        # Reason must not contain numeric stat references
        if any(c.isdigit() for c in reason):
            return None

        cleaned[faction_id] = {
            "reaction": reaction,
            "confidence": confidence,
            "reason": reason,
        }

    return cleaned


def compute_ai_modifiers(
    validated_reactions: dict[str, dict[str, str]],
) -> dict[str, int]:
    """Convert validated reaction classifications into bounded integer modifiers."""
    modifiers: dict[str, int] = {}
    for faction_id, entry in validated_reactions.items():
        raw_mod = AI_MODIFIER_TABLE[entry["reaction"]][entry["confidence"]]
        modifiers[faction_id] = max(MIN_AI_MODIFIER, min(MAX_AI_MODIFIER, raw_mod))
    return modifiers


def apply_ai_modifiers(
    faction_support: dict[str, int],
    modifiers: dict[str, int],
) -> dict[str, int]:
    """Apply bounded AI modifiers on top of already-updated faction support."""
    return {
        k: _clamp(v + modifiers.get(k, 0))
        for k, v in faction_support.items()
    }


# ── Threshold events ──────────────────────────────────────────────────────────

def check_thresholds(
    national_stats: dict[str, int],
    faction_support: dict[str, int],
    already_triggered: set[str],
) -> list[str]:
    """Return list of newly triggered threshold event keys."""
    triggered: list[str] = []
    for event_key, spec in THRESHOLD_EVENTS.items():
        if event_key in already_triggered:
            continue
        if all(
            _check_condition(key, op, val, national_stats, faction_support)
            for key, op, val in spec["conditions"]
        ):
            triggered.append(event_key)
    return triggered


def apply_threshold_effects(
    event_key: str,
    national_stats: dict[str, int],
    faction_support: dict[str, int],
) -> tuple[dict[str, int], dict[str, int]]:
    spec = THRESHOLD_EVENTS[event_key]
    stat_fx    = spec.get("stat_effects", {})
    faction_fx = spec.get("faction_effects", {})
    return apply_base_effects(national_stats, faction_support, stat_fx, faction_fx)


# ── Loss / win evaluation ─────────────────────────────────────────────────────

def check_loss(
    national_stats: dict[str, int],
    faction_support: dict[str, int],
) -> tuple[bool, str]:
    """Return (is_lost, reason_text)."""
    for key, op, val, text in LOSS_CONDITIONS:
        value = national_stats.get(key) if key in national_stats else faction_support.get(key, 100)
        if _OPS[op](value, val):
            return True, text
    return False, ""


def determine_end_state(
    national_stats: dict[str, int],
    faction_support: dict[str, int],
) -> tuple[str, str]:
    """Return (end_state_name, flavour_text) — first matching rule wins."""
    combined = {**national_stats, **faction_support}
    for name, conditions, flavour in END_STATE_RULES:
        if all(_OPS[op](combined.get(k, 0), v) for k, (op, v) in conditions.items()):
            return name, flavour
    # Should always match the fallback rule, but just in case:
    return "Failed Democrat", "History will be kind. History is usually wrong."


# ── Recent events window ──────────────────────────────────────────────────────

def update_recent_events(
    recent_events: list[str],
    new_events: list[str],
) -> list[str]:
    combined = recent_events + new_events
    return combined[-RECENT_EVENTS_WINDOW:]
