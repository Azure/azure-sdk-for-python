"""SQLite access layer: connection, schema init, and typed idempotent upserts.

Centralizes all SQL so pipeline stages never hand-write queries. Upserts honor the
``UNIQUE`` constraints in ``schema.sql`` so re-running a stage for the same ``run_id``
updates existing rows instead of duplicating them.
"""

from __future__ import annotations

import logging
import sqlite3
from importlib import resources
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 2


def _load_schema_sql() -> str:
    return resources.files("analyzer.store").joinpath("schema.sql").read_text(encoding="utf-8")


def connect(path: str | Path) -> sqlite3.Connection:
    """Open a connection with foreign keys enforced and row access by name."""
    p = Path(path)
    if p.parent and not p.parent.exists():
        raise FileNotFoundError(f"Directory does not exist for DB path: {p.parent}")
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create tables idempotently and stamp the schema version.

    Safe to run repeatedly: uses ``CREATE TABLE IF NOT EXISTS`` and never drops data.
    """
    conn.executescript(_load_schema_sql())
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    conn.commit()
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    db_path = _db_path(conn)
    logger.info("init_db: path=%s user_version=%s", db_path, version)


def _db_path(conn: sqlite3.Connection) -> str:
    row = conn.execute("PRAGMA database_list").fetchone()
    return row["file"] if row and row["file"] else ":memory:"


def schema_version(conn: sqlite3.Connection) -> int:
    """Return the ``PRAGMA user_version`` stored in the DB."""
    return int(conn.execute("PRAGMA user_version").fetchone()[0])


# --------------------------------------------------------------------------- runs


def insert_run(
    conn: sqlite3.Connection,
    *,
    repo: str,
    started_at: str,
    window_start: str,
    window_end: str,
    pr_state: str,
    model: str,
    config_hash: str | None = None,
    status: str = "started",
) -> int:
    """Insert a new run row and return its id."""
    cur = conn.execute(
        """
        INSERT INTO runs (repo, started_at, window_start, window_end, pr_state,
                          model, config_hash, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (repo, started_at, window_start, window_end, pr_state, model, config_hash, status),
    )
    conn.commit()
    return int(cur.lastrowid or 0)


def finish_run(
    conn: sqlite3.Connection,
    run_id: int,
    *,
    status: str,
    finished_at: str,
    pr_count: int | None = None,
    error_summary: str | None = None,
) -> None:
    """Mark a run terminal (completed|failed) with an optional error summary."""
    fields = ["status = ?", "finished_at = ?"]
    params: list[Any] = [status, finished_at]
    if pr_count is not None:
        fields.append("pr_count = ?")
        params.append(pr_count)
    if error_summary is not None:
        fields.append("error_summary = ?")
        params.append(error_summary)
    params.append(run_id)
    conn.execute(f"UPDATE runs SET {', '.join(fields)} WHERE id = ?", params)
    conn.commit()


def latest_completed_run(conn: sqlite3.Connection) -> sqlite3.Row | None:
    """Return the most recent successfully completed run, or ``None``."""
    return conn.execute(
        "SELECT * FROM runs WHERE status = 'completed' ORDER BY id DESC LIMIT 1"
    ).fetchone()


# --------------------------------------------------------------------------- prs


def upsert_pr(
    conn: sqlite3.Connection,
    *,
    run_id: int,
    number: int,
    title: str | None = None,
    author: str | None = None,
    state: str | None = None,
    url: str | None = None,
    created_at: str | None = None,
    merged_at: str | None = None,
    closed_at: str | None = None,
    additions: int | None = None,
    deletions: int | None = None,
) -> int:
    """Insert or update a PR row keyed by ``(run_id, number)``; return its id."""
    conn.execute(
        """
        INSERT INTO prs (run_id, number, title, author, state, url, created_at,
                         merged_at, closed_at, additions, deletions)
        VALUES (:run_id, :number, :title, :author, :state, :url, :created_at,
                :merged_at, :closed_at, :additions, :deletions)
        ON CONFLICT(run_id, number) DO UPDATE SET
            title = excluded.title,
            author = excluded.author,
            state = excluded.state,
            url = excluded.url,
            created_at = excluded.created_at,
            merged_at = excluded.merged_at,
            closed_at = excluded.closed_at,
            additions = excluded.additions,
            deletions = excluded.deletions
        """,
        {
            "run_id": run_id,
            "number": number,
            "title": title,
            "author": author,
            "state": state,
            "url": url,
            "created_at": created_at,
            "merged_at": merged_at,
            "closed_at": closed_at,
            "additions": additions,
            "deletions": deletions,
        },
    )
    conn.commit()
    row = conn.execute(
        "SELECT id FROM prs WHERE run_id = ? AND number = ?", (run_id, number)
    ).fetchone()
    return int(row["id"])


