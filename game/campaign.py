"""
Campaign Mode — 26 scripted crisis cards across three acts.

Structure:
  Act 1 (Turns 1–3):  Fixed opening → conditional month 2 → convergent Kosic anchor
  Act 2 (Turns 4–7):  Track A (kosic_ally) vs Track B (enemy/wary/ignored)
                       + convergent protest anchor + branched press crisis
  Act 3 (Turns 8–12): Path-specific crises — Reformer, Pragmatist, or Consolidator

Flag keys written to campaign_flags via option["flag_effects"]:
  fiscal_opening      : "transparent" | "political" | "quiet"
  kosic_relationship  : "ally" | "enemy" | "wary" | "ignored"
  dossier_use         : "public" | "prosecutor" | "drawer"   (Track A, turn 4)
  budget_response     : "approved" | "refused" | "negotiated" (Track B, turn 4)
  protest_response    : "dialogue" | "contained" | "ignored" | "crackdown"
  press_response      : "cooperate" | "dispute" | "source" | "ads"
  path                : "reformer" | "pragmatist" | "consolidator"  (set at turn 8)
"""

from typing import Any

from game.state import GameState


# ── Path determination ─────────────────────────────────────────────────────────

def _determine_path(flags: dict) -> str:
    """
    Score the accumulated flags to determine which leader the player has become.
    Called once at turn 8 if path is not already set.
    """
    reformer = 0
    pragmatist = 0
    consolidator = 0

    fo = flags.get("fiscal_opening", "")
    if fo == "transparent":  reformer += 2
    elif fo == "political":  pragmatist += 2
    elif fo == "quiet":      consolidator += 2

    kr = flags.get("kosic_relationship", "")
    if kr == "enemy":         reformer += 2
    elif kr == "wary":        reformer += 1; pragmatist += 1
    elif kr == "ignored":     reformer += 1; consolidator += 1
    elif kr == "ally":        pragmatist += 1; consolidator += 2

    pr = flags.get("protest_response", "")
    if pr == "dialogue":    reformer += 2
    elif pr == "contained": pragmatist += 2
    elif pr == "crackdown": consolidator += 2
    elif pr == "ignored":   pragmatist += 1; consolidator += 1

    press = flags.get("press_response", "")
    if press == "cooperate":          reformer += 2
    elif press == "dispute":          pragmatist += 2
    elif press in ("source", "ads"):  consolidator += 2

    scores = {"reformer": reformer, "pragmatist": pragmatist, "consolidator": consolidator}
    # tie-break: pragmatist (the middle path)
    best = max(scores.values())
    for path in ("pragmatist", "reformer", "consolidator"):
        if scores[path] == best:
            return path
    return "pragmatist"


# ── Crisis card definitions ────────────────────────────────────────────────────

