# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Regression tests for the in-process backend parity runner."""
from __future__ import annotations

import pytest

from common import _parity_helpers
from azure.cosmos._backend.legacy import LEGACY_BACKEND


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


def test_exception_message_suffix_is_not_truncated():
    """Semantic differences after 240 characters must remain visible."""
    prefix = "x" * 300
    first = ValueError(prefix + " alpha")
    second = ValueError(prefix + " bravo")

    assert (
        _parity_helpers._normalize_exception_message(first)
        != _parity_helpers._normalize_exception_message(second)
    )
