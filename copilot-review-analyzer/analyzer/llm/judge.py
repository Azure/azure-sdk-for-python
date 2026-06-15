"""LLM judge: classify human review comments as substantive / diff_detectable.

This module is HTTP-free: it depends only on a :data:`Completer` callable so it can
be unit-tested with a mock. It batches comments, validates the JSON response against
a strict schema, performs exactly one corrective retry on malformed/missing output,
and never crashes the run — unparseable comments are returned as ``unjudged``.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from analyzer.llm import prompts
from analyzer.llm.client import Completer

logger = logging.getLogger(__name__)

_MAX_FIELD_CHARS = 2000
_VALID_CATEGORIES = {
    "bug",
    "security",
    "perf",
    "design",
    "test-gap",
    "docs",
    "nit",
    "style",
    "question",
    "social",
}
_SUBSTANTIVE_CATEGORIES = {"bug", "security", "perf", "design", "test-gap"}


@dataclass(frozen=True)
class CommentItem:
    """Input to the judge for a single comment."""

    id: int
    file_path: str | None
    line_start: int | None
    line_end: int | None
    diff_hunk: str | None
    body: str | None


@dataclass(frozen=True)
class Judgement:
    """A validated judge result for one comment."""

    id: int
    is_substantive: bool
    diff_detectable: bool
    category: str
    rationale: str
    confidence: float


@dataclass
class JudgeResult:
    """Aggregate judge output for a set of comments."""

    judgements: dict[int, Judgement]
    unjudged_ids: set[int]
    retries: int = 0


def _truncate(text: str | None, limit: int = _MAX_FIELD_CHARS) -> str:
    if not text:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n…[truncated]"


def _render_block(items: Iterable[CommentItem]) -> str:
    return "\n".join(
        prompts.COMMENT_ITEM_TEMPLATE.format(
            id=item.id,
            file_path=item.file_path or "(none)",
            line_start=item.line_start if item.line_start is not None else "?",
            line_end=item.line_end if item.line_end is not None else "?",
            diff_hunk=_truncate(item.diff_hunk),
            body=_truncate(item.body),
        )
        for item in items
    )


def _chunks(items: list[CommentItem], size: int) -> Iterable[list[CommentItem]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _validate_entry(entry: Any, valid_ids: set[int]) -> Judgement | None:
    if not isinstance(entry, dict):
        return None
    raw_id = entry.get("id")
    if not isinstance(raw_id, int) or isinstance(raw_id, bool) or raw_id not in valid_ids:
        return None
    category = entry.get("category")
    if category not in _VALID_CATEGORIES:
        category = "nit"
    is_substantive = entry.get("is_substantive")
    diff_detectable = entry.get("diff_detectable")
    confidence = entry.get("confidence")
    if not isinstance(is_substantive, bool) or not isinstance(diff_detectable, bool):
        return None
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        return None
    conf = max(0.0, min(1.0, float(confidence)))
    rationale = entry.get("rationale")
    return Judgement(
        id=raw_id,
        is_substantive=is_substantive,
        diff_detectable=diff_detectable,
        category=category,
        rationale=str(rationale) if rationale is not None else "",
        confidence=conf,
    )


def _parse_response(content: str, valid_ids: set[int]) -> dict[int, Judgement]:
    """Parse a model response into validated judgements keyed by id."""
    try:
        data = json.loads(content)
    except (ValueError, TypeError):
        return {}
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        return {}
    out: dict[int, Judgement] = {}
    for entry in results:
        judgement = _validate_entry(entry, valid_ids)
        if judgement is not None:
            out[judgement.id] = judgement
    return out


def _judge_batch(batch: list[CommentItem], complete: Completer) -> tuple[dict[int, Judgement], int]:
    """Judge one batch, with a single corrective retry for missing ids."""
    valid_ids = {item.id for item in batch}
    user = prompts.JUDGE_USER_TEMPLATE.format(comments_block=_render_block(batch))
    retries = 0
    try:
        content = complete(prompts.JUDGE_SYSTEM, user)
    except Exception as exc:  # noqa: BLE001 - LLM failure must not crash the run
        logger.warning("Judge call failed: %s", exc)
        content = ""
    judged = _parse_response(content, valid_ids)

    missing = valid_ids - set(judged)
    if missing:
        retries = 1
        missing_items = [item for item in batch if item.id in missing]
        nudge = (
            "Your previous response was missing or invalid for these ids: "
            f"{sorted(missing)}. Return STRICT JSON with one result per id.\n\n"
            + prompts.JUDGE_USER_TEMPLATE.format(comments_block=_render_block(missing_items))
        )
        try:
            content = complete(prompts.JUDGE_SYSTEM, nudge)
            judged.update(_parse_response(content, missing))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Judge retry failed: %s", exc)
    return judged, retries


def judge_comments(
    items: list[CommentItem], *, complete: Completer, batch_size: int = 10
) -> JudgeResult:
    """Judge all comments, batching and chunking under the model context.

    Comments that cannot be parsed even after the corrective retry are returned in
    ``unjudged_ids`` (the caller records them with NULL confidence).
    """
    judgements: dict[int, Judgement] = {}
    total_retries = 0
    for batch in _chunks(items, max(1, batch_size)):
        judged, retries = _judge_batch(batch, complete)
        judgements.update(judged)
        total_retries += retries
    all_ids = {item.id for item in items}
    unjudged = all_ids - set(judgements)
    return JudgeResult(judgements=judgements, unjudged_ids=unjudged, retries=total_retries)
