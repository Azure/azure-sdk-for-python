# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared fixtures for the recorded and live test suites in this package."""
import functools

from devtools_testutils import EnvironmentVariableLoader

from azure.ai.voiceagents.models import AgentDefinitionOptInKeys

# All voice agent operations currently require this preview feature opt-in.
PREVIEW = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

# Loads the real environment variables in live mode, and sanitizes them to the
# values below when recording (so secrets/identifiers never end up in the
# checked-in cassette) and in playback (so recorded interactions can be
# matched). Kwarg names are uppercased to get the real environment variable
# name, e.g. azure_voice_agents_endpoint -> AZURE_VOICE_AGENTS_ENDPOINT.
VoiceAgentsPreparer = functools.partial(
    EnvironmentVariableLoader,
    "",
    azure_voice_agents_endpoint="https://sanitized-account.services.ai.azure.com/api/projects/sanitized-project",
    azure_voice_agents_agent_name="sanitized-agent-name",
    azure_voice_agents_conversation_id="sanitized-conversation-id",
)
