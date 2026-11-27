# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Fixtures for recording the Voice Agents telephony REST tests.

Set FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_VOICE_MODEL_NAME to a test project
and its Realtime deployment. Binding error-path tests do not need a provider
connection or a provisioned number.

Outbound tests also need FOUNDRY_VOICE_TEST_CONNECTION_NAME for a dedicated
Twilio test connection, FOUNDRY_VOICE_TEST_SOURCE_PHONE_NUMBER for its source
number, and FOUNDRY_VOICE_TEST_DESTINATION_PHONE_NUMBER for a test sink you
control. The jobs and campaigns are scheduled for the next day, expire an
hour later, and are cancelled and deleted by the tests. Never use a customer
connection or phone number.
"""

from datetime import datetime, timedelta, timezone
from functools import partial
import re
from urllib.parse import quote
from uuid import uuid4

from azure.ai.projects import models
from devtools_testutils import (
    EnvironmentVariableLoader,
    add_body_key_sanitizer,
    add_general_regex_sanitizer,
    remove_batch_sanitizers,
)
from devtools_testutils.helpers import get_recording_id

voiceTelephonyServicePreparer = partial(
    EnvironmentVariableLoader,
    "",
    foundry_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    foundry_voice_model_name="sanitized-model-deployment-name",
)
voiceOutboundServicePreparer = partial(
    voiceTelephonyServicePreparer,
    foundry_voice_test_connection_name="sanitized-telephony-connection",
    foundry_voice_test_source_phone_number="+12025550100",
    foundry_voice_test_destination_phone_number="+12025550101",
)

MISSING_BINDING_PHONE_NUMBER = "+12025550183"  # Reserved fictional number in the North American Numbering Plan.
MISSING_CALL_ID = "00000000-0000-4000-8000-000000000001"
TERMINAL_CALL_JOB_STATES = frozenset({"completed", "blocked", "expired", "failed", "cancelled"})
TERMINAL_CAMPAIGN_STATES = frozenset({"completed", "failed", "cancelled"})
POLL_TIMEOUT = 90


def voice_definition(model: str) -> models.VoiceAgentDefinition:
    return models.VoiceAgentDefinition(
        model_type=models.VoiceModelType.MANAGED,
        model=model,
        instructions="You are a voice agent for testing the telephony APIs.",
        audio=models.VoiceAgentAudioConfig(
            output=models.VoiceAgentAudioOutputConfig(
                voice="en-US-AvaNeural", voice_type=models.VoiceType.AZURE_STANDARD
            )
        ),
        output_modalities=[models.VoiceOutputModality.AUDIO],
    )


def sanitize_telephony_value(actual: str, replacement: str) -> None:
    add_general_regex_sanitizer(regex=re.escape(actual), value=replacement, function_scoped=True)
    encoded = quote(actual, safe="")
    if encoded != actual:
        add_general_regex_sanitizer(regex=re.escape(encoded), value=quote(replacement, safe=""), function_scoped=True)


def preserve_telephony_etags() -> None:
    # AZSDK3490 masks response-body ETags but not the corresponding If-Match header.
    recording_id = get_recording_id()
    if recording_id:
        remove_batch_sanitizers(["AZSDK3490"], headers={"x-recording-id": recording_id})


def owned_agent_name(scenario: str, *, live: bool) -> str:
    sanitized = f"voice-telephony-{scenario}"
    if not live:
        return sanitized
    name = f"{sanitized}-{uuid4().hex[:12]}"
    sanitize_telephony_value(name, sanitized)
    for field in ("principal_id", "client_id"):
        add_body_key_sanitizer(
            json_path=f"$..{field}", value="00000000-0000-0000-0000-000000000000", function_scoped=True
        )
    return name


def request_id(number: int, *, live: bool) -> str:
    sanitized = f"00000000-0000-4000-8000-{number:012d}"
    if not live:
        return sanitized
    value = str(uuid4())
    sanitize_telephony_value(value, sanitized)
    return value


def schedule_window(*, live: bool, variables: dict[str, str] | None) -> tuple[datetime, datetime]:
    if live:
        start = (datetime.now(timezone.utc) + timedelta(days=1)).replace(microsecond=0)
    else:
        assert variables is not None, "Playback requires the recorded schedule timestamp."
        start = datetime.fromisoformat(variables["scheduled_at"])
    return start, start + timedelta(hours=1)