# ----------------------------------------------------------------------- comments


def upsert_comment(
    conn: sqlite3.Connection,
    *,
    run_id: int,
    pr_id: int,
    source_key: str,
    author_kind: str,
    external_id: int | None = None,
    author: str | None = None,
    is_review_body: bool = False,
    file_path: str | None = None,
    line_start: int | None = None,
    line_end: int | None = None,
    coord_space: str | None = None,
    body: str | None = None,
    diff_hunk: str | None = None,
    created_at: str | None = None,
    url: str | None = None,
) -> int:
    """Insert or update a comment keyed by ``(run_id, source_key)``; return its id.

    Only ingest/attribute fields are written here; LLM-judge fields are updated
    separately via :func:`update_comment_judgement`.
    """
    conn.execute(
        """
        INSERT INTO comments (run_id, pr_id, external_id, source_key, author,
                              author_kind, is_review_body, file_path, line_start,
                              line_end, coord_space, body, diff_hunk, created_at, url)
        VALUES (:run_id, :pr_id, :external_id, :source_key, :author, :author_kind,
                :is_review_body, :file_path, :line_start, :line_end, :coord_space,
                :body, :diff_hunk, :created_at, :url)
        ON CONFLICT(run_id, source_key) DO UPDATE SET
            pr_id = excluded.pr_id,
            external_id = excluded.external_id,
            author = excluded.author,
            author_kind = excluded.author_kind,
            is_review_body = excluded.is_review_body,
            file_path = excluded.file_path,
            line_start = excluded.line_start,
            line_end = excluded.line_end,
            coord_space = excluded.coord_space,
            body = excluded.body,
            diff_hunk = excluded.diff_hunk,
            created_at = excluded.created_at,
            url = excluded.url
        """,
        {
            "run_id": run_id,
            "pr_id": pr_id,
            "external_id": external_id,
            "source_key": source_key,
            "author": author,
            "author_kind": author_kind,
            "is_review_body": 1 if is_review_body else 0,
            "file_path": file_path,
            "line_start": line_start,
            "line_end": line_end,
            "coord_space": coord_space,
            "body": body,
            "diff_hunk": diff_hunk,
            "created_at": created_at,
            "url": url,
        },
    )
    conn.commit()
    row = conn.execute(
        "SELECT id FROM comments WHERE run_id = ? AND source_key = ?",
        (run_id, source_key),
    ).fetchone()
    return int(row["id"])


def set_comment_overlap(conn: sqlite3.Connection, comment_id: int, overlap: bool | None) -> None:
    """Record whether a human comment was overlapped by a Copilot comment.

    ``None`` records SQL NULL (overlap undeterminable, e.g. no comparable range).
    """
    conn.execute(
        "UPDATE comments SET copilot_overlap = ? WHERE id = ?",
        (None if overlap is None else (1 if overlap else 0), comment_id),
    )
    conn.commit()


def update_comment_judgement(
    conn: sqlite3.Connection,
    comment_id: int,
    *,
    is_substantive: bool | None,
    diff_detectable: bool | None,
    category: str | None,
    judge_rationale: str | None,
    judge_confidence: float | None,
) -> None:
    """Write LLM-judge results onto a comment row."""
    conn.execute(
        """
        UPDATE comments SET
            is_substantive = ?,
            diff_detectable = ?,
            category = ?,
            judge_rationale = ?,
            judge_confidence = ?
        WHERE id = ?
        """,
        (
            None if is_substantive is None else int(is_substantive),
            None if diff_detectable is None else int(diff_detectable),
            category,
            judge_rationale,
            judge_confidence,
            comment_id,
        ),
    )
    conn.commit()


def set_comment_acted_on(conn: sqlite3.Connection, comment_id: int, acted_on: bool | None) -> None:
    """Record the coarse ``acted_on`` deterministic signal for a comment."""
    conn.execute(
        "UPDATE comments SET acted_on = ? WHERE id = ?",
        (None if acted_on is None else int(acted_on), comment_id),
    )
    conn.commit()


# --------------------------------------------------------------------------- gaps


