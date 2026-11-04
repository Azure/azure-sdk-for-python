# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline coverage for Foundry-owned GPT Live protocol metadata."""

from collections.abc import Mapping
from typing import get_type_hints

import pytest

from azure.ai.projects import models, operations
from azure.ai.projects.aio import operations as async_operations


def _session(delegation):
    return {
        "id": "live-session-test",
        "model": "synthetic-live-model",
        "expires_at": 2000000000,
        "status": "active",
        "delegation": delegation,
    }


@pytest.mark.parametrize(
    "event_model,event_type",
    [
        (models.LiveServerEventLiveSessionStarted, "session.started"),
        (models.LiveServerEventLiveSessionUpdated, "session.updated"),
        (models.LiveServerEventLiveSessionClosed, "session.closed"),
    ],
)
def test_live_lifecycle_snapshots_report_the_pinned_foundry_delegation(event_model, event_type):
    delegation = {
        "type": "foundry_managed_agent",
        "agent_name": "prompt-agent-test",
        "agent_version": "7",
    }
    payload = {
        "type": event_type,
        "event_id": "event-test",
        "session": _session(delegation),
    }
    if event_type == "session.started":
        payload["conversation_id"] = "conversation-test"
    elif event_type == "session.closed":
        payload.update(reason="close_requested", usage={"seconds": 1.25})

    event = event_model(payload)

    assert isinstance(event.session, models.VoiceAgentLiveSessionResource)
    assert isinstance(event.session.delegation, Mapping)
    assert event.session.delegation["type"] == "foundry_managed_agent"
    assert event.session.delegation["agent_name"] == "prompt-agent-test"
    assert event.session.delegation["agent_version"] == "7"
    assert event.session.status == "active"
    assert event.as_dict() == payload


@pytest.mark.parametrize("target", ["client", "responses", "foundry_managed_agent"])
def test_live_delegation_created_reports_the_effective_owner_without_task_content(target):
    payload = {
        "type": "session.delegation.created",
        "event_id": "event-test",
        "offset_ms": 0,
        "delegation": {"type": "delegation", "id": "delegation-test", "target": target},
    }
    if target == "responses":
        payload["delegation"]["response_id"] = "response-test"

    event = models.LiveServerEventLiveDelegationCreated(payload)

    assert isinstance(event.delegation, models.VoiceAgentLiveDelegationItem)
    assert event.delegation.target == target
    assert event.delegation.id == "delegation-test"
    assert "input" not in event.delegation and "task" not in event.delegation
    assert event.as_dict() == payload


@pytest.mark.parametrize(
    "delegation",
    [
        None,
        {"type": "client"},
        {"type": "responses", "model": "synthetic-responses-model"},
    ],
)
def test_foundry_live_session_preserves_native_and_null_delegation_modes(delegation):
    payload = _session(delegation)
    session = models.VoiceAgentLiveSessionResource(payload)

    if delegation is None:
        assert session.delegation is None
    else:
        assert isinstance(session.delegation, Mapping)
        assert dict(session.delegation) == delegation
    assert session.as_dict() == payload


def test_foundry_live_protocol_metadata_models_are_publicly_exported():
    assert "VoiceAgentLiveSessionResource" in models.__all__
    assert "VoiceAgentLiveDelegationItem" in models.__all__


@pytest.mark.parametrize(
    "session_type,session_arguments,delegation_type,delegation_arguments,expected_delegation",
    [
        (
            models.LiveSessionCreateParams,
            {"model": "synthetic-live-model"},
            models.LiveSessionCreateParamsDelegationLiveClientDelegationParam,
            {"acknowledgement_delay_ms": 0},
            {"type": "client", "acknowledgement_delay_ms": 0},
        ),
        (
            models.LiveSessionCreateParams,
            {"model": "synthetic-live-model"},
            models.LiveSessionCreateParamsDelegationLiveResponsesDelegationParam,
            {"responses": models.LiveResponsesDelegationSettingsInputParam(model="synthetic-backend-model")},
            {"type": "responses", "responses": {"model": "synthetic-backend-model"}},
        ),
        (
            models.LiveSessionUpdateParams,
            {},
            models.LiveSessionUpdateParamsDelegationLiveClientDelegationParam,
            {"acknowledgement_delay_ms": 0},
            {"type": "client", "acknowledgement_delay_ms": 0},
        ),
        (
            models.LiveSessionUpdateParams,
            {},
            models.LiveResponsesDelegationUpdateParam,
            {"responses": models.LiveResponsesDelegationSettingsUpdateInputParam(instructions="Keep replies brief.")},
            {"type": "responses", "responses": {"instructions": "Keep replies brief."}},
        ),
    ],
)
def test_native_live_session_delegation_discriminators_round_trip(
    session_type, session_arguments, delegation_type, delegation_arguments, expected_delegation
):
    delegation = delegation_type(**delegation_arguments)
    session = session_type(**session_arguments, delegation=delegation)
    expected = {**session_arguments, "delegation": expected_delegation}

    assert session.as_dict(exclude_readonly=True) == expected

    restored = session_type(expected)
    assert isinstance(restored.delegation, delegation_type)
    assert restored.as_dict() == expected


@pytest.mark.parametrize("operation_module", [operations, async_operations])
def test_live_conversation_operation_type_is_public(operation_module):
    assert "BetaVoiceAgentsLiveConversationsOperations" in operation_module.__all__
    annotations = get_type_hints(operation_module.BetaVoiceAgentsOperations)
    assert annotations["live_conversations"] is operation_module.BetaVoiceAgentsLiveConversationsOperations


@pytest.mark.parametrize(
    "destination_type,arguments,payload",
    [
        (
            models.VoiceAgentRoutinePostCallDestination,
            {"name": "routine-test"},
            {"type": "routine", "name": "routine-test"},
        ),
        (
            models.VoiceAgentEventGridPostCallDestination,
            {"connection_name": "connection-test"},
            {"type": "event_grid", "connection_name": "connection-test"},
        ),
    ],
)
def test_post_call_destination_configuration_round_trip(destination_type, arguments, payload):
    configuration = models.VoiceAgentPostCallConfig(destinations=[destination_type(**arguments)])
    expected = {"destinations": [payload]}
    assert configuration.as_dict() == expected

    restored = models.VoiceAgentPostCallConfig(expected)
    assert isinstance(restored.destinations[0], destination_type)
    assert restored.as_dict() == expected
