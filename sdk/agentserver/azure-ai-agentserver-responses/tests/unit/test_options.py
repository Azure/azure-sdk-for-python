# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for server options behavior."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses._options import ResponsesServerOptions


def test_options__defaults_match_public_contract() -> None:
    options = ResponsesServerOptions()

    assert options.default_fetch_history_count == -1
    assert options.default_model is None
    assert options.additional_server_version is None
    assert options.sse_keep_alive_enabled is False


def test_options__environment_values_override_defaults() -> None:
    options = ResponsesServerOptions.from_env(
        {
            "DEFAULT_FETCH_HISTORY_ITEM_COUNT": "42",
        }
    )

    assert options.default_fetch_history_count == 42


def test_options__sse_keep_alive_set_via_constructor() -> None:
    """SSE keep-alive is set explicitly via the constructor, not from_env()."""
    options = ResponsesServerOptions(sse_keep_alive_interval_seconds=12)
    assert options.sse_keep_alive_interval_seconds == 12
    assert options.sse_keep_alive_enabled is True


def test_options__invalid_boundary_values_fail_fast() -> None:
    with pytest.raises(ValueError):
        ResponsesServerOptions(default_fetch_history_count=0)

    with pytest.raises(ValueError):
        ResponsesServerOptions(sse_keep_alive_interval_seconds=0)

    with pytest.raises(ValueError):
        ResponsesServerOptions.from_env({"DEFAULT_FETCH_HISTORY_ITEM_COUNT": "-2"})


@pytest.mark.parametrize("limit", [-1, 1, 10, 1000])
def test_options__history_limit_from_constructor_and_environment(limit: int) -> None:
    assert ResponsesServerOptions(default_fetch_history_count=limit).default_fetch_history_count == limit
    assert (
        ResponsesServerOptions.from_env({"DEFAULT_FETCH_HISTORY_ITEM_COUNT": str(limit)}).default_fetch_history_count
        == limit
    )


@pytest.mark.parametrize("limit", [0, -2, -100])
def test_options__invalid_history_limits(limit: int) -> None:
    with pytest.raises(ValueError, match="unlimited"):
        ResponsesServerOptions(default_fetch_history_count=limit)
    with pytest.raises(ValueError, match="unlimited"):
        ResponsesServerOptions.from_env({"DEFAULT_FETCH_HISTORY_ITEM_COUNT": str(limit)})


@pytest.mark.parametrize("value", ["invalid", "1.5"])
def test_options__invalid_history_environment_value(value: str) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        ResponsesServerOptions.from_env({"DEFAULT_FETCH_HISTORY_ITEM_COUNT": value})


@pytest.mark.parametrize("environ", [{}, {"DEFAULT_FETCH_HISTORY_ITEM_COUNT": ""}])
def test_options__environment_defaults_to_unlimited(environ: dict[str, str]) -> None:
    assert ResponsesServerOptions.from_env(environ).default_fetch_history_count == -1


def test_options__spec_environment_variable_names_are_supported() -> None:
    """Verify the spec-aligned env var names."""
    options = ResponsesServerOptions.from_env(
        {
            "DEFAULT_FETCH_HISTORY_ITEM_COUNT": "55",
        }
    )

    assert options.default_fetch_history_count == 55
    # SSE keep-alive is resolved from AgentConfig, not from_env()
    assert options.sse_keep_alive_interval_seconds is None


def test_options__legacy_environment_variable_names_are_ignored() -> None:
    """Old prefixed names must NOT be picked up."""
    options = ResponsesServerOptions.from_env(
        {
            "AZURE_AI_RESPONSES_SERVER_DEFAULT_FETCH_HISTORY_ITEM_COUNT": "42",
        }
    )

    assert options.default_model is None
    assert options.default_fetch_history_count == -1
    assert options.sse_keep_alive_interval_seconds is None
