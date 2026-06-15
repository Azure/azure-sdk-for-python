"""Stage 4 — Theme tagging: map each gap into the controlled vocabulary.

A second LLM-assisted task, but all model I/O stays behind the ``Completer`` callable
so this module is HTTP-free and unit-testable. Each gap is assigned exactly one label
from ``config.vocab``; anything out-of-vocab (or a per-gap miss) coerces to ``other``.
If the model call fails entirely for every batch the run's themes are left unavailable
(no theme rows, ``gaps.theme_id`` NULL) without disturbing already-computed metrics.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from analyzer.config import Config
from analyzer.llm import prompts
from analyzer.llm.client import Completer

logger = logging.getLogger(__name__)

_MAX_BODY_CHARS = 1000
_GAP_ITEM_TEMPLATE = (
    "--- GAP id={id} ---\n"
    "Category: {category}\n"
    "File: {file_path}  Lines: {line_start}-{line_end}\n"
    'Comment:\n"""{body}"""\n'
)


@dataclass(frozen=True)
class GapItem:
    """A gap plus the human comment context used for theme assignment."""

    gap_id: int
    category: str | None
    file_path: str | None
    line_start: int | None
    line_end: int | None
    body: str | None


@dataclass(frozen=True)
class ThemeStats:
    """Outcome of theme tagging for a run."""

    available: bool
    gap_count: int
    histogram: dict[str, int]


def normalize_label(label: object, vocab: Sequence[str]) -> str:
    """Coerce a model label into the vocab; unknown/blank -> ``other``."""
    if isinstance(label, str):
        stripped = label.strip().lower()
        for term in vocab:
            if term.lower() == stripped:
                return term
    return "other"


def _truncate(text: str | None, limit: int = _MAX_BODY_CHARS) -> str:
    if not text:
        return ""
    return text if len(text) <= limit else text[:limit] + "\n…[truncated]"


def _render_block(items: Iterable[GapItem]) -> str:
    return "\n".join(
        _GAP_ITEM_TEMPLATE.format(
            id=item.gap_id,
            category=item.category or "(none)",
            file_path=item.file_path or "(none)",
            line_start=item.line_start if item.line_start is not None else "?",
            line_end=item.line_end if item.line_end is not None else "?",
            body=_truncate(item.body),
        )
        for item in items
    )


def _chunks(items: list[GapItem], size: int) -> Iterable[list[GapItem]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def _parse_results(content: str) -> dict[int, str]:
    try:
        data = json.loads(content)
    except (ValueError, TypeError):
        return {}
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list):
        return {}
    out: dict[int, str] = {}
    for entry in results:
        if not isinstance(entry, dict):
            continue
        gid = entry.get("id")
        theme = entry.get("theme")
        if isinstance(gid, int) and not isinstance(gid, bool) and isinstance(theme, str):
            out[gid] = theme
    return out


def assign_themes(
    items: list[GapItem], *, complete: Completer, vocab: Sequence[str], batch_size: int = 10
) -> tuple[dict[int, str], bool]:
    """Assign a vocab label to every gap.

    Returns ``(labels_by_gap_id, any_success)``. Every gap gets a label (missing/
    invalid → ``other``); ``any_success`` is ``False`` only if no batch produced any
    parseable result, signalling the run's themes should be marked unavailable.
    """
    vocab_str = ", ".join(vocab)
    labels: dict[int, str] = {}
    any_success = False
    for batch in _chunks(items, max(1, batch_size)):
        user = prompts.THEME_USER_TEMPLATE.format(vocab=vocab_str, gaps_block=_render_block(batch))
        try:
            content = complete(prompts.THEME_SYSTEM, user)
        except Exception as exc:  # noqa: BLE001 - theme failure must not crash the run
            logger.warning("Theme call failed: %s", exc)
            content = ""
        raw = _parse_results(content)
        if raw:
            any_success = True
        for item in batch:
            labels[item.gap_id] = normalize_label(raw.get(item.gap_id), vocab)
    return labels, any_success


def _load_gaps(conn: sqlite3.Connection, run_id: int) -> list[GapItem]:
    rows = conn.execute(
        """
        SELECT g.id, g.category, c.file_path, c.line_start, c.line_end, c.body
        FROM gaps g
        JOIN comments c ON c.id = g.comment_id
        WHERE g.run_id = ?
        """,
        (run_id,),
    ).fetchall()
    return [
        GapItem(
            gap_id=int(r[0]),
            category=r[1],
            file_path=r[2],
            line_start=r[3],
            line_end=r[4],
            body=r[5],
        )
        for r in rows
    ]


def tag_run(
    conn: sqlite3.Connection, run_id: int, config: Config, *, complete: Completer
) -> ThemeStats:
    """Tag every gap in ``run_id`` with a theme and persist themes + links."""
    from analyzer.store import db

    gaps = _load_gaps(conn, run_id)
    if not gaps:
        return ThemeStats(available=True, gap_count=0, histogram={})

    labels, any_success = assign_themes(
        gaps, complete=complete, vocab=config.vocab, batch_size=config.judge_batch_size
    )
    if not any_success:
        logger.warning("Run %s themes unavailable (all theme batches failed)", run_id)
        return ThemeStats(available=False, gap_count=len(gaps), histogram={})

    histogram = Counter(labels.values())
    theme_ids: dict[str, int] = {
        label: db.upsert_theme(conn, run_id=run_id, label=label, gap_count=count)
        for label, count in histogram.items()
    }
    for gap in gaps:
        db.set_gap_theme(conn, gap.gap_id, theme_ids[labels[gap.gap_id]])

    logger.info("Run %s theme histogram: %s", run_id, dict(histogram))
    return ThemeStats(available=True, gap_count=len(gaps), histogram=dict(histogram))
