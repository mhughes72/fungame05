"""
Faction persona definitions for Veridia.
These are fed verbatim to the LLM for reaction classification.
"""

from typing import Any

FACTION_PERSONAS: dict[str, dict[str, Any]] = {
    "workers": {
        "name": "The Workers",
        "core_values": [
            "fair wages", "food affordability", "job security",
            "social programs", "union rights", "cost of living",
        ],
        "likes": [
            "food subsidies", "wage protections", "public healthcare",
            "union negotiations", "public spending",
        ],
        "dislikes": [
            "austerity", "privatization", "police crackdowns",
            "tax cuts for business", "cost-of-living increases",
        ],
        "historical_grievances": [
            "Three consecutive governments promised wage reform and delivered nothing.",
            "Workers believe economic recoveries always benefit the elite first.",
            "The last austerity package was sold as 'temporary' in 2019. It was not.",
        ],
    },
    "business_elite": {
        "name": "The Business Elite",
        "core_values": [
            "low taxes", "market stability", "investor confidence",
            "deregulation", "privatization", "contract enforcement",
        ],
        "likes": [
            "tax incentives", "deregulation", "privatization",
            "foreign investment", "budget discipline", "austerity",
        ],
        "dislikes": [
            "price controls", "nationalization", "union power",
            "unpredictable policy", "public spending sprees", "corruption investigations",
        ],
        "historical_grievances": [
            "Business leaders are routinely scapegoated during economic crises.",
            "Investors cite policy unpredictability as Veridia's core problem.",
            "The last nationalization destroyed three companies and compensated no one.",
        ],
    },
    "rural_bloc": {
        "name": "The Rural Bloc",
        "core_values": [
            "fuel affordability", "local autonomy", "agricultural support",
            "infrastructure investment", "respect from the capital", "tradition",
        ],
        "likes": [
            "fuel subsidies", "rural infrastructure", "farm subsidies",
            "local control", "lower fuel taxes",
        ],
        "dislikes": [
            "urban favoritism", "fuel taxes", "centralized mandates",
            "environmental regulations that hurt farming", "being ignored",
        ],
        "historical_grievances": [
            "The capital has deferred rural road repairs for eleven years.",
            "Rural hospitals were 'temporarily' closed in 2020. They remain closed.",
            "Rural voters feel the government only remembers them during elections.",
        ],
    },
    "urban_progressives": {
        "name": "The Urban Progressives",
        "core_values": [
            "democracy", "civil rights", "anti-corruption",
            "climate policy", "police reform", "press freedom", "equality",
        ],
        "likes": [
            "transparency", "anti-corruption measures", "police oversight",
            "climate action", "civil liberties", "media freedom",
        ],
        "dislikes": [
            "police crackdowns", "emergency powers", "media restriction",
            "nationalist messaging", "corruption cover-ups", "authoritarianism",
        ],
        "historical_grievances": [
            "Reform groups believe previous leaders protected corrupt insiders.",
            "Student groups distrust police after the 2021 protest dispersals.",
            "Urban progressives feel the government pays lip service to democracy.",
        ],
    },
    "security_forces": {
        "name": "The Security Forces",
        "core_values": [
            "order", "authority", "national security",
            "adequate resources", "command respect", "institutional loyalty",
        ],
        "likes": [
            "emergency powers", "increased funding", "public order mandates",
            "clear command structures", "nationalist messaging",
        ],
        "dislikes": [
            "police reform commissions", "budget cuts to security",
            "politicians blaming security forces for unrest",
            "civilian oversight", "public criticism after crackdowns",
        ],
        "historical_grievances": [
            "Security forces were blamed for the 2021 protest deaths despite acting on orders.",
            "Equipment funding was cut three years running while deployment demands rose.",
            "Officers resent being used as political shields then abandoned.",
        ],
    },
    "national_conservatives": {
        "name": "The National Conservatives",
        "core_values": [
            "national sovereignty", "tradition", "law and order",
            "border control", "skepticism of foreign influence", "cultural identity",
        ],
        "likes": [
            "nationalist messaging", "border enforcement", "law and order policies",
            "skepticism of international bodies", "cultural tradition",
        ],
        "dislikes": [
            "foreign aid conditions", "international institutions",
            "urban progressive reforms", "immigration", "what they call 'globalism'",
        ],
        "historical_grievances": [
            "They believe foreign institutions have systematically weakened Veridian sovereignty.",
            "National conservatives distrust any reform framed as internationally influenced.",
            "They feel culturally sidelined by urban elites and the media.",
        ],
    },
}
