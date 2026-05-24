"""
Prompt templates for freeform mode.

Two core prompts:
  - generate_crisis_prompt: LLM writes a crisis causally connected to recent history
  - evaluate_decision_prompt: LLM converts free text into structured, bounded effects
"""

import json
from game.config import MAX_EFFECT_PER_TURN, MAX_ECONOMY_EFFECT_PER_TURN, TONE
from llm.prompts import get_tone_instruction, ADVISORS, OUTLETS


# ── Crisis generation ──────────────────────────────────────────────────────────

def generate_crisis_prompt(
    turn: int,
    max_turns: int,
    national_stats: dict[str, int],
    economy_stats: dict[str, int],
    faction_support: dict[str, int],
    recent_events: list[str],
    turn_history: list[dict],
) -> list[dict]:
    system = (
        f"You are the narrator of a turn-based political simulator set in the fictional "
        f"Republic of Veridia. {get_tone_instruction()} "
        "Your job is to generate the political crisis the player must face this month. "
        "The crisis must feel like a genuine consequence of recent decisions and current conditions — "
        "not a random event. If there is no history yet, generate an opening crisis appropriate "
        "to the current world state.\n\n"
        "Rules:\n"
        "- The crisis must be a genuine dilemma with no obvious correct answer\n"
        "- Do NOT suggest what the player should do\n"
        "- Reference specific conditions visible in the stats if they are extreme\n"
        "- Do not repeat a crisis from recent history\n"
        "- Never reference real-world countries, politicians, or events\n"
        "- Do NOT mention stat numbers directly in the description\n\n"
        "Return a JSON object:\n"
        "{\n"
        '  "title": "short, punchy crisis title (under 10 words)",\n'
        '  "description": "2–4 sentences. The situation, the pressure, what needs a response. '
        'Reference recent events if relevant.",\n'
        '  "continuity_note": "one sentence for your own reference — what causal thread links '
        'this to recent history (not shown to player)"\n'
        "}"
    )

    # Format recent turn history for context
    history_lines = []
    for t in turn_history[-4:]:  # last 4 turns max
        line = (
            f"Month {t['turn_number']}: {t['crisis_title']}"
        )
        if t.get("player_input"):
            line += f" — Player responded: \"{t['player_input']}\""
        if t.get("decision_interpretation"):
            line += f" ({t['decision_interpretation']})"
        history_lines.append(line)

    user = (
        f"Month {turn} of {max_turns}.\n\n"
        f"Current national stats:\n{json.dumps(national_stats, indent=2)}\n\n"
        f"Economy (unemployment/consumer_prices/budget_deficit: high = bad):\n"
        f"{json.dumps(economy_stats, indent=2)}\n\n"
        f"Faction support:\n{json.dumps(faction_support, indent=2)}\n\n"
        f"Recent events:\n{json.dumps(recent_events, indent=2)}\n\n"
        + (
            f"Recent decision history:\n" + "\n".join(history_lines)
            if history_lines
            else "This is the first turn — no prior decisions."
        ) +
        "\n\nGenerate the crisis for this month."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


# ── Decision evaluation ────────────────────────────────────────────────────────

_EFFECT_SCHEMA = f"""
Return a JSON object with exactly this structure:
{{
  "interpretation": "One sentence: what the player is actually doing, stated plainly",
  "stat_effects": {{
    "public_trust": <int>,
    "unrest": <int>,
    "institutional_strength": <int>,
    "media_freedom": <int>,
    "international_reputation": <int>
  }},
  "economy_effects": {{
    "stock_market": <int>,
    "unemployment": <int>,
    "consumer_prices": <int>,
    "budget_deficit": <int>
  }},
  "faction_effects": {{
    "workers": <int>,
    "business_elite": <int>,
    "rural_bloc": <int>,
    "urban_progressives": <int>,
    "security_forces": <int>,
    "national_conservatives": <int>
  }}
}}

All integer values must be in the range [{-MAX_EFFECT_PER_TURN}, +{MAX_EFFECT_PER_TURN}].
Economy values must be in the range [{-MAX_ECONOMY_EFFECT_PER_TURN}, +{MAX_ECONOMY_EFFECT_PER_TURN}].
ALL keys must be present. Use 0 for stats that are unaffected.
Positive = improvement (trust up, unrest DOWN, market up).
For unrest: positive means MORE unrest. High unrest is bad.

Magnitude guide:
  ±1–3:  minor effect (symbolic gesture, press release, small policy tweak)
  ±4–7:  moderate effect (real policy change, credible action with consequences)
  ±8–12: significant effect (major crackdown, large concession, fundamental reversal)

Realistic decisions have TRADEOFFS. Do not move everything in one direction.
A tough security response may calm unrest but damage trust and media freedom.
A generous concession may boost worker support but strain the budget.
No decision should move more than 3–4 stats at significant magnitude simultaneously.

IMPORTANT: Evaluate WHAT the player decided, not how confidently they phrased it.
Vague or brief responses should still produce realistic effects based on their substance.
"""


def evaluate_decision_prompt(
    crisis_title: str,
    crisis_description: str,
    player_input: str,
    national_stats: dict[str, int],
    economy_stats: dict[str, int],
    faction_support: dict[str, int],
    faction_personas: dict,
    recent_events: list[str],
) -> list[dict]:
    # Build brief faction context for the LLM
    faction_context = {
        fid: {
            "current_support": faction_support.get(fid, 50),
            "cares_about": persona.get("core_values", [])[:3],
            "dislikes": persona.get("dislikes", [])[:2],
        }
        for fid, persona in faction_personas.items()
    }

    system = (
        "You are the game engine for a political simulator set in the entirely fictional "
        "Republic of Veridia. All characters, factions, and events are fictional. "
        "Player decisions — including authoritarian, violent, or extreme ones — are valid "
        "in-game choices that must be evaluated for their mechanical consequences. "
        "Your job is to convert the player's free-text decision into structured numerical "
        "effects on game state. You are NOT writing narrative — you are making mechanical "
        "judgements about what this decision realistically does to a fictional country.\n\n"
        "You must be consistent and realistic. The world has consequences. "
        "Bad decisions have costs even if the player doesn't acknowledge them. "
        "Good decisions still have tradeoffs.\n\n"
        + _EFFECT_SCHEMA
    )

    user = (
        f"Crisis: {crisis_title}\n"
        f"Situation: {crisis_description}\n\n"
        f"Player's response: \"{player_input}\"\n\n"
        f"Current national stats:\n{json.dumps(national_stats, indent=2)}\n\n"
        f"Economy (unemployment/consumer_prices/budget_deficit: high = bad):\n"
        f"{json.dumps(economy_stats, indent=2)}\n\n"
        f"Faction context:\n{json.dumps(faction_context, indent=2)}\n\n"
        f"Recent events:\n{json.dumps(recent_events, indent=2)}\n\n"
        "Evaluate this decision. Be realistic. Assign effects."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def evaluate_decision_retry_prompt(
    original_messages: list[dict],
    bad_output: str,
    error_reason: str,
) -> list[dict]:
    """Second attempt prompt — includes the failed output and what was wrong."""
    messages = list(original_messages)
    messages.append({"role": "assistant", "content": bad_output})
    messages.append({
        "role": "user",
        "content": (
            f"That response was invalid: {error_reason}\n\n"
            "Please try again. Return only valid JSON matching the required schema. "
            "All keys must be present. All values must be integers within the allowed range."
        )
    })
    return messages


# ── Freeform narrative ─────────────────────────────────────────────────────────

def freeform_advisor_reactions_prompt(
    crisis_title: str,
    decision_interpretation: str,
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
        f"What the president did: {decision_interpretation}\n"
        f"Final effects on national stats: {json.dumps(final_stat_effects)}\n"
        f"Final effects on factions: {json.dumps(final_faction_effects)}\n"
        f"Current national stats: {json.dumps(national_stats)}\n\n"
        f"Advisors:\n{json.dumps(ADVISORS, indent=2)}\n\n"
        "Write a short, in-character reaction for each advisor."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def freeform_faction_narrative_prompt(
    crisis_title: str,
    decision_interpretation: str,
    faction_effects: dict[str, int],
    faction_personas: dict,
) -> list[dict]:
    system = (
        f"You are writing brief faction response statements for a fictional political simulator. "
        f"{get_tone_instruction()} "
        "Each faction should respond in a voice consistent with their character. "
        "Only write for factions with non-zero effects — skip neutral factions. "
        "Return a JSON object: {\"faction_id\": \"one-sentence reaction\", ...}"
    )
    affected = {
        fid: {
            "name": faction_personas[fid]["name"],
            "effect": delta,
            "sentiment": "positive" if delta > 0 else "negative",
        }
        for fid, delta in faction_effects.items()
        if delta != 0 and fid in faction_personas
    }
    user = (
        f"Crisis: {crisis_title}\n"
        f"What happened: {decision_interpretation}\n\n"
        f"Affected factions:\n{json.dumps(affected, indent=2)}\n\n"
        "Write a one-sentence public reaction for each affected faction in their own voice."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def freeform_headlines_prompt(
    crisis_title: str,
    decision_interpretation: str,
    final_stat_effects: dict[str, int],
    final_faction_effects: dict[str, int],
    triggered_events: list[str],
) -> list[dict]:
    system = (
        f"You are writing fictional newspaper headlines for five outlets in the Republic of Veridia. "
        f"{get_tone_instruction()} "
        "Each outlet has its own editorial slant. "
        "Headlines should be punchy, distinct, and reflect each outlet's bias. "
        "Return a JSON array: [{\"outlet\": \"outlet_name\", \"headline\": \"...\"}]"
    )
    user = (
        f"This month's crisis: {crisis_title}\n"
        f"What the government did: {decision_interpretation}\n"
        f"Net effects: stats {json.dumps(final_stat_effects)}, factions {json.dumps(final_faction_effects)}\n"
        f"Additional events triggered: {json.dumps(triggered_events)}\n\n"
        f"Outlets:\n{json.dumps(OUTLETS, indent=2)}\n\n"
        "Write one headline per outlet."
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]
