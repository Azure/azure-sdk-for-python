# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline execution of the Realtime text and local function-tool sample entrypoints."""

import asyncio
import base64
from collections import deque
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from azure.ai.projects import models
from azure.ai.projects.operations import BetaRealtimeConnection

pytestmark = pytest.mark.asyncio
_SAMPLE_DIRECTORY = Path(__file__).resolve().parents[2].joinpath("samples", "agents", "voice")
_ENDPOINT = "https://example.invalid/api/projects/offline"
_AGENT_NAME = "realtime-offline"
_OWNED_VERSION = "owned-realtime-version"
_CONVERSATION_ID = "conversation-offline"
_TEXT_SAMPLES = ("sample_voice_agent_realtime_text_conversation_async.py",)
_TOOL_SAMPLE = "sample_voice_agent_realtime_function_tool_async.py"


def _load_sample(monkeypatch, filename):
    name = f"offline_{Path(filename).stem}"
    spec = importlib.util.spec_from_file_location(name, _SAMPLE_DIRECTORY.joinpath(filename))
    assert spec is not None and spec.loader is not None
    sample = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, sample)
    spec.loader.exec_module(sample)
    return sample


def _session_created():
    return models.RealtimeServerEventSessionCreated(
        {
            "event_id": "session-created",
            "session": {"id": "session-offline", "type": "realtime"},
            "conversation_id": _CONVERSATION_ID,
        }
    )


def _response_created(response_id):
    return models.RealtimeServerEventResponseCreated(
        {"event_id": f"created-{response_id}", "response": {"id": response_id, "status": "in_progress"}}
    )


def _response_done(response_id, *, status="completed", output=None):
    return models.RealtimeServerEventResponseDone(
        {
            "event_id": f"done-{response_id}",
            "response": {"id": response_id, "status": status, "output": output or []},
        }
    )


def _transcript_done(response_id, transcript):
    return models.RealtimeServerEventResponseAudioTranscriptDone(
        {
            "event_id": f"transcript-{response_id}",
            "response_id": response_id,
            "item_id": f"item-{response_id}",
            "output_index": 0,
            "content_index": 0,
            "transcript": transcript,
        }
    )


def _error():
    return models.RealtimeServerEventError(
        {
            "type": "error",
            "event_id": "error-offline",
            "error": {"type": "invalid_request_error", "message": "offline command rejected"},
        }
    )


def _function_arguments(*, call_id="canonical-call-test", name="get_weather", arguments='{"city":"Seattle"}'):
    return models.RealtimeServerEventResponseFunctionCallArgumentsDone(
        {
            "event_id": f"arguments-{call_id}",
            "response_id": "tool-response",
            "item_id": f"item-{call_id}",
            "output_index": 0,
            "call_id": call_id,
            "name": name,
            "arguments": arguments,
        }
    )


@pytest.fixture(params=["ga", "legacy"], ids=["ga-output-events", "legacy-output-events"])
def realtime_output_event(request):
    event_types = {
        "audio.delta": (
            "response.output_audio.delta",
            "response.audio.delta",
            models.RealtimeServerEventResponseAudioDelta,
        ),
        "audio.done": (
            "response.output_audio.done",
            "response.audio.done",
            models.RealtimeServerEventResponseAudioDone,
        ),
        "audio_transcript.delta": (
            "response.output_audio_transcript.delta",
            "response.audio_transcript.delta",
            models.RealtimeServerEventResponseAudioTranscriptDelta,
        ),
        "audio_transcript.done": (
            "response.output_audio_transcript.done",
            "response.audio_transcript.done",
            models.RealtimeServerEventResponseAudioTranscriptDone,
        ),
        "text.delta": (
            "response.output_text.delta",
            "response.text.delta",
            models.RealtimeServerEventResponseTextDelta,
        ),
        "text.done": (
            "response.output_text.done",
            "response.text.done",
            models.RealtimeServerEventResponseTextDone,
        ),
    }

    def parse(kind, response_id, **fields):
        ga_type, legacy_type, event_model = event_types[kind]
        event_type = ga_type if request.param == "ga" else legacy_type
        if kind == "audio.delta":
            fields["delta"] = base64.b64encode(fields["delta"]).decode("ascii")
        payload = {
            "type": event_type,
            "event_id": f"{kind}-{response_id}",
            "response_id": response_id,
            "item_id": f"item-{response_id}",
            "output_index": 0,
            "content_index": 0,
            **fields,
        }
        transport = MagicMock()
        transport.recv.return_value = json.dumps(payload)
        with BetaRealtimeConnection(transport) as connection:
            event = connection.recv()
        if request.param == "ga":
            assert type(event) is event_model
            assert event.as_dict() == payload
        else:
            assert type(event) is dict
            assert event == payload
        assert event["type"] == event_type
        return event

    return parse


