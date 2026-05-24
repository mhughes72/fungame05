"""
Economy sub-stat system.

Handles autonomous drift, faction pressure, crisis weighting, and composite score.
Runs at the start of each turn before crisis selection.
"""

import random
import operator as op_module
from typing import Any

from game.config import (
    CRISIS_BASE_WEIGHT,
    CRISIS_BOOST_WEIGHT,
    CRISIS_WEIGHT_RULES,
    ECONOMY_DRIFT_RULES,
    ECONOMY_RANDOM_RANGE,
    FACTION_PRESSURE_RULES,
    INVERTED_ECONOMY_STATS,
    STAT_MAX,
    STAT_MIN,
)

_OPS = {
    "<":  op_module.lt,
    ">":  op_module.gt,
    "==": op_module.eq,
    "<=": op_module.le,
    ">=": op_module.ge,
}


def _clamp(value: int) -> int:
    return max(STAT_MIN, min(STAT_MAX, value))


def _lookup(key: str, economy_stats: dict, national_stats: dict) -> int:
    """Resolve a key from either stat dict."""
    if key in economy_stats:
        return economy_stats[key]
    return national_stats.get(key, 0)


# ── Autonomous drift ───────────────────────────────────────────────────────────

def compute_economy_drift(
    economy_stats: dict[str, int],
    national_stats: dict[str, int],
) -> tuple[dict[str, int], list[str]]:
    """
    Apply drift rules and random variance to economy sub-stats.
    Returns (new_economy_stats, list of triggered rule descriptions).
    """
    deltas: dict[str, int] = {k: 0 for k in economy_stats}
    triggered_descriptions: list[str] = []

    for trigger_key, oper, threshold, affected_key, delta, description in ECONOMY_DRIFT_RULES:
        trigger_value = _lookup(trigger_key, economy_stats, national_stats)
        if _OPS[oper](trigger_value, threshold):
            deltas[affected_key] = deltas.get(affected_key, 0) + delta
            triggered_descriptions.append(description)

    # Random variance — the chance element
    for key in economy_stats:
        deltas[key] = deltas.get(key, 0) + random.randint(-ECONOMY_RANDOM_RANGE, ECONOMY_RANDOM_RANGE)

    new_stats = {
        k: _clamp(economy_stats[k] + deltas.get(k, 0))
        for k in economy_stats
    }
    return new_stats, triggered_descriptions


# ── Faction pressure ───────────────────────────────────────────────────────────

def compute_faction_pressure(
    economy_stats: dict[str, int],
    faction_support: dict[str, int],
) -> tuple[dict[str, int], list[str]]:
    """
    Apply passive faction support pressure from economy conditions.
    Returns (new_faction_support, list of triggered pressure descriptions).
    """
    deltas: dict[str, int] = {k: 0 for k in faction_support}
    triggered: list[str] = []

    for trigger_key, oper, threshold, faction_id, delta, description in FACTION_PRESSURE_RULES:
        trigger_value = economy_stats.get(trigger_key, 0)
        if _OPS[oper](trigger_value, threshold):
            deltas[faction_id] = deltas.get(faction_id, 0) + delta
            triggered.append(f"{faction_id} {delta:+d} ({description})")

    new_factions = {
        k: _clamp(faction_support[k] + deltas.get(k, 0))
        for k in faction_support
    }
    return new_factions, triggered


# ── Crisis weighting ───────────────────────────────────────────────────────────

def get_crisis_weights(
    economy_stats: dict[str, int],
    national_stats: dict[str, int],
    available_crises: list[dict],
) -> list[int]:
    """
    Return a weight for each available crisis based on current economy conditions.
    Contextually relevant crises are more likely to be selected.
    """
    weights: list[int] = []
    combined = {**national_stats, **economy_stats}

    for crisis in available_crises:
        cid = crisis["crisis_id"]
        conditions = CRISIS_WEIGHT_RULES.get(cid, [])
        if conditions and all(
            _OPS[oper](combined.get(key, 0), threshold)
            for key, oper, threshold in conditions
        ):
            weights.append(CRISIS_BOOST_WEIGHT)
        else:
            weights.append(CRISIS_BASE_WEIGHT)

    return weights


# ── Composite economy score ────────────────────────────────────────────────────

def composite_economy_score(economy_stats: dict[str, int]) -> int:
    """
    Single 0–100 health score for summary display.
    Inverted stats are flipped so high always means good.
    """
    scores = []
    for key, value in economy_stats.items():
        scores.append(100 - value if key in INVERTED_ECONOMY_STATS else value)
    return sum(scores) // len(scores)


# ── Apply economy effects ──────────────────────────────────────────────────────

def apply_economy_effects(
    economy_stats: dict[str, int],
    effects: dict[str, int],
) -> dict[str, int]:
    """Apply a delta dict to economy sub-stats with clamping."""
    return {
        k: _clamp(v + effects.get(k, 0))
        for k, v in economy_stats.items()
    }
