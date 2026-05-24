"""
Debug output module. All debug printing goes through here.
Gated by game.config.DEBUG — set via --debug flag or DEBUG=true in .env.
"""

import json
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich import box

_console = Console(stderr=True, style="dim")


def _enabled() -> bool:
    from game.config import DEBUG
    return DEBUG


def _json(data: Any) -> str:
    try:
        return json.dumps(data, indent=2, default=str)
    except Exception:
        return str(data)


# ── Node lifecycle ─────────────────────────────────────────────────────────────

def node_enter(name: str) -> None:
    if not _enabled():
        return
    _console.print(f"\n[bold cyan]▶ NODE: {name}[/bold cyan]", highlight=False)


def node_exit(name: str, updates: dict) -> None:
    if not _enabled():
        return
    keys = ", ".join(k for k in updates if updates[k] is not None)
    _console.print(f"[dim cyan]  ✓ {name} → updated: [{keys}][/dim cyan]", highlight=False)


# ── LLM calls ─────────────────────────────────────────────────────────────────

def llm_prompt(label: str, messages: list[dict]) -> None:
    if not _enabled():
        return
    parts = []
    for m in messages:
        role = m["role"].upper()
        content = m["content"]
        parts.append(f"[bold]{role}[/bold]\n{content}")
    _console.print(Panel(
        "\n\n".join(parts),
        title=f"[yellow]LLM PROMPT — {label}[/yellow]",
        border_style="yellow",
        padding=(0, 2),
    ))


def llm_response(label: str, raw: Any) -> None:
    if not _enabled():
        return
    text = _json(raw) if not isinstance(raw, str) else raw
    _console.print(Panel(
        Syntax(text, "json" if not isinstance(raw, str) else "text", theme="monokai", word_wrap=True),
        title=f"[yellow]LLM RESPONSE — {label}[/yellow]",
        border_style="dark_orange",
        padding=(0, 2),
    ))


def llm_fallback(label: str, reason: str) -> None:
    if not _enabled():
        return
    _console.print(f"  [red]⚠ LLM FALLBACK ({label}): {reason}[/red]")


# ── Effects pipeline ───────────────────────────────────────────────────────────

def base_effects(stat_effects: dict, faction_effects: dict) -> None:
    if not _enabled():
        return
    _console.print(Panel(
        f"Stats:    {_json(stat_effects)}\nFactions: {_json(faction_effects)}",
        title="[green]BASE EFFECTS (deterministic)[/green]",
        border_style="green",
        padding=(0, 2),
    ))


def ai_modifier_pipeline(
    raw_reactions: Any,
    validated: dict | None,
    modifiers: dict,
    faction_support_before: dict,
    faction_support_after: dict,
) -> None:
    if not _enabled():
        return

    table = Table(box=box.SIMPLE, show_header=True, padding=(0, 2))
    table.add_column("Faction",    style="dim",   width=24)
    table.add_column("Reaction",   width=14)
    table.add_column("Confidence", width=10)
    table.add_column("Modifier",   width=10)
    table.add_column("Before",     width=8)
    table.add_column("After",      width=8)
    table.add_column("Reason",     width=40)

    if validated:
        for fid, r in validated.items():
            mod = modifiers.get(fid, 0)
            before = faction_support_before.get(fid, "?")
            after  = faction_support_after.get(fid, "?")
            mod_text = Text(f"{mod:+d}", style="green" if mod > 0 else ("red" if mod < 0 else "dim"))
            table.add_row(
                fid, r["reaction"], r["confidence"],
                mod_text, str(before), str(after), r["reason"]
            )
    else:
        table.add_row("[red]VALIDATION FAILED[/red]", "", "", "0", "", "", "Fallback to base effects")

    _console.print(Panel(
        table,
        title="[magenta]AI MODIFIER PIPELINE[/magenta]",
        border_style="magenta",
        padding=(0, 1),
    ))

    if validated is None and raw_reactions is not None:
        _console.print(Panel(
            Syntax(_json(raw_reactions), "json", theme="monokai", word_wrap=True),
            title="[red]REJECTED LLM OUTPUT[/red]",
            border_style="red",
            padding=(0, 2),
        ))


# ── Threshold checks ───────────────────────────────────────────────────────────

