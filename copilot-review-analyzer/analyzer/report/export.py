"""Export per-run reports as markdown / JSON / CSV.

Markdown feeds the GitHub Actions issue body; JSON/CSV are for downstream tools.
Output ordering is deterministic so golden snapshots are stable.
"""

from __future__ import annotations

import csv
import io
import json
import sqlite3
from typing import Any

from analyzer.report import data

# Documented JSON schema version for the `--format json` output.
JSON_SCHEMA_VERSION = 2

_METRIC_FIELDS = [
    "miss_rate",
    "copilot_overlap_rate",
    "copilot_acted_on_rate",
    "human_burden_per_pr",
]
_COUNT_FIELDS = [
    "substantive_human_count",
    "copilot_comment_count",
    "gap_count",
    "judged_human_count",
    "unjudged_human_count",
    "low_confidence_human_count",
]


def _fmt(value: float | None) -> str:
    return "N/A" if value is None else f"{value:.3f}"


def build_prompt_addendum(suggestions: list[dict[str, Any]]) -> str:
    """Synthesize a deterministic, pasteable review-prompt addendum from suggestions.

    Generalizable ``prompt_improvement`` rules are grouped by theme and deduplicated
    (case-insensitive), each annotated with the PRs that motivated it. The result is a
    chunk of markdown a user can paste directly into their Copilot review prompt. Returns
    an empty string when there are no suggestions.
    """
    if not suggestions:
        return ""

    # theme -> {normalized_rule: (display_rule, sorted_pr_set)}
    grouped: dict[str, dict[str, tuple[str, set[int]]]] = {}
    for s in suggestions:
        rule = (s.get("prompt_improvement") or "").strip()
        if not rule:
            continue
        theme = (s.get("theme") or "other") or "other"
        key = rule.lower()
        bucket = grouped.setdefault(theme, {})
        display, prs = bucket.get(key, (rule, set()))
        pr = s.get("pr_number")
        if isinstance(pr, int):
            prs.add(pr)
        bucket[key] = (display, prs)

    if not grouped:
        return ""

    lines: list[str] = []
    lines.append("## Suggested review-prompt additions")
    lines.append("")
    lines.append(
        "Paste the rules below into your Copilot review prompt. Each was inferred from a "
        "substantive issue a human reviewer caught that the Copilot reviewer missed."
    )
    lines.append("")
    for theme in sorted(grouped):
        lines.append(f"### {theme}")
        rules = grouped[theme]
        for key in sorted(rules):
            display, prs = rules[key]
            cite = f"  _(from {', '.join(f'#{n}' for n in sorted(prs))})_" if prs else ""
            lines.append(f"- {display}{cite}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_report_dict(conn: sqlite3.Connection, run_id: int) -> dict[str, Any]:
    """Assemble a deterministic, JSON-serializable report for one run."""
    run = data.get_run(conn, run_id)
    metrics = data.get_metrics(conn, run_id)
    themes = data.get_themes(conn, run_id, min_count=1)
    suggestion_rows = data.get_gap_suggestions(conn, run_id)

    metric_values = {f: (metrics[f] if metrics else None) for f in _METRIC_FIELDS}
    count_values = {f: (metrics[f] if metrics else 0) for f in _COUNT_FIELDS}

    suggestions = [
        {
            "pr_number": s["pr_number"],
            "url": s["url"],
            "category": s["category"],
            "theme": s["theme"],
            "file_path": s["file_path"],
            "line_start": s["line_start"],
            "missed_finding": s["missed_finding"],
            "prompt_improvement": s["prompt_improvement"],
        }
        for s in suggestion_rows
    ]

    return {
        "schema_version": JSON_SCHEMA_VERSION,
        "run": {
            "id": run["id"],
            "repo": run["repo"],
            "status": run["status"],
            "pr_state": run["pr_state"],
            "pr_count": run["pr_count"],
            "window_start": run["window_start"],
            "window_end": run["window_end"],
            "model": run["model"],
            "config_hash": run["config_hash"],
            "started_at": run["started_at"],
            "finished_at": run["finished_at"],
            "error_summary": run["error_summary"],
        },
        "metrics": metric_values,
        "counts": count_values,
        "themes": [
            {"label": t["label"], "gap_count": t["gap_count"], "description": t["description"]}
            for t in themes
        ],
        "suggestions": suggestions,
        "prompt_addendum": build_prompt_addendum(suggestions),
        "caveat": data.RECALL_CAVEAT,
    }


def to_json(conn: sqlite3.Connection, run_id: int) -> str:
    """Render the run report as pretty JSON (validates against the documented schema)."""
    return json.dumps(build_report_dict(conn, run_id), indent=2, sort_keys=True)


def to_csv(conn: sqlite3.Connection, run_id: int) -> str:
    """Render a flat one-row CSV of run metrics and counts."""
    report = build_report_dict(conn, run_id)
    buf = io.StringIO()
    fieldnames = ["run_id", "repo", "status", "pr_count"] + _METRIC_FIELDS + _COUNT_FIELDS
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    row = {
        "run_id": report["run"]["id"],
        "repo": report["run"]["repo"],
        "status": report["run"]["status"],
        "pr_count": report["run"]["pr_count"],
        **report["metrics"],
        **report["counts"],
    }
    writer.writerow(row)
    return buf.getvalue()


def to_markdown(conn: sqlite3.Connection, run_id: int) -> str:
    """Render the run report as markdown for an Actions issue body."""
    r = build_report_dict(conn, run_id)
    run = r["run"]
    lines: list[str] = []
    lines.append(f"# Copilot review effectiveness — run {run['id']}")
    lines.append("")
    lines.append(
        f"**Repo:** {run['repo']}  |  **State:** {run['pr_state']}  |  "
        f"**PRs:** {run['pr_count']}  |  **Model:** {run['model']}"
    )
    lines.append(f"**Window:** {run['window_start']} → {run['window_end']}")
    lines.append(f"**Status:** {run['status']}")
    if run["error_summary"]:
        lines.append(f"**Error:** {run['error_summary']}")
    lines.append("")
    lines.append("## Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("| --- | --- |")
    for f in _METRIC_FIELDS:
        lines.append(f"| {f} | {_fmt(r['metrics'][f])} |")
    lines.append("")
    lines.append("## Data quality")
    lines.append("")
    lines.append("| Counter | Value |")
    lines.append("| --- | --- |")
    for f in _COUNT_FIELDS:
        lines.append(f"| {f} | {r['counts'][f]} |")
    lines.append("")
    if r["themes"]:
        lines.append("## Top themes")
        lines.append("")
        lines.append("| Theme | Gaps |")
        lines.append("| --- | --- |")
        for t in r["themes"]:
            lines.append(f"| {t['label']} | {t['gap_count']} |")
        lines.append("")
    if r["suggestions"]:
        lines.append("## What Copilot missed (per gap)")
        lines.append("")
        for s in r["suggestions"]:
            loc = f"{s['file_path']}:{s['line_start']}" if s["file_path"] else "(no file)"
            pr = f"#{s['pr_number']}" if s["pr_number"] is not None else "(unknown PR)"
            header = f"**{pr}** [{s['theme'] or 'other'}] `{loc}`"
            if s["url"]:
                header += f" — [comment]({s['url']})"
            lines.append(f"- {header}")
            lines.append(f"  - Missed: {s['missed_finding']}")
            lines.append(f"  - Prompt fix: {s['prompt_improvement']}")
        lines.append("")
    if r["prompt_addendum"]:
        lines.append(r["prompt_addendum"].rstrip())
        lines.append("")
    lines.append(f"> {r['caveat']}")
    lines.append("")
    return "\n".join(lines)