class _SampleHarness:
    """Provide strict scripted receives and record sends without replacing the sample loops."""

    def __init__(self, monkeypatch, filename):
        self.is_async = filename.endswith("_async.py")
        self.is_text = filename in _TEXT_SAMPLES
        self.events = deque()
        self.prompts = deque()
        self.actions = []
        self.players = []
        self.client = MagicMock()
        self.credential = MagicMock()
        self.connection = MagicMock()
        self.manager = self.client.voice_agents.realtime.connect.return_value
        mock_type = AsyncMock if self.is_async else MagicMock

        for resource in (self.client, self.credential):
            getattr(resource, "__aenter__" if self.is_async else "__enter__").return_value = resource
            getattr(resource, "__aexit__" if self.is_async else "__exit__").return_value = False
        getattr(self.manager, "__aenter__" if self.is_async else "__enter__").return_value = self.connection
        getattr(self.manager, "__aexit__" if self.is_async else "__exit__").return_value = False

        self.client.agents.create_version = mock_type(return_value=SimpleNamespace(version=_OWNED_VERSION))
        self.client.agents.delete_version = mock_type()
        self.connection.recv = mock_type(side_effect=self._receive)
        self.connection.conversation.item.create = mock_type(side_effect=self._create_item)
        self.connection.response.create = mock_type(side_effect=self._create_response)
        self.connection.response.cancel = mock_type(side_effect=self._cancel_response)
        if self.is_async:
            self.connection.__aiter__.side_effect = self._iterate

        self.conversations = self.client.voice_agents.conversations
        self.conversations.get = mock_type(
            return_value=SimpleNamespace(id=_CONVERSATION_ID, status="completed", created_at=0)
        )
        persisted_items = [
            {"id": "stored-user", "role": "user", "content": [{"text": "Stored user turn."}]},
            {"id": "stored-agent", "role": "assistant", "content": [{"transcript": "Stored assistant turn."}]},
        ]
        if self.is_async:
            page = MagicMock()
            page.__aiter__.return_value = persisted_items
            self.conversations.list_items.return_value = page
        else:
            self.conversations.list_items.return_value = persisted_items

        monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", _ENDPOINT)
        monkeypatch.setenv("FOUNDRY_VOICE_AGENT_MODEL", "realtime-deployment-offline")
        monkeypatch.setenv("FOUNDRY_VOICE_AGENT_NAME", _AGENT_NAME)
        monkeypatch.setattr("dotenv.load_dotenv", lambda: False)
        monkeypatch.setitem(sys.modules, "pyaudio", None)
        self.client_factory = MagicMock(return_value=self.client)
        self.credential_factory = MagicMock(return_value=self.credential)
        namespace = "azure.ai.projects.aio" if self.is_async else "azure.ai.projects"
        identity_namespace = "azure.identity.aio" if self.is_async else "azure.identity"
        monkeypatch.setattr(f"{namespace}.AIProjectClient", self.client_factory)
        monkeypatch.setattr(f"{identity_namespace}.DefaultAzureCredential", self.credential_factory)
        monkeypatch.setattr("builtins.input", self._read_input)
        self.sample = _load_sample(monkeypatch, filename)
        if self.is_text:
            speaker_type = self.sample._SpeakerPlayer

            def create_speaker():
                player = speaker_type()
                player.play = MagicMock(wraps=player.play)
                player.close = MagicMock(wraps=player.close)
                self.players.append(player)
                return player

            monkeypatch.setattr(self.sample, "_SpeakerPlayer", MagicMock(side_effect=create_speaker))
        if self.is_async:
            monkeypatch.setattr(
                self.sample.asyncio, "to_thread", AsyncMock(side_effect=lambda function, *args: function(*args))
            )

    def _receive(self, **kwargs):
        if "timeout" in kwargs:
            assert kwargs["timeout"] > 0
        assert self.events, "The sample received beyond its scripted event sequence."
        event = self.events.popleft()
        if isinstance(event, BaseException):
            raise event
        self.actions.append(("receive", event))
        return event

    async def _iterate(self):
        while True:
            yield await self.connection.recv()

    def _read_input(self, prompt):
        assert prompt
        assert self.prompts, "The sample requested unexpected interactive input."
        value = self.prompts.popleft()
        if isinstance(value, BaseException):
            raise value
        self.actions.append(("input", value))
        return value

    def _create_item(self, *, item):
        self.actions.append(("item", item))

    def _create_response(self):
        self.actions.append(("response.create", None))

    def _cancel_response(self, **kwargs):
        self.actions.append(("response.cancel", kwargs))

    async def run(self):
        if self.is_async and self.is_text:
            await self.sample.text_conversation()
        elif self.is_text:
            self.sample.text_conversation()
        else:
            await self.sample.main()

    def assert_call(self, mock, *args, **kwargs):
        if self.is_async:
            mock.assert_awaited_once_with(*args, **kwargs)
        else:
            mock.assert_called_once_with(*args, **kwargs)

    def assert_cleanup(self, *, created=True, connected=True):
        if created:
            self.assert_call(self.client.agents.delete_version, agent_name=_AGENT_NAME, agent_version=_OWNED_VERSION)
        else:
            self.client.agents.delete_version.assert_not_called()
        self.client.agents.delete.assert_not_called()
        self.client.beta.voice_agents.live.connect.assert_not_called()
        for resource in (self.client, self.credential):
            if self.is_async:
                resource.__aenter__.assert_awaited_once()
                resource.__aexit__.assert_awaited_once()
            else:
                resource.__enter__.assert_called_once()
                resource.__exit__.assert_called_once()
        exit_mock = self.manager.__aexit__ if self.is_async else self.manager.__exit__
        if not connected:
            exit_mock.assert_not_called()
        elif self.is_async:
            exit_mock.assert_awaited_once()
        else:
            exit_mock.assert_called_once()
        for player in self.players:
            player.close.assert_called_once_with()
        if self.is_async:
            for operation in (
                self.client.agents.create_version,
                self.client.agents.delete_version,
                self.conversations.get,
                self.connection.recv,
                self.connection.conversation.item.create,
                self.connection.response.create,
                self.connection.response.cancel,
            ):
                assert operation.await_count == operation.call_count
        self.credential_factory.assert_called_once_with()
        self.client_factory.assert_called_once_with(endpoint=_ENDPOINT, credential=self.credential)


