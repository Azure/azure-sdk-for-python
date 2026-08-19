# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for the typed resilient-recovery boundary (Spec 033 §3.1).

Covers FR-001 (single typed producer/consumer), FR-002 (input embedded once,
fail-closed serialization, the ``agent_reference`` regression generalized),
FR-002f (fail-closed on malformed persisted input), and FR-003 (single isolation
derivation).
"""

from __future__ import annotations

import json

import pytest

from azure.ai.agentserver.responses.hosting._resilient_input import (
    ResilientResponseInput,
    RuntimeRefs,
    platform_context_from_params,
)
from azure.ai.agentserver.responses.models._generated import AgentReference, CreateResponse


def _make_request() -> CreateResponse:
    return CreateResponse(
        {
            "input": "crash during task",
            "model": "test-model",
            "store": True,
            "stream": False,
            "background": True,
        }
    )


def _make_input(**overrides) -> ResilientResponseInput:
    kwargs = dict(
        request=_make_request(),
        response_id="resp_abc",
        disposition="re-invoke",
        agent_reference={"name": "a", "version": "1"},
        agent_session_id="sess_1",
        user_id_key="user-key",
        call_id="call-key",
        client_headers={"client-trace-id": "t-1"},
        query_parameters={"foo": "bar"},
    )
    kwargs.update(overrides)
    return ResilientResponseInput(**kwargs)


# --------------------------------------------------------------------------- #
# FR-001 / FR-002 — single producer/consumer, input embedded once
# --------------------------------------------------------------------------- #


def test_round_trip_preserves_all_fields() -> None:
    """``to_task_input`` → ``from_task_input`` preserves every persisted field."""
    original = _make_input()
    restored = ResilientResponseInput.from_task_input(original.to_task_input())

    assert restored.response_id == "resp_abc"
    assert restored.disposition == "re-invoke"
    assert restored.agent_session_id == "sess_1"
    assert restored.user_id_key == "user-key"
    assert restored.call_id == "call-key"
    assert restored.client_headers == {"client-trace-id": "t-1"}
    assert restored.query_parameters == {"foo": "bar"}
    # request carries the input — once.
    assert restored.request["input"] == "crash during task"
    assert restored.request["model"] == "test-model"
    assert restored.request["store"] is True


def test_input_embedded_once_no_input_items_key() -> None:
    """FR-002: the conversation input lives only inside the persisted request;
    there is no separate ``input_items`` persisted key."""
    params = _make_input().to_task_input()
    assert "input_items" not in params
    assert "request" in params
    # the input is recoverable from the request alone
    assert ResilientResponseInput.from_task_input(params).request["input"] == "crash during task"


def test_to_task_input_is_json_serializable_fail_closed() -> None:
    """FR-002: ``to_task_input`` asserts JSON-safety (no leaked model/ref)."""
    params = _make_input().to_task_input()
    # Must not raise — the producer guarantees JSON-safety.
    json.dumps(params)


def test_agent_reference_model_is_normalized_not_leaked() -> None:
    """FR-002 (the ``agent_reference`` regression generalized): an
    ``AgentReference`` model is normalized to a plain dict so it cannot leak a
    non-serializable value into the resilient input."""
    resilient = _make_input(agent_reference=AgentReference(name="agent-x", version="2"))
    params = resilient.to_task_input()  # would raise TypeError if the model leaked
    json.dumps(params)
    assert isinstance(params["agent_reference"], dict)
    assert params["agent_reference"]["name"] == "agent-x"


def test_runtime_refs_never_serialized() -> None:
    """FR-001: runtime object refs live in RuntimeRefs, never in the input."""
    refs = RuntimeRefs(record=object(), context=object(), parsed=object(), cancel=object(), runtime_state=object())
    params = _make_input().to_task_input()
    for ref_key in ("_record_ref", "_context_ref", "_parsed_ref", "_cancel_ref", "_runtime_state_ref"):
        assert ref_key not in params
    # RuntimeRefs holds the live objects out-of-band.
    assert refs.record is not None and refs.context is not None


# --------------------------------------------------------------------------- #
# FR-002f — fail-closed on malformed persisted input
# --------------------------------------------------------------------------- #


def test_from_task_input_missing_request_raises() -> None:
    with pytest.raises(ValueError):
        ResilientResponseInput.from_task_input({"response_id": "resp_abc"})


def test_from_task_input_missing_response_id_raises() -> None:
    with pytest.raises(ValueError):
        ResilientResponseInput.from_task_input({"request": {"input": "hi"}})


def test_from_task_input_non_dict_raises() -> None:
    with pytest.raises(ValueError):
        ResilientResponseInput.from_task_input(None)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# FR-003 — single isolation derivation
# --------------------------------------------------------------------------- #


def test_isolation_method_and_params_helper_agree() -> None:
    """The typed ``platform_context()`` and the params-based ``platform_context_from_params``
    produce the same identity pair — the single derivation.

    Both the durable ``user_id_key`` and the ``call_id`` captured at creation are
    persisted and replayed on recovery (protocol ``2.0.0``)."""
    resilient = _make_input()
    params = resilient.to_task_input()

    iso_typed = resilient.platform_context()
    iso_params = platform_context_from_params(params)

    assert iso_typed.user_id_key == iso_params.user_id_key == "user-key"
    assert iso_typed.call_id == iso_params.call_id == "call-key"


def test_isolation_absent_keys_default_to_none() -> None:
    resilient = _make_input(user_id_key=None, call_id=None)
    iso = resilient.platform_context()
    assert iso.user_id_key is None
    assert iso.call_id is None
