"""Tests for theme tagging: vocab constraint, out-of-vocab coercion, aggregation."""

from __future__ import annotations

import json
from pathlib import Path

from analyzer.config import Config
from analyzer.pipeline import themes
from analyzer.pipeline.themes import GapItem, assign_themes, normalize_label
from analyzer.store import db

_VOCAB = ("bug", "security", "perf", "other")


def test_normalize_label_in_vocab() -> None:
    assert normalize_label("Security", _VOCAB) == "security"


def test_normalize_label_out_of_vocab_is_other() -> None:
    assert normalize_label("banana", _VOCAB) == "other"
    assert normalize_label(None, _VOCAB) == "other"
    assert normalize_label(123, _VOCAB) == "other"


def _gap(gid: int) -> GapItem:
    return GapItem(
        gap_id=gid, category="bug", file_path="a.py", line_start=1, line_end=1, body=f"g{gid}"
    )


def test_assign_themes_constrains_to_vocab() -> None:
    items = [_gap(1), _gap(2)]

    def complete(system: str, user: str) -> str:
        return json.dumps(
            {"results": [{"id": 1, "theme": "security"}, {"id": 2, "theme": "banana"}]}
        )

    labels, ok = assign_themes(items, complete=complete, vocab=_VOCAB, batch_size=10)
    assert ok is True
    assert labels == {1: "security", 2: "other"}


def test_assign_themes_missing_id_defaults_other() -> None:
    items = [_gap(1), _gap(2)]

    def complete(system: str, user: str) -> str:
        return json.dumps({"results": [{"id": 1, "theme": "perf"}]})

    labels, ok = assign_themes(items, complete=complete, vocab=_VOCAB, batch_size=10)
    assert ok is True
    assert labels == {1: "perf", 2: "other"}


def test_assign_themes_total_failure_marks_unavailable() -> None:
    items = [_gap(1)]

    def complete(system: str, user: str) -> str:
        return "garbage"

    labels, ok = assign_themes(items, complete=complete, vocab=_VOCAB, batch_size=10)
    assert ok is False
    assert labels == {1: "other"}


def _config() -> Config:
    return Config(repos=("o/n",), copilot_logins=("copilot",), model="m", vocab=_VOCAB)


def _setup_with_gaps(tmp_path: Path, n: int):
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
    gap_ids = []
    for i in range(1, n + 1):
        cid = db.upsert_comment(
            conn, run_id=run_id, pr_id=pr_id, source_key=f"h{i}", author_kind="human", body=f"c{i}"
        )
        gap_ids.append(db.upsert_gap(conn, run_id=run_id, pr_id=pr_id, comment_id=cid))
    return conn, run_id, gap_ids


def test_tag_run_aggregates_gap_counts(tmp_path: Path) -> None:
    conn, run_id, gap_ids = _setup_with_gaps(tmp_path, 3)

    def complete(system: str, user: str) -> str:
        ids = [
            int(line.split("id=")[1].split(" ")[0])
            for line in user.splitlines()
            if "GAP id=" in line
        ]
        # First two -> bug, third -> perf.
        mapping = {ids[0]: "bug", ids[1]: "bug", ids[2]: "perf"}
        return json.dumps({"results": [{"id": i, "theme": mapping[i]} for i in ids]})

    stats = themes.tag_run(conn, run_id, _config(), complete=complete)
    assert stats.available is True
    assert stats.gap_count == 3
    assert stats.histogram == {"bug": 2, "perf": 1}

    rows = dict(
        conn.execute("SELECT label, gap_count FROM themes WHERE run_id = ?", (run_id,)).fetchall()
    )
    assert rows == {"bug": 2, "perf": 1}
    linked = conn.execute(
        "SELECT COUNT(*) FROM gaps WHERE run_id = ? AND theme_id IS NOT NULL", (run_id,)
    ).fetchone()[0]
    assert linked == 3


def test_tag_run_no_gaps_writes_nothing(tmp_path: Path) -> None:
    conn, run_id, _ = _setup_with_gaps(tmp_path, 0)

    def complete(system: str, user: str) -> str:  # pragma: no cover - never called
        raise AssertionError("should not be called")

    stats = themes.tag_run(conn, run_id, _config(), complete=complete)
    assert stats.available is True
    assert stats.gap_count == 0


def test_tag_run_unavailable_leaves_themes_empty(tmp_path: Path) -> None:
    conn, run_id, _ = _setup_with_gaps(tmp_path, 2)

    def complete(system: str, user: str) -> str:
        return "not json"

    stats = themes.tag_run(conn, run_id, _config(), complete=complete)
    assert stats.available is False
    theme_count = conn.execute(
        "SELECT COUNT(*) FROM themes WHERE run_id = ?", (run_id,)
    ).fetchone()[0]
    assert theme_count == 0
    null_links = conn.execute(
        "SELECT COUNT(*) FROM gaps WHERE run_id = ? AND theme_id IS NULL", (run_id,)
    ).fetchone()[0]
    assert null_links == 2
