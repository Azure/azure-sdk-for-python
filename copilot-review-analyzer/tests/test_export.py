"""Tests for report export (golden snapshots) and run resolution."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from analyzer.report import data, export, render
from analyzer.store import db


def _seed(tmp_path: Path):
    conn = db.connect(tmp_path / "a.db")
    db.init_db(conn)
    run_id = db.insert_run(
        conn,
        repo="octo/example",
        started_at="2024-01-01T00:00:00Z",
        window_start="2023-12-25T00:00:00Z",
        window_end="2024-01-01T00:00:00Z",
        pr_state="merged",
        model="gpt-4o",
        config_hash="cfg123",
    )
    pr_id = db.upsert_pr(conn, run_id=run_id, number=1, title="t")
    for i in range(3):
        cid = db.upsert_comment(
            conn, run_id=run_id, pr_id=pr_id, source_key=f"h{i}", author_kind="human"
        )
        db.update_comment_judgement(
            conn,
            cid,
            is_substantive=True,
            diff_detectable=True,
            category="bug",
            judge_rationale="r",
            judge_confidence=1.0,
        )
        db.set_comment_overlap(conn, cid, i == 0)  # first overlapped
        if i != 0:
            db.upsert_gap(conn, run_id=run_id, pr_id=pr_id, comment_id=cid, category="bug")
    db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key="c1", author_kind="copilot")
    db.upsert_theme(conn, run_id=run_id, label="security", gap_count=2, description="d")
    db.upsert_theme(conn, run_id=run_id, label="docs", gap_count=1)
    db.upsert_metrics(
        conn,
        run_id,
        substantive_human_count=3,
        copilot_comment_count=1,
        gap_count=2,
        judged_human_count=3,
        miss_rate=2 / 3,
        copilot_overlap_rate=1 / 3,
        human_burden_per_pr=3.0,
    )
    db.finish_run(conn, run_id, status="completed", finished_at="2024-01-01T01:00:00Z", pr_count=1)
    return conn, run_id


def test_resolve_latest_completed(tmp_path: Path) -> None:
    conn, run_id = _seed(tmp_path)
    # A later failed run must not be chosen by 'latest'.
    failed = db.insert_run(
        conn,
        repo="octo/example",
        started_at="t",
        window_start="a",
        window_end="b",
        pr_state="merged",
        model="m",
    )
    db.finish_run(conn, failed, status="failed", finished_at="t")
    assert data.resolve_run_id(conn, "latest") == run_id
    assert data.resolve_run_id(conn, "latest", include_incomplete=True) == failed


def test_resolve_failed_run_requires_flag(tmp_path: Path) -> None:
    conn, _ = _seed(tmp_path)
    failed = db.insert_run(
        conn,
        repo="octo/example",
        started_at="t",
        window_start="a",
        window_end="b",
        pr_state="merged",
        model="m",
    )
    db.finish_run(conn, failed, status="failed", finished_at="t")
    with pytest.raises(data.NoDataError):
        data.resolve_run_id(conn, str(failed))
    assert data.resolve_run_id(conn, str(failed), include_incomplete=True) == failed


def test_json_export_schema(tmp_path: Path) -> None:
    conn, run_id = _seed(tmp_path)
    payload = json.loads(export.to_json(conn, run_id))
    assert payload["schema_version"] == export.JSON_SCHEMA_VERSION
    assert payload["run"]["repo"] == "octo/example"
    assert payload["metrics"]["miss_rate"] == pytest.approx(2 / 3)
    assert payload["counts"]["gap_count"] == 2
    # Themes ordered by gap_count desc, then label.
    assert [t["label"] for t in payload["themes"]] == ["security", "docs"]
    assert "RELATIVE" in payload["caveat"]


def test_json_export_deterministic(tmp_path: Path) -> None:
    conn, run_id = _seed(tmp_path)
    assert export.to_json(conn, run_id) == export.to_json(conn, run_id)


def test_markdown_export_contains_caveat_and_metrics(tmp_path: Path) -> None:
    conn, run_id = _seed(tmp_path)
    md = export.to_markdown(conn, run_id)
    assert "# Copilot review effectiveness — run" in md
    assert "miss_rate" in md
    assert "| security | 2 |" in md
    assert "Caveat:" in md


def test_suggestions_surface_in_report(tmp_path: Path) -> None:
    conn, run_id = _seed(tmp_path)
    gap_id = conn.execute(
        "SELECT id, comment_id FROM gaps WHERE run_id = ? ORDER BY id LIMIT 1", (run_id,)
    ).fetchone()
    db.upsert_gap_suggestion(
        conn,
        run_id=run_id,
        gap_id=gap_id["id"],
        comment_id=gap_id["comment_id"],
        missed_finding="off-by-one in loop bound",
        prompt_improvement="Flag loop bounds for off-by-one errors",
        created_at="2024-01-01T02:00:00Z",
    )
    payload = json.loads(export.to_json(conn, run_id))
    assert payload["suggestions"][0]["missed_finding"] == "off-by-one in loop bound"
    assert "Suggested review-prompt additions" in payload["prompt_addendum"]
    md = export.to_markdown(conn, run_id)
    assert "What Copilot missed (per gap)" in md
    assert "Flag loop bounds for off-by-one errors" in md


def test_csv_export_single_row(tmp_path: Path) -> None:
    conn, run_id = _seed(tmp_path)
    csv_text = export.to_csv(conn, run_id)
    lines = [ln for ln in csv_text.splitlines() if ln.strip()]
    assert len(lines) == 2  # header + one row
    assert "miss_rate" in lines[0]


def test_sparkline_basic() -> None:
    assert render.sparkline([0.0, 0.5, 1.0]) == "▁▅█"
    assert render.sparkline([None, None]) == ""
    # Single distinct value -> mid tick.
    assert set(render.sparkline([0.5, 0.5])) <= set("▁▂▃▄▅▆▇█")


def test_trend_series_excludes_failed(tmp_path: Path) -> None:
    conn, run_id = _seed(tmp_path)
    failed = db.insert_run(
        conn,
        repo="octo/example",
        started_at="t",
        window_start="a",
        window_end="b",
        pr_state="merged",
        model="m",
    )
    db.finish_run(conn, failed, status="failed", finished_at="t")
    series = data.trend_series(conn, "miss_rate")
    assert [rid for rid, _ in series] == [run_id]
