# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Tests for cross-process reconstruction in `_execute_in_task` (T-022).

Covers spec 013 US1 deliverable (a) acceptance scenario 1: when the in-memory
references (`_record_ref`, `_context_ref`, `_parsed_ref`, `_cancel_ref`,
`_runtime_state_ref`) are missing from the resilient task input (as they would
be after a cross-process restart), the orchestrator reconstructs them from
the serialized params and proceeds.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest


def _build_params_for_recovery() -> dict:
    """Build a resilient-task input dict via the single producer
    (``ResilientResponseInput.to_task_input``) — exactly what ``start_resilient``
    persists and what cross-process recovery reads back."""
    from azure.ai.agentserver.responses.hosting._resilient_input import (
        ResilientResponseInput,
    )
    from azure.ai.agentserver.responses.models._generated import CreateResponse

    request = CreateResponse(
        {
            "input": "hello",
            "model": "test-model",
            "stream": False,
            "store": True,
            "background": True,
            "conversation": "conv_abc",
        }
    )
    return ResilientResponseInput(
        request=request,
        response_id="resp_recover_001",
        disposition="re-invoke",
        agent_reference={"name": "test-agent"},
        agent_session_id="session_xyz",
        user_id_key=None,
        client_headers={"client-trace-id": "abc"},
        query_parameters={"q": "1"},
    ).to_task_input()


def test_reconstruct_from_params_returns_record_and_context() -> None:
    """``_reconstruct_from_params`` rebuilds ResponseExecution and ResponseContext."""
    from azure.ai.agentserver.responses._options import ResponsesServerOptions
    from azure.ai.agentserver.responses.hosting._resilient_orchestrator import (
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


def test_reconstruct_preserves_client_headers_and_query() -> None:  # Spec 033 FR-002b
    """A recovered handler observes the SAME ``client_headers`` /
    ``query_parameters`` as fresh entry — they MUST NOT be dropped to ``{}``
    on recovery (the latent drop bug §3.1 fixes)."""
    from azure.ai.agentserver.responses._options import ResponsesServerOptions
    from azure.ai.agentserver.responses.hosting._resilient_orchestrator import (
        _reconstruct_from_params,
    )

    _, context = _reconstruct_from_params(
        params=_build_params_for_recovery(),
        response_id="resp_recover_001",
        provider=None,
        runtime_state=None,
        runtime_options=ResponsesServerOptions(),
    )
    assert context.client_headers == {"client-trace-id": "abc"}
    assert context.query_parameters == {"q": "1"}


def test_reconstruct_uses_response_id_from_params_not_regenerated() -> None:
    """Reconstruction must use params['response_id'], never generate a new one.

    Spec US1 scenario 7 — response-id stability regression guard.
    """
    from azure.ai.agentserver.responses._options import ResponsesServerOptions
    from azure.ai.agentserver.responses.hosting._resilient_orchestrator import (
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


def test_reconstruct_parsed_re_parses_request() -> None:
    """``_reconstruct_parsed_from_params`` re-hydrates the request model from
    the single persisted ``request`` (Spec 033 §3.1)."""
    from azure.ai.agentserver.responses.hosting._resilient_orchestrator import (
        _reconstruct_parsed_from_params,
    )

    parsed = _reconstruct_parsed_from_params(_build_params_for_recovery())
    assert parsed is not None
    # The parsed model should expose the same fields as the original.
    assert parsed.get("model") == "test-model"


def test_reconstruct_parsed_raises_when_request_missing() -> None:
    """If the persisted request is absent, reconstruction fails closed
    (Spec 033 FR-002f)."""
    from azure.ai.agentserver.responses.hosting._resilient_orchestrator import (
        _reconstruct_parsed_from_params,
    )

    with pytest.raises(ValueError, match="request"):
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
        / "_resilient_orchestrator.py"
    ).read_text()
    # The "Phase 1 (no recovery yet)" framing must be replaced.
    assert "Phase 1 (no recovery yet)" not in src
    # And the reconstruction call must be in place.
    assert "_reconstruct_from_params" in src
