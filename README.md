# Republic of Veridia — Political Simulator

A turn-based political simulator where you govern a small, troubled fictional republic through twelve months of crises. Every decision you make shifts faction loyalty, national stability, and your grip on power — narrated by an LLM with a dark sense of humour.

Built with LangGraph, OpenAI, and Rich.

---

## What It Is

You are the newly elected leader of the Republic of Veridia. Each month, a political crisis lands on your desk. You choose how to respond from 3–4 options. The consequences are deterministic — but an AI modifier system reads each faction's mood, values, and recent history to fine-tune how strongly they react. Then the LLM writes the narrative: advisor reactions, faction statements, and five newspaper headlines from outlets with very different opinions of you.

The world doesn't just react to your decisions — it reacts to their consequences. The economy runs as an autonomous subsystem: stock market, unemployment, consumer prices, and budget deficit all drift every turn based on current conditions, exert passive pressure on faction support, and weight which crises are likely to appear next.

Survive twelve months without collapse, coup, or total institutional failure.

### Core design principle

> Deterministic logic decides the bounds of truth. The LLM interprets faction attitudes inside those bounds.

The game engine owns all numerical outcomes. The LLM never writes directly to game state — it classifies reactions (from an allowed set) and generates narrative text only.

---

## Setup

**Prerequisites:** Python 3.11+, an OpenAI API key.

```bash
# 1. Clone and enter the project
cd fungame05

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Play
python main.py

# Or start with a scenario
python main.py --scenario depression
python main.py --list-scenarios   # see all options
```

---

## How to Play

Each turn:

1. Read the **situation briefing** — the LLM describes the current political atmosphere
2. Review your **national stats** and **faction support** (all on a 0–100 scale)
3. Read the **crisis** — something has gone wrong (again)
4. Choose a **response** (1–4) — you won't see the numerical effects until after
5. Review the **consequences** — stat changes, faction reactions, advisor opinions, press coverage

Survive all 12 turns to win. Your end state is determined by how you governed.

### Win condition
Survive 12 months without collapse.

### Loss conditions
- Public Trust reaches 0
- Unrest reaches 100
- Stock Market reaches 0
- Unemployment reaches 100
- Institutional Strength reaches 0

### End states
Depending on your final stats, you'll be classified as one of:
- **Reformist Survivor** — governed with integrity, somehow
- **Business-Backed Technocrat** — the markets loved you
- **Populist Strongman** — orderly, efficient, the press is very complimentary now that you've chosen the press
- **Authoritarian Ruler** — functional, in the way a fist is a functioning hand
- **Crisis Manager** — survived through stubborn presence rather than vision
- **Failed Democrat** — history will be kind; history is usually wrong

---

## Project Structure

```
fungame05/
├── main.py                   Entry point and outer game loop
├── requirements.txt
├── .env.example              Copy to .env and add your API key
│
├── game/
│   ├── config.py             All tuneable constants — start here for balancing
│   ├── state.py              LangGraph state TypedDict
│   ├── factions.py           Six faction personas (values, grievances, dislikes)
│   ├── crises.py             12 authored crisis templates with full effect data
│   ├── engine.py             Deterministic rules engine, AI modifier math, win/loss logic
│   ├── economy.py            Economy subsystem: drift, faction pressure, crisis weighting
│   ├── scenarios.py          Named starting presets that layer on top of config.py
│   └── mood.py               Hybrid mood system (Option C — see below)
│
├── llm/
│   ├── client.py             OpenAI client via LangChain
│   └── prompts.py            All LLM prompt templates (tone-controlled)
│
├── graph/
│   ├── nodes.py              LangGraph node functions (one per turn phase)
│   └── game_graph.py         Compiled turn graph
│
└── cli/
    └── display.py            Rich-based terminal display
```

---

## National Stats

Five numbers (0–100) representing the structural health of Veridia. All start at 50. They move only via deterministic `stat_effects` authored in each crisis option and via threshold event penalties — the LLM never sets them directly.

| Stat | Represents | Consequence of going low |
|---|---|---|
| **Public Trust** | Belief that the government is competent and legitimate | Loss condition at 0; makes negative events hit harder |
| **Unrest** | Protests, strikes, street conflict, disorder | Loss condition at 100 (inverted — high is bad); triggers threshold events (coup, mass protest, general strike) |
| **Institutional Strength** | Courts, civil service, rule of law, constitutional norms | Loss condition at 0; triggers constitutional crisis threshold; enables authoritarian drift |
| **Media Freedom** | Independence of the press | No direct loss, but low values trigger the mass protest threshold and push toward authoritarian end states |
| **International Reputation** | How foreign governments and investors view Veridia | No direct loss, but low values cause sanctions, aid reductions, and investor flight |

