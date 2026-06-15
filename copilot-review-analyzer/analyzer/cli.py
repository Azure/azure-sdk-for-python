"""Command-line interface for the analyzer (typer app).

Commands are added incrementally per implementation phase.
"""

from __future__ import annotations

import json
import logging

import typer
from rich.console import Console

from analyzer.config import Config
from analyzer.github.client import GitHubClient
from analyzer.llm.client import make_completer
from analyzer.pipeline import ingest, orchestrate
from analyzer.pipeline import suggest as pipeline_suggest
from analyzer.report import data as report_data
from analyzer.report import export, render
from analyzer.store import db

app = typer.Typer(add_completion=False, help="Copilot Code-Review Effectiveness Analyzer")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


@app.command("init-db")
def init_db(db_path: str = typer.Option("analyzer.db", "--db", help="SQLite DB path")) -> None:
    """Create a fresh SQLite database (idempotent)."""
    _configure_logging()
    conn = db.connect(db_path)
    try:
        db.init_db(conn)
    finally:
        conn.close()
    typer.echo(f"Initialized database at {db_path}")


@app.command("run")
def run(
    repo: str = typer.Option(..., "--repo", help="owner/name"),
    since: str = typer.Option("7d", "--since", help="Window duration, e.g. 7d, 24h, 2w"),
    state: str = typer.Option("merged", "--state", help="merged | closed | all"),
    max_prs: int = typer.Option(50, "--max-prs", help="Max PRs to sample"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print normalized JSON, write nothing"),
    use_llm: bool = typer.Option(
        False, "--use-llm", help="Run the real LLM judge + theme tagging (else stub judge)"
    ),
    config: str = typer.Option("config.yaml", "--config", help="Config file path"),
    db_path: str = typer.Option("analyzer.db", "--db", help="SQLite DB path"),
) -> None:
    """Ingest PRs in a window and run the analysis pipeline.

    With ``--dry-run`` it prints normalized JSON and writes nothing.
    """
    _configure_logging()
    if state not in ("merged", "closed", "all"):
        raise typer.BadParameter("--state must be one of merged|closed|all")
    cfg = Config.load(config)
    if dry_run:
        window_start, window_end = ingest.compute_window(since)
        with GitHubClient() as client:
            prs = ingest.fetch_window(
                client,
                repo,
                window_start=window_start,
                window_end=window_end,
                state=state,
                max_prs=min(max_prs, cfg.max_prs),
            )
        payload = [ingest.normalized_pr_to_dict(p) for p in prs]
        typer.echo(json.dumps(payload, indent=2))
        return
    result = orchestrate.run_analysis(
        cfg,
        repo=repo,
        since=since,
        state=state,
        max_prs=max_prs,
        db_path=db_path,
        use_llm=use_llm,
    )
    typer.echo(
        f"Run {result.run_id} completed: {result.pr_count} PR(s), "
        f"{result.gap_count} gap(s). DB: {db_path}"
    )


@app.command("report")
def report(
    run: str = typer.Option("latest", "--run", help="Run id or 'latest'"),
    fmt: str = typer.Option("table", "--format", help="table | markdown | json | csv"),
    db_path: str = typer.Option("analyzer.db", "--db", help="SQLite DB path"),
    include_incomplete: bool = typer.Option(
        False, "--include-incomplete", help="Allow failed/partial runs"
    ),
) -> None:
    """Render a per-run report."""
    if fmt not in ("table", "markdown", "json", "csv"):
        raise typer.BadParameter("--format must be one of table|markdown|json|csv")
    conn = db.connect(db_path)
    try:
        try:
            run_id = report_data.resolve_run_id(conn, run, include_incomplete=include_incomplete)
        except report_data.NoDataError as exc:
            typer.echo(f"No data: {exc}")
            raise typer.Exit(code=0) from None
        if fmt == "table":
            render.render_report(conn, run_id, Console())
        elif fmt == "markdown":
            typer.echo(export.to_markdown(conn, run_id))
        elif fmt == "json":
            typer.echo(export.to_json(conn, run_id))
        else:
            typer.echo(export.to_csv(conn, run_id))
    finally:
        conn.close()


@app.command("themes")
def themes(
    run: str = typer.Option("latest", "--run", help="Run id or 'latest'"),
    min_count: int = typer.Option(1, "--min-count", help="Minimum gap_count to show"),
    db_path: str = typer.Option("analyzer.db", "--db", help="SQLite DB path"),
    include_incomplete: bool = typer.Option(False, "--include-incomplete"),
) -> None:
    """Render the theme histogram for a run."""
    conn = db.connect(db_path)
    try:
        try:
            run_id = report_data.resolve_run_id(conn, run, include_incomplete=include_incomplete)
        except report_data.NoDataError as exc:
            typer.echo(f"No data: {exc}")
            raise typer.Exit(code=0) from None
        render.render_themes(conn, run_id, Console(), min_count=min_count)
    finally:
        conn.close()


@app.command("trend")
def trend(
    metric: str = typer.Option("miss_rate", "--metric", help="Metric to trend"),
    db_path: str = typer.Option("analyzer.db", "--db", help="SQLite DB path"),
    include_incomplete: bool = typer.Option(False, "--include-incomplete"),
) -> None:
    """Render a metric trend across runs."""
    conn = db.connect(db_path)
    try:
        try:
            render.render_trend(conn, metric, Console(), include_incomplete=include_incomplete)
        except report_data.NoDataError as exc:
            typer.echo(f"No data: {exc}")
            raise typer.Exit(code=0) from None
    finally:
        conn.close()


@app.command("suggest-prompts")
def suggest_prompts(
    run: str = typer.Option("latest", "--run", help="Run id or 'latest'"),
    config: str = typer.Option("config.yaml", "--config", help="Config file path"),
    db_path: str = typer.Option("analyzer.db", "--db", help="SQLite DB path"),
    include_incomplete: bool = typer.Option(False, "--include-incomplete"),
) -> None:
    """Generate prompt-improvement suggestions for a run's gaps (uses the LLM).

    For each gap (a substantive issue the Copilot reviewer missed) this stores a
    PR-specific finding and a generalizable prompt rule, then prints a paste-ready
    addendum for your Copilot review prompt. View it later via ``analyzer report``.
    """
    _configure_logging()
    cfg = Config.load(config)
    conn = db.connect(db_path)
    try:
        db.init_db(conn)
        try:
            run_id = report_data.resolve_run_id(conn, run, include_incomplete=include_incomplete)
        except report_data.NoDataError as exc:
            typer.echo(f"No data: {exc}")
            raise typer.Exit(code=0) from None
        completer = make_completer(cfg.model)
        stats = pipeline_suggest.suggest_run(conn, run_id, cfg, complete=completer)
        if stats.total == 0:
            typer.echo(f"Run {run_id} has no gaps to learn from.")
            raise typer.Exit(code=0)
        typer.echo(
            f"Generated {stats.suggested}/{stats.total} suggestion(s) for run {run_id} "
            f"({stats.unsuggested} skipped).\n"
        )
        addendum = export.build_prompt_addendum(
            export.build_report_dict(conn, run_id)["suggestions"]
        )
        if addendum:
            typer.echo(addendum)
    finally:
        conn.close()


@app.callback()
def _main() -> None:
    """Analyzer CLI entrypoint."""


if __name__ == "__main__":  # pragma: no cover
    _configure_logging()
    app()
