"""
Rich-based CLI display.
All print-to-screen logic lives here so the rest of the code stays clean.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box
from rich.rule import Rule
from rich.columns import Columns

console = Console()

STAT_LABELS = {
    "public_trust":             "Public Trust",
    "unrest":                   "Unrest",
    "economy":                  "Economy",
    "budget":                   "Budget",
    "institutional_strength":   "Institutions",
    "media_freedom":            "Media Freedom",
    "international_reputation": "Int'l Reputation",
}

FACTION_LABELS = {
    "workers":               "Workers",
    "business_elite":        "Business Elite",
    "rural_bloc":            "Rural Bloc",
    "urban_progressives":    "Urban Progressives",
    "security_forces":       "Security Forces",
    "national_conservatives": "National Conservatives",
}

# Colours for score bands
def _score_colour(value: int, invert: bool = False) -> str:
    """invert=True for Unrest (high is bad)."""
    bad   = value > 60 if invert else value < 35
    good  = value < 35 if invert else value > 65
    if bad:  return "red"
    if good: return "green"
    return "yellow"


def _bar(value: int, width: int = 20, invert: bool = False) -> Text:
    filled  = round(value / 100 * width)
    colour  = _score_colour(value, invert)
    bar_str = "█" * filled + "░" * (width - filled)
    t = Text()
    t.append(bar_str, style=colour)
    t.append(f" {value:3d}", style="bold " + colour)
    return t


# ── Start screen ───────────────────────────────────────────────────────────────

def display_start_screen() -> None:
    console.print()
    console.print(Panel(
        "[bold white]REPUBLIC OF VERIDIA[/bold white]\n"
        "[dim]A Political Simulator[/dim]\n\n"
        "You have been elected leader of a small, troubled republic.\n"
        "Survive twelve months. Make decisions. Live with them.\n\n"
        "[dim italic]The country will not be improved by optimism.[/dim italic]",
        title="[bold red]■ VERIDIA[/bold red]",
        border_style="red",
        padding=(1, 4),
    ))
    console.print()


# ── Stats dashboard ────────────────────────────────────────────────────────────

def display_stats(national_stats: dict, faction_support: dict) -> None:
    # National stats table
    stat_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    stat_table.add_column("Stat", style="dim", width=22)
    stat_table.add_column("Bar", width=28)

    invert_keys = {"unrest"}
    for key, label in STAT_LABELS.items():
        val = national_stats.get(key, 0)
        stat_table.add_row(label, _bar(val, invert=key in invert_keys))

    # Faction support table
    fac_table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    fac_table.add_column("Faction", style="dim", width=24)
    fac_table.add_column("Bar", width=26)

    for key, label in FACTION_LABELS.items():
        val = faction_support.get(key, 0)
        fac_table.add_row(label, _bar(val))

    console.print(Panel(
        Columns([stat_table, fac_table], equal=False, expand=True),
        title="[bold]NATIONAL STATUS[/bold]",
        border_style="blue",
        padding=(0, 1),
    ))


# ── Turn screen ────────────────────────────────────────────────────────────────

def display_turn_screen(state: dict) -> None:
    console.print()
    console.print(Rule(
        f"[bold]MONTH {state['current_turn']} / {state['max_turns']}[/bold]",
        style="dim",
    ))
    console.print()

    # Situation briefing
    if state.get("situation_briefing"):
        console.print(Panel(
            f"[italic]{state['situation_briefing']}[/italic]",
            title="[dim]SITUATION REPORT[/dim]",
            border_style="dim",
            padding=(0, 2),
        ))
        console.print()

    # Stats
    display_stats(state["national_stats"], state["faction_support"])
    console.print()

    # Crisis card
    crisis = state["active_crisis"]
    console.print(Panel(
        crisis["description"],
        title=f"[bold yellow]■ {crisis['title'].upper()}[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
    ))
    console.print()

    # Options (no effects shown — player sees them only after choosing)
    console.print("  [bold]How do you respond?[/bold]\n")
    for i, opt in enumerate(crisis["options"], 1):
        console.print(f"  [bold cyan]{i}.[/bold cyan] [bold]{opt['label']}[/bold]")
        console.print(f"     [dim]{opt['description']}[/dim]")
        console.print()


# ── Consequence screen ─────────────────────────────────────────────────────────

def display_consequences(state: dict) -> None:
    console.print()
    console.print(Rule("[bold]CONSEQUENCES[/bold]", style="dim"))
    console.print()

    option = state["active_crisis"]["options"][state["player_choice_index"]]

    # Decision taken
    console.print(f"  [bold]Decision:[/bold] {option['label']}")
    console.print()

    # Stat changes
    _display_effect_table(
        "NATIONAL STATS",
        state.get("final_stat_effects") or {},
        STAT_LABELS,
    )

    # Faction changes
    _display_effect_table(
        "FACTION SUPPORT",
        state.get("final_faction_effects") or {},
        FACTION_LABELS,
    )

    # Threshold events
    if state.get("triggered_events"):
        from game.config import THRESHOLD_EVENTS
        console.print(Panel(
            "\n".join(
                f"[bold red]⚠ {k.replace('_', ' ').upper()}[/bold red]\n  {THRESHOLD_EVENTS[k]['description']}"
                for k in state["triggered_events"]
                if k in THRESHOLD_EVENTS
            ),
            title="[bold red]CRISIS EVENTS TRIGGERED[/bold red]",
            border_style="red",
        ))
        console.print()

    # AI reaction reasons (faction context modifier)
    reactions = state.get("ai_reactions") or {}
    if reactions:
        console.print("  [bold dim]Faction readings:[/bold dim]")
        for fid, r in reactions.items():
            label = FACTION_LABELS.get(fid, fid)
            sentiment = r["reaction"].replace("_", " ")
            console.print(f"    [dim]{label}:[/dim] {sentiment} ({r['confidence']}) — {r['reason']}")
        console.print()

    # Advisor reactions
    advisors = state.get("advisor_reactions") or []
    if advisors:
        console.print(Panel(
            "\n\n".join(
                f"[bold]{a['name']}:[/bold] {a['reaction']}"
                for a in advisors
            ),
            title="[bold]ADVISOR REACTIONS[/bold]",
            border_style="cyan",
            padding=(0, 2),
        ))
        console.print()

    # Faction narrative
    faction_narr = state.get("faction_narrative") or {}
    if faction_narr:
        console.print("  [bold dim]Public statements:[/bold dim]")
        for fid, text in faction_narr.items():
            label = FACTION_LABELS.get(fid, fid)
            console.print(f"    [dim]{label}:[/dim] \"{text}\"")
        console.print()

    # Headlines
    headlines = state.get("headlines") or []
    if headlines:
        console.print("  [bold dim]THE PRESS:[/bold dim]")
        for h in headlines:
            outlet = h.get("outlet", "Unknown")
            headline = h.get("headline", "")
            console.print(f"    [italic dim]{outlet}:[/italic dim] {headline}")
        console.print()

    # Updated stats
    console.print()
    display_stats(state["national_stats"], state["faction_support"])
    console.print()

    input("  [Press Enter to continue...]")


def _display_effect_table(title: str, effects: dict, labels: dict) -> None:
    if not effects:
        return
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    table.add_column("Item", style="dim", width=26)
    table.add_column("Change", width=10)

    for key, label in labels.items():
        delta = effects.get(key)
        if delta is None:
            continue
        if delta > 0:
            change = Text(f"+{delta}", style="green bold")
        elif delta < 0:
            change = Text(str(delta), style="red bold")
        else:
            change = Text("±0", style="dim")
        table.add_row(label, change)

    console.print(Panel(table, title=f"[bold]{title}[/bold]", border_style="dim", padding=(0, 1)))
    console.print()


# ── End game screen ────────────────────────────────────────────────────────────

def display_end_screen(state: dict) -> None:
    console.print()
    console.print(Rule("[bold]YEAR ONE: COMPLETE[/bold]", style="bold"))
    console.print()

    won = state["game_status"] == "won"
    end_state = state.get("end_state", "Failed Democrat")

    if won:
        status_style = "bold green"
        status_text  = "SURVIVED"
    else:
        status_style = "bold red"
        status_text  = "FALLEN"

    console.print(Panel(
        f"[{status_style}]{status_text}[/{status_style}]\n\n"
        f"[bold]{end_state}[/bold]\n\n"
        f"{state.get('loss_reason', '')}",
        title="[bold]VERDICT[/bold]",
        border_style="red" if not won else "green",
        padding=(1, 4),
    ))
    console.print()

    display_stats(state["national_stats"], state["faction_support"])
    console.print()

    if state.get("end_summary"):
        console.print(Panel(
            f"[italic]{state['end_summary']}[/italic]",
            title="[dim]HISTORICAL RECORD[/dim]",
            border_style="dim",
            padding=(1, 2),
        ))
        console.print()


# ── Turn history ───────────────────────────────────────────────────────────────

def display_turn_history(turn_history: list) -> None:
    if not turn_history:
        console.print("[dim]No history yet.[/dim]")
        return
    for record in turn_history:
        console.print(
            f"  Month {record['turn_number']:2d}: [bold]{record['crisis_title']}[/bold] "
            f"→ {record['selected_option']}"
        )


# ── Loss screen ────────────────────────────────────────────────────────────────

def display_loss_screen(state: dict) -> None:
    console.print()
    console.print(Panel(
        f"[bold red]GOVERNMENT COLLAPSED[/bold red]\n\n"
        f"{state.get('loss_reason', 'Veridia has had enough of you.')}",
        title="[bold red]■ DEFEAT[/bold red]",
        border_style="red",
        padding=(1, 4),
    ))
    console.print()
    display_stats(state["national_stats"], state["faction_support"])