### Where national stats are read

| Where | Purpose |
|---|---|
| `run_economy_drift` | Some drift rules trigger on national stats (e.g. `unrest > 70` spooks investors) |
| `check_threshold_events` | Threshold conditions check stat values directly, e.g. `unrest > 70` |
| `check_loss` | Loss conditions check `public_trust == 0`, `unrest == 100`, etc. |
| `classify_faction_reactions` | Sent to LLM as context so it understands the national mood |
| `generate_situation_briefing` | Sent to LLM so it can describe what Veridia feels like this month |
| `determine_end_state` | Final stat values decide which end state category you get |
| `cli/display.py` | Shown to the player as stat bars on every turn screen |

The key distinction from faction support: national stats have no personas and no AI modifiers. They're the structural health of the country; factions are the political relationships.

---

## Economy Sub-Stats

Four sub-stats (0–100) that run as an autonomous subsystem beneath the national stats. They start at 50 and change every turn via drift rules, random variance, and crisis effects — whether or not you take any action that targets them directly.

| Sub-stat | Represents | Direction | Loss condition |
|---|---|---|---|
| **Stock Market** | Investor confidence, business activity | High = good | Reaches 0 |
| **Unemployment** | Joblessness, economic exclusion | High = bad | Reaches 100 |
| **Consumer Prices** | Cost of living, inflation | High = bad | None (but high values hammer Workers and Rural Bloc) |
| **Budget Deficit** | Government fiscal position | High = bad | None (but high values restrict end-state scoring) |

### Autonomous drift

Every turn, before the crisis is selected, `run_economy_drift` fires 12 conditional rules against the current economy and national stats. When a condition holds, the relevant sub-stat shifts. Examples:

- `unemployment > 60` → stock market −2 ("high unemployment spooks investors")
- `budget_deficit > 70` → stock market −2 ("fiscal fears hit markets")
- `unrest > 70` → stock market −2 ("political instability rattles markets")
- `stock_market < 35` → unemployment +3 ("recession drives layoffs")
- `budget_deficit > 60` → consumer_prices +2 ("deficit spending drives inflation")

After the rules, every sub-stat gets a ±1 random variance roll — identical decisions don't produce identical outcomes.

### Faction pressure

After drift, 14 pressure rules check economy sub-stats against faction support. Bad economic conditions passively drain faction loyalty every turn:

- `unemployment > 65` → Workers −2/turn
- `consumer_prices > 65` → Workers −2/turn, Rural Bloc −2/turn
- `stock_market < 35` → Business Elite −3/turn
- `budget_deficit > 70` → Business Elite −1/turn

Good conditions do the reverse — `stock_market > 70` gives Business Elite +2/turn, low unemployment and prices give Workers a small passive bonus.

### Crisis weighting

`select_crisis` uses economy conditions to weight which crisis is more likely to appear. A crisis with matching conditions gets 4× the base probability. Examples:

| Crisis | Boosted when |
|---|---|
| The Bread Is Too Expensive Again | consumer_prices > 60 |
| The Money Is Leaving | stock_market < 45 |
| The Civil Servants Have Had Enough | unemployment > 55 AND budget_deficit > 55 |
| The Lenders Have Opinions | budget_deficit > 65 |
| No One Can Afford to Live Anywhere | consumer_prices > 60 AND unemployment > 50 |

### Where economy sub-stats are read

| Where | Purpose |
|---|---|
| `run_economy_drift` | Drift rules and random variance applied each turn |
| `apply_base_effects` | Crisis option `economy_effects` applied to sub-stats |
| `check_threshold_events` | Threshold conditions can reference sub-stats (e.g. capital flight checks `stock_market < 40`) |
| `check_loss` | Stock market == 0 and unemployment == 100 are loss conditions |
| `classify_faction_reactions` | Sent to LLM so factions can react to economic conditions |
| `generate_situation_briefing` | Sent to LLM so the briefing reflects economic reality |
| `determine_end_state` | Business-Backed Technocrat end state requires strong stock market and low deficit |
| `cli/display.py` | Shown as a separate column of bars on every turn screen, with a composite health score |

---

## Architecture

### Turn flow (LangGraph)

Each turn is a single invocation of the compiled turn graph:

