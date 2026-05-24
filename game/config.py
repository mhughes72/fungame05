"""
All tuneable game constants. Adjust freely for balancing and tone experiments.
"""

import os

# ─── Debug ────────────────────────────────────────────────────────────────────
# Set via --debug CLI flag, or DEBUG=true in .env
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

# ─── Tone ─────────────────────────────────────────────────────────────────────
# Options: "serious" | "satirical" | "darkly_comic"
TONE = "darkly_comic"

# ─── Game length ──────────────────────────────────────────────────────────────
MAX_TURNS = 12
RECENT_EVENTS_WINDOW = 4  # past events carried as LLM context each turn

# ─── Starting national stats (all 0–100 scale) ────────────────────────────────
STARTING_NATIONAL_STATS: dict[str, int] = {
    "public_trust":             50,
    "unrest":                   50,
    "institutional_strength":   50,
    "media_freedom":            50,
    "international_reputation": 50,
}

# ─── Starting economy sub-stats (all 0–100 scale) ─────────────────────────────
# stock_market:    high = good  (investor confidence)
# unemployment:    high = bad   (inverted — more jobs = better)
# consumer_prices: high = bad   (inverted — lower prices = better)
# budget_deficit:  high = bad   (inverted — lower deficit = better)
STARTING_ECONOMY_STATS: dict[str, int] = {
    "stock_market":    50,
    "unemployment":    50,
    "consumer_prices": 50,
    "budget_deficit":  50,
}

# ─── Inverted economy stats (high = bad, displayed accordingly) ───────────────
INVERTED_ECONOMY_STATS: set[str] = {"unemployment", "consumer_prices", "budget_deficit"}

# ─── Starting faction support ─────────────────────────────────────────────────
STARTING_FACTION_SUPPORT: dict[str, int] = {
    "workers":                50,
    "business_elite":         50,
    "rural_bloc":             50,
    "urban_progressives":     50,
    "security_forces":        50,
    "national_conservatives": 50,
}

# ─── Stat bounds ──────────────────────────────────────────────────────────────
STAT_MIN = 0
STAT_MAX = 100

# ─── Economy drift rules ──────────────────────────────────────────────────────
# Applied automatically each turn before crisis selection.
# Format: (trigger_key, operator, threshold, affected_key, delta, description)
# trigger_key can be an economy_stat OR a national_stat.
ECONOMY_DRIFT_RULES: list[tuple[str, str, int, str, int, str]] = [
    # Stock market pressures
    ("unemployment",            ">", 60, "stock_market",    -2, "high unemployment spooks investors"),
    ("budget_deficit",          ">", 70, "stock_market",    -2, "fiscal fears hit markets"),
    ("international_reputation","<", 40, "stock_market",    -1, "foreign investor flight"),
    ("unrest",                  ">", 70, "stock_market",    -2, "political instability rattles markets"),
    # Unemployment pressures
    ("stock_market",    "<", 35, "unemployment",    +3, "recession drives layoffs"),
    ("consumer_prices", ">", 65, "unemployment",    +2, "cost crisis kills small businesses"),
    # Consumer price pressures
    ("budget_deficit",  ">", 60, "consumer_prices", +2, "deficit spending drives inflation"),
    ("unemployment",    ">", 65, "consumer_prices", +1, "wage pressure feeds into prices"),
    ("stock_market",    ">", 70, "consumer_prices", +1, "growth economy raises prices"),
    # Budget deficit pressures
    ("stock_market",    "<", 40, "budget_deficit",  +2, "lower tax revenues widen deficit"),
    ("unemployment",    ">", 60, "budget_deficit",  +2, "welfare spending widens deficit"),
    ("unrest",          ">", 65, "budget_deficit",  +1, "security spending widens deficit"),
]

# Random drift applied to each economy sub-stat each turn: ±ECONOMY_RANDOM_RANGE
# This is the chance element — identical decisions won't produce identical outcomes.
ECONOMY_RANDOM_RANGE: int = 1

