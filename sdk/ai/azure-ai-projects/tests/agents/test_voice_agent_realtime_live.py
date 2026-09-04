# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

"""
Live-only tests for the hand-written sync ``client.realtime`` WebSocket streaming client.

Unlike ``tests/agents/test_realtime_client.py`` (which mocks the transport to unit-test URL
construction, auth, and error paths without a live service), these tests open a REAL WebSocket
connection to a live voice agent and assert on the actual streamed server events. They are
modeled on the live realtime test pattern used by the ``azure-ai-voicelive`` package
(``sdk/voicelive/azure-ai-voicelive/tests/live/``): skip entirely unless running live, use
generous per-event timeouts, and assert on event *types* and content presence/length rather than
exact audio bytes (the model's actual audio/text output is not deterministic).

These tests do not use ``store=True`` / read back a persisted conversation -- that surface
(``project_client.beta.agent_endpoint_conversations.*``) is covered by the separate recorded
tests in ``test_voice_agent_conversations.py``, which need a real conversation id but replay
against a recorded cassette rather than opening a live WebSocket connection on every run.
"""

import json
import time
from typing import Any, cast, Final

import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live
from azure.ai.projects.models import (
    RealtimeConversationItemFunctionCallOutput,
    RealtimeConversationItemMessageUser,
    RealtimeConversationItemMessageUserContent,
    RealtimeConversationItemType,
    RealtimeServerEventError,
    RealtimeServerEventResponseAudioDelta,
    RealtimeServerEventResponseAudioTranscriptDone,
    RealtimeServerEventResponseDone,
    RealtimeServerEventResponseFunctionCallArgumentsDone,
    RealtimeServerEventResponseTextDone,
    RealtimeServerEventSessionCreated,
    VoiceAgentAudioConfig,
    VoiceAgentAudioOutputConfig,
    VoiceAgentDefinition,
    VoiceAgentFunctionTool,
    VoiceModelType,
    VoiceOutputModality,
)

# Seconds to wait for a single server event (session handshake, an audio delta, ...).
_EVENT_TIMEOUT: Final = 30
# Seconds to wait for a full response turn to finish (may include a tool round-trip).
_RESPONSE_TIMEOUT: Final = 45


def _get_weather(city: str) -> str:
    """A trivial local "tool" implementation the agent can call.

    :param city: The city to look up.
    :type city: str
    :return: A canned weather report for the city.
    :rtype: str
    """
    return json.dumps({"city": city, "condition": "sunny", "temperature_f": 72})