```
run_economy_drift              (deterministic + ±1 random)
    → select_crisis            (economy-weighted random)
    → generate_situation_briefing   (LLM)
    → get_player_choice             (blocking input)
    → apply_base_effects            (deterministic)
    → classify_faction_reactions    (LLM — bounded categories only)
    → compute_final_effects         (deterministic)
    → check_threshold_events        (deterministic)
    → generate_narrative            (LLM — advisors, factions, headlines)
    → save_turn_history
```

The outer game loop in `main.py` checks win/loss conditions between turns.

### Node reference

| Node | What happens |
|---|---|
| `run_economy_drift` | Applies 12 conditional drift rules to economy sub-stats, then ±1 random variance; applies 14 faction pressure rules; fires before any player input |
| `select_crisis` | Picks a weighted-random unused crisis template (crises contextually relevant to current economy get 4× weight), resets all per-turn state fields |
| `generate_situation_briefing` | LLM writes a 2–3 sentence mood summary of Veridia this month, informed by both national and economy stats |
| `get_player_choice` | Displays the turn screen (including economy drift summary and bars), blocks waiting for the player to type 1–4 |
| `apply_base_effects` | Looks up the chosen option's authored deltas, adds them to `national_stats`, `economy_stats`, and `faction_support`, stages event flags |
| `classify_faction_reactions` | Sends faction personas + game context (including economy conditions) to LLM, gets back `loves_it/hates_it/etc`, validates the output, applies ±1–3 modifier on top of faction support |
| `compute_final_effects` | Records the net faction deltas (base + AI modifier) and economy effects for display and history — no new math |
| `check_threshold_events` | Evaluates all 5 threshold conditions against current stats (can reference economy sub-stats), applies extra stat/faction/economy hits for any that trigger |
| `generate_narrative` | Three LLM calls: advisor reactions, faction statements, newspaper headlines — all display only |
| `save_turn_history` | Writes the full turn record (including economy snapshot) to history, increments `current_turn` |

### Bounded AI modifier system

The LLM is never asked "what should the stat change be?" It is only asked to classify each faction's reaction using a fixed vocabulary:

| Reaction | High | Medium | Low |
|---|---|---|---|
| `loves_it` | +3 | +2 | +1 |
| `likes_it` | +2 | +1 | +1 |
| `neutral` | 0 | 0 | 0 |
| `dislikes_it` | -2 | -1 | -1 |
| `hates_it` | -3 | -2 | -1 |

These modifiers apply only to faction support values, never to national stats. Invalid LLM output falls back to base deterministic effects with no modifier.

### Faction mood (Option C hybrid)

Each faction's mood context is built from two sources:

1. **Deterministic tier** — derived from current support score (0–20: desperate, 21–40: resentful, 41–60: uneasy, 61–80: cautiously supportive, 81–100: enthusiastic)
2. **One-turn event flags** — set by the chosen crisis option (e.g. "were cracked down on during food protests last month") — gives the LLM contextual nuance without adding extra calls

---

## Scenarios

Scenarios are named starting presets that override specific values in `config.py` and extend its rules. They are layered on top — `config.py` stays as the human-editable baseline and scenarios modify only what they need to.

```bash
python main.py --scenario at_war
python main.py --scenario depression
python main.py --scenario honeymoon
python main.py --scenario on_the_brink
python main.py --list-scenarios        # print all options with descriptions

# Flags compose freely
python main.py --scenario depression --debug
```

### What a scenario can change

| Layer | Mechanism | Effect |
|---|---|---|
| Starting stats | Overrides specific keys in `STARTING_NATIONAL_STATS`, `STARTING_ECONOMY_STATS`, `STARTING_FACTION_SUPPORT` | Different world state at turn 1 |
| Drift rules | Appends to `ECONOMY_DRIFT_RULES` | Extra conditions that fire every turn |
| Faction pressure | Appends to `FACTION_PRESSURE_RULES` | Extra passive drains/gains from economy |
| Crisis weights | Updates `CRISIS_WEIGHT_RULES` | Makes contextually relevant crises more likely |
| Flavour | `description` + `opening_text` | Replaces the default start screen text |

The append/update approach means scenario rules stack on top of the config baseline — a `depression` game still has all the default drift rules plus three harsher ones. To override a rule entirely rather than add to it, edit `config.py` directly.

### Built-in scenarios

| Scenario | Description |
|---|---|
| `at_war` | Six weeks into a border conflict. Budget bleeding, generals restless, international reputation in the gutter. Extra drift rules: war spending widens the deficit, sanctions hit markets. |
| `depression` | Eighteen months of economic freefall before you took office. Stock market at 22, unemployment at 72. Extra drift rules: deeper recession cascades, stagflation feedback loop, debt crisis. |
| `honeymoon` | Landslide election, 18-point mandate, press cautiously optimistic. Cleaner starting position, no extra rules. Enjoy it while it lasts. |
| `on_the_brink` | The previous government dissolved rather than fell. Everything starts at ~28–30. One bad turn can end it. |

