# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

"""
Live-only tests for the hand-written async ``async_client.realtime`` WebSocket streaming client.

Async counterpart of ``test_voice_agent_realtime_live.py``. See that module's docstring for the
overall rationale (modeled on the ``azure-ai-voicelive`` package's live realtime test pattern:
skip entirely unless running live, generous per-event timeouts, assert on event types and
content presence/length rather than exact audio bytes).
"""

import asyncio
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
class TestVoiceAgentRealtimeLiveAsync(TestBase):
    """
    Live tests covering ``async_client.realtime.connect()`` (the hand-written async WebSocket
    streaming client) against a real voice agent and a real service connection.
    """

    def _make_agent_name(self, suffix: str) -> str:
        return f"test-realtime-live-async-{suffix}"

    async def _create_basic_agent(self, project_client, agent_name: str, model: str) -> None:
        await project_client.agents.create_version(
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
    # pytest tests\agents\test_voice_agent_realtime_live_async.py::TestVoiceAgentRealtimeLiveAsync::test_realtime_session_lifecycle_async -s
    @servicePreparer()
    async def test_realtime_session_lifecycle_async(self, **kwargs):
        """
        Test opening and cleanly closing a realtime WebSocket session, and receiving the initial
        ``session.created`` handshake event.
        """
        print("\n")
        model = kwargs.get("foundry_voice_model_name")
        assert model is not None
        project_client = self.create_async_client(operation_group="agents", allow_preview=True, **kwargs)
        agent_name = self._make_agent_name("lifecycle")

        try:
            await self._create_basic_agent(project_client, agent_name, model)

            async with project_client.realtime.connect(agent_name=agent_name) as conn:
                event = await asyncio.wait_for(conn.recv(), timeout=_EVENT_TIMEOUT)
                assert isinstance(event, RealtimeServerEventSessionCreated)
                assert event.type == "session.created"
            # The `async with` block above closes the connection; a second `recv()` after close
            # would raise, so we don't attempt one -- clean exit from the block is the assertion.
        finally:
            await project_client.agents.delete(agent_name=agent_name)
            await project_client.close()

    # To run only this test:
    # pytest tests\agents\test_voice_agent_realtime_live_async.py::TestVoiceAgentRealtimeLiveAsync::test_realtime_text_turn_produces_audio_and_transcript_async -s
    @servicePreparer()
    async def test_realtime_text_turn_produces_audio_and_transcript_async(self, **kwargs):
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
        project_client = self.create_async_client(operation_group="agents", allow_preview=True, **kwargs)
        agent_name = self._make_agent_name("text-turn")

        try:
            await self._create_basic_agent(project_client, agent_name, model)

            async with project_client.realtime.connect(agent_name=agent_name) as conn:
                session_created = await asyncio.wait_for(conn.recv(), timeout=_EVENT_TIMEOUT)
                assert isinstance(session_created, RealtimeServerEventSessionCreated)

                await conn.conversation.item.create(
                    item=RealtimeConversationItemMessageUser(
                        type=RealtimeConversationItemType.MESSAGE,
                        content=[
                            RealtimeConversationItemMessageUserContent(
                                type="input_text", text="Say the word 'hello' and nothing else."
                            )
                        ],
                    )
                )
                await conn.response.create()

                audio_delta_count = 0
                audio_bytes = 0
                transcript_done_count = 0
                got_response_done = False
                deadline = time.monotonic() + _RESPONSE_TIMEOUT

                while time.monotonic() < deadline and not got_response_done:
                    remaining = max(deadline - time.monotonic(), 0.1)
                    event = await asyncio.wait_for(conn.recv(), timeout=min(_EVENT_TIMEOUT, remaining))
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
            await project_client.agents.delete(agent_name=agent_name)
            await project_client.close()

    # To run only this test:
    # pytest tests\agents\test_voice_agent_realtime_live_async.py::TestVoiceAgentRealtimeLiveAsync::test_realtime_function_tool_call_async -s
    @servicePreparer()
    async def test_realtime_function_tool_call_async(self, **kwargs):
        """
        Test a client-executed function-tool round trip during a live realtime session.

        Configures the agent with a ``get_weather`` function tool, sends a prompt that should
        trigger it, executes the tool call locally when the service asks for it, and sends the
        result back so the agent can finish its reply -- the async counterpart of
        ``sample_voice_agent_live_function_tool.py``'s pattern, adapted into an automated
        assertion-based test.
        """
        print("\n")
        model = kwargs.get("foundry_voice_model_name")
        assert model is not None
        project_client = self.create_async_client(operation_group="agents", allow_preview=True, **kwargs)
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
            await project_client.agents.create_version(
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

            async with project_client.realtime.connect(agent_name=agent_name) as conn:
                session_created = await asyncio.wait_for(conn.recv(), timeout=_EVENT_TIMEOUT)
                assert isinstance(session_created, RealtimeServerEventSessionCreated)

                await conn.conversation.item.create(
                    item=RealtimeConversationItemMessageUser(
                        type=RealtimeConversationItemType.MESSAGE,
                        content=[
                            RealtimeConversationItemMessageUserContent(
                                type="input_text", text="What's the weather like in Seattle right now?"
                            )
                        ],
                    )
                )
                await conn.response.create()

                tool_call_count = 0
                final_text = ""
                deadline = time.monotonic() + _RESPONSE_TIMEOUT
                done = False

                while time.monotonic() < deadline and not done:
                    remaining = max(deadline - time.monotonic(), 0.1)
                    event = await asyncio.wait_for(conn.recv(), timeout=min(_EVENT_TIMEOUT, remaining))
                    if isinstance(event, RealtimeServerEventResponseFunctionCallArgumentsDone):
                        tool_call_count += 1
                        assert event.name == "get_weather"
                        args = json.loads(event.arguments)
                        assert "city" in args
                        result = _get_weather(**args)
                        await conn.conversation.item.create(
                            item=RealtimeConversationItemFunctionCallOutput(call_id=event.call_id, output=result)
                        )
                        await conn.response.create()
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
            await project_client.agents.delete(agent_name=agent_name)
            await project_client.close()