@pytest.fixture(params=_TEXT_SAMPLES, ids=["async-text"])
def text_sample(monkeypatch, request):
    return _SampleHarness(monkeypatch, request.param)


@pytest.fixture
def tool_sample(monkeypatch):
    return _SampleHarness(monkeypatch, _TOOL_SAMPLE)


@pytest.fixture(params=(*_TEXT_SAMPLES, _TOOL_SAMPLE), ids=["async-text", "function-tool"])
def entrypoint_sample(monkeypatch, request):
    return _SampleHarness(monkeypatch, request.param)


async def test_text_entrypoint_drains_greeting_and_reuses_one_persisted_conversation(
    text_sample, realtime_output_event, capsys
):
    greeting_done = _response_done("greeting")
    first_done = _response_done("first")
    second_done = _response_done("second")
    audio = [b"\x01\x00" * 4, b"\x02\x00" * 6, b"\x03\x00" * 8]
    text_sample.prompts.extend(["  Remember Ada.  ", "What name did I give?", "QUIT"])
    text_sample.events.extend(
        [
            {"type": "future.event", "count": 0},
            _session_created(),
            _response_created("greeting"),
            realtime_output_event("audio.delta", "greeting", delta=audio[0]),
            realtime_output_event("audio.done", "greeting"),
            realtime_output_event("audio_transcript.delta", "greeting", delta="Greeting "),
            realtime_output_event("audio_transcript.delta", "greeting", delta="transcript."),
            realtime_output_event("audio_transcript.done", "greeting", transcript="Greeting transcript."),
            greeting_done,
            _response_created("first"),
            realtime_output_event("audio.delta", "first", delta=audio[1]),
            realtime_output_event("audio.done", "first"),
            realtime_output_event("audio_transcript.delta", "first", delta="First turn "),
            realtime_output_event("audio_transcript.delta", "first", delta="transcript."),
            realtime_output_event("audio_transcript.done", "first", transcript="First turn transcript."),
            first_done,
            _response_created("second"),
            realtime_output_event("audio.delta", "second", delta=audio[2]),
            realtime_output_event("audio.done", "second"),
            realtime_output_event("audio_transcript.delta", "second", delta="Second turn "),
            realtime_output_event("audio_transcript.delta", "second", delta="transcript."),
            realtime_output_event("audio_transcript.done", "second", transcript="Second turn transcript."),
            second_done,
        ]
    )

    await text_sample.run()

    connection = text_sample.connection
    items = [submitted.kwargs["item"] for submitted in connection.conversation.item.create.call_args_list]
    assert [item.as_dict() for item in items] == [
        {"type": "message", "role": "user", "content": [{"type": "input_text", "text": prompt}]}
        for prompt in ("Remember Ada.", "What name did I give?")
    ]
    actions = text_sample.actions
    assert actions.index(("receive", greeting_done)) < actions.index(("item", items[0]))
    assert actions.index(("item", items[0])) < actions.index(("receive", first_done))
    assert actions.index(("receive", first_done)) < actions.index(("item", items[1]))
    assert actions.index(("item", items[1])) < actions.index(("receive", second_done))
    assert connection.response.create.call_args_list == [call(), call()]
    connection.response.cancel.assert_not_called()
    text_sample.client.voice_agents.realtime.connect.assert_called_once_with(agent_name=_AGENT_NAME)
    text_sample.assert_call(text_sample.conversations.get, _AGENT_NAME, _CONVERSATION_ID)
    text_sample.conversations.list_items.assert_called_once_with(_AGENT_NAME, _CONVERSATION_ID)
    definition = text_sample.client.agents.create_version.call_args.kwargs["definition"]
    assert isinstance(definition, models.VoiceAgentDefinition)
    assert definition.model_type == models.VoiceModelType.MANAGED
    assert definition.model == "realtime-deployment-offline"
    assert definition.store is True
    assert definition.output_modalities == [models.VoiceOutputModality.AUDIO]
    assert isinstance(definition.greeting, models.VoiceAgentTemplateGreetingConfig)
    assert text_sample.sample.pyaudio is None
    assert len(text_sample.players) == 1
    assert text_sample.players[0].play.call_args_list == [call(chunk) for chunk in audio]
    assert text_sample.players[0].bytes_received == sum(len(chunk) for chunk in audio)
    assert not text_sample.events
    text_sample.assert_cleanup()
    output = capsys.readouterr().out
    for transcript in ("Greeting transcript.", "First turn transcript.", "Second turn transcript."):
        assert output.count(f"Agent: {transcript}\n") == 1


