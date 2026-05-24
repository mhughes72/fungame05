"""
Scenario presets — named starting configurations that override and extend game/config.py.

Each scenario patches game.config in-place at startup via apply_scenario(), so config.py
remains the human-editable baseline. Scenarios layer on top; they never replace it.

Mutating the config lists/dicts in-place means all downstream modules (economy.py,
engine.py, etc.) see the patched values without any changes to their import statements.
"""

from typing import Any

# ── Scenario definitions ───────────────────────────────────────────────────────

SCENARIOS: dict[str, dict[str, Any]] = {

    "at_war": {
        "description": "Veridia is six weeks into a border conflict with its eastern neighbour.",
        "opening_text": (
            "The ceasefire lasted three years, which is about two years and eleven months longer "
            "than anyone expected. It ended on a Tuesday. You were briefed on Wednesday, "
            "which tells you everything about how the previous administration ran things.\n\n"
            "The country is mobilised, the budget is bleeding, and the generals have opinions."
        ),
        "stat_overrides": {
            "unrest":                   65,
            "international_reputation": 30,
            "institutional_strength":   45,
        },
        "economy_overrides": {
            "stock_market":   38,
            "budget_deficit": 68,
        },
        "faction_overrides": {
            "security_forces":    70,
            "workers":            38,
            "urban_progressives": 35,
        },
        "extra_drift_rules": [
            # (trigger_key, operator, threshold, affected_key, delta, description)
            ("unrest",                  ">", 55, "budget_deficit", +2, "war mobilisation spending"),
            ("international_reputation","<", 35, "stock_market",   -2, "war sanctions hit markets"),
            ("budget_deficit",          ">", 70, "stock_market",   -2, "war debt unnerves investors"),
        ],
        "extra_faction_pressure": [
            # (trigger_key, operator, threshold, faction_id, delta, description)
            ("budget_deficit", ">", 75, "workers",            -2, "war austerity cuts"),
            ("budget_deficit", ">", 75, "rural_bloc",         -2, "conscription and farm losses"),
            ("budget_deficit", ">", 80, "urban_progressives", -2, "civil spending gutted for war"),
        ],
        "extra_crisis_weights": {
            # crisis_id: [(trigger_key, operator, threshold), ...]
            "foreign_pressure":    [("international_reputation", "<", 40)],
            "military_demands":    [("unrest",                   ">", 55)],
            "intelligence_leak":   [("international_reputation", "<", 45)],
            "public_sector_strike":[("budget_deficit",           ">", 65)],
        },
    },

    "depression": {
        "description": "Veridia's economy has been in freefall for eighteen months. You inherited the wreckage.",
        "opening_text": (
            "The previous government described the situation as 'a period of structural adjustment.' "
            "The people described it as not being able to afford bread. "
            "The economists described it as the worst downturn in forty years.\n\n"
            "Everyone agrees it is your problem now."
        ),
        "stat_overrides": {
            "public_trust": 38,
            "unrest":       62,
        },
        "economy_overrides": {
            "stock_market":    22,
            "unemployment":    72,
            "consumer_prices": 68,
            "budget_deficit":  72,
        },
        "faction_overrides": {
            "workers":        28,
            "business_elite": 25,
            "rural_bloc":     33,
        },
        "extra_drift_rules": [
            ("stock_market",   "<", 30, "unemployment",    +3, "depression deepens layoffs"),
            ("unemployment",   ">", 70, "consumer_prices", +2, "stagflation feedback loop"),
            ("budget_deficit", ">", 75, "stock_market",    -3, "debt crisis spooks markets"),
        ],
        "extra_faction_pressure": [
            ("unemployment",    ">", 70, "workers",       -3, "mass unemployment crisis"),
            ("unemployment",    ">", 70, "rural_bloc",    -2, "rural economic collapse"),
            ("stock_market",    "<", 30, "business_elite",-4, "depression-level market crash"),
            ("consumer_prices", ">", 70, "workers",       -2, "cost of living catastrophe"),
        ],
        "extra_crisis_weights": {
            "food_price_protests":  [("consumer_prices", ">", 55)],
            "investment_freeze":    [("stock_market",    "<", 50)],
            "public_sector_strike": [("unemployment",    ">", 60)],
            "foreign_austerity":    [("budget_deficit",  ">", 60)],
            "housing_crisis":       [("consumer_prices", ">", 55), ("unemployment", ">", 60)],
            "rural_fuel_protests":  [("consumer_prices", ">", 60)],
        },
    },

    "honeymoon": {
        "description": "A landslide election, a strong mandate, and a country that — briefly — believes in you.",
        "opening_text": (
            "You won by eighteen points. The opposition is in disarray. "
            "The press is cautiously optimistic, which for the Veridian press is practically a ticker-tape parade.\n\n"
            "Enjoy this. It won't last."
        ),
        "stat_overrides": {
            "public_trust": 68,
            "unrest":       32,
            "media_freedom": 62,
        },
        "economy_overrides": {
            "stock_market": 62,
        },
        "faction_overrides": {
            "urban_progressives": 65,
            "workers":            62,
        },
        "extra_drift_rules": [],
        "extra_faction_pressure": [],
        "extra_crisis_weights": {},
    },

    "on_the_brink": {
        "description": "Everything is already failing. You have months, not years.",
        "opening_text": (
            "The last government didn't fall so much as dissolve. "
            "You were the only candidate willing to take the job, "
            "which should have been your first warning.\n\n"
            "The second warning was the state of the briefing files. "
            "The third warning is this meeting you're about to walk into."
        ),
        "stat_overrides": {
            "public_trust":             28,
            "unrest":                   72,
            "institutional_strength":   30,
            "media_freedom":            32,
            "international_reputation": 28,
        },
        "economy_overrides": {
            "stock_market":    28,
            "unemployment":    68,
            "consumer_prices": 65,
            "budget_deficit":  70,
        },
        "faction_overrides": {
            "workers":                28,
            "business_elite":         25,
            "rural_bloc":             30,
            "urban_progressives":     28,
            "security_forces":        35,
            "national_conservatives": 35,
        },
        "extra_drift_rules": [
            ("unrest", ">", 65, "budget_deficit", +2, "emergency security spending"),
        ],
        "extra_faction_pressure": [
            ("unemployment", ">", 65, "workers",       -2, "mass unemployment"),
            ("stock_market",  "<", 35, "business_elite",-2, "investor flight"),
        ],
        "extra_crisis_weights": {},
    },
}


