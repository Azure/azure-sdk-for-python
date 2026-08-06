"""Read-only queries backing the report/themes/trend commands.

By default only successfully **completed** runs are considered (failed/partial runs
are retained for audit but excluded). The ``RECALL_CAVEAT`` is surfaced by every
report so ``miss_rate`` is never read as an absolute.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

RECALL_CAVEAT = (
    "Caveat: miss_rate is RELATIVE to issues humans actually commented on, not "
    "ground truth. Issues nobody flagged are invisible. Track precision and recall "
    "separately; never read miss_rate as an absolute."
)


class NoDataError(RuntimeError):
    """Raised when a requested run or any completed run does not exist."""


@dataclass(frozen=True)
class DataQuality:
    """Data-quality counters surfaced alongside metrics."""

    judged_human_count: int
    unjudged_human_count: int
    low_confidence_human_count: int


def resolve_run_id(
    conn: sqlite3.Connection, run: str = "latest", *, include_incomplete: bool = False
) -> int:
    """Resolve ``"latest"`` or a numeric run id to a concrete run id.

    ``latest`` resolves to the newest completed run unless ``include_incomplete``.
    """
    if run != "latest":
        try:
            run_id = int(run)
        except ValueError as exc:
            raise NoDataError(f"Invalid run id '{run}'") from exc
        row = conn.execute("SELECT id, status FROM runs WHERE id = ?", (run_id,)).fetchone()
        if row is None:
            raise NoDataError(f"Run {run_id} not found")
        if not include_incomplete and row["status"] != "completed":
            raise NoDataError(
                f"Run {run_id} has status '{row['status']}'; pass --include-incomplete"
            )
        return run_id

    if include_incomplete:
        row = conn.execute("SELECT id FROM runs ORDER BY id DESC LIMIT 1").fetchone()
    else:
        row = conn.execute(
            "SELECT id FROM runs WHERE status = 'completed' ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if row is None:
        raise NoDataError("No runs found")
    return int(row["id"])


def get_run(conn: sqlite3.Connection, run_id: int) -> sqlite3.Row:
    row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    if row is None:
        raise NoDataError(f"Run {run_id} not found")
    return row


def get_metrics(conn: sqlite3.Connection, run_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM metrics WHERE run_id = ?", (run_id,)).fetchone()


def get_themes(conn: sqlite3.Connection, run_id: int, *, min_count: int = 1) -> list[sqlite3.Row]:
    return conn.execute(
        """
        SELECT label, description, gap_count
        FROM themes
        WHERE run_id = ? AND gap_count >= ?
        ORDER BY gap_count DESC, label ASC
        """,
        (run_id, min_count),
    ).fetchall()


def get_gap_suggestions(conn: sqlite3.Connection, run_id: int) -> list[sqlite3.Row]:
    """Return per-gap prompt suggestions joined with their PR / theme context."""
    return conn.execute(
        """
        SELECT s.gap_id AS gap_id, p.number AS pr_number, c.url AS url,
               g.category AS category, t.label AS theme,
               c.file_path AS file_path, c.line_start AS line_start,
               s.missed_finding AS missed_finding,
               s.prompt_improvement AS prompt_improvement
        FROM gap_suggestions s
        JOIN gaps g ON g.id = s.gap_id
        JOIN comments c ON c.id = s.comment_id
        JOIN prs p ON p.id = g.pr_id
        LEFT JOIN themes t ON t.id = g.theme_id
        WHERE s.run_id = ?
        ORDER BY t.label ASC, p.number ASC, s.gap_id ASC
        """,
        (run_id,),
    ).fetchall()


def list_runs(conn: sqlite3.Connection, *, include_incomplete: bool = False) -> list[sqlite3.Row]:
    where = "" if include_incomplete else "WHERE status = 'completed'"
    return conn.execute(f"SELECT * FROM runs {where} ORDER BY id ASC").fetchall()


_TREND_METRICS = {
    "miss_rate",
    "copilot_overlap_rate",
    "copilot_acted_on_rate",
    "human_burden_per_pr",
}


def trend_series(
    conn: sqlite3.Connection, metric: str, *, include_incomplete: bool = False
) -> list[tuple[int, float | None]]:
    """Return ``[(run_id, metric_value), ...]`` across runs, oldest first."""
    if metric not in _TREND_METRICS:
        raise NoDataError(f"Unknown metric '{metric}'; choose from {sorted(_TREND_METRICS)}")
    join = "" if include_incomplete else "AND r.status = 'completed'"
    rows = conn.execute(
        f"""
        SELECT r.id AS run_id, m.{metric} AS value
        FROM runs r
        LEFT JOIN metrics m ON m.run_id = r.id
        WHERE 1 = 1 {join}
        ORDER BY r.id ASC
        """
    ).fetchall()
    return [(int(r["run_id"]), r["value"]) for r in rows]