async def test_text_entrypoint_displays_completed_output_text_once(text_sample, realtime_output_event, capsys):
    text_sample.prompts.extend(["Reply using text.", "exit"])
    text_sample.events.extend(
        [
            _session_created(),
            _response_done("greeting"),
            _response_created("text-response"),
            realtime_output_event("text.delta", "text-response", delta="Text-only "),
            realtime_output_event("text.delta", "text-response", delta="reply."),
            realtime_output_event("text.done", "text-response", text="Text-only reply."),
            _response_done("text-response"),
        ]
    )

    await text_sample.run()

    text_sample.assert_call(text_sample.connection.response.create)
    text_sample.connection.response.cancel.assert_not_called()
    text_sample.players[0].play.assert_not_called()
    assert not text_sample.events
    text_sample.assert_cleanup()
    output = capsys.readouterr().out
    assert output.count("Agent: Text-only reply.\n") == 1
    assert "Agent: Text-only \n" not in output
    assert "Agent: reply.\n" not in output


async def test_text_entrypoint_drains_matching_cancellation_before_the_next_turn(text_sample, capsys):
    cancelled_done = _response_done("cancelled-response", status="cancelled")
    fresh_done = _response_done("fresh-response")
    timeout = asyncio.TimeoutError() if text_sample.is_async else TimeoutError()
    text_sample.prompts.extend(["First turn", "Second turn", "exit"])
    text_sample.events.extend(
        [
            _session_created(),
            _response_done("greeting"),
            _response_created("cancelled-response"),
            timeout,
            _response_done("unrelated-response"),
            cancelled_done,
            _response_created("fresh-response"),
            _transcript_done("fresh-response", "Fresh reply after cancellation."),
            fresh_done,
        ]
    )

    await text_sample.run()

    text_sample.assert_call(text_sample.connection.response.cancel, response_id="cancelled-response")
    submitted = text_sample.connection.conversation.item.create.call_args_list
    assert len(submitted) == 2
    second_item = submitted[1].kwargs["item"]
    assert second_item.content[0].text == "Second turn"
    assert text_sample.actions.index(("receive", cancelled_done)) < text_sample.actions.index(("item", second_item))
    assert text_sample.actions.index(("item", second_item)) < text_sample.actions.index(("receive", fresh_done))
    assert text_sample.connection.response.create.call_args_list == [call(), call()]
    assert not text_sample.events
    text_sample.assert_cleanup()
    assert "Agent: Fresh reply after cancellation." in capsys.readouterr().out