# ── Active scenario tracking ───────────────────────────────────────────────────

_active: str | None = None


def get_active_scenario() -> dict[str, Any] | None:
    """Return the active scenario dict, or None if playing default."""
    if _active is None:
        return None
    return SCENARIOS.get(_active)


# ── Apply scenario ─────────────────────────────────────────────────────────────

def apply_scenario(name: str) -> None:
    """
    Patch game.config in-place with scenario overrides.
    Must be called before initialize_game runs.
    All patched structures are mutable (dicts/lists), so downstream modules
    that imported them by reference see the updated values automatically.
    """
    global _active

    preset = SCENARIOS.get(name)
    if not preset:
        available = ", ".join(SCENARIOS)
        raise SystemExit(f"Unknown scenario '{name}'. Available: {available}")

    import game.config as cfg

    # Starting stat overrides — only specified keys change, rest stay at config defaults
    cfg.STARTING_NATIONAL_STATS.update(preset.get("stat_overrides", {}))
    cfg.STARTING_ECONOMY_STATS.update(preset.get("economy_overrides", {}))
    cfg.STARTING_FACTION_SUPPORT.update(preset.get("faction_overrides", {}))

    # Rule extensions — scenario rules append on top of config baseline
    cfg.ECONOMY_DRIFT_RULES.extend(preset.get("extra_drift_rules", []))
    cfg.FACTION_PRESSURE_RULES.extend(preset.get("extra_faction_pressure", []))

    # Crisis weight overrides — scenario entries win over defaults for the same crisis_id
    cfg.CRISIS_WEIGHT_RULES.update(preset.get("extra_crisis_weights", {}))

    _active = name


# ── List scenarios ─────────────────────────────────────────────────────────────

def list_scenarios() -> None:
    print("\nAvailable scenarios:\n")
    for name, preset in SCENARIOS.items():
        print(f"  --scenario {name}")
        print(f"  {preset['description']}\n")
