"""Unit tests for server options behavior."""

from __future__ import annotations

import pytest

from azure.ai.agentserver.responses._options import ResponsesServerOptions


def test_options__defaults_match_public_contract() -> None:
    options = ResponsesServerOptions()

    assert options.default_fetch_history_count == 100
    assert options.default_model is None
    assert options.additional_server_identity is None
    assert options.sse_keep_alive_enabled is False


def test_options__environment_values_override_defaults() -> None:
    options = ResponsesServerOptions.from_env(  # type: ignore[attr-defined]
        {
            "RESPONSES_DEFAULT_MODEL": "gpt-4o",
            "RESPONSES_FETCH_HISTORY_COUNT": "42",
        }
    )

    assert options.default_model == "gpt-4o"
    assert options.default_fetch_history_count == 42


def test_options__invalid_boundary_values_fail_fast() -> None:
    with pytest.raises(ValueError):
        ResponsesServerOptions(default_fetch_history_count=0)

    with pytest.raises(ValueError):
        ResponsesServerOptions(sse_keep_alive_interval_seconds=0)

    with pytest.raises(ValueError):
        ResponsesServerOptions.from_env(  # type: ignore[attr-defined]
            {"RESPONSES_FETCH_HISTORY_COUNT": "-1"}
        )