@pytest.mark.parametrize("phase", ["create", "receive"])
async def test_entrypoint_failures_clean_up_only_resources_the_sample_owns(entrypoint_sample, phase):
    harness = entrypoint_sample
    failure = RuntimeError(f"offline {phase} failure")
    if phase == "create":
        harness.client.agents.create_version.side_effect = failure
    elif phase == "connect":
        enter = harness.manager.__aenter__ if harness.is_async else harness.manager.__enter__
        enter.side_effect = failure
    else:
        harness.events.append(failure)

    with pytest.raises(RuntimeError, match=f"offline {phase} failure"):
        await harness.run()

    if phase == "create":
        harness.client.voice_agents.realtime.connect.assert_not_called()
        assert not harness.players
    harness.conversations.get.assert_not_called()
    harness.assert_cleanup(created=phase != "create", connected=phase == "receive")


@pytest.mark.parametrize("cities", [("Seattle", "Oslo")], ids=["multiple-tools"])
async def test_function_tool_entrypoint_returns_canonical_call_ids_after_the_completed_cycle(
    tool_sample, cities, realtime_output_event, capsys
):
    arguments = [
        _function_arguments(call_id=f"canonical-call-{index}", arguments=json.dumps({"city": city}))
        for index, city in enumerate(cities)
    ]
    function_done = _response_done(
        "tool-response",
        output=[
            {
                "type": "function_call",
                "id": event.item_id,
                "call_id": event.call_id,
                "name": event.name,
                "arguments": event.arguments,
            }
            for event in arguments
        ],
    )
    final_done = _response_done("final-response")
    tool_sample.events.extend(
        [
            _session_created(),
            _response_created("tool-response"),
            *arguments,
            function_done,
            realtime_output_event("text.delta", "final-response", delta="Tool results "),
            realtime_output_event("text.delta", "final-response", delta="received."),
            realtime_output_event("text.done", "final-response", text="Tool results received."),
            final_done,
        ]
    )

    await tool_sample.run()

    submitted = tool_sample.connection.conversation.item.create.call_args_list
    assert len(submitted) == len(cities) + 1
    assert isinstance(submitted[0].kwargs["item"], models.RealtimeConversationItemMessageUser)
    done_index = tool_sample.actions.index(("receive", function_done))
    continuation_indices = [index for index, action in enumerate(tool_sample.actions) if action[0] == "response.create"]
    assert len(continuation_indices) == 2
    for submitted_call, event, city in zip(submitted[1:], arguments, cities):
        result = submitted_call.kwargs["item"]
        assert isinstance(result, models.RealtimeConversationItemFunctionCallOutput)
        assert result.call_id == event.call_id
        assert result.call_id != event.item_id
        assert json.loads(result.output) == {"city": city, "condition": "sunny", "temperature_f": 72}
        result_index = tool_sample.actions.index(("item", result))
        assert done_index < result_index < continuation_indices[1]
    assert continuation_indices[1] < tool_sample.actions.index(("receive", final_done))
    assert tool_sample.connection.response.create.call_args_list == [call(), call()]
    tool_sample.connection.response.cancel.assert_not_called()
    definition = tool_sample.client.agents.create_version.call_args.kwargs["definition"]
    assert isinstance(definition, models.VoiceAgentDefinition)
    assert definition.output_modalities == [models.VoiceOutputModality.TEXT]
    assert len(definition.tools) == 1
    assert isinstance(definition.tools[0], models.VoiceAgentFunctionTool)
    assert definition.tools[0].name == "get_weather"
    assert not tool_sample.events
    tool_sample.assert_cleanup()
    assert capsys.readouterr().out.count("Agent: Tool results received.\n") == 1


