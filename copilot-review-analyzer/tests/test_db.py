"""Tests for the SQLite storage layer."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from analyzer.store import db


def _new_db(tmp_path: Path) -> sqlite3.Connection:
    conn = db.connect(tmp_path / "a.db")
    db.init_db(conn)
    return conn


def _seed_run(conn: sqlite3.Connection) -> int:
    return db.insert_run(
        conn,
        repo="o/n",
        started_at="2024-01-01T00:00:00Z",
        window_start="2023-12-25T00:00:00Z",
        window_end="2024-01-01T00:00:00Z",
        pr_state="merged",
        model="gpt-4o",
        config_hash="abc",
    )


def test_init_db_sets_user_version(tmp_path: Path) -> None:
    conn = _new_db(tmp_path)
    assert db.schema_version(conn) == db.SCHEMA_VERSION


def test_init_db_idempotent(tmp_path: Path) -> None:
    conn = _new_db(tmp_path)
    run_id = _seed_run(conn)
    db.init_db(conn)  # re-init must not drop data
    assert conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0] == 1
    assert run_id == 1


def test_all_tables_exist(tmp_path: Path) -> None:
    conn = _new_db(tmp_path)
    names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"runs", "prs", "comments", "themes", "gaps", "metrics"} <= names


def test_missing_directory_errors(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        db.connect(tmp_path / "nope" / "a.db")


def test_foreign_keys_enforced(tmp_path: Path) -> None:
    conn = _new_db(tmp_path)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO prs (run_id, number) VALUES (999, 1)")


def test_fk_cascade(tmp_path: Path) -> None:
    conn = _new_db(tmp_path)
    run_id = _seed_run(conn)
    pr_id = db.upsert_pr(conn, run_id=run_id, number=1)
    cid = db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key="k1", author_kind="human")
    db.upsert_gap(conn, run_id=run_id, pr_id=pr_id, comment_id=cid)
    db.upsert_metrics(conn, run_id, gap_count=1)
    conn.execute("DELETE FROM runs WHERE id = ?", (run_id,))
    conn.commit()
    for table in ("prs", "comments", "gaps", "metrics"):
        assert conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0


def test_upsert_comment_updates_on_conflict(tmp_path: Path) -> None:
    conn = _new_db(tmp_path)
    run_id = _seed_run(conn)
    pr_id = db.upsert_pr(conn, run_id=run_id, number=1)
    c1 = db.upsert_comment(
        conn, run_id=run_id, pr_id=pr_id, source_key="k", author_kind="human", body="v1"
    )
    c2 = db.upsert_comment(
        conn, run_id=run_id, pr_id=pr_id, source_key="k", author_kind="human", body="v2"
    )
    assert c1 == c2  # same row
    assert conn.execute("SELECT COUNT(*) FROM comments").fetchone()[0] == 1
    assert conn.execute("SELECT body FROM comments WHERE id=?", (c1,)).fetchone()[0] == "v2"


def test_null_external_id_does_not_duplicate(tmp_path: Path) -> None:
    conn = _new_db(tmp_path)
    run_id = _seed_run(conn)
    pr_id = db.upsert_pr(conn, run_id=run_id, number=1)
    # Two comments with NULL external_id but distinct source_keys -> two rows.
    db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key="a", author_kind="human")
    db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key="b", author_kind="human")
    # Same source_key again -> still two rows (dedup by source_key, not external_id).
    db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key="a", author_kind="human")
    assert conn.execute("SELECT COUNT(*) FROM comments").fetchone()[0] == 2


def test_gaps_unique_on_run_comment(tmp_path: Path) -> None:
    conn = _new_db(tmp_path)
    run_id = _seed_run(conn)
    pr_id = db.upsert_pr(conn, run_id=run_id, number=1)
    cid = db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key="k", author_kind="human")
    g1 = db.upsert_gap(conn, run_id=run_id, pr_id=pr_id, comment_id=cid, category="bug")
    g2 = db.upsert_gap(conn, run_id=run_id, pr_id=pr_id, comment_id=cid, category="perf")
    assert g1 == g2
    assert conn.execute("SELECT COUNT(*) FROM gaps").fetchone()[0] == 1
    assert conn.execute("SELECT category FROM gaps WHERE id=?", (g1,)).fetchone()[0] == "perf"


def test_finish_run_and_latest_completed(tmp_path: Path) -> None:
    conn = _new_db(tmp_path)
    r1 = _seed_run(conn)
    db.finish_run(conn, r1, status="failed", finished_at="2024-01-01T01:00:00Z")
    assert db.latest_completed_run(conn) is None
    r2 = _seed_run(conn)
    db.finish_run(conn, r2, status="completed", finished_at="2024-01-02T01:00:00Z", pr_count=3)
    row = db.latest_completed_run(conn)
    assert row is not None and row["id"] == r2 and row["pr_count"] == 3


def test_upsert_metrics_idempotent(tmp_path: Path) -> None:
    conn = _new_db(tmp_path)
    run_id = _seed_run(conn)
    db.upsert_metrics(conn, run_id, gap_count=1, miss_rate=0.5)
    db.upsert_metrics(conn, run_id, gap_count=2, miss_rate=0.25)
    assert conn.execute("SELECT COUNT(*) FROM metrics").fetchone()[0] == 1
    row = conn.execute("SELECT gap_count, miss_rate FROM metrics").fetchone()
    assert row["gap_count"] == 2 and row["miss_rate"] == 0.25