def upsert_gap(
    conn: sqlite3.Connection,
    *,
    run_id: int,
    pr_id: int,
    comment_id: int,
    category: str | None = None,
    theme_id: int | None = None,
) -> int:
    """Insert or update a gap keyed by ``(run_id, comment_id)``; return its id."""
    conn.execute(
        """
        INSERT INTO gaps (run_id, pr_id, comment_id, category, theme_id)
        VALUES (:run_id, :pr_id, :comment_id, :category, :theme_id)
        ON CONFLICT(run_id, comment_id) DO UPDATE SET
            pr_id = excluded.pr_id,
            category = excluded.category,
            theme_id = excluded.theme_id
        """,
        {
            "run_id": run_id,
            "pr_id": pr_id,
            "comment_id": comment_id,
            "category": category,
            "theme_id": theme_id,
        },
    )
    conn.commit()
    row = conn.execute(
        "SELECT id FROM gaps WHERE run_id = ? AND comment_id = ?", (run_id, comment_id)
    ).fetchone()
    return int(row["id"])


# ------------------------------------------------------------------------- themes


def upsert_theme(
    conn: sqlite3.Connection,
    *,
    run_id: int,
    label: str,
    description: str | None = None,
    gap_count: int = 0,
) -> int:
    """Insert or update a theme keyed by ``(run_id, label)``; return its id."""
    conn.execute(
        """
        INSERT INTO themes (run_id, label, description, gap_count)
        VALUES (:run_id, :label, :description, :gap_count)
        ON CONFLICT(run_id, label) DO UPDATE SET
            description = excluded.description,
            gap_count = excluded.gap_count
        """,
        {"run_id": run_id, "label": label, "description": description, "gap_count": gap_count},
    )
    conn.commit()
    row = conn.execute(
        "SELECT id FROM themes WHERE run_id = ? AND label = ?", (run_id, label)
    ).fetchone()
    return int(row["id"])


def set_gap_theme(conn: sqlite3.Connection, gap_id: int, theme_id: int | None) -> None:
    """Link a gap to its assigned theme (or clear it with ``None``)."""
    conn.execute("UPDATE gaps SET theme_id = ? WHERE id = ?", (theme_id, gap_id))
    conn.commit()


# -------------------------------------------------------------- gap_suggestions


def upsert_gap_suggestion(
    conn: sqlite3.Connection,
    *,
    run_id: int,
    gap_id: int,
    comment_id: int,
    missed_finding: str | None,
    prompt_improvement: str | None,
    created_at: str | None = None,
) -> int:
    """Insert or update a per-gap prompt suggestion keyed by ``(run_id, gap_id)``."""
    conn.execute(
        """
        INSERT INTO gap_suggestions
            (run_id, gap_id, comment_id, missed_finding, prompt_improvement, created_at)
        VALUES (:run_id, :gap_id, :comment_id, :missed_finding, :prompt_improvement, :created_at)
        ON CONFLICT(run_id, gap_id) DO UPDATE SET
            comment_id = excluded.comment_id,
            missed_finding = excluded.missed_finding,
            prompt_improvement = excluded.prompt_improvement,
            created_at = excluded.created_at
        """,
        {
            "run_id": run_id,
            "gap_id": gap_id,
            "comment_id": comment_id,
            "missed_finding": missed_finding,
            "prompt_improvement": prompt_improvement,
            "created_at": created_at,
        },
    )
    conn.commit()
    row = conn.execute(
        "SELECT id FROM gap_suggestions WHERE run_id = ? AND gap_id = ?", (run_id, gap_id)
    ).fetchone()
    return int(row["id"])


def upsert_metrics(conn: sqlite3.Connection, run_id: int, **values: Any) -> None:
    """Insert or update the single metrics row for a run."""
    columns = [
        "substantive_human_count",
        "copilot_comment_count",
        "gap_count",
        "judged_human_count",
        "unjudged_human_count",
        "low_confidence_human_count",
        "miss_rate",
        "copilot_overlap_rate",
        "copilot_acted_on_rate",
        "human_burden_per_pr",
    ]
    # Count columns are NOT NULL DEFAULT 0; coalesce missing values to 0 rather
    # than NULL. Rate columns remain nullable.
    count_columns = {
        "substantive_human_count",
        "copilot_comment_count",
        "gap_count",
        "judged_human_count",
        "unjudged_human_count",
        "low_confidence_human_count",
    }
    data = {c: (values.get(c, 0) if c in count_columns else values.get(c)) for c in columns}
    set_clause = ", ".join(f"{c} = excluded.{c}" for c in columns)
    conn.execute(
        f"""
        INSERT INTO metrics (run_id, {', '.join(columns)})
        VALUES (:run_id, {', '.join(':' + c for c in columns)})
        ON CONFLICT(run_id) DO UPDATE SET {set_clause}
        """,
        {"run_id": run_id, **data},
    )
    conn.commit()
