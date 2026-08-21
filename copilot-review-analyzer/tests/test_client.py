"""HTTP client tests with mocked transport (no live calls)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest

from analyzer.github.client import AuthError, GitHubClient, GitHubError

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _client(handler) -> GitHubClient:
    transport = httpx.MockTransport(handler)
    http = httpx.Client(transport=transport)
    return GitHubClient(token="t", client=http, sleep=lambda _s: None)


def test_fetch_pr_paginates_threads_and_commits() -> None:
    page1 = _load("pr_page1.json")
    page2 = _load("pr_page2.json")
    calls: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        calls.append(body["variables"])
        threads_after = body["variables"]["threadsAfter"]
        payload = page1 if threads_after is None else page2
        return httpx.Response(200, json=payload)

    with _client(handler) as client:
        pr = client.fetch_pr("octo", "example", 42)

    assert len(calls) == 2  # two pages fetched
    assert calls[1]["threadsAfter"] == "THREADS_P1"
    assert calls[1]["commitsAfter"] == "COMMITS_P1"
    # Comments: 2 thread review-points from page1 + 1 review body + 1 from page2.
    ext_ids = {c.external_id for c in pr.comments}
    assert {1001, 1003, 2001, 1010} <= ext_ids
    assert 1002 not in ext_ids  # reply not promoted
    assert {c.oid for c in pr.commits} == {"aaa111", "bbb222"}
    assert pr.skipped_replies == 1
    assert pr.rate_limit is not None


def test_auth_error_on_401() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "Bad credentials"})

    with _client(handler) as client:
        with pytest.raises(AuthError):
            client.fetch_pr("octo", "example", 42)


def test_retry_on_502_then_success() -> None:
    state = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        state["n"] += 1
        if state["n"] == 1:
            return httpx.Response(502, text="bad gateway")
        return httpx.Response(200, json=_load("pr_page2.json"))

    with _client(handler) as client:
        pr = client.fetch_pr("octo", "example", 42)
    assert state["n"] == 2
    assert pr.meta.number == 42


def test_secondary_rate_limit_retry_after_honored() -> None:
    state = {"n": 0}

    def handler(_request: httpx.Request) -> httpx.Response:
        state["n"] += 1
        if state["n"] == 1:
            return httpx.Response(
                403, headers={"Retry-After": "1"}, json={"message": "secondary rate limit"}
            )
        return httpx.Response(200, json=_load("pr_page2.json"))

    with _client(handler) as client:
        pr = client.fetch_pr("octo", "example", 42)
    assert state["n"] == 2
    assert pr.meta.number == 42


def test_graphql_http_error_raises() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, text="bad query")

    with _client(handler) as client:
        with pytest.raises(GitHubError):
            client.graphql("query{}", {})


def test_list_prs_filters_by_terminal_date_and_state() -> None:
    window_start = datetime(2024, 5, 1, tzinfo=timezone.utc)
    window_end = datetime(2024, 5, 10, tzinfo=timezone.utc)
    pulls = [
        # In-window merged.
        {
            "number": 42,
            "state": "closed",
            "merged_at": "2024-05-03T12:00:00Z",
            "closed_at": "2024-05-03T12:00:00Z",
            "updated_at": "2024-05-03T12:00:00Z",
        },
        # Closed-unmerged: excluded when state=merged.
        {
            "number": 43,
            "state": "closed",
            "merged_at": None,
            "closed_at": "2024-05-04T12:00:00Z",
            "updated_at": "2024-05-04T12:00:00Z",
        },
        # Merged before window: excluded and triggers stop (updated < window_start).
        {
            "number": 10,
            "state": "closed",
            "merged_at": "2024-04-01T12:00:00Z",
            "closed_at": "2024-04-01T12:00:00Z",
            "updated_at": "2024-04-01T12:00:00Z",
        },
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.params.get("page") == "1":
            return httpx.Response(200, json=pulls)
        return httpx.Response(200, json=[])

    with _client(handler) as client:
        refs = client.list_prs(
            "octo",
            "example",
            window_start=window_start,
            window_end=window_end,
            state="merged",
            max_prs=50,
        )
    assert [r.number for r in refs] == [42]


def test_list_prs_closed_state_excludes_merged() -> None:
    window_start = datetime(2024, 5, 1, tzinfo=timezone.utc)
    window_end = datetime(2024, 5, 10, tzinfo=timezone.utc)
    pulls = [
        {
            "number": 42,
            "state": "closed",
            "merged_at": "2024-05-03T12:00:00Z",
            "closed_at": "2024-05-03T12:00:00Z",
            "updated_at": "2024-05-03T12:00:00Z",
        },
        {
            "number": 43,
            "state": "closed",
            "merged_at": None,
            "closed_at": "2024-05-04T12:00:00Z",
            "updated_at": "2024-05-04T12:00:00Z",
        },
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.params.get("page") == "1":
            return httpx.Response(200, json=pulls)
        return httpx.Response(200, json=[])

    with _client(handler) as client:
        refs = client.list_prs(
            "octo",
            "example",
            window_start=window_start,
            window_end=window_end,
            state="closed",
            max_prs=50,
        )
    assert [r.number for r in refs] == [43]