### Adding a scenario

Add an entry to `SCENARIOS` in `game/scenarios.py`. No other files need changing.

```python
"my_scenario": {
    "description": "One-line description shown in --list-scenarios.",
    "opening_text": "Flavour text shown on the start screen.",
    "stat_overrides":      {"unrest": 70, "public_trust": 35},
    "economy_overrides":   {"stock_market": 30},
    "faction_overrides":   {"security_forces": 65},
    "extra_drift_rules":   [
        # (trigger_key, operator, threshold, affected_key, delta, description)
        ("unrest", ">", 60, "budget_deficit", +2, "emergency spending"),
    ],
    "extra_faction_pressure": [
        # (trigger_key, operator, threshold, faction_id, delta, description)
        ("budget_deficit", ">", 75, "workers", -2, "austerity cuts"),
    ],
    "extra_crisis_weights": {
        # crisis_id: [(trigger_key, operator, threshold), ...]
        "military_demands": [("unrest", ">", 55)],
    },
},
```

---

## Configuration

Everything tuneable lives in `game/config.py`.

### Change the tone

```python
# Options: "serious" | "satirical" | "darkly_comic"
TONE = "darkly_comic"
```

All LLM prompts pull from this — one change updates everything.

### Adjust starting values

```python
STARTING_NATIONAL_STATS = {
    "public_trust":             50,   # raise for an easier start
    "unrest":                   50,   # lower for a calmer opening
    "institutional_strength":   50,
    "media_freedom":            50,
    "international_reputation": 50,
}

STARTING_ECONOMY_STATS = {
    "stock_market":    50,   # lower = economy starts weak
    "unemployment":    50,   # raise = higher starting joblessness
    "consumer_prices": 50,   # raise = higher starting inflation
    "budget_deficit":  50,   # raise = starting in fiscal trouble
}

STARTING_FACTION_SUPPORT = {
    "workers":               50,
    "business_elite":        50,
    ...
}
```

### Tune economy drift and pressure

```python
# How much random noise each sub-stat gets every turn (±N)
ECONOMY_RANDOM_RANGE: int = 1

# Crisis selection weights
CRISIS_BOOST_WEIGHT: int = 4   # economy-relevant crises
CRISIS_BASE_WEIGHT:  int = 1   # all others
```

To add or adjust drift rules, edit `ECONOMY_DRIFT_RULES` and `FACTION_PRESSURE_RULES` in `config.py`. Each rule is a tuple of `(trigger_key, operator, threshold, affected_key, delta, description)`.

### Change the AI modifier caps

```python
MAX_AI_MODIFIER = 3   # max bonus the LLM can add
MIN_AI_MODIFIER = -3  # max penalty
```

### Change the model

In `.env`:
```
OPENAI_MODEL=gpt-4o-mini   # or gpt-4o, gpt-4.1-mini, etc.
```

---

## Characters

### Factions (6) — mechanically active all game

These are the only characters that affect numbers. Their support scores (0–100) feed into threshold events, loss conditions, and the AI modifier system.

| Faction | Cares about | Active in |
|---|---|---|
| **Workers** | Wages, food prices, unions, cost of living | Base effects every turn, modifier classification, threshold events (general strike, mass protest) |
| **Business Elite** | Taxes, investment, stability, deregulation | Base effects every turn, modifier classification, threshold event (capital flight) |
| **Rural Bloc** | Fuel prices, agriculture, local autonomy, being noticed | Base effects every turn, modifier classification |
| **Urban Progressives** | Democracy, civil rights, anti-corruption, police reform | Base effects every turn, modifier classification, threshold events (mass protest, constitutional crisis) |
| **Security Forces** | Order, authority, funding, command respect | Base effects every turn, modifier classification, threshold event (coup attempt) |
| **National Conservatives** | Sovereignty, tradition, law and order, skepticism of foreign influence | Base effects every turn, modifier classification |