# ─── Faction pressure rules ───────────────────────────────────────────────────
# Economy sub-stats exert passive pressure on faction support each turn.
# Format: (trigger_key, operator, threshold, faction_id, delta_per_turn, description)
FACTION_PRESSURE_RULES: list[tuple[str, str, int, str, int, str]] = [
    ("unemployment",    ">", 65, "workers",              -2, "mass unemployment"),
    ("unemployment",    ">", 55, "workers",              -1, "rising joblessness"),
    ("consumer_prices", ">", 65, "workers",              -2, "cost of living crisis"),
    ("consumer_prices", ">", 65, "rural_bloc",           -2, "fuel and food prices"),
    ("consumer_prices", ">", 55, "rural_bloc",           -1, "rising prices"),
    ("stock_market",    "<", 35, "business_elite",       -3, "market collapse"),
    ("stock_market",    "<", 50, "business_elite",       -1, "weak markets"),
    ("budget_deficit",  ">", 70, "business_elite",       -1, "fiscal recklessness"),
    ("unemployment",    ">", 70, "urban_progressives",   -1, "economic inequality"),
    ("budget_deficit",  ">", 75, "workers",              -1, "austerity risk"),
    ("budget_deficit",  ">", 75, "rural_bloc",           -1, "budget cuts threatening services"),
    # Positive pressures (good economy lifts all boats slightly)
    ("stock_market",    ">", 70, "business_elite",       +2, "strong markets"),
    ("unemployment",    "<", 35, "workers",              +1, "low unemployment"),
    ("consumer_prices", "<", 35, "workers",              +1, "affordable cost of living"),
    ("consumer_prices", "<", 35, "rural_bloc",           +1, "affordable fuel and food"),
]

# ─── Crisis weight rules ──────────────────────────────────────────────────────
# Economy conditions that boost the likelihood of specific crises being selected.
# Format: {crisis_id: [(trigger_key, operator, threshold), ...]}
# A crisis gets CRISIS_BOOST_WEIGHT if ALL its conditions hold, else CRISIS_BASE_WEIGHT.
CRISIS_WEIGHT_RULES: dict[str, list[tuple[str, str, int]]] = {
    "food_price_protests":  [("consumer_prices", ">", 60)],
    "investment_freeze":    [("stock_market",    "<", 45)],
    "rural_fuel_protests":  [("consumer_prices", ">", 60)],
    "public_sector_strike": [("unemployment",    ">", 55), ("budget_deficit", ">", 55)],
    "foreign_austerity":    [("budget_deficit",  ">", 65)],
    "housing_crisis":       [("consumer_prices", ">", 60), ("unemployment", ">", 50)],
}
CRISIS_BOOST_WEIGHT: int = 4   # weight for contextually relevant crisis
CRISIS_BASE_WEIGHT:  int = 1   # weight for all other crises

# ─── Faction mood tiers (deterministic base, Option C hybrid) ─────────────────
MOOD_TIERS: list[tuple[int, int, str]] = [
    (0,  20, "desperate"),
    (21, 40, "resentful"),
    (41, 60, "uneasy"),
    (61, 80, "cautiously supportive"),
    (81, 100, "enthusiastic"),
]

# ─── AI modifier table ────────────────────────────────────────────────────────
AI_MODIFIER_TABLE: dict[str, dict[str, int]] = {
    "loves_it":    {"high": 3,  "medium": 2,  "low": 1},
    "likes_it":    {"high": 2,  "medium": 1,  "low": 1},
    "neutral":     {"high": 0,  "medium": 0,  "low": 0},
    "dislikes_it": {"high": -2, "medium": -1, "low": -1},
    "hates_it":    {"high": -3, "medium": -2, "low": -1},
}

ALLOWED_REACTIONS: set[str] = {"loves_it", "likes_it", "neutral", "dislikes_it", "hates_it"}
ALLOWED_CONFIDENCE: set[str] = {"high", "medium", "low"}
MAX_AI_MODIFIER = 3
MIN_AI_MODIFIER = -3

