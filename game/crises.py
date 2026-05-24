"""
12 authored crisis templates for Veridia.

Each option defines:
  stat_effects      – deterministic national stat deltas
  faction_effects   – deterministic faction support deltas
  policy_tags       – list of tags for LLM reaction context
  affected_factions – factions the LLM should classify reactions for
  event_flags       – {faction_id: [flag_strings]} for Option C mood modifiers
"""

from typing import Any

CRISIS_TEMPLATES: list[dict[str, Any]] = [

    # ── 1 ─────────────────────────────────────────────────────────────────────
    {
        "crisis_id": "food_price_protests",
        "title": "The Bread Is Too Expensive Again",
        "description": (
            "Food prices have risen for three consecutive months. "
            "Protesters are gathering outside the Assembly with signs that range from "
            "the heartfelt to the grammatically ambitious. Unions are demanding emergency subsidies. "
            "Your Finance Minister is demanding you not give them. Both are using the word 'obviously.'"
        ),
        "options": [
            {
                "label": "Introduce emergency food subsidies",
                "description": "Fund direct price relief. Expensive but immediate.",
                "stat_effects":    {"budget": -12, "unrest": -10, "public_trust": 5},
                "faction_effects": {"workers": 8, "urban_progressives": 4, "business_elite": -4},
                "policy_tags":     ["food_subsidy", "public_spending", "cost_of_living_relief"],
                "affected_factions": ["workers", "urban_progressives", "business_elite", "rural_bloc"],
                "event_flags":     {},
            },
            {
                "label": "Negotiate with union leaders, delay spending",
                "description": "Buy time with dialogue. Cheaper, but the protests continue.",
                "stat_effects":    {"budget": -2, "unrest": -3, "public_trust": 2},
                "faction_effects": {"workers": 3, "urban_progressives": 2},
                "policy_tags":     ["union_negotiation", "delayed_spending", "compromise"],
                "affected_factions": ["workers", "urban_progressives", "business_elite"],
                "event_flags":     {},
            },
            {
                "label": "Deploy police to disperse the protests",
                "description": "Clear the streets. Order restored. Trust destroyed.",
                "stat_effects":    {"unrest": -5, "institutional_strength": -6, "media_freedom": -3},
                "faction_effects": {"security_forces": 6, "workers": -5, "urban_progressives": -8},
                "policy_tags":     ["police_crackdown", "public_order", "civil_liberties_risk"],
                "affected_factions": ["workers", "urban_progressives", "security_forces", "rural_bloc"],
                "event_flags":     {
                    "workers": ["were cracked down on during food protests last month"],
                    "urban_progressives": ["witnessed police dispersal of food protesters"],
                },
            },
            {
                "label": "Blame foreign suppliers, launch nationalist media campaign",
                "description": "Point outward. Briefly unifying. Internationally problematic.",
                "stat_effects":    {"unrest": -2, "public_trust": -2, "international_reputation": -5},
                "faction_effects": {"national_conservatives": 6, "rural_bloc": 2, "urban_progressives": -4},
                "policy_tags":     ["nationalist_messaging", "foreign_blame", "media_campaign"],
                "affected_factions": ["national_conservatives", "rural_bloc", "urban_progressives", "business_elite"],
                "event_flags":     {},
            },
        ],
    },

    # ── 2 ─────────────────────────────────────────────────────────────────────
    {
        "crisis_id": "investment_freeze",
        "title": "The Money Is Leaving",
        "description": (
            "The Veridia Business Council has issued a joint statement: "
            "they are 'pausing investment decisions pending policy clarity.' "
            "This is business language for 'we are terrified.' "
            "Your economy minister says this is very bad. Your party strategist says "
            "this is an opportunity to look strong. They are both right, which is the problem."
        ),
        "options": [
            {
                "label": "Offer targeted tax incentives to retain investors",
                "description": "Sweeten the deal. Budget takes a hit; confidence may recover.",
                "stat_effects":    {"budget": -8, "economy": 5, "international_reputation": 4},
                "faction_effects": {"business_elite": 10, "workers": -3, "urban_progressives": -2},
                "policy_tags":     ["tax_incentives", "business_friendly", "fiscal_cost"],
                "affected_factions": ["business_elite", "workers", "urban_progressives"],
                "event_flags":     {},
            },
            {
                "label": "Roll back recent regulations to ease business concerns",
                "description": "Deregulate. Business is happy. Others are less happy.",
                "stat_effects":    {"economy": 4, "institutional_strength": -4},
                "faction_effects": {"business_elite": 8, "workers": -6, "urban_progressives": -5},
                "policy_tags":     ["deregulation", "business_friendly", "worker_rights_risk"],
                "affected_factions": ["business_elite", "workers", "urban_progressives"],
                "event_flags":     {
                    "workers": ["saw worker protections rolled back to court investors"],
                },
            },
            {
                "label": "Threaten nationalization of key sectors",
                "description": "Call their bluff. Populist but economically dangerous.",
                "stat_effects":    {"economy": -6, "budget": -4, "international_reputation": -6},
                "faction_effects": {"workers": 7, "business_elite": -12, "national_conservatives": 3},
                "policy_tags":     ["nationalization", "anti_business", "populist"],
                "affected_factions": ["workers", "business_elite", "national_conservatives", "rural_bloc"],
                "event_flags":     {
                    "business_elite": ["faced nationalization threats from the government"],
                },
            },
            {
                "label": "Dismiss the concerns as market speculation",
                "description": "Do nothing and hope confidence returns. It probably won't.",
                "stat_effects":    {"economy": -4, "public_trust": -3},
                "faction_effects": {"business_elite": -5, "workers": -2},
                "policy_tags":     ["inaction", "dismissal"],
                "affected_factions": ["business_elite", "workers", "urban_progressives"],
                "event_flags":     {},
            },
        ],
    },

    # ── 3 ─────────────────────────────────────────────────────────────────────
    {
        "crisis_id": "corruption_scandal",
        "title": "Someone in the Cabinet Has Been Stealing",
        "description": (
            "An investigative journalist has published financial records suggesting "
            "your Trade Minister redirected infrastructure contracts to a company "
            "owned by his cousin's wife's brother. The minister says this is coincidence. "
            "The journalist has thirty-seven pages of coincidences. The public is watching."
        ),
        "options": [
            {
                "label": "Launch a full independent investigation",
                "description": "Costly politically but restores credibility if you can survive the findings.",
                "stat_effects":    {"public_trust": 8, "institutional_strength": 6, "budget": -3},
                "faction_effects": {"urban_progressives": 10, "workers": 4, "business_elite": -4, "security_forces": -3},
                "policy_tags":     ["anti_corruption", "transparency", "rule_of_law"],
                "affected_factions": ["urban_progressives", "workers", "business_elite", "national_conservatives"],
                "event_flags":     {},
            },
            {
                "label": "Sack the minister and declare the matter closed",
                "description": "One sacrifice. Quick. Clean. Doesn't fully satisfy anyone.",
                "stat_effects":    {"public_trust": 3, "unrest": -2},
                "faction_effects": {"urban_progressives": 3, "workers": 2, "business_elite": 2},
                "policy_tags":     ["scapegoating", "partial_accountability"],
                "affected_factions": ["urban_progressives", "workers", "business_elite"],
                "event_flags":     {},
            },
            {
                "label": "Control the narrative — discredit the journalist",
                "description": "Attack the messenger. Works short-term. Damages democracy long-term.",
                "stat_effects":    {"media_freedom": -8, "institutional_strength": -5, "public_trust": -4},
                "faction_effects": {"national_conservatives": 5, "urban_progressives": -10, "workers": -4},
                "policy_tags":     ["media_restriction", "authoritarian", "cover_up"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives", "business_elite"],
                "event_flags":     {
                    "urban_progressives": ["watched the government attack a journalist exposing corruption"],
                },
            },
            {
                "label": "Blame the opposition for orchestrating the leak",
                "description": "Deflect. Polarizing but galvanizes your base.",
                "stat_effects":    {"public_trust": -5, "institutional_strength": -4, "unrest": 4},
                "faction_effects": {"national_conservatives": 6, "urban_progressives": -8, "workers": -3},
                "policy_tags":     ["deflection", "polarization", "nationalist_messaging"],
                "affected_factions": ["urban_progressives", "national_conservatives", "workers"],
                "event_flags":     {},
            },
        ],
    },

    # ── 4 ─────────────────────────────────────────────────────────────────────
    {
        "crisis_id": "rural_fuel_protests",
        "title": "The Tractors Are Blocking the Highway",
        "description": (
            "Rural communities are blocking three major arterial roads with tractors, "
            "hay bales, and what one regional governor is calling 'a frankly impressive "
            "level of organizational commitment.' The immediate cause is fuel prices. "
            "The deeper cause is a decade of feeling invisible to the capital. "
            "Your advisors agree it is 'not great.'"
        ),
        "options": [
            {
                "label": "Introduce rural fuel subsidies",
                "description": "Address the immediate trigger. Expensive but effective.",
                "stat_effects":    {"budget": -10, "unrest": -8},
                "faction_effects": {"rural_bloc": 10, "business_elite": -3, "workers": 3},
                "policy_tags":     ["fuel_subsidy", "rural_infrastructure", "public_spending"],
                "affected_factions": ["rural_bloc", "business_elite", "workers", "national_conservatives"],
                "event_flags":     {},
            },
            {
                "label": "Commission a rural development dialogue",
                "description": "Form a committee. Rural voters have seen committees before.",
                "stat_effects":    {"budget": -1, "unrest": -2},
                "faction_effects": {"rural_bloc": 3, "urban_progressives": 2},
                "policy_tags":     ["delayed_spending", "consultation", "compromise"],
                "affected_factions": ["rural_bloc", "urban_progressives", "national_conservatives"],
                "event_flags":     {},
            },
            {
                "label": "Dispatch police to clear the roads",
                "description": "Reopen the arteries. Earn the resentment of everyone who owns a tractor.",
                "stat_effects":    {"unrest": -4, "institutional_strength": -5, "media_freedom": -2},
                "faction_effects": {"security_forces": 5, "rural_bloc": -12, "urban_progressives": -5},
                "policy_tags":     ["police_crackdown", "public_order", "rural_alienation"],
                "affected_factions": ["rural_bloc", "security_forces", "urban_progressives", "workers"],
                "event_flags":     {
                    "rural_bloc": ["had their blockade forcibly dispersed by police last month"],
                },
            },
            {
                "label": "Impose emergency fuel price controls",
                "description": "Cap prices by decree. Quick fix with long-term market distortions.",
                "stat_effects":    {"budget": -5, "economy": -3, "unrest": -5},
                "faction_effects": {"rural_bloc": 7, "workers": 5, "business_elite": -7},
                "policy_tags":     ["price_controls", "emergency_powers", "anti_market"],
                "affected_factions": ["rural_bloc", "workers", "business_elite", "national_conservatives"],
                "event_flags":     {
                    "business_elite": ["had fuel prices capped by emergency decree"],
                },
            },
        ],
    },

    # ── 5 ─────────────────────────────────────────────────────────────────────
    {
        "crisis_id": "police_reform_demands",
        "title": "The Students Want the Police to Stop Hitting People",
        "description": (
            "University student groups have organized a series of marches demanding "
            "a civilian oversight board for the police, following a protest dispersal "
            "in which several students required medical attention. "
            "The police describe their actions as 'proportionate.' The hospital describes "
            "the injuries as 'inconsistent with that characterization.'"
        ),
        "options": [
            {
                "label": "Establish an independent police oversight commission",
                "description": "Real reform. The Security Forces will not love you for this.",
                "stat_effects":    {"institutional_strength": 7, "public_trust": 6, "media_freedom": 3},
                "faction_effects": {"urban_progressives": 12, "workers": 4, "security_forces": -8},
                "policy_tags":     ["police_reform", "civil_liberties", "institutional_reform"],
                "affected_factions": ["urban_progressives", "workers", "security_forces", "national_conservatives"],
                "event_flags":     {
                    "security_forces": ["had civilian oversight imposed over their objections"],
                },
            },
            {
                "label": "Meet with student leaders and promise a review",
                "description": "Dialogue without commitment. Buys time, satisfies no one permanently.",
                "stat_effects":    {"unrest": -3, "public_trust": 2},
                "faction_effects": {"urban_progressives": 4, "workers": 2, "security_forces": -2},
                "policy_tags":     ["consultation", "delayed_reform", "compromise"],
                "affected_factions": ["urban_progressives", "security_forces"],
                "event_flags":     {},
            },
            {
                "label": "Dismiss the demands as outside agitation",
                "description": "Frame reformers as foreign-influenced troublemakers. The base loves it.",
                "stat_effects":    {"media_freedom": -5, "institutional_strength": -4, "public_trust": -3},
                "faction_effects": {"national_conservatives": 7, "security_forces": 4, "urban_progressives": -10},
                "policy_tags":     ["nationalist_messaging", "civil_liberties_risk", "dismissal"],
                "affected_factions": ["urban_progressives", "national_conservatives", "security_forces"],
                "event_flags":     {
                    "urban_progressives": ["had their reform demands dismissed as foreign interference"],
                },
            },
            {
                "label": "Announce symbolic reforms with no enforcement mechanism",
                "description": "The appearance of accountability. Fools no one but annoys everyone slightly less.",
                "stat_effects":    {"public_trust": 1, "unrest": -2},
                "faction_effects": {"urban_progressives": 2, "security_forces": -1, "workers": 1},
                "policy_tags":     ["symbolic_reform", "optics", "partial_accountability"],
                "affected_factions": ["urban_progressives", "security_forces"],
                "event_flags":     {},
            },
        ],
    },

    # ── 6 ─────────────────────────────────────────────────────────────────────
    {
        "crisis_id": "border_tensions",
        "title": "The Neighbour Is Being a Problem Again",
        "description": (
            "The neighbouring state of Caldronia has moved military units to the border "
            "following a dispute over a river that both countries claim. "
            "No shots have been fired. Yet. Your Defence Minister says this is an outrage. "
            "Your Foreign Affairs Minister says this is normal. They have agreed to disagree "
            "by not being in the same room."
        ),
        "options": [
            {
                "label": "Pursue diplomatic talks through international mediators",
                "description": "Measured. Slow. Internationally respectable.",
                "stat_effects":    {"international_reputation": 7, "unrest": -3},
                "faction_effects": {"urban_progressives": 6, "national_conservatives": -5, "security_forces": -3},
                "policy_tags":     ["diplomacy", "international_cooperation", "foreign_affairs"],
                "affected_factions": ["urban_progressives", "national_conservatives", "security_forces"],
                "event_flags":     {},
            },
            {
                "label": "Respond with military posturing and public statements",
                "description": "Show strength. Rally the base. Escalate the situation.",
                "stat_effects":    {"unrest": 5, "economy": -4, "international_reputation": -5},
                "faction_effects": {"security_forces": 8, "national_conservatives": 9, "urban_progressives": -6, "business_elite": -4},
                "policy_tags":     ["militarism", "nationalist_messaging", "escalation"],
                "affected_factions": ["security_forces", "national_conservatives", "urban_progressives", "business_elite"],
                "event_flags":     {},
            },
            {
                "label": "Impose economic sanctions on Caldronia",
                "description": "Targeted pressure. Hurts trade on both sides.",
                "stat_effects":    {"economy": -5, "budget": -4, "international_reputation": 2},
                "faction_effects": {"business_elite": -6, "national_conservatives": 4, "rural_bloc": -3},
                "policy_tags":     ["economic_sanctions", "foreign_policy", "trade_disruption"],
                "affected_factions": ["business_elite", "national_conservatives", "rural_bloc"],
                "event_flags":     {
                    "business_elite": ["saw cross-border trade disrupted by sanctions"],
                },
            },
            {
                "label": "Appeal to international courts and bodies",
                "description": "Principled and slow. Your sovereignty hawks will be furious.",
                "stat_effects":    {"international_reputation": 8, "institutional_strength": 4},
                "faction_effects": {"urban_progressives": 8, "national_conservatives": -8, "security_forces": -4},
                "policy_tags":     ["international_law", "diplomacy", "sovereignty_concern"],
                "affected_factions": ["urban_progressives", "national_conservatives", "security_forces"],
                "event_flags":     {},
            },
        ],
    },

    # ── 7 ─────────────────────────────────────────────────────────────────────
    {
        "crisis_id": "document_leak",
        "title": "Someone Left the Filing Cabinet Open",
        "description": (
            "A digital cache of internal government communications has been published "
            "by an anonymous source. The documents reveal, among other things: "
            "a minister who described the budget as 'a polite fiction,' "
            "a security briefing that used the phrase 'containable unrest' three months "
            "before the unrest became very much less containable, "
            "and a memo from your own office that you do not remember writing but "
            "almost certainly did."
        ),
        "options": [
            {
                "label": "Embrace transparency — hold a full public disclosure",
                "description": "Get ahead of it. Painful, honest, potentially survivable.",
                "stat_effects":    {"public_trust": 9, "institutional_strength": 5, "unrest": -3},
                "faction_effects": {"urban_progressives": 10, "workers": 5, "business_elite": -5, "security_forces": -4},
                "policy_tags":     ["transparency", "accountability", "media_freedom"],
                "affected_factions": ["urban_progressives", "workers", "business_elite", "national_conservatives"],
                "event_flags":     {},
            },
            {
                "label": "Deny the documents' authenticity",
                "description": "Lie. This works until it doesn't. Then it really doesn't.",
                "stat_effects":    {"public_trust": -7, "institutional_strength": -5, "media_freedom": -4},
                "faction_effects": {"urban_progressives": -9, "workers": -4, "national_conservatives": 3},
                "policy_tags":     ["cover_up", "disinformation", "media_restriction"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives", "business_elite"],
                "event_flags":     {
                    "urban_progressives": ["watched the government deny authenticated leaked documents"],
                },
            },
            {
                "label": "Partial disclosure — release selected documents, launch leak investigation",
                "description": "Controlled damage. Looks like accountability without being it.",
                "stat_effects":    {"public_trust": 4, "institutional_strength": 2, "media_freedom": -2},
                "faction_effects": {"urban_progressives": 4, "workers": 3, "business_elite": 1},
                "policy_tags":     ["partial_transparency", "investigation", "media_management"],
                "affected_factions": ["urban_progressives", "workers", "business_elite"],
                "event_flags":     {},
            },
            {
                "label": "Declare the leak a national security threat and restrict coverage",
                "description": "Silence the story. The story gets louder.",
                "stat_effects":    {"media_freedom": -10, "public_trust": -6, "international_reputation": -5},
                "faction_effects": {"national_conservatives": 4, "urban_progressives": -12, "workers": -5},
                "policy_tags":     ["emergency_powers", "media_restriction", "authoritarian"],
                "affected_factions": ["urban_progressives", "national_conservatives", "security_forces", "workers"],
                "event_flags":     {
                    "urban_progressives": ["had press coverage of the document leak suppressed"],
                },
            },
        ],
    },

    # ── 8 ─────────────────────────────────────────────────────────────────────
    {
        "crisis_id": "military_emergency_powers",
        "title": "The Generals Would Like More Power, Please",
        "description": (
            "The Security Chief has submitted a formal request for expanded emergency powers, "
            "citing rising unrest, regional instability, and what he calls 'an operational need "
            "for cleaner command lines.' Your Reform Advisor describes this as 'a cheerful way "
            "of asking to bypass the courts.' Both are technically correct."
        ),
        "options": [
            {
                "label": "Grant expanded emergency powers to the Security Forces",
                "description": "Order is restored. Something else may be less easily restored.",
                "stat_effects":    {"unrest": -10, "institutional_strength": -10, "media_freedom": -5},
                "faction_effects": {"security_forces": 12, "urban_progressives": -10, "workers": -5, "national_conservatives": 6},
                "policy_tags":     ["emergency_powers", "authoritarian", "security_priority"],
                "affected_factions": ["security_forces", "urban_progressives", "workers", "national_conservatives"],
                "event_flags":     {
                    "urban_progressives": ["saw emergency powers granted to the military without judicial review"],
                },
            },
            {
                "label": "Grant limited powers with sunset clauses and oversight",
                "description": "A compromise. The generals get some of what they want; you retain some control.",
                "stat_effects":    {"unrest": -5, "institutional_strength": -3},
                "faction_effects": {"security_forces": 5, "urban_progressives": -4, "workers": -2},
                "policy_tags":     ["limited_emergency_powers", "oversight", "compromise"],
                "affected_factions": ["security_forces", "urban_progressives", "workers"],
                "event_flags":     {},
            },
            {
                "label": "Decline — offer increased funding instead",
                "description": "Pay them, don't empower them. Preserves institutions. Annoys the generals.",
                "stat_effects":    {"budget": -8, "institutional_strength": 5},
                "faction_effects": {"security_forces": -6, "urban_progressives": 7, "workers": 2},
                "policy_tags":     ["institutional_protection", "military_funding", "democracy"],
                "affected_factions": ["security_forces", "urban_progressives", "workers"],
                "event_flags":     {
                    "security_forces": ["were denied emergency powers and given a budget increase instead"],
                },
            },
            {
                "label": "Form a review committee to study the request",
                "description": "The government's answer to everything. Buys six weeks and no goodwill.",
                "stat_effects":    {"unrest": 2},
                "faction_effects": {"security_forces": -3, "urban_progressives": 1},
                "policy_tags":     ["delay", "consultation", "bureaucratic"],
                "affected_factions": ["security_forces", "urban_progressives"],
                "event_flags":     {},
            },
        ],
    },

    # ── 9 ─────────────────────────────────────────────────────────────────────
    {
        "crisis_id": "public_sector_strike",
        "title": "The Civil Servants Have Had Enough",
        "description": (
            "Public sector unions representing teachers, transit workers, and hospital "
            "staff have announced a general strike in forty-eight hours unless wage "
            "negotiations resume. Your Finance Minister says there is no money. "
            "Your Party Strategist says there is no time. "
            "A transit driver told a journalist: 'We have been being patient for four years.' "
            "The journalist found this sentence grammatically interesting and morally compelling."
        ),
        "options": [
            {
                "label": "Negotiate immediate wage increases",
                "description": "Expensive. The strike is averted. The budget is not improved.",
                "stat_effects":    {"budget": -12, "unrest": -8, "public_trust": 4},
                "faction_effects": {"workers": 10, "urban_progressives": 5, "business_elite": -5},
                "policy_tags":     ["union_negotiation", "wage_increase", "public_spending"],
                "affected_factions": ["workers", "urban_progressives", "business_elite", "rural_bloc"],
                "event_flags":     {},
            },
            {
                "label": "Declare the strike illegal and order workers back",
                "description": "Legally dubious. Politically explosive. Briefly effective.",
                "stat_effects":    {"institutional_strength": -8, "unrest": 5, "public_trust": -5},
                "faction_effects": {"security_forces": 5, "workers": -12, "urban_progressives": -8, "business_elite": 3},
                "policy_tags":     ["anti_union", "emergency_powers", "authoritarian"],
                "affected_factions": ["workers", "urban_progressives", "security_forces", "business_elite"],
                "event_flags":     {
                    "workers": ["had their strike declared illegal and were ordered back to work"],
                    "urban_progressives": ["watched the government criminalize public sector strikes"],
                },
            },
            {
                "label": "Offer non-monetary benefits — extra leave, job protections",
                "description": "Creative compromise. Unions are cautiously unenthusiastic.",
                "stat_effects":    {"budget": -2, "unrest": -4},
                "faction_effects": {"workers": 4, "urban_progressives": 3, "business_elite": 1},
                "policy_tags":     ["compromise", "non_monetary", "union_negotiation"],
                "affected_factions": ["workers", "urban_progressives", "business_elite"],
                "event_flags":     {},
            },
            {
                "label": "Wait them out — let the strike run its course",
                "description": "Inaction as strategy. The public will suffer. You hope the unions blink first.",
                "stat_effects":    {"unrest": 8, "economy": -6, "public_trust": -4},
                "faction_effects": {"workers": -8, "urban_progressives": -5, "business_elite": -3},
                "policy_tags":     ["inaction", "waiting_game", "confrontational"],
                "affected_factions": ["workers", "urban_progressives", "business_elite"],
                "event_flags":     {},
            },
        ],
    },

    # ── 10 ────────────────────────────────────────────────────────────────────
    {
        "crisis_id": "foreign_austerity",
        "title": "The Lenders Have Opinions About How You Spend Money",
        "description": (
            "Veridia's primary foreign creditors have released a joint statement "
            "recommending 'fiscal consolidation measures as a precondition for "
            "continued lending arrangements.' Your Finance Minister translates: "
            "they want cuts. Your party base calls this 'foreign interference.' "
            "Both statements are accurate, which is what makes this awkward."
        ),
        "options": [
            {
                "label": "Accept the austerity conditions",
                "description": "Improve fiscal credibility. Devastate the people who elected you.",
                "stat_effects":    {"budget": 10, "economy": 3, "international_reputation": 7, "unrest": 6},
                "faction_effects": {"business_elite": 7, "workers": -10, "urban_progressives": -5, "rural_bloc": -6},
                "policy_tags":     ["austerity", "foreign_aid", "fiscal_discipline"],
                "affected_factions": ["workers", "business_elite", "urban_progressives", "rural_bloc", "national_conservatives"],
                "event_flags":     {
                    "workers": ["saw austerity measures accepted under pressure from foreign lenders"],
                    "rural_bloc": ["experienced cuts to rural programs due to foreign lender conditions"],
                },
            },
            {
                "label": "Negotiate partial compliance — agree to some conditions",
                "description": "A diplomatic middle path. Lenders are mildly satisfied. Citizens are mildly furious.",
                "stat_effects":    {"budget": 5, "economy": 1, "international_reputation": 3, "unrest": 3},
                "faction_effects": {"business_elite": 4, "workers": -5, "urban_progressives": -2, "rural_bloc": -3},
                "policy_tags":     ["partial_austerity", "negotiation", "compromise"],
                "affected_factions": ["workers", "business_elite", "national_conservatives"],
                "event_flags":     {},
            },
            {
                "label": "Reject conditions — seek alternative financing domestically",
                "description": "Assert sovereignty. Riskier economically, popular with nationalists.",
                "stat_effects":    {"budget": -5, "economy": -4, "international_reputation": -7},
                "faction_effects": {"national_conservatives": 10, "rural_bloc": 5, "business_elite": -8, "urban_progressives": 3},
                "policy_tags":     ["sovereignty", "anti_austerity", "nationalist_messaging"],
                "affected_factions": ["national_conservatives", "rural_bloc", "business_elite", "urban_progressives"],
                "event_flags":     {},
            },
            {
                "label": "Reject conditions publicly while secretly continuing negotiations",
                "description": "The classic. Everyone discovers the contradiction eventually.",
                "stat_effects":    {"public_trust": -7, "institutional_strength": -4, "international_reputation": -3},
                "faction_effects": {"national_conservatives": 4, "workers": -3, "urban_progressives": -6, "business_elite": 2},
                "policy_tags":     ["duplicity", "nationalist_messaging", "disinformation"],
                "affected_factions": ["urban_progressives", "national_conservatives", "business_elite"],
                "event_flags":     {},
            },
        ],
    },

    # ── 11 ────────────────────────────────────────────────────────────────────
    {
        "crisis_id": "housing_crisis",
        "title": "No One Can Afford to Live Anywhere",
        "description": (
            "Rent in Veridia's capital has increased forty percent in three years. "
            "Young professionals are relocating to the provinces. "
            "Young non-professionals are relocating to their parents. "
            "A tent city has appeared outside the Assembly building. "
            "The Assembly members describe this as 'a visual concern.'"
        ),
        "options": [
            {
                "label": "Introduce rent controls and tenant protections",
                "description": "Immediate relief for renters. Landlords and developers will not send a thank-you note.",
                "stat_effects":    {"unrest": -6, "public_trust": 5, "economy": -2},
                "faction_effects": {"workers": 9, "urban_progressives": 8, "business_elite": -8, "rural_bloc": 2},
                "policy_tags":     ["rent_control", "housing_policy", "anti_market"],
                "affected_factions": ["workers", "urban_progressives", "business_elite", "rural_bloc"],
                "event_flags":     {
                    "business_elite": ["had rent controls imposed on their property investments"],
                },
            },
            {
                "label": "Fund a major public housing construction program",
                "description": "Long-term solution. Short-term budget hit. Takes years to show results.",
                "stat_effects":    {"budget": -10, "economy": 3, "public_trust": 4},
                "faction_effects": {"workers": 6, "urban_progressives": 5, "business_elite": 3, "rural_bloc": 3},
                "policy_tags":     ["public_spending", "housing_construction", "infrastructure"],
                "affected_factions": ["workers", "urban_progressives", "business_elite"],
                "event_flags":     {},
            },
            {
                "label": "Publicly blame wealthy landlords and speculators",
                "description": "Populist and accurate. No policy attached. Feels good. Changes little.",
                "stat_effects":    {"unrest": -4, "public_trust": 2, "economy": -1},
                "faction_effects": {"workers": 6, "urban_progressives": 5, "business_elite": -10, "rural_bloc": 1},
                "policy_tags":     ["populist", "scapegoating", "no_policy"],
                "affected_factions": ["workers", "urban_progressives", "business_elite"],
                "event_flags":     {},
            },
            {
                "label": "Deregulate planning to boost private construction",
                "description": "Market solution. Will take years and probably won't help the people in tents.",
                "stat_effects":    {"economy": 2, "institutional_strength": -3},
                "faction_effects": {"business_elite": 8, "workers": -4, "urban_progressives": -5},
                "policy_tags":     ["deregulation", "market_solution", "housing_policy"],
                "affected_factions": ["business_elite", "workers", "urban_progressives"],
                "event_flags":     {},
            },
        ],
    },

    # ── 12 ────────────────────────────────────────────────────────────────────
    {
        "crisis_id": "early_election_call",
        "title": "The Opposition Would Like an Election Right Now",
        "description": (
            "The opposition coalition has submitted a formal motion calling for early elections, "
            "citing 'a crisis of democratic legitimacy' and several specific decisions you've made "
            "that they find objectionable. They have listed forty-seven of them. "
            "Your Party Strategist says calling early elections would be 'catastrophically brave.' "
            "Your Reform Advisor says refusing them would be 'democratically revealing.' "
            "You are beginning to understand why your predecessor retired to a vineyard."
        ),
        "options": [
            {
                "label": "Call early elections — demonstrate democratic confidence",
                "description": "Brave. Principled. You are betting your tenure on public support.",
                "stat_effects":    {"institutional_strength": 10, "public_trust": 8, "media_freedom": 3},
                "faction_effects": {"urban_progressives": 10, "national_conservatives": -3, "security_forces": -4, "workers": 4},
                "policy_tags":     ["democracy", "elections", "institutional_confidence"],
                "affected_factions": ["urban_progressives", "workers", "national_conservatives", "business_elite"],
                "event_flags":     {},
            },
            {
                "label": "Dismiss the motion as political maneuvering",
                "description": "Defensible position. Plays poorly in a free press.",
                "stat_effects":    {"public_trust": -4, "institutional_strength": -3},
                "faction_effects": {"national_conservatives": 4, "urban_progressives": -6, "workers": -2},
                "policy_tags":     ["deflection", "political_maneuvering", "dismissal"],
                "affected_factions": ["urban_progressives", "national_conservatives", "workers"],
                "event_flags":     {},
            },
            {
                "label": "Propose a national dialogue process instead",
                "description": "The politics of the long table. Buys time. May build genuine consensus.",
                "stat_effects":    {"public_trust": 3, "institutional_strength": 3},
                "faction_effects": {"urban_progressives": 5, "workers": 3, "national_conservatives": -4},
                "policy_tags":     ["consultation", "compromise", "democratic_process"],
                "affected_factions": ["urban_progressives", "national_conservatives", "workers", "business_elite"],
                "event_flags":     {},
            },
            {
                "label": "Launch an investigation into the opposition's funding",
                "description": "Weaponize institutions. Dangerous precedent. Your opponents will remember.",
                "stat_effects":    {"institutional_strength": -8, "public_trust": -6, "media_freedom": -4},
                "faction_effects": {"national_conservatives": 5, "urban_progressives": -12, "workers": -4, "business_elite": -3},
                "policy_tags":     ["authoritarian", "institutional_abuse", "polarization"],
                "affected_factions": ["urban_progressives", "national_conservatives", "workers", "business_elite"],
                "event_flags":     {
                    "urban_progressives": ["watched the government open investigations into the political opposition"],
                },
            },
        ],
    },
]

# Quick lookup by ID
CRISIS_BY_ID: dict[str, dict] = {c["crisis_id"]: c for c in CRISIS_TEMPLATES}
