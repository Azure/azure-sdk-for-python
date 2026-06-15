"""Tests for the HTTP-free prompt suggester core and the addendum synthesizer."""

from __future__ import annotations

import json

from analyzer.llm.suggest import GapContext, suggest_for_gaps
from analyzer.report.export import build_prompt_addendum


def _gap(gid: int, *, theme: str | None = "bug") -> GapContext:
    return GapContext(
        gap_id=gid,
        comment_id=gid + 100,
        pr_number=gid,
        category="bug",
        theme=theme,
        file_path="a.py",
        line_start=1,
        line_end=2,
        diff_hunk="- x\n+ y",
        body=f"comment {gid}",
        rationale="diff-detectable bug",
    )


def _entry(gid: int, **over: object) -> dict[str, object]:
    base: dict[str, object] = {
        "id": gid,
        "missed_finding": f"missed {gid}",
        "prompt_improvement": f"rule {gid}",
    }
    base.update(over)
    return base


def test_valid_response_all_suggested() -> None:
    gaps = [_gap(1), _gap(2)]

    def complete(system: str, user: str) -> str:
        return json.dumps({"results": [_entry(1), _entry(2)]})

    out = suggest_for_gaps(gaps, complete=complete, batch_size=10)
    assert out.unsuggested_ids == set()
    assert out.retries == 0
    assert out.suggestions[1].missed_finding == "missed 1"
    assert out.suggestions[2].prompt_improvement == "rule 2"
    assert out.suggestions[1].comment_id == 101


def test_missing_id_triggers_corrective_retry() -> None:
    gaps = [_gap(1), _gap(2)]
    calls: list[str] = []

    def complete(system: str, user: str) -> str:
        calls.append(user)
        if len(calls) == 1:
            return json.dumps({"results": [_entry(1)]})  # id 2 missing
        return json.dumps({"results": [_entry(2)]})

    out = suggest_for_gaps(gaps, complete=complete, batch_size=10)
    assert out.unsuggested_ids == set()
    assert out.retries == 1
    assert len(calls) == 2


def test_malformed_json_yields_unsuggested() -> None:
    gaps = [_gap(1)]

    def complete(system: str, user: str) -> str:
        return "not json"

    out = suggest_for_gaps(gaps, complete=complete, batch_size=10)
    assert out.unsuggested_ids == {1}
    assert out.suggestions == {}


def test_invalid_fields_rejected() -> None:
    gaps = [_gap(1), _gap(2), _gap(3)]

    def complete(system: str, user: str) -> str:
        return json.dumps(
            {
                "results": [
                    _entry(1, missed_finding=""),  # empty -> rejected
                    _entry(2, prompt_improvement=123),  # wrong type -> rejected
                    _entry(3),  # valid
                ]
            }
        )

    out = suggest_for_gaps(gaps, complete=complete, batch_size=10)
    assert 3 in out.suggestions
    assert {1, 2} <= out.unsuggested_ids


def test_completer_exception_never_crashes() -> None:
    gaps = [_gap(1)]

    def complete(system: str, user: str) -> str:
        raise RuntimeError("boom")

    out = suggest_for_gaps(gaps, complete=complete, batch_size=10)
    assert out.unsuggested_ids == {1}


def test_batching_splits_calls() -> None:
    import re

    gaps = [_gap(i) for i in range(1, 6)]
    seen_batches: list[int] = []

    def complete(system: str, user: str) -> str:
        present = sorted({int(m) for m in re.findall(r"GAP id=(\d+)", user)})
        seen_batches.append(len(present))
        return json.dumps({"results": [_entry(i) for i in present]})

    out = suggest_for_gaps(gaps, complete=complete, batch_size=2)
    assert out.unsuggested_ids == set()
    # 5 gaps, batch_size 2 -> 3 batches.
    assert len(seen_batches) == 3


def test_addendum_groups_dedups_and_cites() -> None:
    suggestions = [
        {"prompt_improvement": "Check for None", "theme": "bug", "pr_number": 1},
        {"prompt_improvement": "check for none", "theme": "bug", "pr_number": 2},
        {"prompt_improvement": "Document params", "theme": "docs", "pr_number": 3},
    ]
    out = build_prompt_addendum(suggestions)
    assert "## Suggested review-prompt additions" in out
    assert "### bug" in out
    assert "### docs" in out
    # Deduplicated case-insensitively, both PRs cited under one rule.
    assert out.count("Check for None") == 1
    assert "#1, #2" in out


def test_addendum_empty_when_no_suggestions() -> None:
    assert build_prompt_addendum([]) == ""
    assert build_prompt_addendum([{"prompt_improvement": "", "theme": "x"}]) == ""
