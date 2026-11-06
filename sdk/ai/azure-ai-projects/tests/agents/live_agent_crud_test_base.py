# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Narrow preparer and assertions for persisted Live-agent REST tests."""

import functools
import re
from uuid import uuid4

from azure.ai.projects import models
from devtools_testutils import EnvironmentVariableLoader, add_general_regex_sanitizer

liveAgentServicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "",
    foundry_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    foundry_voice_live_model_name="sanitized-model-deployment-name",
    foundry_model_name="sanitized-model-deployment-name",
)

PROMPT_INSTRUCTIONS = (
    "Handle the delegated question. Return a [thinking] section with a brief task status, "
    "not private reasoning, followed by a [commentary] section containing a short answer."
)


def owned_agent_name(scenario, *, live):
    sanitized = f"sanitized-live-crud-{scenario}"
    if not live:
        return sanitized
    name = f"live-crud-{uuid4().hex}"
    add_general_regex_sanitizer(regex=re.escape(name), value=sanitized, function_scoped=True)
    return name


def sanitize_live_deployments(kwargs):
    # Match the package's session-scoped gpt-* fallback regardless of sanitizer order.
    for key in ("foundry_voice_live_model_name", "foundry_model_name"):
        value = kwargs[key]
        assert value
        add_general_regex_sanitizer(
            regex=re.escape(value), value="sanitized-model-deployment-name", function_scoped=True
        )


def live_definition(mode, live_model, backend_model, instructions, *, backend=None):
    # Startup rejects acknowledgement_delay_ms; its writable JSON remains covered by model tests.
    if mode == "client":
        delegation = models.VoiceAgentLiveClientDelegation()
    elif mode == "responses":
        delegation = models.VoiceAgentLiveResponsesDelegation(
            responses=models.LiveResponsesDelegationSettingsInputParam(
                model=backend_model, instructions="Answer the question briefly."
            ),
        )
    elif mode == "foundry_managed_agent":
        assert backend is not None
        delegation = models.VoiceAgentLiveManagedAgentDelegation(agent_name=backend.name, agent_version=backend.version)
    else:
        raise ValueError(f"Unknown Live delegation mode: {mode}")
    return models.VoiceAgentLiveDefinition(
        model_type=models.VoiceModelType.SELF_DEPLOYED,
        model=live_model,
        instructions=instructions,
        store=False,
        audio=models.LiveInitialSessionAudioParam(
            format=models.LiveSessionAudioFormatPCMParam(rate=24000),
            output=models.LiveInitialSessionAudioOutputParam(voice="marin"),
        ),
        delegation=delegation,
    )


def assert_live_version(version, expected, *, name, version_id=None):
    assert isinstance(version, models.AgentVersionDetails)
    assert version.name == name and version.id and version.version
    if version_id is not None:
        assert version.version == version_id
    definition = version.definition
    assert isinstance(definition, models.VoiceAgentLiveDefinition)
    assert definition.kind == "voice"
    assert definition.sub_protocol == "live"
    assert definition.model_type == "self_deployed"
    assert definition.model == expected.model
    assert definition.instructions == expected.instructions
    assert definition.store is False
    assert isinstance(definition.audio, models.LiveInitialSessionAudioParam)
    assert isinstance(definition.audio.format, models.LiveSessionAudioFormatPCMParam)
    assert definition.audio.format.rate == 24000
    assert definition.audio.output.voice == "marin"
    assert isinstance(definition.delegation, type(expected.delegation))
    assert definition.delegation.type == expected.delegation.type
    if isinstance(definition.delegation, models.VoiceAgentLiveManagedAgentDelegation):
        assert definition.delegation.agent_name == expected.delegation.agent_name
        assert definition.delegation.agent_version == expected.delegation.agent_version
    elif isinstance(definition.delegation, models.VoiceAgentLiveResponsesDelegation):
        assert isinstance(definition.delegation.responses, models.LiveResponsesDelegationSettingsInputParam)
        assert definition.delegation.responses.model == expected.delegation.responses.model
        assert definition.delegation.responses.instructions == expected.delegation.responses.instructions