CAMPAIGN_CRISES: dict[str, dict[str, Any]] = {

    # ── ACT 1 ─────────────────────────────────────────────────────────────────

    # Turn 1 — Fixed for everyone
    "what_they_left_behind": {
        "crisis_id": "what_they_left_behind",
        "title": "What They Left Behind",
        "description": (
            "The outgoing finance minister has handed you the real numbers. "
            "The deficit is forty percent worse than publicly disclosed. "
            "You have approximately one week before the bond markets figure this out "
            "on their own, at which point your options become significantly less interesting. "
            "Your predecessor is reportedly already at the vineyard."
        ),
        "options": [
            {
                "label": "Announce it publicly and commit to austerity",
                "description": "Take the hit early. Trust the public with the truth.",
                "stat_effects":    {"public_trust": -6, "institutional_strength": 5, "unrest": 3},
                "economy_effects": {"budget_deficit": -6, "stock_market": 3},
                "faction_effects": {"urban_progressives": 5, "business_elite": 4, "workers": -5, "rural_bloc": -3},
                "policy_tags":     ["transparency", "fiscal_discipline", "austerity"],
                "affected_factions": ["urban_progressives", "workers", "business_elite", "rural_bloc"],
                "event_flags":     {},
                "flag_effects":    {"fiscal_opening": "transparent"},
            },
            {
                "label": "Announce the gap — but blame the previous government",
                "description": "Buy political time. Start a war instead of a conversation.",
                "stat_effects":    {"public_trust": -2, "institutional_strength": -3, "unrest": 4},
                "economy_effects": {"budget_deficit": -2, "stock_market": 1},
                "faction_effects": {"national_conservatives": 5, "urban_progressives": -4, "workers": 1},
                "policy_tags":     ["deflection", "nationalist_messaging", "partial_transparency"],
                "affected_factions": ["national_conservatives", "urban_progressives", "workers"],
                "event_flags":     {},
                "flag_effects":    {"fiscal_opening": "political"},
            },
            {
                "label": "Say nothing publicly — begin quiet restructuring",
                "description": "Manage the gap in silence. Run up a credibility debt instead.",
                "stat_effects":    {"public_trust": 2, "media_freedom": -2},
                "economy_effects": {"budget_deficit": -3},
                "faction_effects": {"business_elite": 4, "urban_progressives": -3},
                "policy_tags":     ["opacity", "fiscal_management", "delayed_transparency"],
                "affected_factions": ["business_elite", "urban_progressives", "workers"],
                "event_flags":     {},
                "flag_effects":    {"fiscal_opening": "quiet"},
            },
        ],
    },

    # Turn 2 — Conditional on fiscal_opening = "transparent"
    "unions_read_budget": {
        "crisis_id": "unions_read_budget",
        "title": "The Unions Have Read the Budget",
        "description": (
            "You made the fiscal gap real by naming it publicly. "
            "The public sector unions have now read the numbers and drawn their own conclusions. "
            "Strike notices have been filed across three major sectors. "
            "Your Finance Minister says this was predictable. Your Reform Advisor says it was correct. "
            "Both are right. This does not help."
        ),
        "options": [
            {
                "label": "Engage unions directly — promise genuine consultation",
                "description": "Meet them at the table before the picket lines form.",
                "stat_effects":    {"public_trust": 4, "unrest": -6},
                "economy_effects": {"budget_deficit": 4},
                "faction_effects": {"workers": 8, "urban_progressives": 5, "business_elite": -4},
                "policy_tags":     ["union_negotiation", "consultation", "compromise"],
                "affected_factions": ["workers", "urban_progressives", "business_elite"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Defend the numbers as necessary — ask for shared sacrifice",
                "description": "Hold the line. Make the case for austerity on its merits.",
                "stat_effects":    {"public_trust": 2, "unrest": 3, "institutional_strength": 2},
                "economy_effects": {},
                "faction_effects": {"business_elite": 5, "workers": -5, "urban_progressives": -2},
                "policy_tags":     ["fiscal_discipline", "austerity", "anti_union"],
                "affected_factions": ["workers", "urban_progressives", "business_elite"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Promise to revisit the cuts after stabilisation",
                "description": "Kick it forward. A promise with an asterisk.",
                "stat_effects":    {"unrest": -3, "public_trust": 1},
                "economy_effects": {"budget_deficit": 1},
                "faction_effects": {"workers": 3, "urban_progressives": 2},
                "policy_tags":     ["delayed_spending", "compromise", "consultation"],
                "affected_factions": ["workers", "urban_progressives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Let the Finance Minister handle it",
                "description": "Delegate the problem. The minister will be blamed. So will you.",
                "stat_effects":    {"public_trust": -3, "unrest": 1},
                "economy_effects": {},
                "faction_effects": {"workers": -4, "urban_progressives": -2, "business_elite": 2},
                "policy_tags":     ["inaction", "delegation"],
                "affected_factions": ["workers", "urban_progressives", "business_elite"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # Turn 2 — Conditional on fiscal_opening = "political"
    "former_govt_lawyer": {
        "crisis_id": "former_govt_lawyer",
        "title": "The Former Government Has a Lawyer",
        "description": (
            "You blamed them for the books. They hired a lawyer. "
            "The former Finance Minister has filed a formal complaint alleging "
            "your characterisation of the deficit was politically motivated and factually selective. "
            "He has a point about the selective part. He is less right about the rest. "
            "The media war you started last month is now fully underway."
        ),
        "options": [
            {
                "label": "Release the full evidence — let the numbers speak",
                "description": "Get ahead of the legal fight with transparency.",
                "stat_effects":    {"public_trust": 6, "institutional_strength": 4},
                "economy_effects": {"stock_market": 2},
                "faction_effects": {"urban_progressives": 7, "national_conservatives": -5, "business_elite": 2},
                "policy_tags":     ["transparency", "accountability", "rule_of_law"],
                "affected_factions": ["urban_progressives", "national_conservatives", "business_elite"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Let the legal process play out — say nothing",
                "description": "Disciplined restraint. The lawyers will take a while.",
                "stat_effects":    {"public_trust": -2, "unrest": 2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 3, "national_conservatives": -2},
                "policy_tags":     ["rule_of_law", "delay", "restraint"],
                "affected_factions": ["urban_progressives", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Hit back harder — escalate politically",
                "description": "Answer a lawyer with a press conference. Things get louder.",
                "stat_effects":    {"public_trust": -4, "unrest": 5, "media_freedom": -4},
                "economy_effects": {"stock_market": -3},
                "faction_effects": {"national_conservatives": 6, "urban_progressives": -6, "workers": -2},
                "policy_tags":     ["polarization", "deflection", "media_war"],
                "affected_factions": ["national_conservatives", "urban_progressives", "workers"],
                "event_flags":     {
                    "urban_progressives": ["watched the government escalate a political media war over the budget"],
                },
                "flag_effects":    {},
            },
            {
                "label": "Offer a quiet settlement — make the lawsuit go away",
                "description": "Pay them to stop. The cost is institutional credibility.",
                "stat_effects":    {"institutional_strength": -5, "public_trust": -3},
                "economy_effects": {"budget_deficit": 3},
                "faction_effects": {"business_elite": 3, "urban_progressives": -5, "workers": -3},
                "policy_tags":     ["cover_up", "compromise", "opacity"],
                "affected_factions": ["business_elite", "urban_progressives", "workers"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # Turn 2 — Conditional on fiscal_opening = "quiet"
    "markets_heard_something": {
        "crisis_id": "markets_heard_something",
        "title": "The Markets Heard Something",
        "description": (
            "A major credit rating agency has sent a formal inquiry. "
            "They have questions about 'fiscal trajectory and disclosure practices.' "
            "This is credit agency language for 'we know something is wrong and we are writing it down.' "
            "Your silence last month has bought you approximately three weeks. "
            "The three weeks are up."
        ),
        "options": [
            {
                "label": "Meet with the agency — provide full fiscal reassurance",
                "description": "Open the books to the people whose opinion moves markets.",
                "stat_effects":    {"international_reputation": 4, "public_trust": 2},
                "economy_effects": {"stock_market": 6, "budget_deficit": -3},
                "faction_effects": {"business_elite": 8, "workers": -2, "urban_progressives": 2},
                "policy_tags":     ["transparency", "fiscal_discipline", "international_cooperation"],
                "affected_factions": ["business_elite", "workers", "urban_progressives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Dismiss the inquiry as speculation — say nothing",
                "description": "Call their bluff. Rarely works. Often expensive.",
                "stat_effects":    {"international_reputation": -5, "public_trust": -2},
                "economy_effects": {"stock_market": -6},
                "faction_effects": {"business_elite": -7, "national_conservatives": 3},
                "policy_tags":     ["dismissal", "opacity", "inaction"],
                "affected_factions": ["business_elite", "national_conservatives", "urban_progressives"],
                "event_flags":     {
                    "business_elite": ["watched the government ignore a formal credit agency inquiry"],
                },
                "flag_effects":    {},
            },
            {
                "label": "Issue a partial fiscal update — control what they see",
                "description": "Selective transparency. Better than silence. Worse than honesty.",
                "stat_effects":    {"public_trust": 3, "media_freedom": -1},
                "economy_effects": {"stock_market": 4, "budget_deficit": -2},
                "faction_effects": {"business_elite": 5, "urban_progressives": 3},
                "policy_tags":     ["partial_transparency", "fiscal_management", "opacity"],
                "affected_factions": ["business_elite", "urban_progressives", "workers"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Leak a positive growth story to distract the markets",
                "description": "Misdirection. Works briefly. Adds to the credibility debt.",
                "stat_effects":    {"media_freedom": -4, "public_trust": -2, "institutional_strength": -2},
                "economy_effects": {"stock_market": 3},
                "faction_effects": {"business_elite": 2, "urban_progressives": -4},
                "policy_tags":     ["disinformation", "media_management", "opacity"],
                "affected_factions": ["business_elite", "urban_progressives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # Turn 3 — Convergent anchor, everyone sees this
    "general_requests_meeting": {
        "crisis_id": "general_requests_meeting",
        "title": "The General Requests a Meeting",
        "description": (
            "General Mihail Kosic, Chief of Military Intelligence and four-star holdover "
            "from the previous two governments, has requested thirty minutes of your time. "
            "His assistant describes this as 'a courtesy call.' "
            "Your Reform Advisor describes Kosic as 'patient, useful, and expensive.' "
            "He has information about the previous government. He wants something modest in return: "
            "the military budget untouched for eighteen months, and a procurement contract. "
            "The thirty minutes are scheduled for Thursday."
        ),
        "options": [
            {
                "label": "Hear him out and agree to the arrangement",
                "description": "He's useful. The price seems manageable. That's the point.",
                "stat_effects":    {"institutional_strength": -5},
                "economy_effects": {"budget_deficit": 8},
                "faction_effects": {"security_forces": 8, "urban_progressives": -6, "workers": -2},
                "policy_tags":     ["backroom_deal", "security_forces", "institutional_risk"],
                "affected_factions": ["security_forces", "urban_progressives", "workers"],
                "event_flags":     {},
                "flag_effects":    {"kosic_relationship": "ally"},
            },
            {
                "label": "Hear him out — then refuse",
                "description": "Let him say his piece. Tell him no. Learn what no costs.",
                "stat_effects":    {"institutional_strength": 5, "unrest": 1},
                "economy_effects": {},
                "faction_effects": {"security_forces": -6, "urban_progressives": 6, "workers": 3},
                "policy_tags":     ["institutional_protection", "anti_corruption", "rule_of_law"],
                "affected_factions": ["security_forces", "urban_progressives", "workers"],
                "event_flags":     {
                    "security_forces": ["had their informal arrangement refused by the new government"],
                },
                "flag_effects":    {"kosic_relationship": "enemy"},
            },
            {
                "label": "Take the meeting but bring your Reform Advisor as a witness",
                "description": "Hear it. Document it. Don't be alone in the room with it.",
                "stat_effects":    {"institutional_strength": 3, "public_trust": 1},
                "economy_effects": {},
                "faction_effects": {"security_forces": -2, "urban_progressives": 4, "workers": 1},
                "policy_tags":     ["institutional_protection", "transparency", "compromise"],
                "affected_factions": ["security_forces", "urban_progressives", "workers"],
                "event_flags":     {},
                "flag_effects":    {"kosic_relationship": "wary"},
            },
            {
                "label": "Decline the meeting entirely — don't give him the room",
                "description": "Harshest signal. Cleanest hands. Longest consequences.",
                "stat_effects":    {"institutional_strength": 4, "unrest": 3},
                "economy_effects": {},
                "faction_effects": {"security_forces": -9, "urban_progressives": 5, "workers": 2},
                "policy_tags":     ["institutional_protection", "isolation", "confrontational"],
                "affected_factions": ["security_forces", "urban_progressives", "workers", "national_conservatives"],
                "event_flags":     {
                    "security_forces": ["were refused a meeting with the new head of government"],
                },
                "flag_effects":    {"kosic_relationship": "ignored"},
            },
        ],
    },

    # ── ACT 2 — TRACK A (kosic_ally) ─────────────────────────────────────────

    # Turn 4 — Track A
    "the_dossier": {
        "crisis_id": "the_dossier",
        "title": "The Dossier",
        "description": (
            "Kosic has delivered. The documents are real — internal records from the previous "
            "government implicating the opposition leader in something genuinely damaging. "
            "Not fabricated. Not exaggerated. Real, legally significant, and currently "
            "sitting in a sealed envelope on your desk. "
            "What you do with it tells everyone — including Kosic — who you are."
        ),
        "options": [
            {
                "label": "Use it publicly — release the documents",
                "description": "The opposition collapses. Everyone sees how you play.",
                "stat_effects":    {"institutional_strength": -6, "public_trust": -4, "media_freedom": -3},
                "economy_effects": {},
                "faction_effects": {"national_conservatives": 5, "urban_progressives": -8, "workers": -3, "security_forces": 4},
                "policy_tags":     ["authoritarian", "political_intelligence", "media_weaponisation"],
                "affected_factions": ["urban_progressives", "national_conservatives", "workers", "security_forces"],
                "event_flags":     {
                    "urban_progressives": ["watched the government weaponise intelligence files against the opposition"],
                },
                "flag_effects":    {"dossier_use": "public"},
            },
            {
                "label": "Pass it to an independent prosecutor",
                "description": "Slower, cleaner. Kosic is annoyed. The law does its work.",
                "stat_effects":    {"institutional_strength": 6, "public_trust": 4},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 7, "workers": 4, "security_forces": -4, "national_conservatives": -3},
                "policy_tags":     ["rule_of_law", "anti_corruption", "transparency"],
                "affected_factions": ["urban_progressives", "workers", "security_forces", "national_conservatives"],
                "event_flags":     {
                    "security_forces": ["had intelligence assets handed to an independent prosecutor without consent"],
                },
                "flag_effects":    {"dossier_use": "prosecutor"},
            },
            {
                "label": "Lock it in a drawer",
                "description": "Kosic expected this. He has copies. You now owe him more.",
                "stat_effects":    {"institutional_strength": -3, "public_trust": -1},
                "economy_effects": {},
                "faction_effects": {"security_forces": 3, "urban_progressives": -2},
                "policy_tags":     ["inaction", "backroom_deal", "opacity"],
                "affected_factions": ["security_forces", "urban_progressives", "business_elite"],
                "event_flags":     {},
                "flag_effects":    {"dossier_use": "drawer"},
            },
        ],
    },

    # Turn 5 — Track A
    "someone_leaked_something": {
        "crisis_id": "someone_leaked_something",
        "title": "Someone Leaked Something",
        "description": (
            "Not the dossier — something adjacent. "
            "A journalist at the Veridian Times has a piece that is seventy percent right. "
            "The thirty percent wrong is flattering to no one. "
            "The piece runs in forty-eight hours unless something stops it. "
            "Kosic's office has noted, informally, that they could 'assist with source identification' "
            "if that would be helpful."
        ),
        "options": [
            {
                "label": "Kill the story through back channels",
                "description": "Use what you have. The story goes away. The cost stays.",
                "stat_effects":    {"media_freedom": -7, "public_trust": -3, "institutional_strength": -3},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": -7, "national_conservatives": 3, "security_forces": 4},
                "policy_tags":     ["media_restriction", "cover_up", "authoritarian"],
                "affected_factions": ["urban_progressives", "national_conservatives", "security_forces"],
                "event_flags":     {
                    "urban_progressives": ["had a newspaper investigation suppressed through government channels"],
                },
                "flag_effects":    {},
            },
            {
                "label": "Confirm the true parts — let the story run with corrections",
                "description": "Get ahead of the seventy percent. Own it before it owns you.",
                "stat_effects":    {"public_trust": 4, "institutional_strength": 4, "media_freedom": 2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 6, "workers": 4, "security_forces": -4},
                "policy_tags":     ["transparency", "accountability", "media_freedom"],
                "affected_factions": ["urban_progressives", "workers", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Complicate it — add context that changes the framing",
                "description": "Don't kill it. Shape it. The story runs, but not the one they had.",
                "stat_effects":    {"public_trust": 1, "media_freedom": -2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 2, "workers": 1, "national_conservatives": 2},
                "policy_tags":     ["media_management", "partial_transparency", "spin"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # ── ACT 2 — TRACK B (kosic_enemy / kosic_wary / kosic_ignored) ────────────

    # Turn 4 — Track B
    "budget_request_arrives": {
        "crisis_id": "budget_request_arrives",
        "title": "The Budget Request Arrives",
        "description": (
            "Twelve days after you refused or complicated Kosic's meeting, "
            "the military has submitted a supplementary budget request. "
            "It is thirty percent above projection. "
            "The justification section is three sentences long. "
            "Your Finance Minister says the timing is 'not coincidental.' "
            "Your Reform Advisor says this is 'what the next nine months look like.'"
        ),
        "options": [
            {
                "label": "Approve it — don't start a fight you don't need",
                "description": "You've blinked. The generals have noted this.",
                "stat_effects":    {"institutional_strength": -4, "public_trust": -2},
                "economy_effects": {"budget_deficit": 12},
                "faction_effects": {"security_forces": 7, "workers": -5, "urban_progressives": -5, "business_elite": -3},
                "policy_tags":     ["military_spending", "appeasement", "fiscal_cost"],
                "affected_factions": ["security_forces", "workers", "urban_progressives", "business_elite"],
                "event_flags":     {},
                "flag_effects":    {"budget_response": "approved"},
            },
            {
                "label": "Refuse it — send it back with a request for justification",
                "description": "Hold the line. The generals are now a formal problem.",
                "stat_effects":    {"institutional_strength": 4, "unrest": 3},
                "economy_effects": {},
                "faction_effects": {"security_forces": -7, "urban_progressives": 5, "workers": 4},
                "policy_tags":     ["institutional_protection", "anti_military", "fiscal_discipline"],
                "affected_factions": ["security_forces", "urban_progressives", "workers"],
                "event_flags":     {
                    "security_forces": ["had their supplementary budget request refused and returned for justification"],
                },
                "flag_effects":    {"budget_response": "refused"},
            },
            {
                "label": "Negotiate — treat it like a normal departmental request",
                "description": "The military finds this offensive. You find this appropriate.",
                "stat_effects":    {"institutional_strength": 3, "unrest": 1},
                "economy_effects": {"budget_deficit": 5},
                "faction_effects": {"security_forces": 2, "urban_progressives": 3, "workers": 2},
                "policy_tags":     ["institutional_normalisation", "negotiation", "compromise"],
                "affected_factions": ["security_forces", "urban_progressives", "workers"],
                "event_flags":     {
                    "security_forces": ["were subjected to standard budget negotiations rather than deference"],
                },
                "flag_effects":    {"budget_response": "negotiated"},
            },
        ],
    },

    # Turn 5 — Track B
    "border_situation": {
        "crisis_id": "border_situation",
        "title": "The Border Situation",
        "description": (
            "A minor incident on Veridia's eastern border has been amplified significantly "
            "by the weekend news cycle. Two vehicles, one flag dispute, no casualties. "
            "It may be real. It may be manufactured. "
            "Kosic's office has offered intelligence briefings on the situation. "
            "The offer is not quite conditional, but the framing makes the relationship clear."
        ),
        "options": [
            {
                "label": "Accept Kosic's intelligence briefings — take the information",
                "description": "Pragmatic. He's still useful. The relationship is complicated.",
                "stat_effects":    {"institutional_strength": -3},
                "economy_effects": {},
                "faction_effects": {"security_forces": 5, "urban_progressives": -4},
                "policy_tags":     ["intelligence_cooperation", "pragmatism", "institutional_risk"],
                "affected_factions": ["security_forces", "urban_progressives", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Establish an independent intelligence assessment",
                "description": "Find another way to know what you need to know.",
                "stat_effects":    {"institutional_strength": 4, "international_reputation": 3},
                "economy_effects": {"budget_deficit": 3},
                "faction_effects": {"security_forces": -5, "urban_progressives": 5, "workers": 2},
                "policy_tags":     ["institutional_reform", "intelligence_independence", "rule_of_law"],
                "affected_factions": ["security_forces", "urban_progressives", "workers"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Downplay the incident — reduce the news temperature",
                "description": "Smaller fire if you don't add fuel. Might not be your fire to control.",
                "stat_effects":    {"unrest": -2, "international_reputation": -2},
                "economy_effects": {},
                "faction_effects": {"national_conservatives": -5, "security_forces": -3, "rural_bloc": 2},
                "policy_tags":     ["de_escalation", "inaction", "dismissal"],
                "affected_factions": ["national_conservatives", "security_forces", "rural_bloc"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Demand a full public accounting from the military",
                "description": "Transparency about the incident and who's amplifying it.",
                "stat_effects":    {"institutional_strength": 5, "unrest": 2},
                "economy_effects": {},
                "faction_effects": {"security_forces": -6, "urban_progressives": 6, "workers": 3},
                "policy_tags":     ["transparency", "institutional_accountability", "confrontational"],
                "affected_factions": ["security_forces", "urban_progressives", "workers"],
                "event_flags":     {
                    "security_forces": ["were required to publicly account for their border incident response"],
                },
                "flag_effects":    {},
            },
        ],
    },

    # Turn 6 — Convergent anchor (everyone sees this, reason differs by track)
    "streets_are_full": {
        "crisis_id": "streets_are_full",
        "title": "The Streets Are Full",
        "description": (
            "A large protest has formed in the capital. On one reading, "
            "they are angry about the whiff of political dirty tricks. "
            "On another, they are angry about military overreach. "
            "On a third reading, they are angry about things that have been accumulating "
            "for longer than your tenure. "
            "The signs are varied. The crowd is not small. "
            "Your Security Chief is waiting for instructions."
        ),
        "options": [
            {
                "label": "Open dialogue — invite protest leaders to formal talks",
                "description": "Treat them as citizens. It costs political capital and earns legitimacy.",
                "stat_effects":    {"public_trust": 6, "unrest": -8, "institutional_strength": 3},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 8, "workers": 6, "security_forces": -3, "rural_bloc": 2},
                "policy_tags":     ["dialogue", "democratic_process", "civil_liberties"],
                "affected_factions": ["urban_progressives", "workers", "security_forces", "rural_bloc"],
                "event_flags":     {},
                "flag_effects":    {"protest_response": "dialogue"},
            },
            {
                "label": "Containment — police presence, no violence, clear message",
                "description": "Order without escalation. The protest ends; the grievance remains.",
                "stat_effects":    {"unrest": -4, "institutional_strength": -2},
                "economy_effects": {},
                "faction_effects": {"security_forces": 4, "urban_progressives": -4, "workers": -2},
                "policy_tags":     ["public_order", "police_presence", "containment"],
                "affected_factions": ["security_forces", "urban_progressives", "workers"],
                "event_flags":     {},
                "flag_effects":    {"protest_response": "contained"},
            },
            {
                "label": "Ignore it — let the march run its course",
                "description": "They'll go home eventually. The question is what they remember.",
                "stat_effects":    {"unrest": 3, "public_trust": -2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": -4, "workers": -3, "rural_bloc": 1},
                "policy_tags":     ["inaction", "dismissal", "waiting_game"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {"protest_response": "ignored"},
            },
            {
                "label": "Crackdown — security forces disperse, arrests made",
                "description": "The streets clear. Something else doesn't.",
                "stat_effects":    {"unrest": -5, "institutional_strength": -8, "media_freedom": -6},
                "economy_effects": {},
                "faction_effects": {"security_forces": 8, "urban_progressives": -10, "workers": -6, "rural_bloc": -3},
                "policy_tags":     ["police_crackdown", "authoritarian", "civil_liberties_risk"],
                "affected_factions": ["security_forces", "urban_progressives", "workers", "rural_bloc"],
                "event_flags":     {
                    "urban_progressives": ["had a mass protest broken up by security forces with arrests"],
                    "workers": ["witnessed a protest crackdown with mass arrests in the capital"],
                },
                "flag_effects":    {"protest_response": "crackdown"},
            },
        ],
    },

    # Turn 7 — Track A (kosic_ally) — intelligence weaponisation angle
    "paper_chooses_sides_a": {
        "crisis_id": "paper_chooses_sides_a",
        "title": "The Paper Chooses Sides",
        "description": (
            "The Veridian Times has published a major investigation. "
            "The piece alleges that political intelligence is being weaponised against opponents. "
            "It is partly right. It names two things you did, one thing you didn't do, "
            "and one thing Kosic did that you technically enabled. "
            "The editor is on record saying the Times is 'committed to following this story.' "
            "That's three words for 'there is more coming.'"
        ),
        "options": [
            {
                "label": "Cooperate with the investigation",
                "description": "Give them access. The truth comes out on your terms.",
                "stat_effects":    {"public_trust": 6, "institutional_strength": 5, "media_freedom": 4},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 8, "workers": 5, "national_conservatives": -3, "security_forces": -4},
                "policy_tags":     ["transparency", "media_freedom", "accountability"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {"press_response": "cooperate"},
            },
            {
                "label": "Dispute the facts publicly",
                "description": "Contest the parts that are wrong. Accept the parts that aren't.",
                "stat_effects":    {"public_trust": -4, "media_freedom": -3},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": -6, "national_conservatives": 5, "security_forces": 3},
                "policy_tags":     ["deflection", "media_war", "partial_accountability"],
                "affected_factions": ["urban_progressives", "national_conservatives", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {"press_response": "dispute"},
            },
            {
                "label": "Find out who the source is",
                "description": "Institutional cost. Someone will be made an example.",
                "stat_effects":    {"media_freedom": -7, "institutional_strength": -4, "public_trust": -2},
                "economy_effects": {},
                "faction_effects": {"security_forces": 4, "urban_progressives": -8, "workers": -3},
                "policy_tags":     ["media_restriction", "institutional_abuse", "source_hunting"],
                "affected_factions": ["security_forces", "urban_progressives", "workers"],
                "event_flags":     {
                    "urban_progressives": ["watched the government launch an investigation to identify a newspaper's source"],
                },
                "flag_effects":    {"press_response": "source"},
            },
            {
                "label": "Pull government advertising from the Times",
                "description": "Don't pretend you wouldn't consider it. You're considering it.",
                "stat_effects":    {"media_freedom": -8, "public_trust": -5, "institutional_strength": -5},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": -10, "national_conservatives": 4, "business_elite": 2},
                "policy_tags":     ["media_restriction", "economic_coercion", "authoritarian"],
                "affected_factions": ["urban_progressives", "national_conservatives", "business_elite"],
                "event_flags":     {
                    "urban_progressives": ["watched government advertising pulled from the Times as retaliation for coverage"],
                },
                "flag_effects":    {"press_response": "ads"},
            },
        ],
    },

    # Turn 7 — Track B (non-ally) — military budget irregularities angle
    "paper_chooses_sides_b": {
        "crisis_id": "paper_chooses_sides_b",
        "title": "The Paper Chooses Sides",
        "description": (
            "The Veridian Times has published a major investigation. "
            "The piece concerns military budget irregularities and the supplementary request "
            "that arrived shortly after you refused or complicated your relationship with "
            "General Kosic. The story is partly right, partly wrong, and entirely unwelcome. "
            "It names the procurement company. It names the contract. "
            "It does not yet name Kosic, but the editor is described as 'thorough.'"
        ),
        "options": [
            {
                "label": "Cooperate with the investigation",
                "description": "Give them access. The truth comes out on your terms.",
                "stat_effects":    {"public_trust": 6, "institutional_strength": 5, "media_freedom": 4},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 8, "workers": 5, "national_conservatives": -3, "security_forces": -5},
                "policy_tags":     ["transparency", "media_freedom", "accountability"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {"press_response": "cooperate"},
            },
            {
                "label": "Dispute the facts publicly",
                "description": "Contest the parts that are wrong. Accept the parts that aren't.",
                "stat_effects":    {"public_trust": -4, "media_freedom": -3},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": -6, "national_conservatives": 5, "security_forces": 3},
                "policy_tags":     ["deflection", "media_war", "partial_accountability"],
                "affected_factions": ["urban_progressives", "national_conservatives", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {"press_response": "dispute"},
            },
            {
                "label": "Find out who the source is",
                "description": "Institutional cost. Someone will be made an example.",
                "stat_effects":    {"media_freedom": -7, "institutional_strength": -4, "public_trust": -2},
                "economy_effects": {},
                "faction_effects": {"security_forces": 4, "urban_progressives": -8, "workers": -3},
                "policy_tags":     ["media_restriction", "institutional_abuse", "source_hunting"],
                "affected_factions": ["security_forces", "urban_progressives", "workers"],
                "event_flags":     {
                    "urban_progressives": ["watched the government launch an investigation to identify a newspaper's source"],
                },
                "flag_effects":    {"press_response": "source"},
            },
            {
                "label": "Pull government advertising from the Times",
                "description": "Don't pretend you wouldn't consider it. You're considering it.",
                "stat_effects":    {"media_freedom": -8, "public_trust": -5, "institutional_strength": -5},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": -10, "national_conservatives": 4, "business_elite": 2},
                "policy_tags":     ["media_restriction", "economic_coercion", "authoritarian"],
                "affected_factions": ["urban_progressives", "national_conservatives", "business_elite"],
                "event_flags":     {
                    "urban_progressives": ["watched government advertising pulled from the Times as retaliation for coverage"],
                },
                "flag_effects":    {"press_response": "ads"},
            },
        ],
    },

    # ── ACT 3 — PATH 1: THE REFORMER ──────────────────────────────────────────

    # Turn 8 — Reformer
    "reformer_foreign_offer": {
        "crisis_id": "reformer_foreign_offer",
        "title": "The Foreign Offer",
        "description": (
            "A trade agreement has arrived from the Western Alliance. "
            "The economic benefits are real — market access, reduced unemployment, "
            "improved investor confidence. "
            "The compromise required is also real: a clause that limits your ability "
            "to regulate one specific sector for fifteen years. "
            "Your Reform Advisor says the clause is significant. "
            "Your Finance Minister says it is the most significant economic opportunity "
            "in a decade. Both of them are right about different things."
        ),
        "options": [
            {
                "label": "Accept the deal — take the benefits, accept the compromise",
                "description": "Pragmatic. Something gets traded. The economy improves.",
                "stat_effects":    {"international_reputation": 5, "institutional_strength": -3},
                "economy_effects": {"stock_market": 8, "unemployment": -6, "budget_deficit": -8},
                "faction_effects": {"business_elite": 8, "workers": -4, "national_conservatives": -4, "urban_progressives": -3},
                "policy_tags":     ["trade_agreement", "international_cooperation", "compromise"],
                "affected_factions": ["business_elite", "workers", "urban_progressives", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Accept with conditions — renegotiate the clause",
                "description": "Slower. Cleaner. The Western Alliance is mildly annoyed.",
                "stat_effects":    {"international_reputation": 3, "institutional_strength": 2},
                "economy_effects": {"stock_market": 4, "unemployment": -3, "budget_deficit": -3},
                "faction_effects": {"business_elite": 4, "workers": 2, "urban_progressives": 4},
                "policy_tags":     ["trade_agreement", "negotiation", "institutional_protection"],
                "affected_factions": ["business_elite", "workers", "urban_progressives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Reject it — the clause is too significant",
                "description": "Principled. The economy does not improve this month.",
                "stat_effects":    {"international_reputation": -4, "institutional_strength": 4},
                "economy_effects": {"stock_market": -4},
                "faction_effects": {"national_conservatives": 5, "urban_progressives": 5, "business_elite": -6},
                "policy_tags":     ["sovereignty", "institutional_protection", "inaction"],
                "affected_factions": ["national_conservatives", "urban_progressives", "business_elite"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Delay — form a committee to study the implications",
                "description": "The government's answer to everything.",
                "stat_effects":    {"public_trust": -2},
                "economy_effects": {},
                "faction_effects": {"business_elite": -3, "urban_progressives": 2, "workers": 1},
                "policy_tags":     ["delay", "consultation", "inaction"],
                "affected_factions": ["business_elite", "urban_progressives", "workers"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # Turn 9 — Reformer
    "reformer_supreme_court": {
        "crisis_id": "reformer_supreme_court",
        "title": "The Supreme Court Has Questions",
        "description": (
            "The old guard's institutional rearguard action has arrived in judicial form. "
            "Three of your reform directives have been suspended pending constitutional review. "
            "The cases are legitimate — your advisors drafted quickly and the legal basis "
            "is genuinely contestable. "
            "This is also clearly coordinated. The timing is not coincidental. "
            "Your Reform Advisor says: 'This is what winning looks like, sometimes.'"
        ),
        "options": [
            {
                "label": "Comply and find lawful workarounds",
                "description": "Accept the rulings. Work within them. Slower, but it holds.",
                "stat_effects":    {"institutional_strength": 6, "public_trust": 3},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 6, "workers": 3, "security_forces": -3},
                "policy_tags":     ["rule_of_law", "institutional_respect", "reform"],
                "affected_factions": ["urban_progressives", "workers", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Challenge the rulings — appeal immediately",
                "description": "Fight it legally. You might win. It will take time.",
                "stat_effects":    {"institutional_strength": -4, "unrest": 4},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": -4, "national_conservatives": 4, "security_forces": 2},
                "policy_tags":     ["legal_challenge", "confrontational", "institutional_conflict"],
                "affected_factions": ["urban_progressives", "national_conservatives", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Negotiate with the Court — seek a compromise interpretation",
                "description": "Pragmatic. Courts can be talked to. This one is listening.",
                "stat_effects":    {"institutional_strength": 4, "public_trust": 2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 5, "workers": 2, "security_forces": -2},
                "policy_tags":     ["negotiation", "institutional_cooperation", "compromise"],
                "affected_factions": ["urban_progressives", "workers", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Make it a public political fight",
                "description": "Name the coordination. Make the old guard visible.",
                "stat_effects":    {"public_trust": -2, "unrest": 5, "institutional_strength": -3},
                "economy_effects": {},
                "faction_effects": {"workers": 5, "urban_progressives": 3, "national_conservatives": -6, "security_forces": -3},
                "policy_tags":     ["populist", "polarization", "institutional_conflict"],
                "affected_factions": ["workers", "urban_progressives", "national_conservatives", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # Turn 10 — Reformer
    "reformer_reform_package": {
        "crisis_id": "reformer_reform_package",
        "title": "The Reform Package",
        "description": (
            "Your signature legislation is on the floor. "
            "You have the votes for the watered-down version. "
            "You do not have the votes for the full version — not yet, possibly not ever. "
            "Your coalition will tell you to take the half-win. "
            "Your Reform Advisor will tell you the half-win is actually a defeat "
            "that takes longer to recognise. "
            "You have forty-eight hours to decide which of them is right."
        ),
        "options": [
            {
                "label": "Water it down and pass it",
                "description": "Something passes. Something is better than nothing. Probably.",
                "stat_effects":    {"institutional_strength": 4, "public_trust": 3},
                "economy_effects": {"budget_deficit": 4},
                "faction_effects": {"urban_progressives": 4, "workers": 4, "business_elite": 5, "national_conservatives": 2},
                "policy_tags":     ["reform", "compromise", "partial_win"],
                "affected_factions": ["urban_progressives", "workers", "business_elite", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Go for the full version — fight for every vote",
                "description": "Win everything or win nothing. The stakes are clear.",
                "stat_effects":    {"institutional_strength": 7, "public_trust": 5, "unrest": 2},
                "economy_effects": {"budget_deficit": 7},
                "faction_effects": {"urban_progressives": 10, "workers": 7, "business_elite": -8, "national_conservatives": -6},
                "policy_tags":     ["reform", "confrontational", "democratic_process"],
                "affected_factions": ["urban_progressives", "workers", "business_elite", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Delay — bring back a stronger version next session",
                "description": "Strategic retreat. Your opponents will use the time too.",
                "stat_effects":    {"public_trust": -3, "unrest": 1},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": -4, "workers": -3, "business_elite": 3},
                "policy_tags":     ["delay", "strategic_retreat", "inaction"],
                "affected_factions": ["urban_progressives", "workers", "business_elite"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # Turn 11 — Reformer
    "reformer_own_side": {
        "crisis_id": "reformer_own_side",
        "title": "Your Own Side",
        "description": (
            "Your coalition is fracturing along a seam that has always been there. "
            "The pragmatists in your party want to deal — take the offer from the "
            "national conservatives, give ground on one significant thing, secure the year. "
            "The idealists want to fight — hold the line, risk the government, "
            "be right about something. "
            "Both factions have scheduled meetings with you for the same afternoon. "
            "You cannot agree with both of them."
        ),
        "options": [
            {
                "label": "Side with the pragmatists — take the deal",
                "description": "You survive. Something changes about what survival means.",
                "stat_effects":    {"public_trust": -3, "institutional_strength": -2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": -5, "workers": -3, "national_conservatives": 5, "business_elite": 3},
                "policy_tags":     ["compromise", "coalition_management", "pragmatism"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives", "business_elite"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Side with the idealists — hold the line",
                "description": "You fight. The outcome is uncertain. The principle is not.",
                "stat_effects":    {"public_trust": 4, "unrest": 2, "institutional_strength": 2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 7, "workers": 5, "national_conservatives": -6, "business_elite": -4},
                "policy_tags":     ["principled_stance", "confrontational", "democratic_process"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives", "business_elite"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Try to hold both wings — find the middle position",
                "description": "You satisfy no one entirely. Everyone stays.",
                "stat_effects":    {"public_trust": 1, "institutional_strength": 1},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 2, "workers": 2, "national_conservatives": 1},
                "policy_tags":     ["coalition_management", "compromise", "delay"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Call a party vote — let the coalition decide",
                "description": "Democratic within the party. You may not like what they choose.",
                "stat_effects":    {"institutional_strength": 4, "public_trust": 2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 4, "workers": 3, "national_conservatives": -2},
                "policy_tags":     ["democratic_process", "coalition_management", "institutional_respect"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # Turn 12 — Reformer
    "reformer_vote": {
        "crisis_id": "reformer_vote",
        "title": "The Vote",
        "description": (
            "No-confidence motion. "
            "Three swing votes. You have spent a year either cultivating or alienating them "
            "through seven months of decisions that felt individual and two months of crises "
            "that tested what you actually believed. "
            "The vote is in seventy-two hours. "
            "Your Reform Advisor says: 'Whatever happens, we built something.' "
            "Your Party Strategist says: 'That's easy for them to say.'"
        ),
        "options": [
            {
                "label": "Fight it head-on — make it a referendum on reform",
                "description": "Name what this year was for. Let Veridia decide.",
                "stat_effects":    {"institutional_strength": 6, "public_trust": 4},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 8, "workers": 6, "national_conservatives": -5, "security_forces": -3},
                "policy_tags":     ["democratic_process", "confrontational", "principled_stance"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Negotiate with swing votes — offer concessions",
                "description": "You survive. Something is traded. The math changes.",
                "stat_effects":    {"public_trust": -2, "institutional_strength": -2},
                "economy_effects": {},
                "faction_effects": {"business_elite": 4, "urban_progressives": -3, "national_conservatives": 3},
                "policy_tags":     ["negotiation", "compromise", "coalition_management"],
                "affected_factions": ["business_elite", "urban_progressives", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Reframe it as an attack on democratic institutions",
                "description": "Make them the story. Works if the press agrees with you.",
                "stat_effects":    {"public_trust": 3, "unrest": 3, "institutional_strength": -2},
                "economy_effects": {},
                "faction_effects": {"workers": 5, "urban_progressives": 4, "national_conservatives": -8},
                "policy_tags":     ["populist", "deflection", "media_campaign"],
                "affected_factions": ["workers", "urban_progressives", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Resign before the vote — on your terms",
                "description": "Principled Failure is still principled.",
                "stat_effects":    {"institutional_strength": 8, "public_trust": 5, "unrest": -2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 7, "workers": 5, "national_conservatives": -3},
                "policy_tags":     ["principled_stance", "democratic_process", "resignation"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # ── ACT 3 — PATH 2: THE PRAGMATIST ────────────────────────────────────────

    # Turn 8 — Pragmatist
    "pragmatist_bill_due": {
        "crisis_id": "pragmatist_bill_due",
        "title": "The Bill Comes Due",
        "description": (
            "A favour granted in month three is being called in. "
            "You knew this was coming. What you did not know is that the ask "
            "would be meaningfully larger than the original arrangement suggested. "
            "This is how these things work. "
            "Your Legal Advisor describes the new request as 'expansive.' "
            "Your Party Strategist describes it as 'the price of governing.' "
            "The invoice is on your desk."
        ),
        "options": [
            {
                "label": "Honour the deal — accept the larger ask",
                "description": "You made a deal. Deals have terms. Pay the terms.",
                "stat_effects":    {"institutional_strength": -5, "public_trust": -3},
                "economy_effects": {"budget_deficit": 10},
                "faction_effects": {"security_forces": 7, "business_elite": 4, "workers": -5, "urban_progressives": -6},
                "policy_tags":     ["backroom_deal", "corruption_risk", "institutional_risk"],
                "affected_factions": ["security_forces", "business_elite", "workers", "urban_progressives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Partially honour — negotiate limits on the expanded ask",
                "description": "You committed to something. Not to everything.",
                "stat_effects":    {"institutional_strength": -2, "public_trust": -1},
                "economy_effects": {"budget_deficit": 5},
                "faction_effects": {"security_forces": 2, "business_elite": 2, "urban_progressives": -2},
                "policy_tags":     ["negotiation", "compromise", "backroom_deal"],
                "affected_factions": ["security_forces", "business_elite", "urban_progressives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Refuse — accept whatever consequences come",
                "description": "Late principle is still principle. The cost is real.",
                "stat_effects":    {"institutional_strength": 4, "unrest": 4, "public_trust": 2},
                "economy_effects": {},
                "faction_effects": {"security_forces": -6, "urban_progressives": 6, "workers": 4},
                "policy_tags":     ["institutional_protection", "confrontational", "anti_corruption"],
                "affected_factions": ["security_forces", "urban_progressives", "workers"],
                "event_flags":     {
                    "security_forces": ["had an informal arrangement refused after payment was expected"],
                },
                "flag_effects":    {},
            },
        ],
    },

    # Turn 9 — Pragmatist
    "pragmatist_scandal": {
        "crisis_id": "pragmatist_scandal",
        "title": "Adjacent to a Scandal",
        "description": (
            "Someone in your orbit has been doing something. "
            "You did not know. This is true. "
            "The thing they were doing is related to decisions you made, "
            "operating on assumptions about what you wanted. "
            "They are not entirely wrong about what you wanted. "
            "The journalist who has discovered this is describing it, correctly, as 'connected.'"
        ),
        "options": [
            {
                "label": "Distance yourself publicly — they acted without authorisation",
                "description": "The truth, more or less. It doesn't fully close the story.",
                "stat_effects":    {"public_trust": 3, "institutional_strength": -2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 4, "national_conservatives": -3, "security_forces": -2},
                "policy_tags":     ["accountability", "scapegoating", "partial_transparency"],
                "affected_factions": ["urban_progressives", "national_conservatives", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Protect them privately — they were doing what needed doing",
                "description": "Loyalty in. The story may still come out.",
                "stat_effects":    {"public_trust": -4, "institutional_strength": -4},
                "economy_effects": {},
                "faction_effects": {"security_forces": 4, "national_conservatives": 3, "urban_progressives": -5},
                "policy_tags":     ["loyalty", "cover_up", "institutional_risk"],
                "affected_factions": ["security_forces", "national_conservatives", "urban_progressives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Launch a genuine internal investigation",
                "description": "Show the process working. The process may not like what it finds.",
                "stat_effects":    {"public_trust": 4, "institutional_strength": 4},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 6, "workers": 4, "security_forces": -4},
                "policy_tags":     ["anti_corruption", "transparency", "rule_of_law"],
                "affected_factions": ["urban_progressives", "workers", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # Turn 10 — Pragmatist
    "pragmatist_cover_up": {
        "crisis_id": "pragmatist_cover_up",
        "title": "The Cover-Up Option",
        "description": (
            "There is a version of the previous month's situation that goes away quietly. "
            "Your Legal Advisor has identified it. "
            "It requires one decision that cannot be undone — a specific instruction "
            "to a specific office that will close a specific inquiry. "
            "The instruction is not illegal, precisely. "
            "The chain of events it would set in motion is harder to describe precisely."
        ),
        "options": [
            {
                "label": "Give the instruction — make it go away",
                "description": "You know what you're doing. You're doing it anyway.",
                "stat_effects":    {"institutional_strength": -8, "media_freedom": -5, "public_trust": -4},
                "economy_effects": {},
                "faction_effects": {"security_forces": 5, "national_conservatives": 3, "urban_progressives": -8, "workers": -4},
                "policy_tags":     ["cover_up", "institutional_abuse", "authoritarian"],
                "affected_factions": ["security_forces", "national_conservatives", "urban_progressives", "workers"],
                "event_flags":     {
                    "urban_progressives": ["saw a government inquiry closed through a direct executive instruction"],
                },
                "flag_effects":    {},
            },
            {
                "label": "Let it come out — control the disclosure yourself",
                "description": "The harder right. It still comes out. You choose the shape.",
                "stat_effects":    {"public_trust": 5, "institutional_strength": 3},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 7, "workers": 4, "security_forces": -4},
                "policy_tags":     ["transparency", "accountability", "self_disclosure"],
                "affected_factions": ["urban_progressives", "workers", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Refer it to an independent body and step back",
                "description": "The process takes over. You stop being the story.",
                "stat_effects":    {"public_trust": 4, "institutional_strength": 5},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 5, "workers": 4, "security_forces": -3},
                "policy_tags":     ["rule_of_law", "transparency", "institutional_respect"],
                "affected_factions": ["urban_progressives", "workers", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # Turn 11 — Pragmatist
    "pragmatist_loyalty_test": {
        "crisis_id": "pragmatist_loyalty_test",
        "title": "The Party Wants a Loyalty Test",
        "description": (
            "Your party leadership has produced a list of names to endorse for appointments. "
            "Twenty-two names. Most are competent. Most are fine. "
            "Three are not. "
            "The three are loyalists in the specific sense that they have done things "
            "for the party that the party would prefer not to be mentioned. "
            "Your Party Strategist says endorsing the full list is 'standard.' "
            "Your Reform Advisor says endorsing the full list is 'a line.'"
        ),
        "options": [
            {
                "label": "Endorse the full list",
                "description": "The standard choice. The party is satisfied. The three names are in.",
                "stat_effects":    {"institutional_strength": -5, "media_freedom": -3, "public_trust": -2},
                "economy_effects": {},
                "faction_effects": {"security_forces": 5, "national_conservatives": 6, "urban_progressives": -8, "workers": -3},
                "policy_tags":     ["institutional_abuse", "loyalty", "corruption_risk"],
                "affected_factions": ["security_forces", "national_conservatives", "urban_progressives", "workers"],
                "event_flags":     {
                    "urban_progressives": ["watched the government endorse three controversial loyalist appointments"],
                },
                "flag_effects":    {},
            },
            {
                "label": "Endorse most — draw the line at three",
                "description": "Twenty-two is fine. Three is not. The party notes your position.",
                "stat_effects":    {"institutional_strength": -2, "public_trust": 3},
                "economy_effects": {},
                "faction_effects": {"national_conservatives": -3, "urban_progressives": 5, "workers": 3},
                "policy_tags":     ["partial_accountability", "institutional_protection", "compromise"],
                "affected_factions": ["national_conservatives", "urban_progressives", "workers"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Refuse the list entirely",
                "description": "The party is now a problem. Something else stops being a problem.",
                "stat_effects":    {"public_trust": 4, "institutional_strength": 2, "unrest": 3},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 7, "workers": 5, "national_conservatives": -7},
                "policy_tags":     ["anti_corruption", "confrontational", "institutional_protection"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # Turn 12 — Pragmatist
    "pragmatist_election_q": {
        "crisis_id": "pragmatist_election_q",
        "title": "The Early Election Question",
        "description": (
            "The opposition wants an early election. "
            "You don't have to agree. You do not want to agree. "
            "The reason you don't want to agree is now the story. "
            "Your Party Strategist says refusing is politically survivable. "
            "Your Reform Advisor says the reason you're refusing is exactly what "
            "the opposition is pointing at. "
            "Both of them have been right about different things all year."
        ),
        "options": [
            {
                "label": "Call early elections — demonstrate confidence",
                "description": "Risky. Democratic. Lets the country weigh a complicated year.",
                "stat_effects":    {"institutional_strength": 6, "public_trust": 5},
                "economy_effects": {"stock_market": 2},
                "faction_effects": {"urban_progressives": 8, "workers": 5, "national_conservatives": -4, "security_forces": -3},
                "policy_tags":     ["democracy", "democratic_process", "elections"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Refuse — explain your reasons",
                "description": "Defensible. The reasons are now the headline.",
                "stat_effects":    {"public_trust": -3, "institutional_strength": -3},
                "economy_effects": {},
                "faction_effects": {"national_conservatives": 4, "urban_progressives": -6, "workers": -3},
                "policy_tags":     ["deflection", "dismissal", "institutional_protection"],
                "affected_factions": ["national_conservatives", "urban_progressives", "workers"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Propose a fixed election date — six months hence",
                "description": "Buy the time. Offer the commitment. The opposition is mildly satisfied.",
                "stat_effects":    {"public_trust": 2, "institutional_strength": 2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 4, "workers": 3, "national_conservatives": -2},
                "policy_tags":     ["compromise", "democratic_process", "delay"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Make it conditional — tie it to opposition behaviour",
                "description": "Tactical. They find it maddening. It is designed to be maddening.",
                "stat_effects":    {"public_trust": -2, "institutional_strength": -2},
                "economy_effects": {},
                "faction_effects": {"national_conservatives": 4, "urban_progressives": -5, "security_forces": 2},
                "policy_tags":     ["political_maneuvering", "deflection", "tactical"],
                "affected_factions": ["national_conservatives", "urban_progressives", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # ── ACT 3 — PATH 3: THE CONSOLIDATOR ──────────────────────────────────────

    # Turn 8 — Consolidator
    "consolidator_efficiency": {
        "crisis_id": "consolidator_efficiency",
        "title": "The Efficiency Argument",
        "description": (
            "Your Senior Advisor has presented a plan. "
            "It is genuinely effective — the projections are solid, the implementation "
            "is achievable, and the outcomes would be measurably better. "
            "It also requires bypassing the Economic Oversight Board for six months "
            "'while the mechanisms are established.' "
            "The Board exists specifically to prevent this kind of bypassing. "
            "Your advisor says 'temporarily' with considerable confidence."
        ),
        "options": [
            {
                "label": "Implement the plan — bypass the Board temporarily",
                "description": "Effective. The 'temporarily' will be tested later.",
                "stat_effects":    {"institutional_strength": -10, "media_freedom": -3, "unrest": -3},
                "economy_effects": {"budget_deficit": -5, "unemployment": -4},
                "faction_effects": {"security_forces": 8, "business_elite": 6, "urban_progressives": -10, "workers": -3},
                "policy_tags":     ["emergency_powers", "authoritarian", "efficiency"],
                "affected_factions": ["security_forces", "business_elite", "urban_progressives", "workers"],
                "event_flags":     {
                    "urban_progressives": ["saw the government bypass the Economic Oversight Board by executive order"],
                },
                "flag_effects":    {},
            },
            {
                "label": "Implement with oversight mechanisms in place",
                "description": "Slower. Cleaner. The plan's benefits are reduced.",
                "stat_effects":    {"institutional_strength": -4, "public_trust": 1},
                "economy_effects": {"budget_deficit": -3, "unemployment": -2},
                "faction_effects": {"security_forces": 4, "business_elite": 3, "urban_progressives": -4},
                "policy_tags":     ["efficiency", "partial_oversight", "compromise"],
                "affected_factions": ["security_forces", "business_elite", "urban_progressives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Reject the plan — the Board exists for a reason",
                "description": "The plan goes away. The advisor is surprised.",
                "stat_effects":    {"institutional_strength": 5, "public_trust": 3},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 6, "workers": 3, "security_forces": -4, "business_elite": -3},
                "policy_tags":     ["institutional_protection", "rule_of_law", "reform"],
                "affected_factions": ["urban_progressives", "workers", "security_forces", "business_elite"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # Turn 9 — Consolidator
    "consolidator_foreign_critics": {
        "crisis_id": "consolidator_foreign_critics",
        "title": "The Foreign Critics",
        "description": (
            "International press coverage of Veridia is turning. "
            "Three major outlets have published pieces using words like 'democratic backsliding' "
            "and 'institutional erosion.' "
            "Two neighbouring governments have raised concerns through diplomatic channels. "
            "Your Foreign Affairs Minister describes the coverage as 'selective.' "
            "Your National Security Advisor describes it as 'coordinated.' "
            "Both agree it is inconvenient."
        ),
        "options": [
            {
                "label": "Engage diplomatically — offer explanations and access",
                "description": "Take the criticism seriously. Some of it is correct.",
                "stat_effects":    {"international_reputation": 5, "media_freedom": 2, "public_trust": 2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 4, "national_conservatives": -3, "business_elite": 2},
                "policy_tags":     ["diplomacy", "transparency", "international_cooperation"],
                "affected_factions": ["urban_progressives", "national_conservatives", "business_elite"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Dismiss as interference — appeal to sovereignty",
                "description": "Veridia's affairs are Veridia's. The base agrees.",
                "stat_effects":    {"international_reputation": -5, "public_trust": 1},
                "economy_effects": {"stock_market": -3},
                "faction_effects": {"national_conservatives": 8, "rural_bloc": 4, "urban_progressives": -5},
                "policy_tags":     ["sovereignty", "nationalist_messaging", "isolationism"],
                "affected_factions": ["national_conservatives", "rural_bloc", "urban_progressives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Restrict foreign media access to government functions",
                "description": "The coverage gets harder to produce. It gets louder anyway.",
                "stat_effects":    {"media_freedom": -8, "international_reputation": -6},
                "economy_effects": {"stock_market": -3},
                "faction_effects": {"national_conservatives": 6, "urban_progressives": -8, "business_elite": -3},
                "policy_tags":     ["media_restriction", "authoritarian", "isolationism"],
                "affected_factions": ["national_conservatives", "urban_progressives", "business_elite"],
                "event_flags":     {
                    "urban_progressives": ["saw foreign press credentials restricted by government order"],
                },
                "flag_effects":    {},
            },
            {
                "label": "Find common ground with sympathetic allied governments",
                "description": "Not everyone is hostile. Build the coalition you have.",
                "stat_effects":    {"international_reputation": 3, "public_trust": 1},
                "economy_effects": {},
                "faction_effects": {"business_elite": 4, "urban_progressives": 2, "national_conservatives": 3},
                "policy_tags":     ["diplomacy", "coalition_building", "international_cooperation"],
                "affected_factions": ["business_elite", "urban_progressives", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # Turn 10 — Consolidator
    "consolidator_real_crisis": {
        "crisis_id": "consolidator_real_crisis",
        "title": "A Real Crisis",
        "description": (
            "Something bad has actually happened. "
            "A major industrial failure in the eastern provinces has left three cities "
            "without reliable power and created a cascading supply disruption. "
            "It is not manufactured. It is not political. It is simply a crisis, "
            "the kind that governments exist to handle. "
            "Your centralised power could fix this faster than any committee could. "
            "This is the best argument for everything you have done this year."
        ),
        "options": [
            {
                "label": "Deploy centralised power — fix it fast",
                "description": "You can, and it works. The cost is what you've already paid.",
                "stat_effects":    {"public_trust": 7, "unrest": -10},
                "economy_effects": {"budget_deficit": 8, "unemployment": -2},
                "faction_effects": {"security_forces": 8, "workers": 5, "urban_progressives": -3, "rural_bloc": 5},
                "policy_tags":     ["emergency_powers", "efficiency", "crisis_management"],
                "affected_factions": ["security_forces", "workers", "urban_progressives", "rural_bloc"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Handle it through normal institutional channels",
                "description": "Slower. Demonstrates the institutions still work.",
                "stat_effects":    {"public_trust": 3, "institutional_strength": 5, "unrest": -4},
                "economy_effects": {"budget_deficit": 5},
                "faction_effects": {"urban_progressives": 6, "workers": 3, "security_forces": -2},
                "policy_tags":     ["institutional_respect", "rule_of_law", "crisis_management"],
                "affected_factions": ["urban_progressives", "workers", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Use the crisis to justify further consolidation",
                "description": "A crisis is also an opportunity. Your opponents know this about you now.",
                "stat_effects":    {"institutional_strength": -8, "unrest": -5, "media_freedom": -3},
                "economy_effects": {"budget_deficit": 6},
                "faction_effects": {"security_forces": 9, "national_conservatives": 7, "urban_progressives": -10, "workers": -4},
                "policy_tags":     ["emergency_powers", "authoritarian", "power_consolidation"],
                "affected_factions": ["security_forces", "national_conservatives", "urban_progressives", "workers"],
                "event_flags":     {
                    "urban_progressives": ["watched the government use an industrial crisis to justify expanded executive powers"],
                },
                "flag_effects":    {},
            },
        ],
    },

    # Turn 11 — Consolidator
    "consolidator_loyalist": {
        "crisis_id": "consolidator_loyalist",
        "title": "A Loyalist Did Something",
        "description": (
            "Someone acting in your name — without your explicit instruction — "
            "has done something they believed you wanted. "
            "They are not entirely wrong about what you wanted. "
            "The action is documented. The documentation has reached a journalist. "
            "Your Chief of Staff says: 'They were trying to help.' "
            "Your Legal Advisor says: 'That is going to be difficult to explain.'"
        ),
        "options": [
            {
                "label": "Defend them publicly — they acted in Veridia's interest",
                "description": "Loyalty in. The story becomes your story.",
                "stat_effects":    {"institutional_strength": -5, "media_freedom": -4, "public_trust": -2},
                "economy_effects": {},
                "faction_effects": {"security_forces": 6, "national_conservatives": 4, "urban_progressives": -8, "workers": -3},
                "policy_tags":     ["loyalty", "institutional_abuse", "authoritarian"],
                "affected_factions": ["security_forces", "national_conservatives", "urban_progressives", "workers"],
                "event_flags":     {
                    "urban_progressives": ["watched the government publicly defend an official who acted without authorisation"],
                },
                "flag_effects":    {},
            },
            {
                "label": "Quietly remove them — let it end there",
                "description": "Clean hands. The story doesn't end there.",
                "stat_effects":    {"public_trust": 3, "institutional_strength": -2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 3, "security_forces": -2, "workers": 2},
                "policy_tags":     ["scapegoating", "opacity", "partial_accountability"],
                "affected_factions": ["urban_progressives", "security_forces", "workers"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Acknowledge it and hold them accountable publicly",
                "description": "The most painful option. The most credible one.",
                "stat_effects":    {"public_trust": 5, "institutional_strength": 4},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 7, "workers": 4, "security_forces": -5},
                "policy_tags":     ["accountability", "transparency", "rule_of_law"],
                "affected_factions": ["urban_progressives", "workers", "security_forces"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Use the incident to restructure the command chain",
                "description": "Turn the problem into an opportunity to tighten control.",
                "stat_effects":    {"institutional_strength": -4, "media_freedom": -2},
                "economy_effects": {},
                "faction_effects": {"security_forces": 5, "national_conservatives": 5, "urban_progressives": -7},
                "policy_tags":     ["power_consolidation", "institutional_restructuring", "authoritarian"],
                "affected_factions": ["security_forces", "national_conservatives", "urban_progressives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },

    # Turn 12 — Consolidator
    "consolidator_legitimacy": {
        "crisis_id": "consolidator_legitimacy",
        "title": "The Legitimacy Question",
        "description": (
            "You have power. "
            "The question the year ends on — the question General Kosic was always going to ask, "
            "one way or another — is whether you have authority. "
            "Power is what you hold. Authority is what people grant you. "
            "They are not the same thing. "
            "Veridia is quiet. Quiet countries have asked this question before."
        ),
        "options": [
            {
                "label": "Assert authority through a popular mandate — call a referendum",
                "description": "Ask Veridia to confirm what you've built. They might.",
                "stat_effects":    {"institutional_strength": 4, "public_trust": 4, "media_freedom": 2},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 5, "national_conservatives": 5, "workers": 3},
                "policy_tags":     ["democratic_process", "elections", "legitimacy"],
                "affected_factions": ["urban_progressives", "national_conservatives", "workers"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Consolidate further — authority is power held long enough",
                "description": "You know what you are. Veridia will know too, eventually.",
                "stat_effects":    {"institutional_strength": -8, "media_freedom": -6, "public_trust": -3},
                "economy_effects": {},
                "faction_effects": {"security_forces": 8, "national_conservatives": 6, "urban_progressives": -10, "workers": -5},
                "policy_tags":     ["authoritarian", "power_consolidation", "institutional_erosion"],
                "affected_factions": ["security_forces", "national_conservatives", "urban_progressives", "workers"],
                "event_flags":     {
                    "urban_progressives": ["watched the government respond to legitimacy questions with further power consolidation"],
                },
                "flag_effects":    {},
            },
            {
                "label": "Step back — initiate a managed transition",
                "description": "The hardest choice. The one the institutions were built for.",
                "stat_effects":    {"institutional_strength": 9, "public_trust": 7, "media_freedom": 5},
                "economy_effects": {},
                "faction_effects": {"urban_progressives": 9, "workers": 6, "security_forces": -5, "national_conservatives": -3},
                "policy_tags":     ["democratic_process", "institutional_respect", "reform"],
                "affected_factions": ["urban_progressives", "workers", "security_forces", "national_conservatives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
            {
                "label": "Ignore the question — govern",
                "description": "The question doesn't go away because you don't answer it.",
                "stat_effects":    {"public_trust": -3, "unrest": 3, "institutional_strength": -2},
                "economy_effects": {},
                "faction_effects": {"national_conservatives": 4, "security_forces": 4, "urban_progressives": -6, "workers": -3},
                "policy_tags":     ["inaction", "dismissal", "authoritarian"],
                "affected_factions": ["national_conservatives", "security_forces", "urban_progressives"],
                "event_flags":     {},
                "flag_effects":    {},
            },
        ],
    },
}


# ── Path → turn → crisis_id routing ───────────────────────────────────────────

_PATH_CRISIS_MAP: dict[str, dict[int, str]] = {
    "reformer": {
        8: "reformer_foreign_offer",
        9: "reformer_supreme_court",
        10: "reformer_reform_package",
        11: "reformer_own_side",
        12: "reformer_vote",
    },
    "pragmatist": {
        8: "pragmatist_bill_due",
        9: "pragmatist_scandal",
        10: "pragmatist_cover_up",
        11: "pragmatist_loyalty_test",
        12: "pragmatist_election_q",
    },
    "consolidator": {
        8: "consolidator_efficiency",
        9: "consolidator_foreign_critics",
        10: "consolidator_real_crisis",
        11: "consolidator_loyalist",
        12: "consolidator_legitimacy",
    },
}


def select_campaign_crisis(state: GameState) -> dict:
    """
    Return the correct campaign crisis for the current turn and flag state.
    Call this from the pre-turn graph node (after path has been determined).
    """
    turn = state["current_turn"]
    flags = state.get("campaign_flags") or {}

    if turn == 1:
        crisis_id = "what_they_left_behind"

    elif turn == 2:
        fo = flags.get("fiscal_opening", "transparent")
        if fo == "political":
            crisis_id = "former_govt_lawyer"
        elif fo == "quiet":
            crisis_id = "markets_heard_something"
        else:
            crisis_id = "unions_read_budget"

    elif turn == 3:
        crisis_id = "general_requests_meeting"

    elif turn == 4:
        crisis_id = "the_dossier" if flags.get("kosic_relationship") == "ally" else "budget_request_arrives"

    elif turn == 5:
        crisis_id = "someone_leaked_something" if flags.get("kosic_relationship") == "ally" else "border_situation"

    elif turn == 6:
        crisis_id = "streets_are_full"

    elif turn == 7:
        crisis_id = "paper_chooses_sides_a" if flags.get("kosic_relationship") == "ally" else "paper_chooses_sides_b"

    else:  # turns 8–12
        path = flags.get("path") or _determine_path(flags)
        turn_key = min(turn, 12)
        crisis_id = _PATH_CRISIS_MAP.get(path, _PATH_CRISIS_MAP["pragmatist"]).get(turn_key)
        if crisis_id is None:
            crisis_id = "what_they_left_behind"  # fallback, shouldn't happen

    return CAMPAIGN_CRISES[crisis_id]
