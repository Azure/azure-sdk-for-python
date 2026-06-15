"""Tests for gap detection."""

from __future__ import annotations

from pathlib import Path

from analyzer.pipeline.gaps import detect_gaps, is_gap
from analyzer.store import db


def test_is_gap_pure() -> None:
    assert is_gap(True, True, False) is True
    assert is_gap(True, True, None) is True  # undeterminable overlap -> still a gap
    assert is_gap(True, True, True) is False  # overlapped by Copilot
    assert is_gap(False, True, False) is False  # not substantive
    assert is_gap(True, False, False) is False  # not diff-detectable


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


def _human(conn, run_id, pr_id, key, *, substantive, detectable, overlap, confidence):
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
    return cid


def test_detect_gaps_overlap_vs_no_overlap(tmp_path: Path) -> None:
    conn, run_id, pr_id = _setup(tmp_path)
    _human(
        conn, run_id, pr_id, "gap", substantive=True, detectable=True, overlap=False, confidence=1.0
    )
    _human(
        conn,
        run_id,
        pr_id,
        "overlapped",
        substantive=True,
        detectable=True,
        overlap=True,
        confidence=1.0,
    )
    summary = detect_gaps(conn, run_id, confidence_threshold=0.5)
    assert summary.gap_count == 1
    assert summary.judged_human_count == 2
    assert conn.execute("SELECT COUNT(*) FROM gaps").fetchone()[0] == 1


def test_detect_gaps_unjudged_and_low_confidence(tmp_path: Path) -> None:
    conn, run_id, pr_id = _setup(tmp_path)
    # Unjudged (NULL confidence).
    db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key="u", author_kind="human")
    # Low confidence -> excluded.
    _human(
        conn, run_id, pr_id, "low", substantive=True, detectable=True, overlap=False, confidence=0.2
    )
    summary = detect_gaps(conn, run_id, confidence_threshold=0.5)
    assert summary.gap_count == 0
    assert summary.unjudged_human_count == 1
    assert summary.low_confidence_human_count == 1
    assert summary.judged_human_count == 0


def test_detect_gaps_idempotent(tmp_path: Path) -> None:
    conn, run_id, pr_id = _setup(tmp_path)
    _human(
        conn, run_id, pr_id, "gap", substantive=True, detectable=True, overlap=False, confidence=1.0
    )
    detect_gaps(conn, run_id, confidence_threshold=0.5)
    detect_gaps(conn, run_id, confidence_threshold=0.5)  # re-run
    assert conn.execute("SELECT COUNT(*) FROM gaps").fetchone()[0] == 1


def test_detect_gaps_empty(tmp_path: Path) -> None:
    conn, run_id, _ = _setup(tmp_path)
    summary = detect_gaps(conn, run_id, confidence_threshold=0.5)
    assert summary.gap_count == 0