Factions are active in three nodes: `apply_base_effects` (their support changes), `classify_faction_reactions` (LLM reads their persona and mood to decide reaction intensity), and `check_threshold_events` (their support score triggers or doesn't trigger cascading events).

### Advisors (4) — narrative only, post-decision

Generated in `generate_narrative` after every turn. They never affect numbers — their only job is to react to what just happened in character, giving the player interpretive context.

| Advisor | Bias | Personality |
|---|---|---|
| **Finance Minister** | Budget discipline, investor confidence, economic stability | Dry, numbers-obsessed, quietly despairing |
| **Security Chief** | Order, control, emergency powers | Direct, slightly menacing, allergic to nuance |
| **Reform Advisor** | Democracy, civil liberties, anti-corruption | Earnest, increasingly frustrated, tries not to lecture |
| **Party Strategist** | Popularity, messaging, political survival | Cheerfully cynical, sees everything as a communications problem |

### Media Outlets (5) — narrative only, post-decision

Also generated in `generate_narrative`, also display-only. Each writes one headline per turn from their editorial slant.

| Outlet | Slant |
|---|---|
| **The Veridian Times** | Mainstream institutional, cautiously establishment |
| **People's Herald** | Labour-aligned, working-class sympathies |
| **Market Ledger** | Business-focused, pro-investor |
| **National Voice** | Nationalist, sovereignty-focused |
| **Free Signal** | Independent reformist, anti-corruption |

### Summary: who matters mechanically vs. narratively

| Character | Affects numbers | Generates text | When |
|---|---|---|---|
| Factions | Yes | Yes (statements) | Every turn, all nodes |
| Advisors | No | Yes | After every decision |
| Media outlets | No | Yes (headlines) | After every decision |

> If you wanted to make advisors or media mechanically meaningful — e.g. ignoring your Finance Minister repeatedly triggers a loyalty event, or suppressing enough press triggers a Media Freedom cascade — the data is already in the state ready to be read by the engine.

---

## Crises

12 authored templates, selected randomly each game:

1. The Bread Is Too Expensive Again
2. The Money Is Leaving
3. Someone in the Cabinet Has Been Stealing
4. The Tractors Are Blocking the Highway
5. The Students Want the Police to Stop Hitting People
6. The Neighbour Is Being a Problem Again
7. Someone Left the Filing Cabinet Open
8. The Generals Would Like More Power, Please
9. The Civil Servants Have Had Enough
10. The Lenders Have Opinions About How You Spend Money
11. No One Can Afford to Live Anywhere
12. The Opposition Would Like an Election Right Now

---

## Threshold Events

Threshold checks run once per turn in `check_threshold_events`, after all crisis effects have been applied. They are a second layer of consequences — things that happen because your stats have drifted into dangerous territory over multiple turns, not because of any single decision.

### How a check works

Every threshold event has a list of conditions. **All conditions must be true simultaneously** for it to trigger. The engine checks every faction support value and national stat against these after each turn.

Each threshold event can only fire **once per game**. Once triggered it is recorded in turn history and skipped in all future checks — it is a crisis escalation, not a recurring punishment.

### What happens when one fires

1. **Immediate stat/faction penalties** are applied on top of everything else that turn
2. **A description** is appended to `recent_events` so the LLM references it in future briefings and narrative
3. If the penalties push a stat past a loss condition (e.g. Unrest hits 100), the game ends on that turn

### The five events

| Event | Conditions | What it hits |
|---|---|---|
| **Coup Attempt** | Security Forces < 25 AND Unrest > 70 AND Institutions < 40 | Institutions −8, Unrest +15, Urban Progressives −10 |
| **General Strike** | Workers < 30 AND Unrest > 65 | Unrest +10, Stock Market −10, Unemployment +8, Budget Deficit +8, Business Elite −8 |
| **Capital Flight** | Business Elite < 25 AND Stock Market < 40 | Int'l Reputation −8, Stock Market −12, Budget Deficit +10, Unemployment +6 |
| **Constitutional Crisis** | Institutions < 25 AND Public Trust < 40 | Institutions −10, Public Trust −8, Stock Market −5, Urban Progressives −8 |
| **Mass Protest** | Urban Progressives < 30 AND Media Freedom < 40 AND Unrest > 60 | Unrest +12, Public Trust −8, Int'l Reputation −6, Stock Market −4 |

### Known gap vs. PRD

The PRD specified that threshold events should produce **additional forced crisis turns** (e.g. a coup attempt injects a special generals ultimatum crisis next turn) and **immediate end states** for the most severe events. Currently the code applies the stat penalties and narrative context but the game continues to the next normal random crisis. This is a planned future enhancement.

---

## Future Plans

- Web UI (React) layered on top of the existing game engine
- Scripted crisis campaigns (fixed sequence for different simulations)
- Election system
- Coalition politics
- Opposition leader AI
- Additional world-state subsystems (military, foreign relations, press freedom index)
- Faction memory across sessions
