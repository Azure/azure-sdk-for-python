"""Tests for deterministic attribution (author classification + overlap)."""

from __future__ import annotations

import pytest

from analyzer.pipeline.attribute import LineRange, classify_author, overlaps

COPILOT = ["copilot-pull-request-reviewer", "github-copilot[bot]"]


@pytest.mark.parametrize(
    "login,expected",
    [
        ("copilot-pull-request-reviewer", "copilot"),  # GraphQL form (no suffix)
        ("copilot-pull-request-reviewer[bot]", "copilot"),  # REST form
        ("Copilot-Pull-Request-Reviewer", "copilot"),  # case-insensitive
        ("github-copilot[bot]", "copilot"),
        ("dependabot[bot]", "other_bot"),
        ("alice", "human"),
        (None, "other_bot"),
        ("", "other_bot"),
        ("   ", "other_bot"),
    ],
)
def test_classify_author_matrix(login, expected) -> None:
    assert classify_author(login, COPILOT) == expected


def _r(path="a.py", start=10, end=20, coord="current") -> LineRange:
    return LineRange(path=path, start=start, end=end, coord_space=coord)


def test_overlap_disjoint() -> None:
    assert overlaps(_r(start=10, end=20), [_r(start=30, end=40)], 0) is False


def test_overlap_touching_with_zero_fuzz() -> None:
    assert overlaps(_r(start=10, end=20), [_r(start=20, end=25)], 0) is True


def test_overlap_nested() -> None:
    assert overlaps(_r(start=10, end=20), [_r(start=12, end=15)], 0) is True


def test_overlap_fuzz_boundary() -> None:
    # Gap of 3 lines; fuzz=2 -> no overlap, fuzz=3 -> overlap.
    human = _r(start=10, end=20)
    copilot = [_r(start=23, end=30)]
    assert overlaps(human, copilot, 2) is False
    assert overlaps(human, copilot, 3) is True


def test_overlap_cross_file_never() -> None:
    assert overlaps(_r(path="a.py"), [_r(path="b.py")], 100) is False


def test_overlap_incomparable_coord_space() -> None:
    human = _r(coord="current")
    copilot = [_r(coord="original")]
    assert overlaps(human, copilot, 5) is False


def test_overlap_empty_copilot_ranges() -> None:
    assert overlaps(_r(), [], 5) is False
