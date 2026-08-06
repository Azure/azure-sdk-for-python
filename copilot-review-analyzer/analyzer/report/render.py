"""Rich rendering for the report/themes/trend commands."""

from __future__ import annotations

import sqlite3

from rich.console import Console
from rich.table import Table

from analyzer.report import data, export

_SPARK_TICKS = "▁▂▃▄▅▆▇█"


def _fmt(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.3f}"


def sparkline(values: list[float | None]) -> str:
    """Render a unicode sparkline; missing values render as a space."""
    present = [v for v in values if v is not None]
    if not present:
        return ""
    lo, hi = min(present), max(present)
    span = hi - lo
    out: list[str] = []
    for v in values:
        if v is None:
            out.append(" ")
        elif span == 0:
            out.append(_SPARK_TICKS[len(_SPARK_TICKS) // 2])
        else:
            idx = round((v - lo) / span * (len(_SPARK_TICKS) - 1))
            out.append(_SPARK_TICKS[idx])
    return "".join(out)


def render_report(conn: sqlite3.Connection, run_id: int, console: Console) -> None:
    """Print a per-run metrics + data-quality + themes summary."""
    report = export.build_report_dict(conn, run_id)
    run = report["run"]

    console.print(
        f"[bold]Run {run['id']}[/bold]  {run['repo']}  "
        f"state={run['pr_state']}  prs={run['pr_count']}  status={run['status']}"
    )

    metrics_table = Table(title="Metrics")
    metrics_table.add_column("Metric")
    metrics_table.add_column("Value", justify="right")
    for field, value in report["metrics"].items():
        metrics_table.add_row(field, _fmt(value))
    console.print(metrics_table)

    dq_table = Table(title="Data quality")
    dq_table.add_column("Counter")
    dq_table.add_column("Value", justify="right")
    for field, value in report["counts"].items():
        dq_table.add_row(field, str(value))
    console.print(dq_table)

    if report["themes"]:
        themes_table = Table(title="Top themes")
        themes_table.add_column("Theme")
        themes_table.add_column("Gaps", justify="right")
        for theme in report["themes"]:
            themes_table.add_row(theme["label"], str(theme["gap_count"]))
        console.print(themes_table)

    if report["suggestions"]:
        sugg_table = Table(title="What Copilot missed → prompt fixes")
        sugg_table.add_column("PR", justify="right")
        sugg_table.add_column("Theme")
        sugg_table.add_column("Missed finding")
        sugg_table.add_column("Prompt improvement")
        for s in report["suggestions"]:
            pr = f"#{s['pr_number']}" if s["pr_number"] is not None else "?"
            sugg_table.add_row(
                pr, s["theme"] or "other", s["missed_finding"], s["prompt_improvement"]
            )
        console.print(sugg_table)
        if report["prompt_addendum"]:
            console.print(
                "[dim]Paste-ready prompt additions below " "(also in --format markdown/json):[/dim]"
            )
            console.print(report["prompt_addendum"])

    console.print(f"[dim]{data.RECALL_CAVEAT}[/dim]")


def render_themes(
    conn: sqlite3.Connection, run_id: int, console: Console, *, min_count: int
) -> None:
    """Print the theme histogram for a run."""
    themes = data.get_themes(conn, run_id, min_count=min_count)
    if not themes:
        console.print(f"[yellow]No themes with gap_count >= {min_count} for run {run_id}.[/yellow]")
        return
    table = Table(title=f"Themes (run {run_id}, min_count={min_count})")
    table.add_column("Theme")
    table.add_column("Gaps", justify="right")
    table.add_column("Description")
    for theme in themes:
        table.add_row(theme["label"], str(theme["gap_count"]), theme["description"] or "")
    console.print(table)


def render_trend(
    conn: sqlite3.Connection,
    metric: str,
    console: Console,
    *,
    include_incomplete: bool = False,
) -> None:
    """Print a metric trend across runs with a sparkline."""
    series = data.trend_series(conn, metric, include_incomplete=include_incomplete)
    if not series:
        console.print("[yellow]No runs to trend.[/yellow]")
        return
    values = [v for _, v in series]
    table = Table(title=f"Trend: {metric}")
    table.add_column("Run")
    table.add_column("Value", justify="right")
    for run_id, value in series:
        table.add_row(str(run_id), _fmt(value))
    console.print(table)
    spark = sparkline(values)
    if spark:
        console.print(f"{metric}: {spark}")
    console.print(f"[dim]{data.RECALL_CAVEAT}[/dim]")
