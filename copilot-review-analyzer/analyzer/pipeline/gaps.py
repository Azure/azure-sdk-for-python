"""Stage 4a — Gap detection.

A **gap** is a human review comment that is substantive and diff-detectable but was
*not* overlapped by any Copilot comment — i.e. something a human caught that Copilot
missed. Only judged, sufficiently-confident comments contribute to gaps; the judge
fields are populated either by the Phase-6 LLM judge or the Phase-4 stub judge.
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass

from analyzer.store import db

logger = logging.getLogger(__name__)


def is_gap(
    is_substantive: bool | None,
    diff_detectable: bool | None,
    copilot_overlap: bool | None,
) -> bool:
    """Pure gap rule: substantive AND diff_detectable AND not overlapped by Copilot.

    ``copilot_overlap`` is treated as "not overlapped" unless it is truthy (SQLite
    stores it as integer ``1``); NULL/0 means no established overlap.
    """
    return bool(is_substantive) and bool(diff_detectable) and not bool(copilot_overlap)


@dataclass
class GapSummary:
    """Per-run gap detection counters."""

    gap_count: int = 0
    judged_human_count: int = 0
    unjudged_human_count: int = 0
    low_confidence_human_count: int = 0


def detect_gaps(
    conn: sqlite3.Connection,
    run_id: int,
    *,
    confidence_threshold: float,
) -> GapSummary:
    """Detect gaps for a run and persist them idempotently into ``gaps``.

    Human comments are partitioned into judged / unjudged (NULL confidence) /
    low-confidence (< threshold). Only judged, confident comments are eligible to be
    gaps. Re-running is safe via ``UNIQUE(run_id, comment_id)``.
    """
    summary = GapSummary()
    rows = conn.execute(
        """
        SELECT id, pr_id, is_substantive, diff_detectable, copilot_overlap,
               judge_confidence, category
        FROM comments
        WHERE run_id = ? AND author_kind = 'human'
        """,
        (run_id,),
    ).fetchall()

    for row in rows:
        confidence = row["judge_confidence"]
        if confidence is None:
            summary.unjudged_human_count += 1
            continue
        if confidence < confidence_threshold:
            summary.low_confidence_human_count += 1
            continue
        summary.judged_human_count += 1
        if is_gap(row["is_substantive"], row["diff_detectable"], row["copilot_overlap"]):
            summary.gap_count += 1
            db.upsert_gap(
                conn,
                run_id=run_id,
                pr_id=row["pr_id"],
                comment_id=row["id"],
                category=row["category"],
            )

    logger.info(
        "Run %s gaps: gap_count=%d judged=%d unjudged=%d low_confidence=%d",
        run_id,
        summary.gap_count,
        summary.judged_human_count,
        summary.unjudged_human_count,
        summary.low_confidence_human_count,
    )
    return summary
