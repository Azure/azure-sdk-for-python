# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline unit tests for the known-failures gate (scripts/v5/check_known_failures.py).
No account, no binding — pure matcher logic."""
import importlib.util
import pathlib

_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_SCRIPT = _ROOT / "scripts" / "v5" / "check_known_failures.py"
_spec = importlib.util.spec_from_file_location("check_known_failures", _SCRIPT)
ckf = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(ckf)


def test_load_patterns_skips_comments_and_blanks():
    """Prove only usable known-failure patterns are loaded."""
    pats = ckf.load_patterns("# c\n\nquery\nFeed\n")
    assert pats == ["query", "feed"]


def test_failed_ids_parses_failed_and_error_lines():
    """Prove failed and errored test IDs are read from pytest output."""
    text = "FAILED tests/test_aad.py::T::test_x\nERROR tests/test_q.py::Q::test_query\nPASSED a\n"
    assert ckf.failed_ids_from_transcript(text) == [
        "tests/test_aad.py::T::test_x", "tests/test_q.py::Q::test_query"]


def test_classify_splits_explained_vs_unexplained():
    """Prove known patterns separate expected failures from new failures."""
    explained, unexplained = ckf.classify(
        ["tests/test_query.py::T::test_query", "tests/test_create.py::T::test_dup"],
        ["query", "partitionless"])
    assert explained == ["tests/test_query.py::T::test_query"]
    assert unexplained == ["tests/test_create.py::T::test_dup"]


def test_real_known_file_matches_query_and_resource_token():
    """Prove the checked-in list recognizes named Rust limitations."""
    pats = ckf.load_patterns((_ROOT / "tests" / "known_rust_failures.txt").read_text())
    _, unexplained = ckf.classify(["x::test_resource_token_auth", "x::test_real_regression"], pats)
    assert unexplained == ["x::test_real_regression"]

