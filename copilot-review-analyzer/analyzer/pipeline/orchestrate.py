"""Run orchestrator: ties the pipeline stages together for ``analyzer run``.

Stages: ingest → attribute → judge (Phase-4 stub or Phase-6 LLM) → gaps → metrics.
A run row tracks terminal status so failed/partial runs are excluded from reports.
"""

from __future__ import annotations

import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone

from analyzer.config import Config
from analyzer.github.client import GitHubClient
from analyzer.github.queries import NormalizedPR
from analyzer.pipeline import attribute, gaps, ingest, metrics
from analyzer.store import db

logger = logging.getLogger(__name__)


@dataclass
class RunResult:
    """Summary of a completed run."""

    run_id: int
    pr_count: int
    gap_count: int
    status: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def apply_stub_judgements(conn: sqlite3.Connection, run_id: int) -> int:
    """Phase-4 stub judge: mark every human comment substantive + diff_detectable.

    This validates gap/metric plumbing without an LLM. It is replaced by the real
    LLM judge in Phase 6. Confidence is set to 1.0 so the comments count as judged.
    """
    cur = conn.execute(
        """
        UPDATE comments
        SET is_substantive = 1, diff_detectable = 1, judge_confidence = 1.0
        WHERE run_id = ? AND author_kind = 'human'
        """,
        (run_id,),
    )
    conn.commit()
    return cur.rowcount


def run_analysis(
    config: Config,
    *,
    repo: str,
    since: str,
    state: str,
    max_prs: int,
    db_path: str,
    client: GitHubClient | None = None,
    now: datetime | None = None,
    use_llm: bool = False,
) -> RunResult:
    """Execute a full analysis run for one repo and persist all tables."""
    window_start, window_end = ingest.compute_window(since, now)
    conn = db.connect(db_path)
    db.init_db(conn)
    run_id = db.insert_run(
        conn,
        repo=repo,
        started_at=_now_iso(),
        window_start=window_start.isoformat(),
        window_end=window_end.isoformat(),
        pr_state=state,
        model=config.model,
        config_hash=config.config_hash,
        status="started",
    )

    owns_client = client is None
    client = client or GitHubClient()
    try:
        prs = ingest.fetch_window(
            client,
            repo,
            window_start=window_start,
            window_end=window_end,
            state=state,
            max_prs=min(max_prs, config.max_prs),
        )
        pairs: list[tuple[NormalizedPR, int]] = []
        for pr in prs:
            pr_id = db.upsert_pr(
                conn,
                run_id=run_id,
                number=pr.meta.number,
                title=pr.meta.title,
                author=pr.meta.author_login,
                state=pr.meta.state,
                url=pr.meta.url,
                created_at=pr.meta.created_at,
                merged_at=pr.meta.merged_at,
                closed_at=pr.meta.closed_at,
                additions=pr.meta.additions,
                deletions=pr.meta.deletions,
            )
            attribute.persist_pr_comments(
                conn,
                run_id=run_id,
                pr_id=pr_id,
                pr=pr,
                copilot_logins=config.copilot_logins,
                line_fuzz=config.line_fuzz,
            )
            pairs.append((pr, pr_id))

        completer = None
        if use_llm:
            from analyzer.llm.client import make_completer
            from analyzer.pipeline import classify as classify_mod

            completer = make_completer(config.model)
            classify_mod.judge_run(conn, run_id, config, complete=completer)
            acted = classify_mod.link_acted_on(
                conn,
                run_id,
                pairs,
                client=client,
                repo=repo,
            )
            logger.info("Run %s acted_on set for %d Copilot comments", run_id, acted)
        else:
            apply_stub_judgements(conn, run_id)

        gap_summary = gaps.detect_gaps(
            conn, run_id, confidence_threshold=config.confidence_threshold
        )
        if use_llm and completer is not None:
            from analyzer.pipeline import themes as themes_mod

            themes_mod.tag_run(conn, run_id, config, complete=completer)
        metrics.compute_and_store(
            conn,
            run_id,
            pr_count=len(prs),
            confidence_threshold=config.confidence_threshold,
        )
        db.finish_run(
            conn,
            run_id,
            status="completed",
            finished_at=_now_iso(),
            pr_count=len(prs),
        )
        logger.info("Run %s completed: prs=%d gaps=%d", run_id, len(prs), gap_summary.gap_count)
        return RunResult(
            run_id=run_id,
            pr_count=len(prs),
            gap_count=gap_summary.gap_count,
            status="completed",
        )
    except Exception as exc:  # noqa: BLE001 - persist failure, then re-raise
        db.finish_run(
            conn,
            run_id,
            status="failed",
            finished_at=_now_iso(),
            error_summary=f"{type(exc).__name__}: {exc}"[:500],
        )
        logger.exception("Run %s failed", run_id)
        raise
    finally:
        if owns_client:
            client.close()
        conn.close()
