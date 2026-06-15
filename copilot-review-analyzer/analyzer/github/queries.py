"""GraphQL query strings and pure response parsers.

Parsers are deliberately pure and side-effect free so they can be tested offline
against recorded fixtures. They translate the GitHub GraphQL response shape into
normalized dataclasses consumed by the rest of the pipeline.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any

PR_REVIEW_DATA_QUERY = """
query PRReviewData(
  $owner: String!
  $name: String!
  $number: Int!
  $threadsAfter: String
  $reviewsAfter: String
  $commitsAfter: String
) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      number
      title
      state
      url
      createdAt
      mergedAt
      closedAt
      additions
      deletions
      author { login }

      reviewThreads(first: 50, after: $threadsAfter) {
        pageInfo { hasNextPage endCursor }
        nodes {
          isResolved
          isOutdated
          path
          line
          originalLine
          startLine
          originalStartLine
          comments(first: 50) {
            pageInfo { hasNextPage endCursor }
            nodes {
              databaseId
              author { login }
              authorAssociation
              body
              createdAt
              url
              diffHunk
            }
          }
        }
      }

      reviews(first: 50, after: $reviewsAfter) {
        pageInfo { hasNextPage endCursor }
        nodes {
          databaseId
          author { login }
          state
          body
          submittedAt
          url
        }
      }

      commits(first: 100, after: $commitsAfter) {
        pageInfo { hasNextPage endCursor }
        nodes {
          commit {
            oid
            committedDate
            changedFilesIfAvailable
          }
        }
      }
    }
  }
  rateLimit { remaining resetAt cost }
}
"""


@dataclass(frozen=True)
class RateLimit:
    """GraphQL rate-limit snapshot from a response."""

    remaining: int | None = None
    reset_at: str | None = None
    cost: int | None = None


@dataclass(frozen=True)
class NormalizedComment:
    """A normalized review comment (review point) or review body."""

    source_key: str
    external_id: int | None
    author_login: str | None
    author_association: str | None
    body: str | None
    created_at: str | None
    url: str | None
    diff_hunk: str | None
    file_path: str | None
    line_start: int | None
    line_end: int | None
    coord_space: str | None  # current | original | None (review body)
    is_review_body: bool


@dataclass(frozen=True)
class NormalizedCommit:
    """A normalized commit from the PR timeline."""

    oid: str
    committed_date: str | None
    changed_files: int | None


@dataclass(frozen=True)
class PRMeta:
    """Normalized PR metadata."""

    number: int
    title: str | None
    state: str | None
    url: str | None
    created_at: str | None
    merged_at: str | None
    closed_at: str | None
    additions: int | None
    deletions: int | None
    author_login: str | None


@dataclass(frozen=True)
class NormalizedPR:
    """A fully normalized PR with comments and commits."""

    meta: PRMeta
    comments: list[NormalizedComment] = field(default_factory=list)
    commits: list[NormalizedCommit] = field(default_factory=list)
    rate_limit: RateLimit | None = None
    warnings: list[str] = field(default_factory=list)
    skipped_replies: int = 0


def _login(author: Any) -> str | None:
    if not isinstance(author, dict):
        return None
    login = author.get("login")
    return login if isinstance(login, str) else None


def parse_rate_limit(data: dict[str, Any]) -> RateLimit | None:
    """Parse the top-level ``rateLimit`` block if present."""
    rl = data.get("rateLimit")
    if not isinstance(rl, dict):
        return None
    return RateLimit(
        remaining=rl.get("remaining"),
        reset_at=rl.get("resetAt"),
        cost=rl.get("cost"),
    )


def parse_graphql_errors(payload: dict[str, Any]) -> list[str]:
    """Return human-readable warning strings for any GraphQL ``errors``."""
    errors = payload.get("errors")
    if not isinstance(errors, list):
        return []
    out: list[str] = []
    for err in errors:
        if isinstance(err, dict):
            msg = err.get("message")
            out.append(str(msg) if msg else str(err))
        else:
            out.append(str(err))
    return out


def parse_pr_metadata(pr: dict[str, Any]) -> PRMeta:
    """Parse the PR metadata fields from a ``pullRequest`` node."""
    return PRMeta(
        number=int(pr["number"]),
        title=pr.get("title"),
        state=pr.get("state"),
        url=pr.get("url"),
        created_at=pr.get("createdAt"),
        merged_at=pr.get("mergedAt"),
        closed_at=pr.get("closedAt"),
        additions=pr.get("additions"),
        deletions=pr.get("deletions"),
        author_login=_login(pr.get("author")),
    )


def _thread_range(
    thread: dict[str, Any],
) -> tuple[int | None, int | None, str | None]:
    """Resolve a thread's line range with the current/original fallback rules.

    Returns ``(line_start, line_end, coord_space)``. ``coord_space`` is ``"current"``
    when the current ``line`` is available, otherwise ``"original"`` (outdated thread),
    or ``None`` when no coordinate is available at all.
    """
    line = thread.get("line")
    original_line = thread.get("originalLine")
    start_line = thread.get("startLine")
    original_start_line = thread.get("originalStartLine")

    if line is not None:
        coord_space: str | None = "current"
        end = line
        start = start_line if start_line is not None else line
    elif original_line is not None:
        coord_space = "original"
        end = original_line
        start = original_start_line if original_start_line is not None else original_line
    else:
        return None, None, None
    return int(start), int(end), coord_space


def _source_key_for(
    external_id: int | None,
    *,
    kind: str,
    path: str | None,
    line_end: int | None,
    created_at: str | None,
    author: str | None,
    url: str | None,
) -> str:
    """Stable dedup key; prefer GitHub databaseId, else hash of stable fields."""
    if external_id is not None:
        return f"{kind}:db:{external_id}"
    raw = "|".join(str(x) for x in (kind, path, line_end, created_at, author, url))
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
    return f"{kind}:h:{digest}"


def parse_review_threads(
    threads_node: dict[str, Any],
) -> tuple[list[NormalizedComment], int]:
    """Parse review threads into review-point comments.

    The thread's **first** comment is the review point; replies are conversation and
    are skipped (counted, not lost). Returns ``(comments, skipped_reply_count)``.
    """
    comments: list[NormalizedComment] = []
    skipped_replies = 0
    nodes = (threads_node or {}).get("nodes") or []
    for thread in nodes:
        if not isinstance(thread, dict):
            continue
        path = thread.get("path")
        line_start, line_end, coord_space = _thread_range(thread)
        thread_comments = ((thread.get("comments") or {}).get("nodes")) or []
        if not thread_comments:
            continue
        first = thread_comments[0]
        skipped_replies += max(0, len(thread_comments) - 1)
        if not isinstance(first, dict):
            continue
        external_id = first.get("databaseId")
        author = _login(first.get("author"))
        comments.append(
            NormalizedComment(
                source_key=_source_key_for(
                    external_id,
                    kind="thread",
                    path=path,
                    line_end=line_end,
                    created_at=first.get("createdAt"),
                    author=author,
                    url=first.get("url"),
                ),
                external_id=external_id,
                author_login=author,
                author_association=first.get("authorAssociation"),
                body=first.get("body"),
                created_at=first.get("createdAt"),
                url=first.get("url"),
                diff_hunk=first.get("diffHunk"),
                file_path=path,
                line_start=line_start,
                line_end=line_end,
                coord_space=coord_space,
                is_review_body=False,
            )
        )
    return comments, skipped_replies


def parse_reviews(reviews_node: dict[str, Any]) -> list[NormalizedComment]:
    """Parse top-level reviews into review-body comments (no line range).

    Reviews with an empty body (e.g. a bare APPROVED with no summary) are skipped.
    """
    out: list[NormalizedComment] = []
    nodes = (reviews_node or {}).get("nodes") or []
    for review in nodes:
        if not isinstance(review, dict):
            continue
        body = review.get("body")
        if not body or not str(body).strip():
            continue
        external_id = review.get("databaseId")
        author = _login(review.get("author"))
        out.append(
            NormalizedComment(
                source_key=_source_key_for(
                    external_id,
                    kind="review",
                    path=None,
                    line_end=None,
                    created_at=review.get("submittedAt"),
                    author=author,
                    url=review.get("url"),
                ),
                external_id=external_id,
                author_login=author,
                author_association=None,
                body=body,
                created_at=review.get("submittedAt"),
                url=review.get("url"),
                diff_hunk=None,
                file_path=None,
                line_start=None,
                line_end=None,
                coord_space=None,
                is_review_body=True,
            )
        )
    return out


def parse_commits(commits_node: dict[str, Any]) -> list[NormalizedCommit]:
    """Parse the commit timeline into normalized commits."""
    out: list[NormalizedCommit] = []
    nodes = (commits_node or {}).get("nodes") or []
    for entry in nodes:
        commit = (entry or {}).get("commit") if isinstance(entry, dict) else None
        if not isinstance(commit, dict):
            continue
        oid = commit.get("oid")
        if not oid:
            continue
        out.append(
            NormalizedCommit(
                oid=str(oid),
                committed_date=commit.get("committedDate"),
                changed_files=commit.get("changedFilesIfAvailable"),
            )
        )
    return out


def page_info(node: dict[str, Any]) -> tuple[bool, str | None]:
    """Return ``(has_next_page, end_cursor)`` for a connection node."""
    pi = (node or {}).get("pageInfo") or {}
    return bool(pi.get("hasNextPage")), pi.get("endCursor")
