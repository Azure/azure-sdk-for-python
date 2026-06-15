"""Tests for deterministic acted_on logic and judge_run persistence."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from analyzer.config import Config
from analyzer.pipeline import classify
from analyzer.pipeline.classify import CommitFiles, JudgeError, acted_on
from analyzer.store import db


def _commit(date: str, paths: set[str] | None) -> CommitFiles:
    return CommitFiles(committed_date=date, paths=paths)


def test_acted_on_commit_after_touching_path_is_true() -> None:
    commits = [_commit("2024-01-02T00:00:00Z", {"a.py", "b.py"})]
    assert acted_on("a.py", "2024-01-01T00:00:00Z", commits) is True


def test_acted_on_commit_before_comment_is_false() -> None:
    commits = [_commit("2024-01-01T00:00:00Z", {"a.py"})]
    assert acted_on("a.py", "2024-01-02T00:00:00Z", commits) is False


def test_acted_on_different_path_is_false() -> None:
    commits = [_commit("2024-01-02T00:00:00Z", {"b.py"})]
    assert acted_on("a.py", "2024-01-01T00:00:00Z", commits) is False


def test_acted_on_unknown_paths_is_none() -> None:
    commits = [_commit("2024-01-02T00:00:00Z", None)]
    assert acted_on("a.py", "2024-01-01T00:00:00Z", commits) is None


def test_acted_on_null_path_is_none() -> None:
    commits = [_commit("2024-01-02T00:00:00Z", {"a.py"})]
    assert acted_on(None, "2024-01-01T00:00:00Z", commits) is None


def test_acted_on_unparseable_comment_time_is_none() -> None:
    commits = [_commit("2024-01-02T00:00:00Z", {"a.py"})]
    assert acted_on("a.py", "not-a-date", commits) is None


def _config(**over: object) -> Config:
    base: dict[str, object] = {
        "repos": ("o/n",),
        "copilot_logins": ("copilot",),
        "model": "m",
    }
    base.update(over)
    return Config(**base)  # type: ignore[arg-type]


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


def test_judge_run_persists_and_leaves_unjudged_null(tmp_path: Path) -> None:
    conn, run_id, pr_id = _setup(tmp_path)
    for i in range(1, 5):
        db.upsert_comment(
            conn,
            run_id=run_id,
            pr_id=pr_id,
            source_key=f"h{i}",
            author_kind="human",
            body=f"c{i}",
        )

    def complete(system: str, user: str) -> str:
        ids = [
            int(line.split("id=")[1].split(" ")[0])
            for line in user.splitlines()
            if "COMMENT id=" in line
        ]
        # Judge all but leave one (highest id) absent every time -> unjudged.
        keep = [i for i in ids if i != 4]
        results = [
            {
                "id": i,
                "is_substantive": True,
                "diff_detectable": True,
                "category": "bug",
                "rationale": "x",
                "confidence": 0.8,
            }
            for i in keep
        ]
        return json.dumps({"results": results})

    stats = classify.judge_run(conn, run_id, _config(), complete=complete)
    assert stats.total == 4
    assert stats.judged == 3
    assert stats.unjudged == 1

    null_count = conn.execute(
        "SELECT COUNT(*) FROM comments WHERE judge_confidence IS NULL AND author_kind='human'"
    ).fetchone()[0]
    assert null_count == 1


def test_judge_run_raises_when_too_many_unjudged(tmp_path: Path) -> None:
    conn, run_id, pr_id = _setup(tmp_path)
    for i in range(1, 5):
        db.upsert_comment(conn, run_id=run_id, pr_id=pr_id, source_key=f"h{i}", author_kind="human")

    def complete(system: str, user: str) -> str:
        return "garbage"  # nothing judged -> ratio 1.0 > 0.5

    with pytest.raises(JudgeError):
        classify.judge_run(conn, run_id, _config(max_unjudged_ratio=0.5), complete=complete)
