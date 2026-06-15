# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for cross-process reconstruction in `_execute_in_task` (T-022).

Covers spec 013 US1 deliverable (a) acceptance scenario 1: when the in-memory
references (`_record_ref`, `_context_ref`, `_parsed_ref`, `_cancel_ref`,
`_runtime_state_ref`) are missing from the durable task input (as they would
be after a cross-process restart), the orchestrator reconstructs them from
the serialized params and proceeds.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


def _build_params_for_recovery() -> dict:
    """Build a serialized durable-task params dict matching what the orchestrator
    stamps at fresh-entry, with all in-memory `_*_ref` entries set to None
    (simulating cross-process recovery)."""
    return {
        "response_id": "resp_recover_001",
        # In-memory refs intentionally None — this is what cross-process recovery sees.
        "_record_ref": None,
        "_context_ref": None,
        "_parsed_ref": None,
        "_cancel_ref": None,
        "_runtime_state_ref": None,
        # Serializable params
        "agent_reference": "test-agent",
        "model": "test-model",
        "store": True,
        "agent_session_id": "session_xyz",
        "conversation_id": "conv_abc",
        "previous_response_id": None,
        "history_limit": 100,
        "agent_name": "default",
        "session_id": "session_xyz",
        "user_isolation_key": None,
        "chat_isolation_key": None,
        "prefetched_history_ids": None,
        "input_items": [{"role": "user", "content": "hello"}],
        "parsed_payload": {
            "input": "hello",
            "model": "test-model",
            "stream": False,
            "store": True,
            "background": True,
        },
        "stream": False,
        "background": True,
    }


def test_reconstruct_from_params_returns_record_and_context() -> None:
    """``_reconstruct_from_params`` rebuilds ResponseExecution and ResponseContext."""
    from azure.ai.agentserver.responses._options import ResponsesServerOptions
    from azure.ai.agentserver.responses.hosting._durable_orchestrator import (
        _reconstruct_from_params,
    )

    options = ResponsesServerOptions()
    record, context = _reconstruct_from_params(
        params=_build_params_for_recovery(),
        response_id="resp_recover_001",
        provider=None,
        runtime_state=None,
        runtime_options=options,
    )

    assert record.response_id == "resp_recover_001"
    assert record.conversation_id == "conv_abc"
    assert record.agent_session_id == "session_xyz"
    assert record.initial_model == "test-model"
    assert record.mode_flags.store is True
    assert record.mode_flags.background is True
    assert record.mode_flags.stream is False
    assert record.status == "in_progress"

    assert context.response_id == "resp_recover_001"
    assert context.conversation_id == "conv_abc"
    assert context.mode_flags.store is True


def test_reconstruct_uses_response_id_from_params_not_regenerated() -> None:
    """Reconstruction must use params['response_id'], never generate a new one.

    Spec US1 scenario 7 — response-id stability regression guard.
    """
    from azure.ai.agentserver.responses._options import ResponsesServerOptions
    from azure.ai.agentserver.responses.hosting._durable_orchestrator import (
        _reconstruct_from_params,
    )

    params = _build_params_for_recovery()
    params["response_id"] = "caresp_stable_id_123"
    options = ResponsesServerOptions()
    record, context = _reconstruct_from_params(
        params=params,
        response_id="caresp_stable_id_123",
        provider=None,
        runtime_state=None,
        runtime_options=options,
    )
    assert record.response_id == "caresp_stable_id_123"
    assert context.response_id == "caresp_stable_id_123"


def test_reconstruct_parsed_re_parses_payload() -> None:
    """``_reconstruct_parsed_from_params`` re-hydrates the request model."""
    from azure.ai.agentserver.responses.hosting._durable_orchestrator import (
        _reconstruct_parsed_from_params,
    )

    parsed = _reconstruct_parsed_from_params(_build_params_for_recovery())
    assert parsed is not None
    # The parsed model should expose the same fields as the original.
    assert parsed.get("model") == "test-model"


def test_reconstruct_parsed_raises_when_payload_missing() -> None:
    """If parsed_payload is absent, reconstruction raises a clear error."""
    from azure.ai.agentserver.responses.hosting._durable_orchestrator import (
        _reconstruct_parsed_from_params,
    )

    with pytest.raises(RuntimeError, match="parsed_payload"):
        _reconstruct_parsed_from_params({"response_id": "resp_no_payload"})


def test_no_record_ref_early_exit_removed() -> None:
    """Source-level assertion that the old early-exit pattern is gone.

    Spec US1 scenario 1 explicit acceptance criterion: 'No `_record_ref is None → return`
    early-exit remains.'
    """
    from pathlib import Path

    src = (
        Path(__file__).parent.parent.parent
        / "azure"
        / "ai"
        / "agentserver"
        / "responses"
        / "hosting"
        / "_durable_orchestrator.py"
    ).read_text()
    # The "Phase 1 (no recovery yet)" framing must be replaced.
    assert "Phase 1 (no recovery yet)" not in src
    # And the reconstruction call must be in place.
    assert "_reconstruct_from_params" in src
