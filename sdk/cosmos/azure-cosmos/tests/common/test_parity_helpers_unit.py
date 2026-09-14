# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Regression tests for the in-process backend parity runner."""
from __future__ import annotations

import ast
import pathlib
import re

import pytest

from common import _parity_helpers
from azure.cosmos._backend.legacy import LEGACY_BACKEND


def test_header_pushback_references_match_document_headings():
    document = (
        pathlib.Path(__file__).resolve().parents[2] / "docs" / "V5" / "RUST_PARITY_PUSHBACKS.md"
    ).read_text(encoding="utf-8")
    headings = {
        int(number): title
        for number, title in re.findall(r"^## (\d+) — (.+)$", document, re.MULTILINE)
    }
    for number, title in set(_parity_helpers.BackendComparison._HEADER_TO_PUSHBACK.values()):
        assert headings.get(number) == title


@pytest.mark.parametrize(
    "header, pushback",
    [("date", 26), ("x-ms-cosmos-min-throughput", 26)],
)
def test_header_verdict_references_current_pushbacks(header, pushback):
    core = _parity_helpers.CallOutcome(backend="core-python", return_value={}, response_headers={header: "value"})
    rust = _parity_helpers.CallOutcome(backend="rust", return_value={}, response_headers={})
    comparison = _parity_helpers.BackendComparison(
        core_python=core, rust=rust, diffs=_parity_helpers.diff_outcomes(core, rust)
    )
    assert f"Pushback #{pushback} " in comparison._verdict()
    assert not comparison.is_parity


@pytest.mark.parametrize("name", ["x-ms-cosmos-sdk-diagnostics", "X-MS-COSMOS-SDK-DIAGNOSTICS"])
@pytest.mark.parametrize("raised", [False, True])
def test_rust_diagnostics_are_reported_as_an_accepted_addition(name, raised):
    error = ValueError("bad request") if raised else None
    core = _parity_helpers.CallOutcome(backend="core-python", response_headers={}, raised=error)
    rust = _parity_helpers.CallOutcome(
        backend="rust", response_headers={name: "activity=abc requests=1"}, raised=error
    )
    comparison = _parity_helpers.BackendComparison(
        core_python=core, rust=rust, diffs=_parity_helpers.diff_outcomes(core, rust)
    )
    assert comparison.is_parity
    report = comparison.format_report()
    assert "ACCEPTED vNext ADDITIONS (not gaps)" in report
    assert "activity=abc requests=1" in report
    assert "HEADER GAP" not in report
    assert "Pushback #32" not in report
    assert name in rust.response_headers


@pytest.mark.parametrize("value", ["", " ", None])
def test_empty_rust_diagnostics_are_not_exempted(value):
    core = _parity_helpers.CallOutcome(backend="core-python", response_headers={})
    rust = _parity_helpers.CallOutcome(
        backend="rust", response_headers={"x-ms-cosmos-sdk-diagnostics": value}
    )
    assert _parity_helpers.diff_outcomes(core, rust)


def test_accepted_diagnostics_do_not_hide_missing_service_headers():
    core = _parity_helpers.CallOutcome(backend="core-python", response_headers={"content-type": "application/json"})
    rust = _parity_helpers.CallOutcome(
        backend="rust", response_headers={"x-ms-cosmos-sdk-diagnostics": "activity=abc"}
    )
    diffs = _parity_helpers.diff_outcomes(core, rust)
    assert diffs == ["headers only on core-python: ['content-type']"]


def test_rust_missing_diagnostics_are_not_exempted_if_core_exposes_them():
    core = _parity_helpers.CallOutcome(
        backend="core-python", response_headers={"x-ms-cosmos-sdk-diagnostics": "activity=abc"}
    )
    rust = _parity_helpers.CallOutcome(backend="rust", response_headers={})
    assert _parity_helpers.diff_outcomes(core, rust) == [
        "headers only on core-python: ['x-ms-cosmos-sdk-diagnostics']"
    ]


