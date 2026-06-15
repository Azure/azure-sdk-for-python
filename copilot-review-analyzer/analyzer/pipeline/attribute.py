"""Stage 2 — Attribution (deterministic, no LLM).

Pure helpers to classify a comment's author as ``copilot``/``human``/``other_bot``
and to test whether a human comment's line range overlaps any Copilot comment.
Also persists the deterministic enrichments onto ``comments`` rows.
"""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from analyzer.github.queries import NormalizedComment, NormalizedPR
from analyzer.store import db

logger = logging.getLogger(__name__)

AuthorKind = str  # "copilot" | "human" | "other_bot"


def _normalize_login(login: str) -> str:
    """Lower-case and strip a trailing ``[bot]`` so REST/GraphQL forms match."""
    return login.strip().lower().removesuffix("[bot]")


def classify_author(login: str | None, copilot_logins: Iterable[str]) -> AuthorKind:
    """Classify a comment author.

    - Configured Copilot logins (matched after normalization) → ``copilot``.
    - A login ending in ``[bot]`` → ``other_bot``.
    - ``None``/empty → ``other_bot`` (unknown actor; never crash).
    - Otherwise → ``human``.
    """
    if not login or not login.strip():
        return "other_bot"
    normalized = _normalize_login(login)
    copilot_set = {_normalize_login(c) for c in copilot_logins}
    if normalized in copilot_set:
        return "copilot"
    if login.strip().lower().endswith("[bot]"):
        return "other_bot"
    return "human"


@dataclass(frozen=True)
class LineRange:
    """A comment's location for overlap testing."""

    path: str
    start: int
    end: int
    coord_space: str  # current | original


def _to_line_range(comment: NormalizedComment) -> LineRange | None:
    if (
        comment.file_path is None
        or comment.line_start is None
        or comment.line_end is None
        or comment.coord_space is None
    ):
        return None
    return LineRange(
        path=comment.file_path,
        start=comment.line_start,
        end=comment.line_end,
        coord_space=comment.coord_space,
    )


def overlaps(human_range: LineRange, copilot_ranges: Sequence[LineRange], line_fuzz: int) -> bool:
    """Whether a human range intersects any Copilot range within ``line_fuzz``.

    Overlap requires the same ``path`` and the same coordinate space; ranges in
    incomparable coordinate spaces never overlap.
    """
    for cr in copilot_ranges:
        if cr.path != human_range.path:
            continue
        if cr.coord_space != human_range.coord_space:
            continue
        if cr.start - line_fuzz <= human_range.end and human_range.start - line_fuzz <= cr.end:
            return True
    return False


@dataclass
class AttributionSummary:
    """Per-PR attribution counters for observability."""

    copilot: int = 0
    human: int = 0
    other_bot: int = 0
    human_with_overlap: int = 0
    human_unknown_coord: int = 0


def persist_pr_comments(
    conn: sqlite3.Connection,
    *,
    run_id: int,
    pr_id: int,
    pr: NormalizedPR,
    copilot_logins: Iterable[str],
    line_fuzz: int,
) -> AttributionSummary:
    """Classify, compute overlap, and upsert all comments for one PR.

    Returns an :class:`AttributionSummary`. Every persisted comment row gets a
    non-null ``author_kind``; ``copilot_overlap`` is set for human comments only
    (NULL when the human comment has no comparable line range).
    """
    copilot_set = list(copilot_logins)
    kinds: list[tuple[NormalizedComment, AuthorKind]] = [
        (c, classify_author(c.author_login, copilot_set)) for c in pr.comments
    ]
    copilot_ranges = [
        lr
        for c, kind in kinds
        if kind == "copilot" and not c.is_review_body and (lr := _to_line_range(c)) is not None
    ]

    summary = AttributionSummary()
    for comment, kind in kinds:
        overlap: bool | None = None
        if kind == "human":
            human_range = _to_line_range(comment)
            if human_range is None:
                summary.human_unknown_coord += 1
            else:
                overlap = overlaps(human_range, copilot_ranges, line_fuzz)
                if overlap:
                    summary.human_with_overlap += 1
        setattr(summary, kind, getattr(summary, kind) + 1)

        comment_id = db.upsert_comment(
            conn,
            run_id=run_id,
            pr_id=pr_id,
            source_key=comment.source_key,
            author_kind=kind,
            external_id=comment.external_id,
            author=comment.author_login,
            is_review_body=comment.is_review_body,
            file_path=comment.file_path,
            line_start=comment.line_start,
            line_end=comment.line_end,
            coord_space=comment.coord_space,
            body=comment.body,
            diff_hunk=comment.diff_hunk,
            created_at=comment.created_at,
            url=comment.url,
        )
        if kind == "human":
            db.set_comment_overlap(conn, comment_id, overlap)

    logger.info(
        "PR #%s attribution: copilot=%d human=%d other_bot=%d "
        "human_with_overlap=%d human_unknown_coord=%d",
        pr.meta.number,
        summary.copilot,
        summary.human,
        summary.other_bot,
        summary.human_with_overlap,
        summary.human_unknown_coord,
    )
    return summary
