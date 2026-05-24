# Republic of Veridia — Political Simulator

A turn-based political simulator where you govern a small, troubled fictional republic through twelve months of crises. Every decision you make shifts faction loyalty, national stability, and your grip on power — narrated by an LLM with a dark sense of humour.

Built with LangGraph, OpenAI, and Rich.

---

## What It Is

You are the newly elected leader of the Republic of Veridia. Each month, a political crisis lands on your desk. You choose how to respond from 3–4 options. The consequences are deterministic — but an AI modifier system reads each faction's mood, values, and recent history to fine-tune how strongly they react. Then the LLM writes the narrative: advisor reactions, faction statements, and five newspaper headlines from outlets with very different opinions of you.

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
- Economy reaches 0
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

Seven numbers (0–100) representing the structural health of Veridia. All start at 50. They move only via deterministic `stat_effects` authored in each crisis option and via threshold event penalties — the LLM never sets them directly.

| Stat | Represents | Consequence of going low |
|---|---|---|
| **Public Trust** | Belief that the government is competent and legitimate | Loss condition at 0; makes negative events hit harder |
| **Unrest** | Protests, strikes, street conflict, disorder | Loss condition at 100; triggers threshold events (coup, mass protest, general strike) |
| **Economy** | General economic health, employment, investment | Loss condition at 0; reduces public support, increases crisis frequency |
| **Budget** | Government's fiscal position | No direct loss condition, but many good options cost budget — run out and your options dry up |
| **Institutional Strength** | Courts, civil service, rule of law, constitutional norms | Loss condition at 0; triggers constitutional crisis threshold; enables authoritarian drift |
| **Media Freedom** | Independence of the press | No direct loss, but low values trigger the mass protest threshold and push toward authoritarian end states |
| **International Reputation** | How foreign governments and investors view Veridia | No direct loss, but low values cause sanctions, aid reductions, and investor flight |

### Where national stats are read

| Where | Purpose |
|---|---|
| `check_threshold_events` | Threshold conditions check stat values directly, e.g. `unrest > 70` |
| `check_loss` | Loss conditions check `public_trust == 0`, `unrest == 100`, etc. |
| `classify_faction_reactions` | Sent to LLM as context so it understands the national mood |
| `generate_situation_briefing` | Sent to LLM so it can describe what Veridia feels like this month |
| `determine_end_state` | Final stat values decide which end state category you get |
| `cli/display.py` | Shown to the player as stat bars on every turn screen |

The key distinction from faction support: national stats have no personas and no AI modifiers. They're the structural health of the country; factions are the political relationships.

---

## Architecture

### Turn flow (LangGraph)

Each turn is a single invocation of the compiled turn graph:

```
select_crisis
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
| `select_crisis` | Picks a random unused crisis template, resets all per-turn state fields |
| `generate_situation_briefing` | LLM writes a 2–3 sentence mood summary of Veridia this month |
| `get_player_choice` | Displays the turn screen, blocks waiting for the player to type 1–4 |
| `apply_base_effects` | Looks up the chosen option's authored deltas, adds them to `national_stats` and `faction_support`, stages event flags |
| `classify_faction_reactions` | Sends faction personas + game context to LLM, gets back `loves_it/hates_it/etc`, validates the output, applies ±1–3 modifier on top of faction support |
| `compute_final_effects` | Records the net faction deltas (base + AI modifier) for display and history — no new math |
| `check_threshold_events` | Evaluates all 5 threshold conditions against current stats, applies extra stat/faction hits for any that trigger |
| `generate_narrative` | Three LLM calls: advisor reactions, faction statements, newspaper headlines — all display only |
| `save_turn_history` | Writes the full turn record to history, increments `current_turn` |

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
    "economy":                  50,
    "budget":                   50,
    "institutional_strength":   50,
    "media_freedom":            50,
    "international_reputation": 50,
}

STARTING_FACTION_SUPPORT = {
    "workers":               50,
    "business_elite":        50,
    ...
}
```

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

Beyond loss conditions, five threshold events can trigger mid-game and apply additional effects:

| Event | Trigger conditions |
|---|---|
| **Coup Attempt** | Security Forces < 25, Unrest > 70, Institutions < 40 |
| **General Strike** | Workers < 30, Unrest > 65 |
| **Capital Flight** | Business Elite < 25, Economy < 40 |
| **Constitutional Crisis** | Institutions < 25, Public Trust < 40 |
| **Mass Protest** | Urban Progressives < 30, Media Freedom < 40, Unrest > 60 |

---

## Future Plans

- Web UI (React) layered on top of the existing game engine
- Scripted crisis campaigns (fixed sequence for different simulations)
- Election system
- Coalition politics
- Opposition leader AI
- More detailed economic model
- Faction memory across sessions
