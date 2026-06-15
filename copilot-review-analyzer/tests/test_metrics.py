"""Tests for per-run metrics, including divide-by-zero -> NULL."""

from __future__ import annotations

from pathlib import Path

from analyzer.pipeline import gaps, metrics
from analyzer.store import db


def _setup(tmp_path: Path):
    conn = db.connect(tmp_path / "a.db")
    db.init_db(conn)
    run_id = db.insert_run(
        conn,
        repo="o/n",
        started_at="t",
        window_start="a",
        window_end="b",
        pr_state="merged",
        model="m",
    )
    pr_id = db.upsert_pr(conn, run_id=run_id, number=1)
    return conn, run_id, pr_id


def _human(conn, run_id, pr_id, key, *, substantive, detectable, overlap, confidence=1.0):
    cid = db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key=key, author_kind="human")
    db.update_comment_judgement(
        conn,
        cid,
        is_substantive=substantive,
        diff_detectable=detectable,
        category=None,
        judge_rationale=None,
        judge_confidence=confidence,
    )
    db.set_comment_overlap(conn, cid, overlap)


def test_metrics_basic(tmp_path: Path) -> None:
    conn, run_id, pr_id = _setup(tmp_path)
    # 3 substantive+detectable human comments: 1 overlapped, 2 gaps.
    _human(conn, run_id, pr_id, "h1", substantive=True, detectable=True, overlap=False)
    _human(conn, run_id, pr_id, "h2", substantive=True, detectable=True, overlap=False)
    _human(conn, run_id, pr_id, "h3", substantive=True, detectable=True, overlap=True)
    # A copilot comment.
    db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key="c1", author_kind="copilot")
    gaps.detect_gaps(conn, run_id, confidence_threshold=0.5)
    out = metrics.compute_and_store(conn, run_id, pr_count=1, confidence_threshold=0.5)

    assert out["miss_rate"] == 2 / 3
    assert out["copilot_overlap_rate"] == 1 / 3
    assert out["human_burden_per_pr"] == 3.0
    assert out["copilot_acted_on_rate"] is None  # acted_on unpopulated

    row = conn.execute("SELECT * FROM metrics WHERE run_id=?", (run_id,)).fetchone()
    assert row["substantive_human_count"] == 3
    assert row["copilot_comment_count"] == 1
    assert row["gap_count"] == 2


def test_metrics_divide_by_zero_is_null(tmp_path: Path) -> None:
    conn, run_id, _ = _setup(tmp_path)
    out = metrics.compute_and_store(conn, run_id, pr_count=0, confidence_threshold=0.5)
    assert out["miss_rate"] is None
    assert out["copilot_overlap_rate"] is None
    assert out["human_burden_per_pr"] is None
    row = conn.execute("SELECT * FROM metrics WHERE run_id=?", (run_id,)).fetchone()
    assert row["substantive_human_count"] == 0
    assert row["gap_count"] == 0


def test_metrics_counts_unjudged_and_low_conf(tmp_path: Path) -> None:
    conn, run_id, pr_id = _setup(tmp_path)
    db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key="u", author_kind="human")
    _human(
        conn, run_id, pr_id, "low", substantive=True, detectable=True, overlap=False, confidence=0.1
    )
    metrics.compute_and_store(conn, run_id, pr_count=1, confidence_threshold=0.5)
    row = conn.execute("SELECT * FROM metrics WHERE run_id=?", (run_id,)).fetchone()
    assert row["unjudged_human_count"] == 1
    assert row["low_confidence_human_count"] == 1
    assert row["judged_human_count"] == 0


def test_metrics_copilot_acted_on_rate(tmp_path: Path) -> None:
    conn, run_id, pr_id = _setup(tmp_path)
    # 3 copilot comments: 1 acted-on, 1 not acted-on (both known), 1 unknown (NULL).
    c1 = db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key="c1", author_kind="copilot")
    c2 = db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key="c2", author_kind="copilot")
    db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key="c3", author_kind="copilot")
    db.set_comment_acted_on(conn, c1, True)
    db.set_comment_acted_on(conn, c2, False)
    out = metrics.compute_and_store(conn, run_id, pr_count=1, confidence_threshold=0.5)
    # Denominator is comments with KNOWN acted_on (2), numerator acted-on (1).
    assert out["copilot_acted_on_rate"] == 0.5


def test_metrics_acted_on_rate_null_when_all_unknown(tmp_path: Path) -> None:
    conn, run_id, pr_id = _setup(tmp_path)
    db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key="c1", author_kind="copilot")
    out = metrics.compute_and_store(conn, run_id, pr_count=1, confidence_threshold=0.5)
    assert out["copilot_acted_on_rate"] is None
