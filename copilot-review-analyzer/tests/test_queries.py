"""Pure parser tests against recorded GraphQL fixtures (offline)."""

from __future__ import annotations

import json
from pathlib import Path

from analyzer.github import queries

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _pr_node(payload: dict) -> dict:
    return payload["data"]["repository"]["pullRequest"]


def test_parse_pr_metadata() -> None:
    pr = _pr_node(_load("pr_page1.json"))
    meta = queries.parse_pr_metadata(pr)
    assert meta.number == 42
    assert meta.author_login == "alice"
    assert meta.merged_at == "2024-05-03T12:00:00Z"
    assert meta.additions == 120


def test_thread_range_current_coordinates() -> None:
    pr = _pr_node(_load("pr_page1.json"))
    comments, skipped = queries.parse_review_threads(pr["reviewThreads"])
    # First thread: current line present -> coord_space current, start from startLine.
    first = next(c for c in comments if c.external_id == 1001)
    assert first.file_path == "src/uploader.py"
    assert (first.line_start, first.line_end) == (47, 50)
    assert first.coord_space == "current"
    # One reply was skipped (the second comment in that thread).
    assert skipped == 1


def test_thread_range_outdated_falls_back_to_original() -> None:
    pr = _pr_node(_load("pr_page1.json"))
    comments, _ = queries.parse_review_threads(pr["reviewThreads"])
    outdated = next(c for c in comments if c.external_id == 1003)
    # line is null -> original coordinates, no startLine -> start == end.
    assert outdated.coord_space == "original"
    assert (outdated.line_start, outdated.line_end) == (200, 200)


def test_review_point_is_first_comment_only() -> None:
    pr = _pr_node(_load("pr_page1.json"))
    comments, _ = queries.parse_review_threads(pr["reviewThreads"])
    # The reply (databaseId 1002) must not become a review point.
    assert all(c.external_id != 1002 for c in comments)


def test_deleted_author_does_not_crash() -> None:
    pr = _pr_node(_load("pr_page2.json"))
    comments, _ = queries.parse_review_threads(pr["reviewThreads"])
    c = next(c for c in comments if c.external_id == 1010)
    assert c.author_login is None
    assert c.source_key.startswith("thread:db:1010")


def test_parse_reviews_skips_empty_body() -> None:
    pr = _pr_node(_load("pr_page1.json"))
    reviews = queries.parse_reviews(pr["reviews"])
    # Only the non-empty review body is kept; the empty APPROVED is dropped.
    assert len(reviews) == 1
    assert reviews[0].external_id == 2001
    assert reviews[0].is_review_body is True
    assert reviews[0].line_start is None


def test_parse_commits() -> None:
    pr = _pr_node(_load("pr_page1.json"))
    commits = queries.parse_commits(pr["commits"])
    assert [c.oid for c in commits] == ["aaa111"]
    assert commits[0].changed_files == 3


def test_rate_limit_surfaced() -> None:
    payload = _load("pr_page1.json")
    rl = queries.parse_rate_limit(payload["data"])
    assert rl is not None
    assert rl.remaining == 4990 and rl.cost == 1


def test_page_info() -> None:
    pr = _pr_node(_load("pr_page1.json"))
    more, cursor = queries.page_info(pr["reviewThreads"])
    assert more is True and cursor == "THREADS_P1"


def test_graphql_errors_recorded() -> None:
    payload = {"data": {}, "errors": [{"message": "Something timed out"}]}
    warnings = queries.parse_graphql_errors(payload)
    assert warnings == ["Something timed out"]


def test_source_key_hash_fallback_when_no_database_id() -> None:
    thread = {
        "path": "a.py",
        "line": 5,
        "originalLine": 5,
        "startLine": None,
        "originalStartLine": None,
        "comments": {
            "pageInfo": {"hasNextPage": False, "endCursor": None},
            "nodes": [
                {
                    "databaseId": None,
                    "author": {"login": "x"},
                    "authorAssociation": "NONE",
                    "body": "b",
                    "createdAt": "2024-01-01T00:00:00Z",
                    "url": "u",
                    "diffHunk": "h",
                }
            ],
        },
    }
    comments, _ = queries.parse_review_threads({"nodes": [thread]})
    assert comments[0].source_key.startswith("thread:h:")
