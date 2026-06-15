"""HTTP client for GitHub GraphQL/REST with auth, retry, throttling, pagination.

All GitHub I/O funnels through here so retry, secondary-rate-limit handling, and
testing are centralized. Network calls are mockable via ``pytest-httpx``/``respx``;
no live calls happen in unit tests.
"""

from __future__ import annotations

import logging
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

from analyzer.github import queries
from analyzer.github.queries import (
    NormalizedPR,
    RateLimit,
    parse_commits,
    parse_graphql_errors,
    parse_pr_metadata,
    parse_rate_limit,
    parse_review_threads,
    parse_reviews,
)

logger = logging.getLogger(__name__)

GRAPHQL_URL = "https://api.github.com/graphql"
REST_BASE = "https://api.github.com"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 4


class GitHubError(RuntimeError):
    """Base error for GitHub client failures."""


class AuthError(GitHubError):
    """Raised when authentication fails (HTTP 401)."""


def resolve_token(explicit: str | None = None) -> str:
    """Resolve a token from an explicit value, env vars, or ``gh auth token``."""
    if explicit:
        return explicit
    for var in ("GH_TOKEN", "GITHUB_TOKEN"):
        val = os.environ.get(var)
        if val:
            return val
    try:
        out = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        token = out.stdout.strip()
        if token:
            return token
    except (FileNotFoundError, subprocess.SubprocessError):  # pragma: no cover
        pass
    raise AuthError("No GitHub token found (set GH_TOKEN/GITHUB_TOKEN or run `gh auth login`)")