def threshold_checks(
    national_stats: dict,
    faction_support: dict,
    triggered: list[str],
) -> None:
    if not _enabled():
        return

    from game.config import THRESHOLD_EVENTS
    import operator as op_module

    _ops = {"<": op_module.lt, ">": op_module.gt, "==": op_module.eq,
            "<=": op_module.le, ">=": op_module.ge}

    table = Table(box=box.SIMPLE, show_header=True, padding=(0, 2))
    table.add_column("Event",     style="dim", width=24)
    table.add_column("Condition", width=32)
    table.add_column("Value",     width=8)
    table.add_column("Pass?",     width=6)

    combined = {**national_stats, **faction_support}
    for event_key, spec in THRESHOLD_EVENTS.items():
        for key, oper, threshold in spec["conditions"]:
            val = combined.get(key, 0)
            passed = _ops[oper](val, threshold)
            table.add_row(
                event_key,
                f"{key} {oper} {threshold}",
                str(val),
                "[green]✓[/green]" if passed else "[red]✗[/red]",
            )

    triggered_text = (
        "[bold red]TRIGGERED: " + ", ".join(triggered) + "[/bold red]"
        if triggered else "[dim]None triggered[/dim]"
    )
    _console.print(Panel(
        str(table) + "\n" + triggered_text,
        title="[blue]THRESHOLD CHECKS[/blue]",
        border_style="blue",
        padding=(0, 1),
    ))
    # Re-print the table properly (workaround for nested rich renderables)
    _console.print(table)
    if triggered:
        _console.print(f"  [bold red]⚠ TRIGGERED: {', '.join(triggered)}[/bold red]")


def threshold_checks_clean(
    national_stats: dict,
    faction_support: dict,
    triggered: list[str],
) -> None:
    """Cleaner version without nested panel issue."""
    if not _enabled():
        return

    from game.config import THRESHOLD_EVENTS
    import operator as op_module

    _ops = {"<": op_module.lt, ">": op_module.gt, "==": op_module.eq,
            "<=": op_module.le, ">=": op_module.ge}

    combined = {**national_stats, **faction_support}

    _console.print("\n  [bold blue]THRESHOLD CHECKS[/bold blue]")
    for event_key, spec in THRESHOLD_EVENTS.items():
        results = []
        for key, oper, threshold in spec["conditions"]:
            val = combined.get(key, 0)
            passed = _ops[oper](val, threshold)
            tick = "[green]✓[/green]" if passed else "[red]✗[/red]"
            results.append(f"{tick} {key} {oper} {threshold} (={val})")
        status = "[bold red]TRIGGERED[/bold red]" if event_key in triggered else "[dim]no[/dim]"
        _console.print(f"  [dim]{event_key}[/dim] → {status}")
        for r in results:
            _console.print(f"    {r}")


# ── State snapshot ─────────────────────────────────────────────────────────────

def state_snapshot(label: str, state: dict, keys: list[str] | None = None) -> None:
    if not _enabled():
        return
    snapshot = {k: state[k] for k in (keys or state) if k in state}
    _console.print(Panel(
        Syntax(_json(snapshot), "json", theme="monokai", word_wrap=True),
        title=f"[dim]STATE SNAPSHOT — {label}[/dim]",
        border_style="dim",
        padding=(0, 2),
    ))


# ── Turn summary ───────────────────────────────────────────────────────────────

def turn_summary(state: dict) -> None:
    if not _enabled():
        return
    _console.print(Panel(
        Syntax(_json({
            "turn":            state["current_turn"] - 1,
            "crisis":          state["active_crisis"]["title"] if state.get("active_crisis") else None,
            "choice":          state["player_choice_index"],
            "base_stat_fx":    state.get("base_stat_effects"),
            "base_faction_fx": state.get("base_faction_effects"),
            "ai_modifiers":    state.get("ai_modifiers"),
            "final_stat_fx":   state.get("final_stat_effects"),
            "final_faction_fx":state.get("final_faction_effects"),
            "triggered":       state.get("triggered_events"),
            "national_stats":  state.get("national_stats"),
            "faction_support": state.get("faction_support"),
        }), "json", theme="monokai", word_wrap=True),
        title="[bold]DEBUG — TURN SUMMARY[/bold]",
        border_style="bright_black",
        padding=(0, 2),
    ))
