"""
All LLM prompt templates.

Tone is controlled by TONE in game/config.py.
To change tone: update TONE and the TONE_INSTRUCTIONS dict below.
All prompts call get_tone_instruction() so the change propagates everywhere.
"""

import json
from game.config import TONE
from game.mood import get_faction_mood_context

# ── Tone instructions injected into every system prompt ───────────────────────

TONE_INSTRUCTIONS: dict[str, str] = {
    "serious": (
        "Write in a grave, realistic tone appropriate for serious political drama. "
        "Be measured and authoritative. No jokes."
    ),
    "satirical": (
        "Write in a sharp, satirical tone. Expose political absurdity with wit. "
        "Think political cartoonist with a thesaurus."
    ),
    "darkly_comic": (
        "Write in a darkly comic tone — like a political novel written by someone who has "
        "lost faith in democracy but retained their sense of humour. "
        "Events are genuinely dire; the prose acknowledges this with wry, exhausted irony. "
        "Think: the lights are going out and someone is making a very good joke about it. "
        "Keep it sharp, not silly. Tragedy with footnotes."
    ),
}


def get_tone_instruction() -> str:
    return TONE_INSTRUCTIONS.get(TONE, TONE_INSTRUCTIONS["darkly_comic"])


# ── Faction context builder ────────────────────────────────────────────────────

def build_faction_context(
    faction_id: str,
    persona: dict,
    support: int,
    event_flags: dict[str, list[str]],
) -> dict:
    mood_ctx = get_faction_mood_context(faction_id, support, event_flags)
    return {
        "faction_id": faction_id,
        "name": persona["name"],
        "core_values": persona["core_values"],
        "likes": persona["likes"],
        "dislikes": persona["dislikes"],
        "historical_grievances": persona["historical_grievances"],
        "current_support": support,
        "current_mood": mood_ctx["base_mood"],
        "recent_events": mood_ctx["recent_events"],
    }


# ── Situation briefing ─────────────────────────────────────────────────────────

