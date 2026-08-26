# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Unit tests for public enum values.

These guard against accidental changes to the wire values that the service
depends on. They are offline and require no credentials or network.
"""

from azure.ai.voiceagents.models import (
    AgentDefinitionOptInKeys,
    AgentState,
    AzureVoiceType,
    VoiceModelType,
    VoiceOutputModality,
    VoiceSystemToolName,
)


def test_agent_definition_opt_in_keys_wire_values():
    assert AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW == "VoiceAgents=V1Preview"


def test_voice_model_type_wire_values():
    assert VoiceModelType.MANAGED == "managed"
    assert VoiceModelType.SELF_DEPLOYED == "self_deployed"


def test_azure_voice_type_wire_values():
    assert AzureVoiceType.AZURE_STANDARD == "azure-standard"


def test_voice_output_modality_wire_values():
    assert VoiceOutputModality.AUDIO == "audio"
    assert VoiceOutputModality.TEXT == "text"


def test_voice_system_tool_name_wire_values():
    assert VoiceSystemToolName.END_CONVERSATION == "end_conversation"


def test_agent_state_wire_values():
    assert AgentState.ENABLED == "enabled"
    assert AgentState.DISABLED == "disabled"
