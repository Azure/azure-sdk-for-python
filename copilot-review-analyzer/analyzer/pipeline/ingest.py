"""Stage 1 — Ingest: enumerate PRs in a window and fetch normalized PR data.

This module holds the deterministic window math and the GitHub fetch orchestration
for a single repo. Persistence to SQLite is layered on in later phases; the Phase-2
deliverable is the normalized ``--dry-run`` dump.
"""

from __future__ import annotations

import logging
import re
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Any

from analyzer.github.client import GitHubClient, GitHubError
from analyzer.github.queries import NormalizedPR

logger = logging.getLogger(__name__)

_SINCE_RE = re.compile(r"^\s*(\d+)\s*([smhdw])\s*$", re.IGNORECASE)
_UNIT_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


def parse_since(value: str) -> timedelta:
    """Parse a duration like ``7d``, ``24h``, ``2w`` into a ``timedelta``."""
    m = _SINCE_RE.match(value)
    if not m:
        raise ValueError(f"Invalid --since value '{value}'; use e.g. 7d, 24h, 2w")
    amount, unit = int(m.group(1)), m.group(2).lower()
    if amount <= 0:
        raise ValueError("--since must be a positive duration")
    return timedelta(seconds=amount * _UNIT_SECONDS[unit])


def compute_window(since: str, now: datetime | None = None) -> tuple[datetime, datetime]:
    """Return ``[window_start, window_end)`` in UTC for a ``--since`` duration."""
    end = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    start = end - parse_since(since)
    return start, end


def split_repo(repo: str) -> tuple[str, str]:
    """Split ``owner/name`` into a tuple, validating shape."""
    if repo.count("/") != 1:
        raise ValueError(f"Invalid repo '{repo}'; expected 'owner/name'")
    owner, name = repo.split("/", 1)
    if not owner or not name:
        raise ValueError(f"Invalid repo '{repo}'; expected 'owner/name'")
    return owner, name


def fetch_window(
    client: GitHubClient,
    repo: str,
    *,
    window_start: datetime,
    window_end: datetime,
    state: str,
    max_prs: int,
    skip_errors: bool = True,
) -> list[NormalizedPR]:
    """Enumerate candidate PRs in the window and fetch each normalized PR.

    A single PR whose detail query keeps failing (e.g. a persistent server-side
    GraphQL 502) must not sink the whole run. When ``skip_errors`` is true such PRs
    are logged and skipped after the client's own retries are exhausted; set it false
    to surface the first error instead.
    """
    owner, name = split_repo(repo)
    refs = client.list_prs(
        owner,
        name,
        window_start=window_start,
        window_end=window_end,
        state=state,
        max_prs=max_prs,
    )
    prs: list[NormalizedPR] = []
    skipped: list[int] = []
    for ref in refs:
        try:
            prs.append(client.fetch_pr(owner, name, ref.number))
        except GitHubError as exc:
            if not skip_errors:
                raise
            skipped.append(ref.number)
            logger.warning("Skipping PR #%d after fetch failure: %s", ref.number, exc)
    if skipped:
        logger.warning("Skipped %d/%d PR(s): %s", len(skipped), len(refs), skipped)
    return prs


def normalized_pr_to_dict(pr: NormalizedPR) -> dict[str, Any]:
    """Serialize a :class:`NormalizedPR` to a JSON-friendly dict (for ``--dry-run``)."""
    return {
        "meta": asdict(pr.meta),
        "comments": [asdict(c) for c in pr.comments],
        "commits": [asdict(c) for c in pr.commits],
        "rate_limit": asdict(pr.rate_limit) if pr.rate_limit else None,
        "warnings": list(pr.warnings),
        "skipped_replies": pr.skipped_replies,
    }