def situation_briefing_prompt(
    turn: int,
    max_turns: int,
    national_stats: dict[str, int],
    faction_support: dict[str, int],
    recent_events: list[str],
) -> list[dict]:
    system = (
        f"You are the narrator of a turn-based political simulator set in the fictional "
        f"Republic of Veridia. {get_tone_instruction()} "
        f"You must write only about the fictional game world. "
        f"Never reference real-world countries, politicians, or events."
    )
    user = (
        f"Write a 2–3 sentence situation briefing for Month {turn} of {max_turns}.\n\n"
        f"Current national stats (0–100 scale):\n{json.dumps(national_stats, indent=2)}\n\n"
        f"Faction support (0–100 scale):\n{json.dumps(faction_support, indent=2)}\n\n"
        f"Recent notable events:\n{json.dumps(recent_events, indent=2)}\n\n"
        "Describe the current political atmosphere. Be specific, not generic. "
        "Name the most pressing tensions. Do NOT mention stat numbers directly."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


# ── Faction reaction classification ───────────────────────────────────────────

REACTION_SCHEMA_DESCRIPTION = """
Return a JSON object where each key is a faction_id from the affected_factions list.
Each value must be an object with exactly three fields:
  "reaction": one of: loves_it | likes_it | neutral | dislikes_it | hates_it
  "confidence": one of: high | medium | low
  "reason": a single sentence explaining why (no numbers, no stat changes, no new factions)

Example:
{
  "workers": {"reaction": "loves_it", "confidence": "high", "reason": "The policy directly addresses their core demand for food affordability."},
  "business_elite": {"reaction": "dislikes_it", "confidence": "medium", "reason": "They worry the cost will be passed to them through future taxes."}
}
"""


def reaction_classification_prompt(
    crisis_title: str,
    selected_option_label: str,
    selected_option_description: str,
    policy_tags: list[str],
    affected_factions: list[str],
    faction_contexts: list[dict],
    national_stats: dict[str, int],
    recent_events: list[str],
) -> list[dict]:
    system = (
        "You are a political analyst for the Republic of Veridia, a fictional country. "
        "Your job is to classify how each faction emotionally reacts to a government decision, "
        "given their values, current mood, and recent history. "
        "You must return only the allowed reaction categories. "
        "You must not invent new factions. "
        "You must not declare win/loss outcomes. "
        "You must not include numerical stat changes in your reasons. "
        f"\n\n{REACTION_SCHEMA_DESCRIPTION}"
    )
    user = (
        f"Crisis: {crisis_title}\n"
        f"Decision taken: {selected_option_label} — {selected_option_description}\n"
        f"Policy tags: {', '.join(policy_tags)}\n\n"
        f"Current national mood (for context):\n{json.dumps(national_stats, indent=2)}\n\n"
        f"Recent notable events:\n{json.dumps(recent_events, indent=2)}\n\n"
        f"Faction contexts:\n{json.dumps(faction_contexts, indent=2)}\n\n"
        f"Classify the reaction of each of these factions: {', '.join(affected_factions)}"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


# ── Advisor reactions ─────────────────────────────────────────────────────────

ADVISORS = [
    {
        "name": "Finance Minister",
        "bias": "economic stability, budget discipline, investor confidence",
        "personality": "dry, numbers-obsessed, quietly despairing",
    },
    {
        "name": "Security Chief",
        "bias": "order, control, intelligence, emergency powers",
        "personality": "direct, slightly menacing, allergic to nuance",
    },
    {
        "name": "Reform Advisor",
        "bias": "democracy, civil liberties, anti-corruption, public trust",
        "personality": "earnest, increasingly frustrated, tries not to lecture",
    },
    {
        "name": "Party Strategist",
        "bias": "faction management, popularity, messaging, political survival",
        "personality": "cheerfully cynical, sees everything as a communications problem",
    },
]


def advisor_reactions_prompt(
    crisis_title: str,
    selected_option_label: str,
    final_stat_effects: dict[str, int],
    final_faction_effects: dict[str, int],
    national_stats: dict[str, int],
) -> list[dict]:
    system = (
        f"You are writing dialogue for four political advisors in a fictional political simulator. "
        f"{get_tone_instruction()} "
        "Each advisor has a distinct bias and personality. "
        "Write one short comment per advisor (1–2 sentences). "
        "The comments should reflect their bias and react to the specific decision and its effects. "
        "Return a JSON array: [{\"name\": \"...\", \"reaction\": \"...\"}, ...]"
    )
    user = (
        f"Crisis just resolved: {crisis_title}\n"
        f"Decision taken: {selected_option_label}\n"
        f"Final effects on national stats: {json.dumps(final_stat_effects)}\n"
        f"Final effects on factions: {json.dumps(final_faction_effects)}\n"
        f"Current national stats: {json.dumps(national_stats)}\n\n"
        f"Advisors and their characters:\n{json.dumps(ADVISORS, indent=2)}\n\n"
        "Write a short, in-character reaction for each advisor."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


# ── Faction narrative reactions ────────────────────────────────────────────────

def faction_narrative_prompt(
    crisis_title: str,
    selected_option_label: str,
    validated_reactions: dict[str, dict[str, str]],
    faction_personas: dict[str, dict],
    final_faction_effects: dict[str, int],
) -> list[dict]:
    system = (
        f"You are writing brief faction response statements for a fictional political simulator. "
        f"{get_tone_instruction()} "
        "Each faction should respond in a voice consistent with their character. "
        "Return a JSON object: {\"faction_id\": \"one-sentence reaction\", ...}"
    )
    affected_faction_data = {
        fid: {
            "name": faction_personas[fid]["name"],
            "reaction_category": validated_reactions[fid]["reaction"],
            "reason": validated_reactions[fid]["reason"],
            "support_change": final_faction_effects.get(fid, 0),
        }
        for fid in validated_reactions
        if fid in faction_personas
    }
    user = (
        f"Crisis: {crisis_title}\nDecision: {selected_option_label}\n\n"
        f"Faction data:\n{json.dumps(affected_faction_data, indent=2)}\n\n"
        "Write a one-sentence public reaction for each faction in their own voice."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


# ── Media headlines ────────────────────────────────────────────────────────────

OUTLETS = [
    {"id": "veridian_times",  "name": "The Veridian Times",  "slant": "mainstream institutional, cautiously establishment"},
    {"id": "peoples_herald",  "name": "People's Herald",     "slant": "labour-aligned, working-class sympathies"},
    {"id": "market_ledger",   "name": "Market Ledger",       "slant": "business-focused, pro-investor"},
    {"id": "national_voice",  "name": "National Voice",      "slant": "nationalist, sovereignty-focused"},
    {"id": "free_signal",     "name": "Free Signal",         "slant": "independent reformist, anti-corruption"},
]


def headlines_prompt(
    crisis_title: str,
    selected_option_label: str,
    final_stat_effects: dict[str, int],
    final_faction_effects: dict[str, int],
    triggered_events: list[str],
) -> list[dict]:
    system = (
        f"You are writing fictional newspaper headlines for five outlets in the Republic of Veridia. "
        f"{get_tone_instruction()} "
        "Each outlet has its own editorial slant. "
        "Headlines should be punchy, distinct, and reflect each outlet's bias. "
        "Return a JSON array of objects: [{\"outlet\": \"outlet_name\", \"headline\": \"...\"}]"
    )
    user = (
        f"This month's major event: {crisis_title}\n"
        f"Government's decision: {selected_option_label}\n"
        f"Net effects: stats {json.dumps(final_stat_effects)}, factions {json.dumps(final_faction_effects)}\n"
        f"Additional events triggered: {json.dumps(triggered_events)}\n\n"
        f"Outlets:\n{json.dumps(OUTLETS, indent=2)}\n\n"
        "Write one headline per outlet."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


# ── End-of-game summary ───────────────────────────────────────────────────────

def end_summary_prompt(
    end_state: str,
    end_state_flavour: str,
    final_stats: dict[str, int],
    final_factions: dict[str, int],
    turn_history: list[dict],
    won: bool,
) -> list[dict]:
    system = (
        f"You are writing the closing chapter of a political memoir for a fictional leader of Veridia. "
        f"{get_tone_instruction()} "
        "This is the end of their first year in power. "
        "Be specific about key decisions they made. "
        "Never reference real-world events or politicians."
    )
    key_decisions = [
        f"Month {t['turn_number']}: {t['crisis_title']} — chose '{t['selected_option']}'"
        for t in turn_history
    ]
    user = (
        f"Outcome: {'Survived the year' if won else 'Fell from power'}\n"
        f"End state: {end_state}\n"
        f"End state assessment: {end_state_flavour}\n\n"
        f"Final national stats: {json.dumps(final_stats)}\n"
        f"Final faction support: {json.dumps(final_factions)}\n\n"
        f"Key decisions this year:\n" + "\n".join(key_decisions) + "\n\n"
        "Write a 3–4 sentence summary of their year in power. "
        "Reference at least two specific decisions. "
        "End with a verdict on what kind of leader they were."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