@pytest.mark.parametrize(
    "header",
    [
        "x-ms-item-lsn", "x-ms-cosmos-item-llsn",
        "x-ms-current-replica-set-size", "x-ms-current-write-quorum",
        "x-ms-unrecognized-test-header",
    ],
)
def test_unrecorded_headers_remain_visible_without_claiming_a_known_defect(header):
    core = _parity_helpers.CallOutcome(backend="core-python", return_value={}, response_headers={header: "1"})
    rust = _parity_helpers.CallOutcome(backend="rust", return_value={}, response_headers={})
    comparison = _parity_helpers.BackendComparison(
        core_python=core, rust=rust, diffs=_parity_helpers.diff_outcomes(core, rust)
    )
    verdict = comparison._verdict()
    assert header in verdict
    assert "NOT YET RECORDED" in verdict
    assert "all known rust-binding gaps" not in verdict
    assert "NEW PUSHBACK NOT NEEDED" not in verdict
    assert not comparison.is_parity


@pytest.mark.parametrize("surface", ["sync", "aio"])
def test_get_or_create_legacy_copies_preserve_preconditions_and_assertions(surface):
    root = pathlib.Path(__file__).resolve().parents[1]
    suffix = "_async" if surface == "aio" else ""
    original = ast.parse((root / f"test_cosmos_responses{suffix}.py").read_text(encoding="utf-8"))
    copied = ast.parse(
        (root / "create_database_if_not_exists" / surface / "legacy" / "test_cosmos_responses.py")
        .read_text(encoding="utf-8")
    )
    for stem in ("test_create_database_if_not_exists_headers", "test_create_database_if_not_exists_headers_negative"):
        name = stem + suffix
        original_method = next(
            n for n in ast.walk(original)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name
        )
        copied_method = next(
            n for n in ast.walk(copied)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name
        )
        assert ast.dump(original_method) == ast.dump(copied_method)
        if "negative" in stem:
            setup_calls = [
                n.func.attr for n in ast.walk(original_method.body[1])
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            ]
            assert setup_calls == ["create_database"]
            assert isinstance(original_method.body[2], ast.Try)
            assert original_method.body[2].finalbody


class _Connection:
    """Provide the connection fields read by the comparison helper."""
    def __init__(self, backend):
        self._backend = backend
        self.last_response_headers = {}


class _Client:
    """Provide a minimal client with a selected request implementation."""
    def __init__(self, backend):
        self.client_connection = _Connection(backend)


class _RustBackend:
    """Identify a fake request implementation as Rust."""
    name = "rust"


def test_runner_rejects_factory_that_returns_core_python_for_rust():
    """A broken factory must not compare core-python against itself."""

    with pytest.raises(AssertionError, match="requested 'rust'"):
        _parity_helpers.run_on_both_backends(
            lambda _client: {"value": 1},
            client_factory=lambda _requested: _Client(LEGACY_BACKEND),
        )


def test_runner_accepts_clients_with_the_requested_backends():
    """The backend identity check accepts one real label per column."""

    def factory(requested):
        return _Client(LEGACY_BACKEND if requested == "core-python" else _RustBackend())

    comparison = _parity_helpers.run_on_both_backends(
        lambda _client: {"value": 1},
        client_factory=factory,
    )

    assert comparison.is_parity


def test_runner_does_not_swallow_process_control_exceptions():
    """KeyboardInterrupt and similar BaseException signals must escape."""

    def call(_client):
        raise KeyboardInterrupt()

    with pytest.raises(KeyboardInterrupt):
        _parity_helpers.run_on_both_backends(
            call,
            client_factory=lambda requested: _Client(
                LEGACY_BACKEND if requested == "core-python" else _RustBackend()
            ),
        )