async def test_function_tool_entrypoint_returns_unknown_tool_errors_with_the_original_call_id(tool_sample):
    arguments = _function_arguments(name="unknown_tool", arguments="{}")
    tool_sample.events.extend([arguments, _response_done("tool-response"), _response_done("final-response")])

    await tool_sample.run()

    submitted = tool_sample.connection.conversation.item.create.call_args_list
    assert len(submitted) == 2
    result = submitted[1].kwargs["item"]
    assert result.call_id == arguments.call_id
    assert json.loads(result.output) == {"error": "Unknown tool: unknown_tool"}
    assert tool_sample.connection.response.create.call_args_list == [call(), call()]
    tool_sample.assert_cleanup()


@pytest.mark.parametrize("failure", ["service-error", "invalid-arguments"])
async def test_function_tool_entrypoint_error_paths_release_its_version_and_context(tool_sample, failure, capsys):
    expected_exception = None
    if failure == "timeout":
        tool_sample.events.append(TimeoutError())
    elif failure == "service-error":
        tool_sample.events.append(_error())
    elif failure == "transport-error":
        tool_sample.events.append(ConnectionResetError("offline transport failed"))
        expected_exception = ConnectionResetError
    else:
        tool_sample.events.append(_function_arguments(arguments="{invalid-json"))
        expected_exception = json.JSONDecodeError

    if expected_exception is None:
        await tool_sample.run()
    else:
        with pytest.raises(expected_exception):
            await tool_sample.run()

    assert tool_sample.connection.conversation.item.create.call_count == 1
    assert tool_sample.connection.response.create.call_args_list == [call()]
    if failure == "timeout":
        tool_sample.connection.response.cancel.assert_called_once_with()
        assert "Timed out waiting" in capsys.readouterr().out
    else:
        tool_sample.connection.response.cancel.assert_not_called()
        if failure == "service-error":
            assert "Session error: offline command rejected" in capsys.readouterr().out
    tool_sample.assert_cleanup()
