"""LLM suggester: turn each missed issue (gap) into prompt-improvement guidance.

HTTP-free, mirroring :mod:`analyzer.llm.judge`: it depends only on a ``Completer``
callable so it is unit-testable with a mock. For every gap it produces a PR-specific
``missed_finding`` (what the Copilot reviewer should have flagged here) and a
generalizable ``prompt_improvement`` (a reusable review rule). Batches gaps, validates
the JSON response, performs one corrective retry for missing ids, and never crashes —
gaps it cannot suggest for are returned in ``unsuggested_ids``.
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


@dataclass(frozen=True)
class GapContext:
    """Context for one gap fed to the suggester."""

    gap_id: int
    comment_id: int
    pr_number: int | None
    category: str | None
    theme: str | None
    file_path: str | None
    line_start: int | None
    line_end: int | None
    diff_hunk: str | None
    body: str | None
    rationale: str | None


@dataclass(frozen=True)
class Suggestion:
    """A validated prompt-improvement suggestion for one gap."""

    gap_id: int
    comment_id: int
    missed_finding: str
    prompt_improvement: str


@dataclass
class SuggestResult:
    """Aggregate suggester output."""

    suggestions: dict[int, Suggestion]
    unsuggested_ids: set[int]
    retries: int = 0


def _truncate(text: str | None, limit: int = _MAX_FIELD_CHARS) -> str:
    if not text:
        return ""
    return text if len(text) <= limit else text[:limit] + "\n…[truncated]"


def _render_block(items: Iterable[GapContext]) -> str:
    return "\n".join(
        prompts.SUGGEST_ITEM_TEMPLATE.format(
            id=item.gap_id,
            category=item.category or "(none)",
            theme=item.theme or "(none)",
            file_path=item.file_path or "(none)",
            line_start=item.line_start if item.line_start is not None else "?",
            line_end=item.line_end if item.line_end is not None else "?",
            diff_hunk=_truncate(item.diff_hunk),
            body=_truncate(item.body),
            rationale=item.rationale or "(none)",
        )
        for item in items
    )


def _chunks(items: list[GapContext], size: int) -> Iterable[list[GapContext]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _validate_entry(entry: Any, by_id: dict[int, GapContext]) -> Suggestion | None:
    if not isinstance(entry, dict):
        return None
    gid = entry.get("id")
    if not isinstance(gid, int) or isinstance(gid, bool) or gid not in by_id:
        return None
    finding = entry.get("missed_finding")
    improvement = entry.get("prompt_improvement")
    if not isinstance(finding, str) or not isinstance(improvement, str):
        return None
    finding = finding.strip()
    improvement = improvement.strip()
    if not finding or not improvement:
        return None
    return Suggestion(
        gap_id=gid,
        comment_id=by_id[gid].comment_id,
        missed_finding=finding,
        prompt_improvement=improvement,
    )


def _parse_response(content: str, by_id: dict[int, GapContext]) -> dict[int, Suggestion]:
    try:
        data = json.loads(content)
    except (ValueError, TypeError):
        return {}
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        return {}
    out: dict[int, Suggestion] = {}
    for entry in results:
        suggestion = _validate_entry(entry, by_id)
        if suggestion is not None:
            out[suggestion.gap_id] = suggestion
    return out


def _suggest_batch(
    batch: list[GapContext], complete: Completer
) -> tuple[dict[int, Suggestion], int]:
    by_id = {g.gap_id: g for g in batch}
    user = prompts.SUGGEST_USER_TEMPLATE.format(gaps_block=_render_block(batch))
    retries = 0
    try:
        content = complete(prompts.SUGGEST_SYSTEM, user)
    except Exception as exc:  # noqa: BLE001 - LLM failure must not crash the run
        logger.warning("Suggest call failed: %s", exc)
        content = ""
    suggested = _parse_response(content, by_id)

    missing = set(by_id) - set(suggested)
    if missing:
        retries = 1
        missing_items = [g for g in batch if g.gap_id in missing]
        missing_by_id = {g.gap_id: g for g in missing_items}
        nudge = (
            "Your previous response was missing or invalid for these ids: "
            f"{sorted(missing)}. Return STRICT JSON with one result per id.\n\n"
            + prompts.SUGGEST_USER_TEMPLATE.format(gaps_block=_render_block(missing_items))
        )
        try:
            content = complete(prompts.SUGGEST_SYSTEM, nudge)
            suggested.update(_parse_response(content, missing_by_id))
        except Exception as exc:  # noqa: BLE001
            logger.warning("Suggest retry failed: %s", exc)
    return suggested, retries


def suggest_for_gaps(
    items: list[GapContext], *, complete: Completer, batch_size: int = 10
) -> SuggestResult:
    """Produce a suggestion for every gap, batching under the model context."""
    suggestions: dict[int, Suggestion] = {}
    total_retries = 0
    for batch in _chunks(items, max(1, batch_size)):
        batch_suggestions, retries = _suggest_batch(batch, complete)
        suggestions.update(batch_suggestions)
        total_retries += retries
    all_ids = {g.gap_id for g in items}
    unsuggested = all_ids - set(suggestions)
    return SuggestResult(
        suggestions=suggestions, unsuggested_ids=unsuggested, retries=total_retries
    )