def test_exception_normalization_keeps_semantic_words_and_numbers():
    """Ordinary error details must not be scrubbed as if they were diagnostics."""

    first = ValueError("Invalid partition key value 4")
    second = ValueError("Invalid container key value 5")

    assert (
        _parity_helpers._normalize_exception_message(first)
        != _parity_helpers._normalize_exception_message(second)
    )


def test_exception_normalization_scrubs_service_replica_ids():
    """Different responding replicas do not change the customer error contract."""
    first = ValueError("Request URI: /partitions/abc/replicas/134135831941489642s")
    second = ValueError("Request URI: /partitions/abc/replicas/134203270553494317s")

    assert (
        _parity_helpers._normalize_exception_message(first)
        == _parity_helpers._normalize_exception_message(second)
    )


def test_exception_assertion_checks_normalized_message():
    """Typed exceptions with different meanings must not pass parity."""
    comparison = _parity_helpers.BackendComparison(
        core_python=_parity_helpers.CallOutcome(
            backend="core-python", raised=ValueError("bad partition key 4")
        ),
        rust=_parity_helpers.CallOutcome(
            backend="rust", raised=ValueError("bad container key 5")
        ),
    )

    with pytest.raises(AssertionError, match="exception.message"):
        comparison.assert_exception_parity()


def test_target_operation_requires_binding_counter_movement(monkeypatch):
    """Setup Rust calls cannot stand in for the target operation."""
    counts = iter((10, 10))
    monkeypatch.setattr(
        _parity_helpers, "_binding_operation_count", lambda: next(counts)
    )

    with pytest.raises(AssertionError, match="did not enter"):
        _parity_helpers.run_target_operation(
            _Client(_RustBackend()), lambda: {"value": 1}
        )


def test_target_operation_can_assert_intentional_fallback(monkeypatch):
    """Fallback tests explicitly require that the target did not enter Rust."""
    counts = iter((10, 10))
    monkeypatch.setattr(
        _parity_helpers, "_binding_operation_count", lambda: next(counts)
    )

    result = _parity_helpers.run_target_operation(
        _Client(_RustBackend()), lambda: {"value": 1}, expect_rust=False
    )

    assert result == {"value": 1}


def test_error_response_headers_are_compared():
    """Matching exceptions with different customer-visible headers are not parity."""
    core = _parity_helpers.CallOutcome(
        backend="core-python",
        raised=ValueError("bad request"),
        response_headers={"x-ms-custom": "core"},
    )
    rust = _parity_helpers.CallOutcome(
        backend="rust",
        raised=ValueError("bad request"),
        response_headers={"x-ms-custom": "rust"},
    )

    diffs = _parity_helpers.diff_outcomes(core, rust)

    assert any(diff.startswith("header x-ms-custom:") for diff in diffs)


def test_functional_exception_parity_allows_header_surface_gap():
    """Known header gaps do not hide a matching typed exception contract."""
    core = _parity_helpers.CallOutcome(
        backend="core-python",
        raised=ValueError("bad request"),
        response_headers={"content-type": "application/json"},
    )
    rust = _parity_helpers.CallOutcome(
        backend="rust",
        raised=ValueError("bad request"),
        response_headers={"x-ms-cosmos-sdk-diagnostics": "details"},
    )
    comparison = _parity_helpers.BackendComparison(
        core_python=core,
        rust=rust,
        diffs=_parity_helpers.diff_outcomes(core, rust),
    )

    comparison.assert_functional_exception_parity()
    verdict = comparison._verdict()
    assert verdict.startswith("FUNCTIONAL PARITY, HEADER GAP:")
    assert "equivalent exceptions" in verdict
    assert "operation successfully" not in verdict


def test_exception_message_suffix_is_not_truncated():
    """Semantic differences after 240 characters must remain visible."""
    prefix = "x" * 300
    first = ValueError(prefix + " alpha")
    second = ValueError(prefix + " bravo")

    assert (
        _parity_helpers._normalize_exception_message(first)
        != _parity_helpers._normalize_exception_message(second)
    )