@dataclass(frozen=True)
class PRRef:
    """A candidate PR identified during enumeration."""

    number: int
    state: str  # open | closed
    merged_at: str | None
    closed_at: str | None
    updated_at: str | None


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class GitHubClient:
    """Thin GitHub client wrapping an ``httpx.Client``."""

    def __init__(
        self,
        token: str | None = None,
        *,
        client: httpx.Client | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        sleep: Any = time.sleep,
    ) -> None:
        self._token = resolve_token(token)
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout)
        self._max_retries = max_retries
        self._sleep = sleep
        self.last_rate_limit: RateLimit | None = None

    # ------------------------------------------------------------------ lifecycle

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> GitHubClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
        }

    # -------------------------------------------------------------------- request

    def _request_with_retry(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Issue a request, retrying transient 5xx and secondary rate limits."""
        attempt = 0
        while True:
            resp = self._client.request(method, url, headers=self._headers, **kwargs)
            if resp.status_code == 401:
                raise AuthError("GitHub authentication failed (HTTP 401)")
            if resp.status_code in (403, 429) and self._is_secondary_rate_limit(resp):
                wait = self._retry_after_seconds(resp)
                if attempt < self._max_retries:
                    logger.warning("Secondary rate limit; backing off %.1fs", wait)
                    self._sleep(wait)
                    attempt += 1
                    continue
            if resp.status_code >= 500 and attempt < self._max_retries:
                wait = 2.0**attempt
                logger.warning("HTTP %s on %s; retry in %.1fs", resp.status_code, url, wait)
                self._sleep(wait)
                attempt += 1
                continue
            return resp

    @staticmethod
    def _is_secondary_rate_limit(resp: httpx.Response) -> bool:
        if "Retry-After" in resp.headers:
            return True
        if resp.headers.get("x-ratelimit-remaining") == "0":
            return True
        try:
            body = resp.json()
        except (ValueError, httpx.DecodingError):
            return False
        msg = str(body.get("message", "")).lower() if isinstance(body, dict) else ""
        return "secondary rate limit" in msg or "rate limit" in msg

    @staticmethod
    def _retry_after_seconds(resp: httpx.Response) -> float:
        ra = resp.headers.get("Retry-After")
        if ra and ra.isdigit():
            return float(ra)
        reset = resp.headers.get("x-ratelimit-reset")
        if reset and reset.isdigit():
            delta = int(reset) - int(time.time())
            return float(max(1, delta))
        return 1.0

    # -------------------------------------------------------------------- graphql

    def graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        """POST a GraphQL query; return the full payload (``data`` + ``errors``)."""
        resp = self._request_with_retry(
            "POST", GRAPHQL_URL, json={"query": query, "variables": variables}
        )
        if resp.status_code >= 400:
            raise GitHubError(f"GraphQL HTTP {resp.status_code}: {resp.text[:200]}")
        payload = resp.json()
        if not isinstance(payload, dict):
            raise GitHubError("GraphQL response was not a JSON object")
        return payload

    # -------------------------------------------------------------- PR enumeration

    def list_prs(
        self,
        owner: str,
        name: str,
        *,
        window_start: datetime,
        window_end: datetime,
        state: str = "merged",
        max_prs: int = 50,
    ) -> list[PRRef]:
        """List PRs whose terminal date falls in ``[window_start, window_end)``.

        Inclusion is decided by ``merged_at``/``closed_at`` (not ``updated_at``, which
        edits/labels can move). Candidates are listed newest-updated first and we stop
        paging once results are older than the window.
        """
        results: list[PRRef] = []
        page = 1
        while len(results) < max_prs:
            resp = self._request_with_retry(
                "GET",
                f"{REST_BASE}/repos/{owner}/{name}/pulls",
                params={
                    "state": "closed" if state in ("merged", "closed") else "all",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": 100,
                    "page": page,
                },
            )
            if resp.status_code >= 400:
                raise GitHubError(f"REST list HTTP {resp.status_code}: {resp.text[:200]}")
            batch = resp.json()
            if not isinstance(batch, list) or not batch:
                break
            stop = False
            for pr in batch:
                ref = self._classify_pr(pr, state)
                if ref is None:
                    continue
                terminal = _parse_iso(ref.merged_at or ref.closed_at)
                if terminal is None:
                    continue
                if terminal < window_start:
                    # Sorted by updated desc; an in-window terminal date can still
                    # appear later, but updated>=terminal, so once updated passes the
                    # window we can stop. Guard on updated_at for the stop decision.
                    upd = _parse_iso(ref.updated_at)
                    if upd is not None and upd < window_start:
                        stop = True
                        break
                    continue
                if terminal >= window_end:
                    continue
                results.append(ref)
                if len(results) >= max_prs:
                    break
            if stop:
                break
            page += 1
        logger.info(
            "Enumerated %d PRs for %s/%s state=%s window=[%s,%s)",
            len(results),
            owner,
            name,
            state,
            window_start.isoformat(),
            window_end.isoformat(),
        )
        return results

    @staticmethod
    def _classify_pr(pr: dict[str, Any], state: str) -> PRRef | None:
        merged_at = pr.get("merged_at")
        closed_at = pr.get("closed_at")
        if state == "merged" and not merged_at:
            return None
        if state == "closed" and (merged_at or not closed_at):
            # "closed" means closed-unmerged.
            return None
        return PRRef(
            number=int(pr["number"]),
            state=pr.get("state", "closed"),
            merged_at=merged_at,
            closed_at=closed_at,
            updated_at=pr.get("updated_at"),
        )

    # ----------------------------------------------------------------- PR fetching

    def fetch_commit_files(self, owner: str, name: str, oid: str) -> set[str] | None:
        """Return the set of file paths changed by a commit, or ``None`` if unavailable.

        Used by the deterministic ``acted_on`` linkage. Returns ``None`` (not an empty
        set) on any error so callers can distinguish "no path data" from "no files".
        """
        try:
            resp = self._request_with_retry(
                "GET", f"{REST_BASE}/repos/{owner}/{name}/commits/{oid}"
            )
        except GitHubError:
            return None
        if resp.status_code >= 400:
            return None
        body = resp.json()
        files = body.get("files") if isinstance(body, dict) else None
        if not isinstance(files, list):
            return None
        paths: set[str] = set()
        for f in files:
            if isinstance(f, dict) and isinstance(f.get("filename"), str):
                paths.add(f["filename"])
        return paths

    def fetch_pr(self, owner: str, name: str, number: int) -> NormalizedPR:
        """Fetch and normalize a single PR, following thread/review/commit cursors."""
        comments = []
        commits = []
        warnings: list[str] = []
        skipped_replies = 0
        rate_limit: RateLimit | None = None

        threads_after: str | None = None
        reviews_after: str | None = None
        commits_after: str | None = None
        threads_more = True
        reviews_more = True
        commits_more = True
        meta = None

        while threads_more or reviews_more or commits_more:
            payload = self.graphql(
                queries.PR_REVIEW_DATA_QUERY,
                {
                    "owner": owner,
                    "name": name,
                    "number": number,
                    "threadsAfter": threads_after,
                    "reviewsAfter": reviews_after,
                    "commitsAfter": commits_after,
                },
            )
            warnings.extend(parse_graphql_errors(payload))
            rl = parse_rate_limit(payload.get("data") or {})
            if rl is not None:
                rate_limit = rl
                self.last_rate_limit = rl

            pr = ((payload.get("data") or {}).get("repository") or {}).get("pullRequest")
            if not isinstance(pr, dict):
                if meta is None:
                    raise GitHubError(f"PR {owner}/{name}#{number} not found or inaccessible")
                break

            if meta is None:
                meta = parse_pr_metadata(pr)

            if threads_more:
                tnode = pr.get("reviewThreads") or {}
                tc, sk = parse_review_threads(tnode)
                comments.extend(tc)
                skipped_replies += sk
                threads_more, threads_after = queries.page_info(tnode)
            if reviews_more:
                rnode = pr.get("reviews") or {}
                comments.extend(parse_reviews(rnode))
                reviews_more, reviews_after = queries.page_info(rnode)
            if commits_more:
                cnode = pr.get("commits") or {}
                commits.extend(parse_commits(cnode))
                commits_more, commits_after = queries.page_info(cnode)

        assert meta is not None
        logger.info(
            "PR #%s: threads/comments=%d commits=%d skipped_replies=%d rate=%s/%s",
            number,
            len(comments),
            len(commits),
            skipped_replies,
            rate_limit.remaining if rate_limit else "?",
            rate_limit.cost if rate_limit else "?",
        )
        return NormalizedPR(
            meta=meta,
            comments=comments,
            commits=commits,
            rate_limit=rate_limit,
            warnings=warnings,
            skipped_replies=skipped_replies,
        )


def utc_now() -> datetime:
    """Current UTC time (helper for window math/testing)."""
    return datetime.now(timezone.utc)
