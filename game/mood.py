"""
Option C hybrid mood system.

Base mood is derived deterministically from faction support score.
One-turn event flags (set by crisis options) append context the LLM also sees.
"""

from game.config import MOOD_TIERS


def get_base_mood(support: int) -> str:
    for lo, hi, label in MOOD_TIERS:
        if lo <= support <= hi:
            return label
    return "uneasy"


def get_faction_mood_context(
    faction_id: str,
    support: int,
    event_flags: dict[str, list[str]],
) -> dict[str, str | list[str]]:
    """Return the full mood context sent to the LLM for a faction."""
    base = get_base_mood(support)
    flags = event_flags.get(faction_id, [])
    return {
        "base_mood": base,
        "recent_events": flags,  # one-turn contextual modifiers
    }
