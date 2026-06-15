"""Stage 6 — Prompt suggestions: learn from gaps to improve the Copilot reviewer.

For each gap (a substantive, diff-detectable issue the Copilot reviewer missed) the LLM
produces a PR-specific ``missed_finding`` and a generalizable ``prompt_improvement``.
Results are persisted to ``gap_suggestions`` and later synthesized into a pasteable
prompt addendum by the reporting layer. All model I/O stays behind the ``Completer``
callable; failures degrade gracefully (gaps without a suggestion are simply skipped).
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from analyzer.config import Config
from analyzer.llm.client import Completer
from analyzer.llm.suggest import GapContext, suggest_for_gaps
from analyzer.store import db

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SuggestStats:
    """Outcome of generating prompt suggestions for a run."""

    total: int
    suggested: int
    unsuggested: int
    retries: int


def _load_gap_contexts(conn: sqlite3.Connection, run_id: int) -> list[GapContext]:
    rows = conn.execute(
        """
        SELECT g.id AS gap_id, g.comment_id AS comment_id, p.number AS pr_number,
               g.category AS category, t.label AS theme,
               c.file_path AS file_path, c.line_start AS line_start,
               c.line_end AS line_end, c.diff_hunk AS diff_hunk,
               c.body AS body, c.judge_rationale AS rationale
        FROM gaps g
        JOIN comments c ON c.id = g.comment_id
        JOIN prs p ON p.id = g.pr_id
        LEFT JOIN themes t ON t.id = g.theme_id
        WHERE g.run_id = ?
        ORDER BY g.id ASC
        """,
        (run_id,),
    ).fetchall()
    return [
        GapContext(
            gap_id=int(r["gap_id"]),
            comment_id=int(r["comment_id"]),
            pr_number=r["pr_number"],
            category=r["category"],
            theme=r["theme"],
            file_path=r["file_path"],
            line_start=r["line_start"],
            line_end=r["line_end"],
            diff_hunk=r["diff_hunk"],
            body=r["body"],
            rationale=r["rationale"],
        )
        for r in rows
    ]


def suggest_run(
    conn: sqlite3.Connection, run_id: int, config: Config, *, complete: Completer
) -> SuggestStats:
    """Generate and persist prompt suggestions for every gap in ``run_id``."""
    contexts = _load_gap_contexts(conn, run_id)
    total = len(contexts)
    if total == 0:
        return SuggestStats(total=0, suggested=0, unsuggested=0, retries=0)

    result = suggest_for_gaps(contexts, complete=complete, batch_size=config.judge_batch_size)
    now = datetime.now(timezone.utc).isoformat()
    for suggestion in result.suggestions.values():
        db.upsert_gap_suggestion(
            conn,
            run_id=run_id,
            gap_id=suggestion.gap_id,
            comment_id=suggestion.comment_id,
            missed_finding=suggestion.missed_finding,
            prompt_improvement=suggestion.prompt_improvement,
            created_at=now,
        )

    suggested = len(result.suggestions)
    unsuggested = len(result.unsuggested_ids)
    logger.info("Run %s suggestions: %d/%d (unsuggested=%d)", run_id, suggested, total, unsuggested)
    return SuggestStats(
        total=total,
        suggested=suggested,
        unsuggested=unsuggested,
        retries=result.retries,
    )
