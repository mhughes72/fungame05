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

# ─── Starting values (all 0–100 scale) ───────────────────────────────────────
STARTING_NATIONAL_STATS: dict[str, int] = {
    "public_trust":             50,
    "unrest":                   50,
    "economy":                  50,
    "budget":                   50,
    "institutional_strength":   50,
    "media_freedom":            50,
    "international_reputation": 50,
}

STARTING_FACTION_SUPPORT: dict[str, int] = {
    "workers":               50,
    "business_elite":        50,
    "rural_bloc":            50,
    "urban_progressives":    50,
    "security_forces":       50,
    "national_conservatives": 50,
}

# ─── Stat bounds ──────────────────────────────────────────────────────────────
STAT_MIN = 0
STAT_MAX = 100

# ─── Faction mood tiers (deterministic base, Option C hybrid) ─────────────────
# (min_support, max_support, mood_label)
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
# Conditions check both national_stats and faction_support keys.
# operator: "<" | ">" | "==" | "<=" | ">="
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
        "stat_effects":    {"economy": -10, "budget": -8, "unrest": 10},
        "faction_effects": {"workers": -5, "business_elite": -8},
    },
    "capital_flight": {
        "conditions": [
            ("business_elite", "<", 25),
            ("economy",        "<", 40),
        ],
        "description": (
            "Three of Veridia's largest companies have registered abroad overnight. "
            "The currency is in freefall."
        ),
        "stat_effects":    {"economy": -12, "budget": -10, "international_reputation": -8},
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
        "faction_effects": {"urban_progressives": -8, "national_conservatives": 5},
    },
}

# ─── Loss conditions ──────────────────────────────────────────────────────────
# (key, operator, value, flavour_text)
# key can be a national_stat OR a faction_support key
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
        "economy", "==", 0,
        "The treasury is empty. The central bank governor has changed the locks. "
        "Economists will study this for decades."
    ),
    (
        "institutional_strength", "==", 0,
        "There are no functioning institutions left to lead. "
        "Congratulations: you have governed yourself out of a country."
    ),
]

# ─── End-state scoring thresholds (first match wins, order matters) ───────────
# Keys are national_stats or faction_support. All conditions must hold.
END_STATE_RULES: list[tuple[str, dict[str, tuple[str, int]], str]] = [
    (
        "Reformist Survivor",
        {"public_trust": (">", 60), "institutional_strength": (">", 55), "media_freedom": (">", 55)},
        "You governed like a decent person, which is statistically unusual.",
    ),
    (
        "Business-Backed Technocrat",
        {"economy": (">", 65), "business_elite": (">", 60), "budget": (">", 55)},
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
