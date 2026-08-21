"""Integration test: persist_pr_comments writes attribution onto comment rows."""

from __future__ import annotations

from pathlib import Path

from analyzer.github.queries import NormalizedComment, NormalizedPR, PRMeta
from analyzer.pipeline.attribute import persist_pr_comments
from analyzer.store import db

COPILOT = ["copilot-pull-request-reviewer"]


def _comment(**kw) -> NormalizedComment:
    base = dict(
        source_key="k",
        external_id=None,
        author_login="alice",
        author_association="MEMBER",
        body="b",
        created_at="2024-01-01T00:00:00Z",
        url="u",
        diff_hunk="h",
        file_path="a.py",
        line_start=10,
        line_end=12,
        coord_space="current",
        is_review_body=False,
    )
    base.update(kw)
    return NormalizedComment(**base)  # type: ignore[arg-type]


def _pr(comments) -> NormalizedPR:
    meta = PRMeta(
        number=1,
        title="t",
        state="MERGED",
        url="u",
        created_at="2024-01-01T00:00:00Z",
        merged_at="2024-01-02T00:00:00Z",
        closed_at="2024-01-02T00:00:00Z",
        additions=1,
        deletions=0,
        author_login="alice",
    )
    return NormalizedPR(meta=meta, comments=comments)


def test_persist_sets_author_kind_and_overlap(tmp_path: Path) -> None:
    conn = db.connect(tmp_path / "a.db")
    db.init_db(conn)
    run_id = db.insert_run(
        conn,
        repo="o/n",
        started_at="2024-01-01T00:00:00Z",
        window_start="2023-12-25T00:00:00Z",
        window_end="2024-01-01T00:00:00Z",
        pr_state="merged",
        model="m",
    )
    pr_id = db.upsert_pr(conn, run_id=run_id, number=1)

    comments = [
        # Copilot comment overlapping the human comment below.
        _comment(
            source_key="c1",
            author_login="copilot-pull-request-reviewer",
            line_start=10,
            line_end=12,
        ),
        # Human comment overlapped by Copilot -> overlap True.
        _comment(source_key="h1", author_login="alice", line_start=11, line_end=13),
        # Human comment on a different file -> overlap False.
        _comment(
            source_key="h2",
            author_login="alice",
            file_path="other.py",
            line_start=100,
            line_end=101,
        ),
        # Human review body (no range) -> overlap NULL.
        _comment(
            source_key="h3",
            author_login="bob",
            is_review_body=True,
            file_path=None,
            line_start=None,
            line_end=None,
            coord_space=None,
        ),
        # Other bot.
        _comment(source_key="b1", author_login="dependabot[bot]"),
    ]
    summary = persist_pr_comments(
        conn,
        run_id=run_id,
        pr_id=pr_id,
        pr=_pr(comments),
        copilot_logins=COPILOT,
        line_fuzz=2,
    )

    assert summary.copilot == 1
    assert summary.human == 3
    assert summary.other_bot == 1
    assert summary.human_with_overlap == 1
    assert summary.human_unknown_coord == 1

    rows = {
        r["source_key"]: r
        for r in conn.execute("SELECT source_key, author_kind, copilot_overlap FROM comments")
    }
    assert all(rows[k]["author_kind"] is not None for k in rows)
    assert rows["c1"]["author_kind"] == "copilot"
    assert rows["h1"]["author_kind"] == "human" and rows["h1"]["copilot_overlap"] == 1
    assert rows["h2"]["copilot_overlap"] == 0
    assert rows["h3"]["copilot_overlap"] is None  # undeterminable
    assert rows["b1"]["author_kind"] == "other_bot"