# ─── Threshold events ─────────────────────────────────────────────────────────
# Conditions can reference national_stats, faction_support, OR economy_stats keys.
THRESHOLD_EVENTS: dict[str, dict] = {
    "coup_attempt": {
        "conditions": [
            ("security_forces",        "<", 25),
            ("unrest",                 ">", 70),
            ("institutional_strength", "<", 40),
        ],
        "description": (
            "Senior generals are meeting without you. "
            "The palace guard has quietly doubled its shifts."
        ),
        "stat_effects":    {"institutional_strength": -8, "unrest": 15},
        "economy_effects": {},
        "faction_effects": {"security_forces": 5, "urban_progressives": -10},
    },
    "general_strike": {
        "conditions": [
            ("workers", "<", 30),
            ("unrest",  ">", 65),
        ],
        "description": (
            "Workers across Veridia have walked off the job. "
            "Trains sit idle. Hospitals are running on skeleton crews."
        ),
        "stat_effects":    {"unrest": 10},
        "economy_effects": {"stock_market": -10, "unemployment": 8, "budget_deficit": 8},
        "faction_effects": {"workers": -5, "business_elite": -8},
    },
    "capital_flight": {
        "conditions": [
            ("business_elite", "<", 25),
            ("stock_market",   "<", 40),
        ],
        "description": (
            "Three of Veridia's largest companies have registered abroad overnight. "
            "The currency is in freefall."
        ),
        "stat_effects":    {"international_reputation": -8},
        "economy_effects": {"stock_market": -12, "budget_deficit": 10, "unemployment": 6},
        "faction_effects": {"business_elite": -10, "workers": -5},
    },
    "constitutional_crisis": {
        "conditions": [
            ("institutional_strength", "<", 25),
            ("public_trust",           "<", 40),
        ],
        "description": (
            "The Supreme Court has refused to implement three of your recent directives. "
            "The opposition is circulating an impeachment petition."
        ),
        "stat_effects":    {"institutional_strength": -10, "public_trust": -8},
        "economy_effects": {"stock_market": -5},
        "faction_effects": {"urban_progressives": -8, "national_conservatives": -5},
    },
    "mass_protest": {
        "conditions": [
            ("urban_progressives", "<", 30),
            ("media_freedom",      "<", 40),
            ("unrest",             ">", 60),
        ],
        "description": (
            "Hundreds of thousands have filled the capital's squares. "
            "They are politely but firmly calling for your resignation."
        ),
        "stat_effects":    {"unrest": 12, "public_trust": -8, "international_reputation": -6},
        "economy_effects": {"stock_market": -4},
        "faction_effects": {"urban_progressives": -8, "national_conservatives": 5},
    },
}

# ─── Loss conditions ──────────────────────────────────────────────────────────
# key can be national_stat, economy_stat, OR faction_support key
LOSS_CONDITIONS: list[tuple[str, str, int, str]] = [
    (
        "public_trust", "==", 0,
        "The last Veridian who trusted you was your mother, and she died disappointed. "
        "You resign before they can push you."
    ),
    (
        "unrest", "==", 100,
        "Veridia has achieved what political scientists call 'complete disorder.' "
        "Your motorcade cannot leave the palace."
    ),
    (
        "stock_market", "==", 0,
        "The stock exchange has closed indefinitely. The central bank governor has changed the locks. "
        "Economists will study this for decades."
    ),
    (
        "unemployment", "==", 100,
        "There is no one left working in Veridia. "
        "Including, shortly, you."
    ),
    (
        "institutional_strength", "==", 0,
        "There are no functioning institutions left to lead. "
        "Congratulations: you have governed yourself out of a country."
    ),
]

# ─── End-state scoring thresholds (first match wins, order matters) ───────────
# Keys can be national_stats, economy_stats, or faction_support.
END_STATE_RULES: list[tuple[str, dict[str, tuple[str, int]], str]] = [
    (
        "Reformist Survivor",
        {"public_trust": (">", 60), "institutional_strength": (">", 55), "media_freedom": (">", 55)},
        "You governed like a decent person, which is statistically unusual.",
    ),
    (
        "Business-Backed Technocrat",
        {"stock_market": (">", 65), "business_elite": (">", 60), "budget_deficit": ("<", 40)},
        "The markets love you. Everyone else is politely indifferent.",
    ),
    (
        "Populist Strongman",
        {"media_freedom": ("<", 35), "national_conservatives": (">", 65), "unrest": ("<", 35)},
        "Orderly. Efficient. The press is very complimentary, now that you've chosen the press.",
    ),
    (
        "Authoritarian Ruler",
        {"media_freedom": ("<", 30), "institutional_strength": ("<", 35)},
        "Veridia functions, in the sense that a fist is a functioning hand.",
    ),
    (
        "Crisis Manager",
        {"unrest": ("<", 45), "public_trust": (">", 40)},
        "You survived. Not through vision, exactly. More through stubborn presence.",
    ),
    (
        "Failed Democrat",
        {},  # fallback
        "History will be kind. History is usually wrong.",
    ),
]
