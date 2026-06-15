"""Stage 3 — Classification: LLM judge + deterministic ``acted_on`` linkage.

Two responsibilities:

1. ``judge_run`` — load a run's human review comments, classify each via the LLM
   judge (``is_substantive`` / ``diff_detectable`` / ``category`` / confidence), and
   persist results. Comments the model cannot judge are left with NULL confidence so
   the metrics layer counts them as *unjudged*. If the unjudged fraction exceeds
   ``config.max_unjudged_ratio`` we raise :class:`JudgeError` so the orchestrator marks
   the whole run failed (a half-judged run would skew the headline metrics).

2. ``link_acted_on`` — a best-effort, deterministic signal: did a later commit touch
   the file a Copilot comment pointed at? Pure logic lives in :func:`acted_on`; the
   only I/O is fetching per-commit file paths via REST. When path data is unavailable
   the signal stays NULL (DESIGN §5 permits this fallback).
"""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from analyzer.config import Config
from analyzer.github.client import GitHubClient
from analyzer.github.queries import NormalizedPR
from analyzer.llm.client import Completer
from analyzer.llm.judge import CommentItem, judge_comments
from analyzer.store import db

logger = logging.getLogger(__name__)

# Skip acted_on path fetching for unusually large PRs — N REST calls per commit is
# not worth it and the signal is only a precision proxy.
_MAX_COMMITS_FOR_ACTED_ON = 50


class JudgeError(RuntimeError):
    """Raised when too many comments could not be judged to trust the run."""


@dataclass(frozen=True)
class JudgeStats:
    """Outcome of judging a run's human comments."""

    total: int
    judged: int
    unjudged: int
    retries: int


@dataclass(frozen=True)
class CommitFiles:
    """A commit's timestamp and the set of paths it touched (``None`` = unknown)."""

    committed_date: str | None
    paths: set[str] | None


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def acted_on(
    path: str | None, comment_created: str | None, commits: Sequence[CommitFiles]
) -> bool | None:
    """Did a commit *after* the comment touch ``path``?

    Returns ``True``/``False`` only when path data is available for at least one
    commit; otherwise ``None`` (unavailable). A ``None`` ``path`` or unparseable
    comment timestamp also yields ``None``.
    """
    if path is None:
        return None
    created = _parse_iso(comment_created)
    if created is None:
        return None
    known = [c for c in commits if c.paths is not None]
    if not known:
        return None
    for commit in known:
        committed = _parse_iso(commit.committed_date)
        if committed is not None and committed > created and path in (commit.paths or set()):
            return True
    return False


def _load_human_items(conn: sqlite3.Connection, run_id: int) -> list[CommentItem]:
    rows = conn.execute(
        """
        SELECT id, file_path, line_start, line_end, diff_hunk, body
        FROM comments
        WHERE run_id = ? AND author_kind = 'human' AND is_review_body = 0
        """,
        (run_id,),
    ).fetchall()
    return [
        CommentItem(
            id=int(r[0]),
            file_path=r[1],
            line_start=r[2],
            line_end=r[3],
            diff_hunk=r[4],
            body=r[5],
        )
        for r in rows
    ]


def judge_run(
    conn: sqlite3.Connection, run_id: int, config: Config, *, complete: Completer
) -> JudgeStats:
    """Classify all human comments for ``run_id`` and persist judgements."""
    items = _load_human_items(conn, run_id)
    total = len(items)
    if total == 0:
        return JudgeStats(total=0, judged=0, unjudged=0, retries=0)

    result = judge_comments(items, complete=complete, batch_size=config.judge_batch_size)

    for comment_id, judgement in result.judgements.items():
        db.update_comment_judgement(
            conn,
            comment_id,
            is_substantive=judgement.is_substantive,
            diff_detectable=judgement.diff_detectable,
            category=judgement.category,
            judge_rationale=judgement.rationale,
            judge_confidence=judgement.confidence,
        )

    # Unjudged comments keep NULL confidence (metrics counts them as unjudged).
    unjudged = len(result.unjudged_ids)
    judged = total - unjudged
    if total > 0 and (unjudged / total) > config.max_unjudged_ratio:
        raise JudgeError(
            f"Unjudged ratio {unjudged}/{total} exceeds max {config.max_unjudged_ratio}"
        )

    logger.info("Run %s judged: %d/%d (unjudged=%d)", run_id, judged, total, unjudged)
    return JudgeStats(total=total, judged=judged, unjudged=unjudged, retries=result.retries)


def _fetch_commit_files(
    client: GitHubClient, owner: str, name: str, pr: NormalizedPR
) -> list[CommitFiles] | None:
    """Fetch per-commit file paths for a PR; ``None`` if too large to bother."""
    if len(pr.commits) > _MAX_COMMITS_FOR_ACTED_ON:
        return None
    out: list[CommitFiles] = []
    for commit in pr.commits:
        paths = client.fetch_commit_files(owner, name, commit.oid)
        out.append(CommitFiles(committed_date=commit.committed_date, paths=paths))
    return out


def link_acted_on(
    conn: sqlite3.Connection,
    run_id: int,
    pairs: Sequence[tuple[NormalizedPR, int]],
    *,
    client: GitHubClient,
    repo: str,
) -> int:
    """Set ``acted_on`` for Copilot comments using deterministic commit-file data.

    Best-effort: any fetch failure leaves the affected comments NULL. Returns the
    number of comments whose ``acted_on`` was set to a non-NULL value.
    """
    owner, _, name = repo.partition("/")
    set_count = 0
    for pr, pr_id in pairs:
        copilot_rows = conn.execute(
            """
            SELECT id, file_path, created_at
            FROM comments
            WHERE run_id = ? AND pr_id = ? AND author_kind = 'copilot'
                  AND file_path IS NOT NULL
            """,
            (run_id, pr_id),
        ).fetchall()
        if not copilot_rows:
            continue
        commits = _fetch_commit_files(client, owner, name, pr)
        if not commits:
            continue
        for comment_id, file_path, created_at in copilot_rows:
            verdict = acted_on(file_path, created_at, commits)
            if verdict is not None:
                db.set_comment_acted_on(conn, int(comment_id), verdict)
                set_count += 1
    return set_count
