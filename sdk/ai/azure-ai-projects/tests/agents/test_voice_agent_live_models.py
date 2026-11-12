# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline coverage for persisted Live definitions, not session-update DTOs."""

import json

import pytest

from azure.ai.projects import models

_DELEGATIONS = [
    pytest.param(
        models.VoiceAgentLiveClientDelegation,
        {"acknowledgement_delay_ms": 0},
        {"type": "client", "acknowledgement_delay_ms": 0},
        id="client",
    ),
    pytest.param(
        models.VoiceAgentLiveResponsesDelegation,
        {
            "acknowledgement_delay_ms": 0,
            "responses": models.LiveResponsesDelegationSettingsInputParam(
                model="backend-deployment-test", instructions="Answer briefly."
            ),
        },
        {
            "type": "responses",
            "acknowledgement_delay_ms": 0,
            "responses": {"model": "backend-deployment-test", "instructions": "Answer briefly."},
        },
        id="responses",
    ),
    pytest.param(
        models.VoiceAgentLiveManagedAgentDelegation,
        {"agent_name": "prompt-agent-test", "agent_version": "7"},
        {"type": "foundry_managed_agent", "agent_name": "prompt-agent-test", "agent_version": "7"},
        id="foundry_managed_agent",
    ),
]


def _definition_payload(delegation):
    return {
        "kind": "voice",
        "sub_protocol": "live",
        "model_type": "self_deployed",
        "model": "live-deployment-test",
        "instructions": "Delegate the spoken question.",
        "store": False,
        "audio": {
            "format": {"type": "audio/pcm", "rate": 24000},
            "output": {"voice": "marin"},
        },
        "delegation": delegation,
    }


@pytest.mark.parametrize("delegation_type,kwargs,payload", _DELEGATIONS)
def test_live_delegation_writable_json_roundtrip(delegation_type, kwargs, payload):
    delegation = delegation_type(**kwargs)
    writable = delegation.as_dict(exclude_readonly=True)
    assert writable == payload
    restored = delegation_type(json.loads(json.dumps(writable)))
    assert restored.as_dict() == payload
    assert restored.type == payload["type"]
    if "acknowledgement_delay_ms" in payload:
        assert restored.acknowledgement_delay_ms == 0
    else:
        assert restored.agent_name == "prompt-agent-test"
        assert restored.agent_version == "7"


@pytest.mark.parametrize("delegation_type,kwargs,payload", _DELEGATIONS)
def test_live_definition_writable_json_roundtrip(delegation_type, kwargs, payload):
    definition = models.VoiceAgentLiveDefinition(
        model_type=models.VoiceModelType.SELF_DEPLOYED,
        model="live-deployment-test",
        instructions="Delegate the spoken question.",
        store=False,
        audio=models.LiveInitialSessionAudioParam(
            format=models.LiveSessionAudioFormatPCMParam(rate=24000),
            output=models.LiveInitialSessionAudioOutputParam(voice="marin"),
        ),
        delegation=delegation_type(**kwargs),
    )
    expected = _definition_payload(payload)
    assert definition.as_dict(exclude_readonly=True) == expected

    restored = models.VoiceAgentLiveDefinition(json.loads(json.dumps(expected)))
    assert restored.kind == "voice"
    assert restored.sub_protocol == "live"
    assert restored.model_type == "self_deployed"
    assert restored.store is False
    assert isinstance(restored.audio, models.LiveInitialSessionAudioParam)
    assert isinstance(restored.audio.format, models.LiveSessionAudioFormatPCMParam)
    assert restored.audio.format.rate == 24000
    assert isinstance(restored.delegation, delegation_type)
    assert restored.delegation.as_dict() == payload
    assert restored.as_dict() == expected


@pytest.mark.parametrize("delegation_type,kwargs,payload", _DELEGATIONS)
def test_live_agent_version_readback_uses_both_native_discriminators(delegation_type, kwargs, payload):
    wire = {
        "object": "agent.version",
        "id": "live-agent-test:3",
        "name": "live-agent-test",
        "version": "3",
        "created_at": 1700000000,
        "metadata": {},
        "definition": _definition_payload(payload),
    }
    version = models.AgentVersionDetails(json.loads(json.dumps(wire)))
    assert isinstance(version.definition, models.VoiceAgentLiveDefinition)
    assert version.definition.kind == "voice"
    assert version.definition.sub_protocol == "live"
    assert version.definition.model_type == "self_deployed"
    assert isinstance(version.definition.delegation, delegation_type)
    assert version.definition.delegation.as_dict() == delegation_type(**kwargs).as_dict() == payload
    assert version.as_dict() == wire
    if "acknowledgement_delay_ms" in payload:
        assert version.definition.delegation.acknowledgement_delay_ms == 0
    else:
        assert version.definition.delegation.agent_name == "prompt-agent-test"
        assert version.definition.delegation.agent_version == "7"


@pytest.mark.parametrize("agent_version", [None, "7"], ids=["active-version", "pinned-version"])
def test_live_managed_agent_delegation_keeps_optional_version(agent_version):
    kwargs = {"agent_name": "prompt-agent-test"}
    expected = {"type": "foundry_managed_agent", **kwargs}
    if agent_version is not None:
        kwargs["agent_version"] = agent_version
        expected["agent_version"] = agent_version
    definition = models.VoiceAgentLiveDefinition(
        model_type="self_deployed",
        model="live-deployment-test",
        delegation=models.VoiceAgentLiveManagedAgentDelegation(**kwargs),
    )
    writable = json.loads(json.dumps(definition.as_dict(exclude_readonly=True)))
    assert writable["delegation"] == expected
    restored = models.VoiceAgentLiveDefinition(writable)
    assert isinstance(restored.delegation, models.VoiceAgentLiveManagedAgentDelegation)
    assert restored.delegation.type == "foundry_managed_agent"
    assert restored.delegation.agent_version == agent_version
