"""Tests for the HTTP-free LLM judge core (batching, validation, retry)."""

from __future__ import annotations

import json

from analyzer.llm.judge import CommentItem, judge_comments


def _item(cid: int) -> CommentItem:
    return CommentItem(
        id=cid,
        file_path="a.py",
        line_start=1,
        line_end=2,
        diff_hunk="- x\n+ y",
        body=f"comment {cid}",
    )


def _result(cid: int, **over: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": cid,
        "is_substantive": True,
        "diff_detectable": True,
        "category": "bug",
        "rationale": "because",
        "confidence": 0.9,
    }
    base.update(over)
    return base


def test_valid_response_all_judged() -> None:
    items = [_item(1), _item(2)]

    def complete(system: str, user: str) -> str:
        return json.dumps({"results": [_result(1), _result(2)]})

    out = judge_comments(items, complete=complete, batch_size=10)
    assert out.unjudged_ids == set()
    assert out.judgements[1].category == "bug"
    assert out.judgements[1].is_substantive is True
    assert out.judgements[2].confidence == 0.9
    assert out.retries == 0


def test_missing_id_triggers_corrective_retry() -> None:
    items = [_item(1), _item(2)]
    calls: list[str] = []

    def complete(system: str, user: str) -> str:
        calls.append(user)
        if len(calls) == 1:
            return json.dumps({"results": [_result(1)]})  # id 2 missing
        return json.dumps({"results": [_result(2)]})  # corrective retry supplies it

    out = judge_comments(items, complete=complete, batch_size=10)
    assert out.unjudged_ids == set()
    assert out.retries == 1
    assert len(calls) == 2
    assert "missing or invalid" in calls[1]


def test_malformed_json_then_failed_retry_marks_unjudged() -> None:
    items = [_item(1)]

    def complete(system: str, user: str) -> str:
        return "not json at all"

    out = judge_comments(items, complete=complete, batch_size=10)
    assert out.unjudged_ids == {1}
    assert 1 not in out.judgements
    assert out.retries == 1


def test_invalid_fields_are_rejected() -> None:
    items = [_item(1), _item(2)]

    def complete(system: str, user: str) -> str:
        # id 1 has a non-bool is_substantive -> invalid; id 2 valid.
        bad = _result(1, is_substantive="yes")
        return json.dumps({"results": [bad, _result(2)]})

    out = judge_comments(items, complete=complete, batch_size=10)
    # id 1 invalid in first pass, retry also returns the same bad shape -> unjudged.
    assert 2 in out.judgements
    assert out.unjudged_ids == {1}


def test_unknown_category_defaults_to_nit() -> None:
    items = [_item(1)]

    def complete(system: str, user: str) -> str:
        return json.dumps({"results": [_result(1, category="banana")]})

    out = judge_comments(items, complete=complete, batch_size=10)
    assert out.judgements[1].category == "nit"


def test_confidence_clamped() -> None:
    items = [_item(1), _item(2)]

    def complete(system: str, user: str) -> str:
        return json.dumps({"results": [_result(1, confidence=5.0), _result(2, confidence=-1.0)]})

    out = judge_comments(items, complete=complete, batch_size=10)
    assert out.judgements[1].confidence == 1.0
    assert out.judgements[2].confidence == 0.0


def test_batching_splits_calls() -> None:
    items = [_item(i) for i in range(1, 6)]  # 5 items
    batch_sizes: list[int] = []

    def complete(system: str, user: str) -> str:
        ids = [
            int(line.split("id=")[1].split(" ")[0])
            for line in user.splitlines()
            if "COMMENT id=" in line
        ]
        batch_sizes.append(len(ids))
        return json.dumps({"results": [_result(i) for i in ids]})

    out = judge_comments(items, complete=complete, batch_size=2)
    assert out.unjudged_ids == set()
    assert batch_sizes == [2, 2, 1]


def test_completer_exception_is_swallowed() -> None:
    items = [_item(1)]

    def complete(system: str, user: str) -> str:
        raise RuntimeError("network down")

    out = judge_comments(items, complete=complete, batch_size=10)
    assert out.unjudged_ids == {1}