@pytest.mark.live_test_only
@pytest.mark.skipif(
    not is_live(),
    reason="Live-only: opens a real WebSocket connection to the realtime service, which cannot "
    "be captured/replayed by the test proxy.",
)
class TestVoiceAgentRealtimeLive(TestBase):
    """
    Live tests covering ``client.realtime.connect()`` (the hand-written sync WebSocket streaming
    client) against a real voice agent and a real service connection.
    """

    def _make_agent_name(self, suffix: str) -> str:
        return f"test-realtime-live-{suffix}"

    def _create_basic_agent(self, project_client, agent_name: str, model: str) -> None:
        project_client.agents.create_version(
            agent_name=agent_name,
            definition=VoiceAgentDefinition(
                model_type=VoiceModelType.MANAGED,
                model=model,
                instructions="You are a helpful voice assistant. Keep replies short.",
                audio=VoiceAgentAudioConfig(
                    output=VoiceAgentAudioOutputConfig(voice="en-US-AvaNeural", voice_type="azure-standard")
                ),
                output_modalities=[VoiceOutputModality.AUDIO],
            ),
        )

    # To run only this test:
    # pytest tests\agents\test_voice_agent_realtime_live.py::TestVoiceAgentRealtimeLive::test_realtime_session_lifecycle -s
    @servicePreparer()
    def test_realtime_session_lifecycle(self, **kwargs):
        """
        Test opening and cleanly closing a realtime WebSocket session, and receiving the initial
        ``session.created`` handshake event.
        """
        print("\n")
        model = kwargs.get("foundry_voice_model_name")
        assert model is not None
        project_client = self.create_client(operation_group="agents", allow_preview=True, **kwargs)
        agent_name = self._make_agent_name("lifecycle")

        try:
            self._create_basic_agent(project_client, agent_name, model)

            with project_client.realtime.connect(agent_name=agent_name) as conn:
                event = conn.recv(timeout=_EVENT_TIMEOUT)
                assert isinstance(event, RealtimeServerEventSessionCreated)
                assert event.type == "session.created"
            # The `with` block above closes the connection; a second `recv()` after close
            # would raise, so we don't attempt one -- clean exit from the block is the assertion.
        finally:
            project_client.agents.delete(agent_name=agent_name)

    # To run only this test:
    # pytest tests\agents\test_voice_agent_realtime_live.py::TestVoiceAgentRealtimeLive::test_realtime_text_turn_produces_audio_and_transcript -s
    @servicePreparer()
    def test_realtime_text_turn_produces_audio_and_transcript(self, **kwargs):
        """
        Test sending one typed user turn and receiving a streamed audio + transcript reply.

        Sends a ``RealtimeConversationItemMessageUser`` text turn and asserts that the service
        streams back at least one non-empty audio delta, a transcript-done event with non-empty
        text, and a final ``response.done``. Content is not asserted verbatim (the model's actual
        wording is not deterministic); only event types, ordering-independent presence, and basic
        size/non-emptiness are checked, matching the ``azure-ai-voicelive`` live test convention.
        """
        print("\n")
        model = kwargs.get("foundry_voice_model_name")
        assert model is not None
        project_client = self.create_client(operation_group="agents", allow_preview=True, **kwargs)
        agent_name = self._make_agent_name("text-turn")

        try:
            self._create_basic_agent(project_client, agent_name, model)

            with project_client.realtime.connect(agent_name=agent_name) as conn:
                session_created = conn.recv(timeout=_EVENT_TIMEOUT)
                assert isinstance(session_created, RealtimeServerEventSessionCreated)

                conn.conversation.item.create(
                    item=RealtimeConversationItemMessageUser(
                        type=RealtimeConversationItemType.MESSAGE,
                        content=[
                            RealtimeConversationItemMessageUserContent(
                                type="input_text", text="Say the word 'hello' and nothing else."
                            )
                        ],
                    )
                )
                conn.response.create()

                audio_delta_count = 0
                audio_bytes = 0
                transcript_done_count = 0
                got_response_done = False
                deadline = time.monotonic() + _RESPONSE_TIMEOUT

                while time.monotonic() < deadline and not got_response_done:
                    event = conn.recv(timeout=_EVENT_TIMEOUT)
                    if isinstance(event, RealtimeServerEventResponseAudioDelta):
                        audio_delta_count += 1
                        audio_bytes += len(event.delta)
                    elif isinstance(event, RealtimeServerEventResponseAudioTranscriptDone):
                        transcript_done_count += 1
                        assert event.transcript is not None and len(event.transcript.strip()) > 0
                    elif isinstance(event, RealtimeServerEventResponseDone):
                        got_response_done = True
                    elif isinstance(event, RealtimeServerEventError):
                        pytest.fail(f"Session error: {event.error.message}")

                assert got_response_done, "Did not receive response.done within the timeout"
                assert audio_delta_count > 0, "Expected at least one response.audio.delta event"
                assert audio_bytes > 0, "Expected non-empty streamed audio"
                assert transcript_done_count == 1, "Expected exactly one audio-transcript-done event"
        finally:
            project_client.agents.delete(agent_name=agent_name)

    # To run only this test:
    # pytest tests\agents\test_voice_agent_realtime_live.py::TestVoiceAgentRealtimeLive::test_realtime_function_tool_call -s
    @servicePreparer()
    def test_realtime_function_tool_call(self, **kwargs):
        """
        Test a client-executed function-tool round trip during a live realtime session.

        Configures the agent with a ``get_weather`` function tool, sends a prompt that should
        trigger it, executes the tool call locally when the service asks for it, and sends the
        result back so the agent can finish its reply -- mirroring
        ``samples/agents/voice/sample_voice_agent_live_function_tool.py``, which this test
        adapts into an automated assertion-based form.
        """
        print("\n")
        model = kwargs.get("foundry_voice_model_name")
        assert model is not None
        project_client = self.create_client(operation_group="agents", allow_preview=True, **kwargs)
        agent_name = self._make_agent_name("tool-call")

        get_weather_tool = VoiceAgentFunctionTool(
            name="get_weather",
            description="Get the current weather for a city.",
            parameters=cast(
                Any,
                {
                    "type": "object",
                    "properties": {"city": {"type": "string", "description": "City name, e.g. Seattle."}},
                    "required": ["city"],
                },
            ),
        )

        try:
            project_client.agents.create_version(
                agent_name=agent_name,
                definition=VoiceAgentDefinition(
                    model_type=VoiceModelType.MANAGED,
                    model=model,
                    instructions=(
                        "You are a helpful voice assistant. Use the get_weather tool when the "
                        "caller asks about the weather, then answer using its result."
                    ),
                    output_modalities=[VoiceOutputModality.TEXT],
                    tools=[get_weather_tool],
                ),
            )

            with project_client.realtime.connect(agent_name=agent_name) as conn:
                session_created = conn.recv(timeout=_EVENT_TIMEOUT)
                assert isinstance(session_created, RealtimeServerEventSessionCreated)

                conn.conversation.item.create(
                    item=RealtimeConversationItemMessageUser(
                        type=RealtimeConversationItemType.MESSAGE,
                        content=[
                            RealtimeConversationItemMessageUserContent(
                                type="input_text", text="What's the weather like in Seattle right now?"
                            )
                        ],
                    )
                )
                conn.response.create()

                tool_call_count = 0
                final_text = ""
                deadline = time.monotonic() + _RESPONSE_TIMEOUT
                done = False

                while time.monotonic() < deadline and not done:
                    event = conn.recv(timeout=_EVENT_TIMEOUT)
                    if isinstance(event, RealtimeServerEventResponseFunctionCallArgumentsDone):
                        tool_call_count += 1
                        assert event.name == "get_weather"
                        args = json.loads(event.arguments)
                        assert "city" in args
                        result = _get_weather(**args)
                        conn.conversation.item.create(
                            item=RealtimeConversationItemFunctionCallOutput(call_id=event.call_id, output=result)
                        )
                        conn.response.create()
                    elif isinstance(event, RealtimeServerEventResponseTextDone):
                        final_text = event.text
                    elif isinstance(event, RealtimeServerEventResponseDone):
                        # A response.done that isn't itself a function call is the final answer.
                        # Output items surface as plain mappings (open union) or typed models.
                        output = event.response.output or []
                        is_function_call = any(
                            (item.get("type") if isinstance(item, dict) else getattr(item, "type", None))
                            == "function_call"
                            for item in output
                        )
                        if not is_function_call:
                            done = True
                    elif isinstance(event, RealtimeServerEventError):
                        pytest.fail(f"Session error: {event.error.message}")

                assert done, "Did not receive a final (non-tool-call) response.done within the timeout"
                assert tool_call_count >= 1, "Expected the agent to invoke the get_weather tool at least once"
                assert final_text is not None and len(final_text.strip()) > 0
        finally:
            project_client.agents.delete(agent_name=agent_name)
