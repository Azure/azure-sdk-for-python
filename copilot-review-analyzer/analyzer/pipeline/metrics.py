"""Stage 5 — Per-run metrics (DESIGN §9).

Computes the four headline metrics plus the data-quality counters and stores one
``metrics`` row per run. Denominators are defined explicitly; any divide-by-zero
yields SQL NULL rather than an error so empty runs do not crash.
"""

from __future__ import annotations

import logging
import sqlite3

from analyzer.store import db

logger = logging.getLogger(__name__)


def _safe_ratio(numerator: int, denominator: int) -> float | None:
    """Return ``numerator/denominator`` or ``None`` when the denominator is 0."""
    if denominator == 0:
        return None
    return numerator / denominator


def compute_and_store(
    conn: sqlite3.Connection,
    run_id: int,
    *,
    pr_count: int,
    confidence_threshold: float,
) -> dict[str, float | None]:
    """Compute and persist the metrics row for ``run_id``; return the metric values.

    Definitions:
      - judged confident human = ``judge_confidence`` not NULL and >= threshold.
      - substantive human = judged confident human with ``is_substantive = 1``.
      - miss_rate = gaps / (substantive AND diff_detectable judged human comments).
      - copilot_overlap_rate = overlapped substantive human / substantive human.
      - human_burden_per_pr = substantive human / pr_count.
      - copilot_acted_on_rate = acted-on Copilot comments / Copilot comments
        (NULL until ``acted_on`` is populated in Phase 6/7).
    """
    judged_filter = "judge_confidence IS NOT NULL AND judge_confidence >= ?"

    def human_count(extra: str = "") -> int:
        sql = "SELECT COUNT(*) FROM comments " "WHERE run_id = ? AND author_kind = 'human' " + extra
        return int(conn.execute(sql, (run_id, confidence_threshold)).fetchone()[0])

    judged_human = human_count(f"AND {judged_filter}")
    substantive_human = human_count(f"AND {judged_filter} AND is_substantive = 1")
    substantive_detectable_human = human_count(
        f"AND {judged_filter} AND is_substantive = 1 AND diff_detectable = 1"
    )
    overlapped_substantive_human = human_count(
        f"AND {judged_filter} AND is_substantive = 1 AND copilot_overlap = 1"
    )

    unjudged_human = int(
        conn.execute(
            "SELECT COUNT(*) FROM comments WHERE run_id = ? AND author_kind = 'human' "
            "AND judge_confidence IS NULL",
            (run_id,),
        ).fetchone()[0]
    )
    low_confidence_human = int(
        conn.execute(
            "SELECT COUNT(*) FROM comments WHERE run_id = ? AND author_kind = 'human' "
            "AND judge_confidence IS NOT NULL AND judge_confidence < ?",
            (run_id, confidence_threshold),
        ).fetchone()[0]
    )

    copilot_comment_count = int(
        conn.execute(
            "SELECT COUNT(*) FROM comments WHERE run_id = ? AND author_kind = 'copilot'",
            (run_id,),
        ).fetchone()[0]
    )
    copilot_acted_on = int(
        conn.execute(
            "SELECT COUNT(*) FROM comments WHERE run_id = ? AND author_kind = 'copilot' "
            "AND acted_on = 1",
            (run_id,),
        ).fetchone()[0]
    )
    copilot_acted_on_known = int(
        conn.execute(
            "SELECT COUNT(*) FROM comments WHERE run_id = ? AND author_kind = 'copilot' "
            "AND acted_on IS NOT NULL",
            (run_id,),
        ).fetchone()[0]
    )

    gap_count = int(
        conn.execute("SELECT COUNT(*) FROM gaps WHERE run_id = ?", (run_id,)).fetchone()[0]
    )

    miss_rate = _safe_ratio(gap_count, substantive_detectable_human)
    copilot_overlap_rate = _safe_ratio(overlapped_substantive_human, substantive_human)
    human_burden_per_pr = _safe_ratio(substantive_human, pr_count)
    # Only report acted-on rate when at least one Copilot comment has known path data.
    copilot_acted_on_rate = (
        _safe_ratio(copilot_acted_on, copilot_acted_on_known)
        if copilot_acted_on_known > 0
        else None
    )

    db.upsert_metrics(
        conn,
        run_id,
        substantive_human_count=substantive_human,
        copilot_comment_count=copilot_comment_count,
        gap_count=gap_count,
        judged_human_count=judged_human,
        unjudged_human_count=unjudged_human,
        low_confidence_human_count=low_confidence_human,
        miss_rate=miss_rate,
        copilot_overlap_rate=copilot_overlap_rate,
        copilot_acted_on_rate=copilot_acted_on_rate,
        human_burden_per_pr=human_burden_per_pr,
    )

    logger.info(
        "Run %s metrics: miss_rate=%s overlap_rate=%s burden/pr=%s gaps=%d substantive=%d",
        run_id,
        miss_rate,
        copilot_overlap_rate,
        human_burden_per_pr,
        gap_count,
        substantive_human,
    )
    return {
        "miss_rate": miss_rate,
        "copilot_overlap_rate": copilot_overlap_rate,
        "copilot_acted_on_rate": copilot_acted_on_rate,
        "human_burden_per_pr": human_burden_per_pr,
    }
