# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline guards for the GPT Live sample protocol, cleanup, and WAV handling."""

import asyncio
import base64
import importlib.util
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import wave

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from azure.ai.projects import models


_SAMPLE_DIRECTORY = Path(__file__).resolve().parents[2] / "samples" / "agents" / "voice"
_SYNC_SCENARIOS = ("connection", "text_conversation", "function_tool")


def _load_module(monkeypatch, filename):
    name = Path(filename).stem
    spec = importlib.util.spec_from_file_location(name, _SAMPLE_DIRECTORY / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


def _started():
    return models.LiveServerEventLiveSessionStarted({"event_id": "start-test", "session": {"id": "session-test"}})


def _closed():
    return models.LiveServerEventLiveSessionClosed(
        {
            "event_id": "closed-test",
            "reason": "close_requested",
            "session": {"id": "session-test"},
            "usage": {"seconds": 1},
        }
    )


def _response(event_type, **fields):
    return models.LiveServerEventLiveResponseEvent(event_id="response-event-test", event={"type": event_type, **fields})


def _text_response(text):
    return [
        _response("response.output_text.delta", item_id="message-test", content_index=0, delta=text),
        _response("response.output_text.done", item_id="message-test", content_index=0, text=text),
        _response("response.completed", response={"status": "completed", "output": []}),
    ]


def _recording(payload=b"\x01\x00" * 1200, *, channels=1, rate=24000, sample_width=2):
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setnchannels(channels)
        writer.setsampwidth(sample_width)
        writer.setframerate(rate)
        writer.writeframes(payload)
    stream.seek(0)
    return wave.open(stream, "rb")


@pytest.fixture
def sample_environment(monkeypatch):
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.invalid/api/projects/offline")
    monkeypatch.setenv("FOUNDRY_VOICE_AGENT_MODEL", "live-deployment-test")
    monkeypatch.setenv("FOUNDRY_MODEL_NAME", "backend-deployment-test")
    monkeypatch.setenv("FOUNDRY_VOICE_AGENT_NAME", "live-offline")
    monkeypatch.setenv("FOUNDRY_VOICE_AUDIO_INPUT_PATH", "offline-input.wav")
    monkeypatch.delenv("FOUNDRY_VOICE_AUDIO_OUTPUT_PATH", raising=False)
    monkeypatch.setattr("dotenv.load_dotenv", lambda: False)

    client = MagicMock()
    client.__enter__.return_value = client
    client.agents.create_version.return_value = SimpleNamespace(version="owned-version")
    connection = client.beta.voice_agents.live.connect.return_value.__enter__.return_value
    monkeypatch.setattr("azure.ai.projects.AIProjectClient", MagicMock(return_value=client))
    monkeypatch.setattr("azure.identity.DefaultAzureCredential", MagicMock())

    async_client = MagicMock()
    async_client.__aenter__.return_value = async_client
    async_client.agents.create_version = AsyncMock(return_value=SimpleNamespace(version="owned-version"))
    async_client.agents.delete_version = AsyncMock()
    async_connection = async_client.beta.voice_agents.live.connect.return_value.__aenter__.return_value
    async_connection.recv = AsyncMock()
    async_connection.session.close = AsyncMock()
    async_connection.session.input_audio.append = AsyncMock()
    async_connection.session.commentary.append = AsyncMock()
    async_connection.response.item.create = AsyncMock()
    async_connection.response.create = AsyncMock()
    monkeypatch.setattr("azure.ai.projects.aio.AIProjectClient", MagicMock(return_value=async_client))
    monkeypatch.setattr("azure.identity.aio.DefaultAzureCredential", MagicMock())

    helper = _load_module(monkeypatch, "live_sample_utils.py")
    return SimpleNamespace(
        client=client,
        connection=connection,
        async_client=async_client,
        async_connection=async_connection,
        helper=helper,
    )


@pytest.mark.parametrize("scenario", _SYNC_SCENARIOS)
def test_sync_samples_delete_only_the_owned_version_on_failure(monkeypatch, sample_environment, scenario):
    sample = _load_module(monkeypatch, f"sample_voice_agent_live_{scenario}.py")
    client = sample_environment.client
    connection = sample_environment.connection
    connection.recv.side_effect = RuntimeError("offline receive failure")
    connection.session.close.side_effect = ConnectionError("offline cleanup failure")

    with pytest.raises(RuntimeError, match="offline receive failure"):
        sample.main()

    agent_name = client.agents.create_version.call_args.kwargs["agent_name"]
    assert agent_name.startswith("live-offline-")
    client.beta.voice_agents.live.connect.assert_called_once_with(
        agent_name=agent_name, agent_version="owned-version", store=False
    )
    client.agents.delete_version.assert_called_once_with(agent_name=agent_name, agent_version="owned-version")
    client.agents.delete.assert_not_called()
    connection.session.close.assert_called_once()
    connection.session.start.assert_not_called()
    connection.response.cancel.assert_not_called()
    client.beta.voice_agents.realtime.connect.assert_not_called()
    client.beta.voice_agents.live.connect.return_value.__exit__.assert_called_once()


@pytest.mark.parametrize("scenario", _SYNC_SCENARIOS)
def test_failed_agent_creation_does_not_delete_an_existing_version(monkeypatch, sample_environment, scenario):
    sample = _load_module(monkeypatch, f"sample_voice_agent_live_{scenario}.py")
    sample_environment.client.agents.create_version.side_effect = RuntimeError("create failed")

    with pytest.raises(RuntimeError, match="create failed"):
        sample.main()

    sample_environment.client.agents.delete_version.assert_not_called()
    sample_environment.client.beta.voice_agents.live.connect.assert_not_called()


def test_connection_waits_for_start_and_confirms_graceful_close(monkeypatch, sample_environment, capsys):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_connection.py")
    connection = sample_environment.connection
    connection.recv.side_effect = [
        {"type": "future.event"},
        _started(),
        {"type": "session.updated"},
        {"type": "session.instructions.appended"},
        _closed(),
    ]

    sample.main()

    definition = sample_environment.client.agents.create_version.call_args.kwargs["definition"]
    assert isinstance(definition, models.VoiceAgentLiveDefinition)
    assert definition.model == "live-deployment-test"
    assert definition.sub_protocol == "live"
    assert definition.model_type == "self_deployed"
    assert definition.audio.format.rate == 24000
    assert definition.audio.output.voice == "marin"
    connection.session.instructions.append.assert_called_once_with(
        content="Keep responses brief. Do not invent external facts.", delegation_id=None
    )
    assert "Live session started: session-test" in capsys.readouterr().out


def test_text_uses_responses_delegation_and_granular_text(monkeypatch, sample_environment, capsys):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_text_conversation.py")
    connection = sample_environment.connection
    connection.recv.side_effect = [_started(), *_text_response("Seattle has a rainy climate."), _closed()]

    sample.main()

    definition = sample_environment.client.agents.create_version.call_args.kwargs["definition"]
    assert isinstance(definition.delegation, models.LiveResponsesDelegationParam)
    assert definition.delegation.responses.model == "backend-deployment-test"
    item = connection.response.item.create.call_args.kwargs["item"]
    assert item["type"] == "message" and item["role"] == "user"
    assert item["content"][0]["type"] == "input_text"
    connection.response.create.assert_called_once_with()
    assert "Responses backend: Seattle has a rainy climate." in capsys.readouterr().out


def test_text_rejects_empty_backend_completion(monkeypatch, sample_environment):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_text_conversation.py")
    sample_environment.connection.recv.side_effect = [
        _started(),
        _response("response.completed", response={"status": "completed", "output": []}),
    ]

    with pytest.raises(RuntimeError, match="without returning any output text"):
        sample.main()

    sample_environment.client.agents.delete_version.assert_called_once()


@pytest.mark.parametrize("event_type", ["error", "response.failed", "response.incomplete", "response.cancelled"])
def test_backend_failures_are_not_successful_completions(sample_environment, event_type):
    with pytest.raises(RuntimeError, match="Responses backend"):
        sample_environment.helper.check_event(_response(event_type, response={"error": {"message": "backend failed"}}))


def test_outer_live_errors_are_raised(sample_environment):
    event = models.LiveServerEventLiveErrorEvent(
        event_id="error-test",
        error=models.LiveLiveError(type="invalid_request_error", code="invalid_command", message="command rejected"),
    )
    with pytest.raises(RuntimeError, match="invalid_command: command rejected"):
        sample_environment.helper.check_event(event)


def test_lifecycle_wait_has_one_deadline(monkeypatch, sample_environment):
    helper = sample_environment.helper
    monkeypatch.setattr(helper, "time", SimpleNamespace(monotonic=MagicMock(side_effect=[0, 1, 61])))
    sample_environment.connection.recv.return_value = {"type": "future.event"}

    with pytest.raises(TimeoutError, match="session.started"):
        helper.wait_for_event(sample_environment.connection, "session.started")

    sample_environment.connection.recv.assert_called_once_with(timeout=59)


@pytest.mark.asyncio
async def test_async_lifecycle_timeout_names_the_missing_event(sample_environment):
    sample_environment.async_connection.recv.side_effect = asyncio.TimeoutError
    with pytest.raises(TimeoutError, match="session.started"):
        await sample_environment.helper.wait_for_event_async(sample_environment.async_connection, "session.started")


@pytest.mark.asyncio
async def test_async_close_send_is_bounded(monkeypatch, sample_environment):
    monkeypatch.setattr(sample_environment.helper, "CLOSE_TIMEOUT", 0.01)

    async def stalled_close():
        await asyncio.Future()

    sample_environment.async_connection.session.close.side_effect = stalled_close
    with pytest.raises(TimeoutError, match="closing the GPT Live session"):
        await sample_environment.helper.close_session_async(sample_environment.async_connection)
    sample_environment.async_connection.session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_close_timeout_preserves_the_original_error(monkeypatch, sample_environment):
    monkeypatch.setattr(sample_environment.helper, "CLOSE_TIMEOUT", 0.01)

    async def stalled_close():
        await asyncio.Future()

    sample_environment.async_connection.session.close.side_effect = stalled_close
    with pytest.raises(RuntimeError, match="original receive failure"):
        try:
            raise RuntimeError("original receive failure")
        finally:
            await sample_environment.helper.close_session_async(sample_environment.async_connection)
    sample_environment.async_connection.session.close.assert_awaited_once()


def test_function_tool_waits_for_each_completed_cycle(monkeypatch, sample_environment, capsys):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_function_tool.py")
    call = {
        "id": "fc-item-test",
        "type": "function_call",
        "name": "get_weather",
        "call_id": "call-test",
        "arguments": '{"city":"Seattle"}',
        "status": "completed",
    }
    connection = sample_environment.connection
    connection.recv.side_effect = [
        _started(),
        _response("response.output_item.added", item={**call, "arguments": "", "status": "in_progress"}),
        _response("response.function_call_arguments.delta", item_id="fc-item-test", delta='{"city":'),
        _response("response.function_call_arguments.delta", item_id="fc-item-test", delta='"Seattle"}'),
        _response(
            "response.function_call_arguments.done",
            item_id="fc-item-test",
            name="get_weather",
            arguments='{"city":"Seattle"}',
        ),
        _response("response.output_item.done", item=call),
        _response("response.output_item.done", item=call),
        _response("response.completed", response={"status": "completed", "output": []}),
        *_text_response("The sample weather in Seattle is sunny, 72 F."),
        _closed(),
    ]

    sample.main()

    submitted = connection.response.item.create.call_args_list
    assert len(submitted) == 2
    result = submitted[1].kwargs["item"]
    assert result["type"] == "function_call_output"
    assert result["call_id"] == "call-test"
    assert json.loads(result["output"]) == {"city": "Seattle", "condition": "sunny", "temperature_f": 72}
    assert connection.response.create.call_count == 2
    assert "Responses backend: The sample weather in Seattle is sunny, 72 F." in capsys.readouterr().out


def test_argument_done_without_call_id_does_not_invent_a_tool_call(sample_environment):
    sample_environment.connection.recv.side_effect = [
        _response(
            "response.function_call_arguments.done",
            item_id="fc-item-test",
            name="get_weather",
            arguments='{"city":"Seattle"}',
        ),
        _response("response.completed", response={"status": "completed", "output": []}),
    ]

    text, calls = sample_environment.helper.receive_response(sample_environment.connection)

    assert text == ""
    assert calls == []


def test_completed_function_call_requires_its_canonical_call_id(sample_environment):
    sample_environment.connection.recv.return_value = _response(
        "response.output_item.done",
        item={"id": "fc-item-test", "type": "function_call", "name": "get_weather", "arguments": '{"city":"Seattle"}'},
    )

    with pytest.raises(RuntimeError, match="function_call item omitted a usable call_id"):
        sample_environment.helper.receive_response(sample_environment.connection)


@pytest.mark.parametrize("arguments", ['{"city":1}', '{"city":"Seattle","extra":true}', '["Seattle"]'])
def test_function_tool_rejects_invalid_arguments(monkeypatch, sample_environment, arguments):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_function_tool.py")
    with pytest.raises(ValueError, match="exactly one string argument"):
        sample._execute_tool({"name": "get_weather", "arguments": arguments})


@pytest.mark.parametrize("options", [{"channels": 2}, {"rate": 16000}, {"sample_width": 1}, {"payload": b""}])
def test_audio_rejects_wrong_or_empty_wav_before_connecting(monkeypatch, sample_environment, options):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_audio_conversation_async.py")
    with _recording(**options) as recording:
        with pytest.raises(ValueError, match="WAV|no audio frames"):
            sample._validate_recording(recording)
    sample_environment.async_client.beta.voice_agents.live.connect.assert_not_called()


@pytest.mark.asyncio
async def test_audio_streams_raw_frames_concurrently_and_collects_transcripts(monkeypatch, sample_environment, capsys):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_audio_conversation_async.py")
    connection = sample_environment.async_connection
    original_sleep = asyncio.sleep

    async def yield_without_delay(_delay):
        await original_sleep(0)

    monkeypatch.setattr(sample.asyncio, "sleep", yield_without_delay)
    monkeypatch.setattr(sample, "_OUTPUT_IDLE_SECONDS", 0)
    payload = b"\x01\x00" * 2400
    reply = b"\x00\x08" * 1200
    events = iter(
        [
            models.LiveServerEventLiveInputTranscriptDelta(event_id="input", start_ms=0, end_ms=50, delta="Hello."),
            models.LiveOutputAudioDelta(delta=base64.b64encode(reply).decode("ascii")),
            models.LiveServerEventLiveOutputTranscriptDelta(event_id="output", start_ms=0, end_ms=50, delta="Hi!"),
            models.LiveServerEventLiveDelegationCreated(
                event_id="delegation",
                offset_ms=50,
                delegation=models.LiveDelegationItem(id="delegation-test", target="client"),
            ),
        ]
    )
    received_during_send = []

    async def receive():
        await original_sleep(0)
        try:
            event = next(events)
        except StopIteration as exc:
            raise asyncio.TimeoutError from exc
        received_during_send.append(connection.session.input_audio.append.await_count < 22)
        return event

    connection.recv.side_effect = receive
    output_stream = io.BytesIO()
    with _recording(payload) as recording, wave.open(output_stream, "wb") as output_file:
        output_file.setparams((1, 2, 24000, 0, "NONE", "not compressed"))
        await sample._stream_recording(connection, recording, output_file)
    output_stream.seek(0)
    with wave.open(output_stream, "rb") as recording:
        assert recording.readframes(recording.getnframes()) == reply
    sent = [call.kwargs["audio"] for call in connection.session.input_audio.append.await_args_list]
    assert b"".join(sent[:2]) == payload
    assert sum(map(len, sent)) == len(payload) + 48000
    assert all(not chunk.startswith(b"RIFF") for chunk in sent)
    assert any(received_during_send)
    connection.session.commentary.append.assert_awaited_once_with(
        content="This sample cannot look up external information. Briefly acknowledge the recorded request.",
        delegation_id="delegation-test",
    )
    text = capsys.readouterr().out
    assert "Input transcript: Hello." in text and "Output transcript: Hi!" in text
    assert f"Received {len(reply)} PCM16 bytes" in text


@pytest.mark.asyncio
async def test_audio_send_failure_cancels_the_receiver(monkeypatch, sample_environment):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_audio_conversation_async.py")
    connection = sample_environment.async_connection
    connection.session.input_audio.append.side_effect = ConnectionError("audio send failed")
    receiver_stopped = asyncio.Event()

    async def receive():
        try:
            await asyncio.Future()
        finally:
            receiver_stopped.set()

    connection.recv.side_effect = receive
    with _recording() as recording:
        with pytest.raises(ConnectionError, match="audio send failed"):
            await sample._stream_recording(connection, recording, None)
    assert receiver_stopped.is_set()
    connection.response.cancel.assert_not_called()


@pytest.mark.asyncio
async def test_audio_cannot_complete_without_reply_bytes(monkeypatch, sample_environment):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_audio_conversation_async.py")
    finished = asyncio.Event()
    finished.set()
    with pytest.raises(TimeoutError, match="GPT Live reply audio"):
        await sample._receive_audio(sample_environment.async_connection, finished, 0, None)
    sample_environment.async_connection.recv.assert_not_awaited()


@pytest.mark.asyncio
async def test_audio_idle_completion_does_not_require_a_receive_timeout(monkeypatch, sample_environment):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_audio_conversation_async.py")
    monkeypatch.setattr(sample, "_OUTPUT_IDLE_SECONDS", 0)
    finished = asyncio.Event()
    finished.set()
    reply = b"\x00\x08" * 1200
    sample_environment.async_connection.recv.return_value = models.LiveOutputAudioDelta(
        delta=base64.b64encode(reply).decode("ascii")
    )
    output = await sample._receive_audio(sample_environment.async_connection, finished, 1, None)
    assert output.num_bytes == len(reply)
    sample_environment.async_connection.recv.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("delta", ["not valid base64", base64.b64encode(b"\x01").decode("ascii")])
async def test_audio_rejects_invalid_or_partial_pcm(monkeypatch, sample_environment, delta):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_audio_conversation_async.py")
    sample_environment.async_connection.recv.return_value = models.LiveOutputAudioDelta(delta=delta)
    with pytest.raises(ValueError):
        await sample._receive_audio(sample_environment.async_connection, asyncio.Event(), 1, None)


@pytest.mark.asyncio
async def test_audio_refuses_to_overwrite_the_input_recording(monkeypatch, sample_environment):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_audio_conversation_async.py")
    monkeypatch.setenv("FOUNDRY_VOICE_AUDIO_OUTPUT_PATH", "offline-input.wav")
    with pytest.raises(ValueError, match="must not overwrite"):
        await sample.main()
    sample_environment.async_client.agents.create_version.assert_not_awaited()


@pytest.mark.asyncio
async def test_audio_refuses_a_hard_link_to_the_input_without_modifying_either_path(
    monkeypatch, sample_environment, tmp_path
):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_audio_conversation_async.py")
    input_path = tmp_path / "input.wav"
    output_path = tmp_path / "hard-linked-output.wav"
    original = _wav_bytes(1)
    input_path.write_bytes(original)
    output_path.hardlink_to(input_path)
    assert input_path.resolve() != output_path.resolve()
    assert output_path.samefile(input_path)
    monkeypatch.setenv("FOUNDRY_VOICE_AUDIO_INPUT_PATH", str(input_path))
    monkeypatch.setenv("FOUNDRY_VOICE_AUDIO_OUTPUT_PATH", str(output_path))
    monkeypatch.setattr(sample, "_run_audio_conversation", AsyncMock())

    with pytest.raises(ValueError, match="must not overwrite"):
        await sample.main()

    assert input_path.read_bytes() == original
    assert output_path.read_bytes() == original
    sample_environment.async_client.agents.create_version.assert_not_awaited()
    sample_environment.async_client.beta.voice_agents.live.connect.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", [RuntimeError("offline receive failed"), asyncio.CancelledError()])
async def test_async_sample_deletes_its_version_on_error_or_cancellation(monkeypatch, sample_environment, failure):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_audio_conversation_async.py")
    with _recording() as recording:
        monkeypatch.setattr(sample, "wave", SimpleNamespace(open=MagicMock(return_value=recording)))
        sample_environment.async_connection.recv.side_effect = failure
        with pytest.raises(type(failure)):
            await sample.main()

    client = sample_environment.async_client
    agent_name = client.agents.create_version.call_args.kwargs["agent_name"]
    client.beta.voice_agents.live.connect.assert_called_once_with(
        agent_name=agent_name, agent_version="owned-version", store=False
    )
    client.agents.delete_version.assert_awaited_once_with(agent_name=agent_name, agent_version="owned-version")
    client.agents.delete.assert_not_called()
    sample_environment.async_connection.session.close.assert_awaited_once()
    client.beta.voice_agents.live.connect.return_value.__aexit__.assert_awaited_once()


def _audio_sample_with_clock(monkeypatch, sample_environment):
    sample = _load_module(monkeypatch, "sample_voice_agent_live_audio_conversation_async.py")
    clock = SimpleNamespace(now=0.0)
    timer = SimpleNamespace(monotonic=lambda: clock.now)
    monkeypatch.setattr(sample, "time", timer)
    monkeypatch.setattr(sample_environment.helper, "time", timer)
    return sample, clock


@pytest.mark.asyncio
@pytest.mark.parametrize("speech_level", [257, -257, 32767, -32768])
@pytest.mark.parametrize("quiet_level", [0, 1, -1, 256, -256])
async def test_audio_completion_ignores_continuous_quiet_pcm(
    monkeypatch, sample_environment, speech_level, quiet_level
):
    sample, clock = _audio_sample_with_clock(monkeypatch, sample_environment)
    connection = sample_environment.async_connection
    speech = speech_level.to_bytes(2, "little", signed=True) * 480
    quiet = quiet_level.to_bytes(2, "little", signed=True) * 480

    async def receive():
        clock.now += 1
        pcm = speech if clock.now == 1 else quiet
        return models.LiveOutputAudioDelta(delta=base64.b64encode(pcm).decode("ascii"))

    connection.recv.side_effect = receive
    finished = asyncio.Event()
    finished.set()
    output_file = MagicMock()

    output = await sample._receive_audio(connection, finished, 10, output_file)

    assert clock.now == 4
    assert output.has_audio_activity
    assert output.num_bytes == len(speech) + 3 * len(quiet)
    assert output.chunks == 4
    assert b"".join(call.args[0] for call in output_file.writeframesraw.call_args_list) == speech + quiet * 3
    assert connection.recv.await_count == 4


@pytest.mark.asyncio
@pytest.mark.parametrize("quiet_level", [0, 1, -1, 256, -256])
async def test_audio_silence_only_cannot_be_a_successful_reply(monkeypatch, sample_environment, quiet_level):
    sample, clock = _audio_sample_with_clock(monkeypatch, sample_environment)
    connection = sample_environment.async_connection
    quiet = quiet_level.to_bytes(2, "little", signed=True) * 480

    async def receive():
        clock.now += 1
        if clock.now == 1:
            return models.LiveOutputAudioDelta(delta=base64.b64encode(quiet).decode("ascii"))
        raise asyncio.TimeoutError

    connection.recv.side_effect = receive
    finished = asyncio.Event()
    finished.set()

    with pytest.raises(TimeoutError, match="GPT Live reply audio"):
        await sample._receive_audio(connection, finished, 10, None)

    assert clock.now == 10
    assert connection.recv.await_count == 10


@pytest.mark.asyncio
async def test_continuous_reply_activity_does_not_extend_the_overall_audio_deadline(monkeypatch, sample_environment):
    sample, clock = _audio_sample_with_clock(monkeypatch, sample_environment)
    connection = sample_environment.async_connection
    pcm = b"\x00\x08" * 480

    async def receive():
        clock.now += 1
        return models.LiveOutputAudioDelta(delta=base64.b64encode(pcm).decode("ascii"))

    connection.recv.side_effect = receive
    finished = asyncio.Event()
    finished.set()

    with pytest.raises(TimeoutError, match="GPT Live reply audio"):
        await sample._receive_audio(connection, finished, 10, None)

    assert clock.now == 10
    assert connection.recv.await_count == 10


def _text_sample(monkeypatch, sample_environment, asynchronous):
    suffix = "_async" if asynchronous else ""
    sample = _load_module(monkeypatch, f"sample_voice_agent_live_text_conversation{suffix}.py")
    client = sample_environment.async_client if asynchronous else sample_environment.client
    connection = sample_environment.async_connection if asynchronous else sample_environment.connection
    return sample, client, connection


async def _run_text_sample(sample, asynchronous, prompts=None):
    if asynchronous:
        await sample.main(prompts)
    else:
        sample.main(prompts)


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_text_samples_reuse_one_session_and_wait_for_each_turn(
    monkeypatch, sample_environment, capsys, asynchronous
):
    sample, client, connection = _text_sample(monkeypatch, sample_environment, asynchronous)
    prompts = ["My name is Ada.", "What is my name?"]
    events = iter([_started(), *_text_response("Hello, Ada."), *_text_response("Your name is Ada."), _closed()])
    completed = 0
    submitted = []

    def receive(*args, **kwargs):
        nonlocal completed
        event = next(events)
        if event.get("type") == "response.event" and event["event"]["type"] == "response.completed":
            completed += 1
        return event

    def submit(*, item):
        assert completed == len(submitted)
        submitted.append(item["content"][0]["text"])

    connection.recv.side_effect = receive
    connection.response.item.create.side_effect = submit

    await _run_text_sample(sample, asynchronous, prompts)

    assert submitted == prompts
    assert completed == 2
    assert connection.response.create.call_count == 2
    assert connection.session.close.call_count == 1
    client.beta.voice_agents.live.connect.assert_called_once()
    client.agents.create_version.assert_called_once()
    client.agents.delete_version.assert_called_once()
    client.agents.delete.assert_not_called()
    connection.session.start.assert_not_called()
    connection.response.cancel.assert_not_called()
    if asynchronous:
        assert connection.response.item.create.await_count == 2
        assert connection.response.create.await_count == 2
        connection.session.close.assert_awaited_once()
        client.agents.delete_version.assert_awaited_once()
        client.beta.voice_agents.live.connect.return_value.__aexit__.assert_awaited_once()
    else:
        client.beta.voice_agents.live.connect.return_value.__exit__.assert_called_once()
    output = capsys.readouterr().out
    assert output.count("Responses backend: Hello, Ada.\n") == 1
    assert output.count("Responses backend: Your name is Ada.\n") == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_text_samples_keep_the_original_single_prompt_default(monkeypatch, sample_environment, asynchronous):
    sample, client, connection = _text_sample(monkeypatch, sample_environment, asynchronous)
    connection.recv.side_effect = [_started(), *_text_response("Seattle has a rainy climate."), _closed()]

    await _run_text_sample(sample, asynchronous)

    definition = client.agents.create_version.call_args.kwargs["definition"]
    assert isinstance(definition.delegation, models.LiveResponsesDelegationParam)
    assert definition.delegation.responses.model == "backend-deployment-test"
    connection.response.item.create.assert_called_once_with(
        item={
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "Why is Seattle known for rain? Answer in one short sentence."}],
        }
    )
    connection.response.create.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("prompts", [[], [""], ["first", " "], "not-a-prompt-list"])
async def test_text_samples_reject_empty_or_invalid_scripted_prompts(
    monkeypatch, sample_environment, asynchronous, prompts
):
    sample, client, _ = _text_sample(monkeypatch, sample_environment, asynchronous)

    with pytest.raises(ValueError, match="prompt"):
        await _run_text_sample(sample, asynchronous, prompts)

    client.agents.create_version.assert_not_called()
    client.beta.voice_agents.live.connect.assert_not_called()
    client.agents.delete_version.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_text_samples_stop_on_a_later_backend_failure_and_clean_up(monkeypatch, sample_environment, asynchronous):
    sample, client, connection = _text_sample(monkeypatch, sample_environment, asynchronous)
    connection.recv.side_effect = [
        _started(),
        *_text_response("First answer."),
        _response("response.failed", response={"error": {"message": "backend failed"}}),
    ]

    with pytest.raises(RuntimeError, match="Responses backend response.failed"):
        await _run_text_sample(sample, asynchronous, ["first", "second", "must not be sent"])

    assert connection.response.item.create.call_count == 2
    assert connection.response.create.call_count == 2
    connection.session.close.assert_called_once()
    agent_name = client.agents.create_version.call_args.kwargs["agent_name"]
    client.agents.delete_version.assert_called_once_with(agent_name=agent_name, agent_version="owned-version")
    if asynchronous:
        client.agents.delete_version.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("empty", [True, False], ids=["empty-text", "unexpected-tool"])
async def test_text_samples_reject_non_text_backend_completions(monkeypatch, sample_environment, asynchronous, empty):
    sample, client, connection = _text_sample(monkeypatch, sample_environment, asynchronous)
    events = [_started()]
    if not empty:
        events.append(
            _response(
                "response.output_item.done",
                item={"type": "function_call", "call_id": "unexpected-call", "name": "unexpected", "arguments": "{}"},
            )
        )
    events.append(_response("response.completed", response={"status": "completed", "output": []}))
    connection.recv.side_effect = events

    with pytest.raises(RuntimeError, match="without returning any output text|unexpectedly requested"):
        await _run_text_sample(sample, asynchronous, ["one", "must not be sent"])

    connection.response.item.create.assert_called_once()
    client.agents.delete_version.assert_called_once()


@pytest.mark.asyncio
async def test_async_text_create_failure_does_not_delete_an_existing_version(monkeypatch, sample_environment):
    sample, client, _ = _text_sample(monkeypatch, sample_environment, True)
    client.agents.create_version.side_effect = RuntimeError("create failed")

    with pytest.raises(RuntimeError, match="create failed"):
        await sample.main()

    client.agents.delete_version.assert_not_awaited()
    client.beta.voice_agents.live.connect.assert_not_called()


@pytest.mark.asyncio
async def test_async_text_cancellation_propagates_and_deletes_the_owned_version(monkeypatch, sample_environment):
    sample, client, connection = _text_sample(monkeypatch, sample_environment, True)
    connection.recv.side_effect = asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        await sample.main()

    connection.session.close.assert_awaited_once()
    agent_name = client.agents.create_version.call_args.kwargs["agent_name"]
    client.agents.delete_version.assert_awaited_once_with(agent_name=agent_name, agent_version="owned-version")
    client.beta.voice_agents.live.connect.return_value.__aexit__.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_response_collection_keeps_canonical_tool_ids_and_granular_text(sample_environment):
    connection = sample_environment.async_connection
    call = {
        "type": "function_call",
        "call_id": "canonical-call",
        "name": "get_weather",
        "arguments": '{"city":"Seattle"}',
    }
    connection.recv.side_effect = [
        _response("response.output_text.delta", item_id="message-test", content_index=0, delta="Partial"),
        _response("response.output_text.done", item_id="message-test", content_index=0, text="Complete text"),
        _response("response.function_call_arguments.done", item_id="different-item-id", arguments='{"city":"Seattle"}'),
        _response("response.output_item.done", item=call),
        _response("response.completed", response={"status": "completed", "output": []}),
    ]

    text, calls = await sample_environment.helper.receive_response_async(connection)

    assert text == "Complete text"
    assert calls == [call]


@pytest.mark.asyncio
async def test_async_response_collection_does_not_extend_its_deadline(monkeypatch, sample_environment):
    helper = sample_environment.helper
    monkeypatch.setattr(helper, "time", SimpleNamespace(monotonic=MagicMock(side_effect=[0, 1, 61])))
    sample_environment.async_connection.recv.return_value = {"type": "future.event"}

    with pytest.raises(TimeoutError, match="Responses backend to complete"):
        await helper.receive_response_async(sample_environment.async_connection)

    sample_environment.async_connection.recv.assert_awaited_once()
    assert sample_environment.async_connection.recv.call_count == 1


@pytest.mark.asyncio
async def test_async_lifecycle_expired_deadline_does_not_create_an_unawaited_receive(monkeypatch, sample_environment):
    helper = sample_environment.helper
    monkeypatch.setattr(helper, "time", SimpleNamespace(monotonic=MagicMock(side_effect=[0, 1, 61])))
    sample_environment.async_connection.recv.return_value = {"type": "future.event"}

    with pytest.raises(TimeoutError, match="session.started"):
        await helper.wait_for_event_async(sample_environment.async_connection, "session.started")

    sample_environment.async_connection.recv.assert_awaited_once()
    assert sample_environment.async_connection.recv.call_count == 1


@pytest.mark.asyncio
async def test_async_close_expired_deadline_does_not_create_an_unawaited_send(monkeypatch, sample_environment):
    helper = sample_environment.helper
    monkeypatch.setattr(helper, "time", SimpleNamespace(monotonic=MagicMock(side_effect=[0, 11])))

    with pytest.raises(TimeoutError, match="closing the GPT Live session"):
        await helper.close_session_async(sample_environment.async_connection)

    sample_environment.async_connection.session.close.assert_not_called()


def _rest_values(values, asynchronous):
    if asynchronous:

        async def iterate():
            for value in values:
                yield value

        return iterate()
    return iter(values)


def _wav_bytes(channels):
    stream = io.BytesIO()
    with wave.open(stream, "wb") as writer:
        writer.setparams((channels, 2, 24000, 0, "NONE", "not compressed"))
        writer.writeframes(b"\x01\x02" * 1200 * channels)
    return stream.getvalue()


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def rest_sample(request, monkeypatch, sample_environment):
    asynchronous = request.param
    filename = "sample_voice_agent_live_read_conversation" + ("_async.py" if asynchronous else ".py")
    sample = _load_module(monkeypatch, filename)
    monkeypatch.setenv("FOUNDRY_VOICE_AGENT_NAME", "stored-agent-test")
    monkeypatch.setenv("FOUNDRY_VOICE_CONVERSATION_ID", "conversation-test")
    client = sample_environment.async_client if asynchronous else sample_environment.client
    operations = client.beta.voice_agents.live_conversations
    method_mock = AsyncMock if asynchronous else MagicMock
    conversation = models.VoiceAgentLiveConversation(
        {"id": "conversation-test", "status": "completed", "created_at": 1, "completed_at": 2}
    )
    audio = models.VoiceAudioItem(
        {
            "conversation_id": "conversation-test",
            "item_id": "speech-test",
            "role": "agent",
            "format": "wav",
            "codec": "pcm16",
            "sample_rate": 24000,
            "channels": 1,
            "duration_ms": 50,
        }
    )
    speech = models.VoiceAgentLiveOutputConversationItem(
        {"id": "speech-test", "transcription": "A synthetic transcript.", "audio": audio.as_dict()}
    )
    delegation = models.VoiceAgentLiveClientDelegationConversationItem(
        {"id": "delegation-test", "created_at": 1, "commentary": "Synthetic application guidance."}
    )
    items = [speech, delegation]
    recording = models.VoiceRecording(
        {
            "conversation_id": "conversation-test",
            "format": "wav",
            "sample_rate": 24000,
            "channels": 2,
            "channel_layout": {"left": "user", "right": "agent"},
            "duration_ms": 50,
        }
    )
    item_bytes, merged_bytes = _wav_bytes(1), _wav_bytes(2)
    operations.get = method_mock(return_value=conversation)
    operations.list = MagicMock(side_effect=lambda *args, **kwargs: _rest_values([conversation], asynchronous))
    operations.list_items = MagicMock(side_effect=lambda *args, **kwargs: _rest_values(items, asynchronous))
    operations.get_item = method_mock(
        side_effect=lambda agent, conversation, item: next(v for v in items if v.id == item)
    )
    operations.get_audio_item = method_mock(return_value=audio)
    operations.get_audio = method_mock(return_value=recording)
    operations.download_audio_item = method_mock(
        side_effect=lambda *args: _rest_values([item_bytes[:12], item_bytes[12:]], asynchronous)
    )
    operations.download_audio = method_mock(
        side_effect=lambda *args: _rest_values([merged_bytes[:12], merged_bytes[12:]], asynchronous)
    )
    operations.delete = method_mock()

    async def run(**kwargs):
        if asynchronous:
            await sample.main(**kwargs)
        else:
            sample.main(**kwargs)

    return SimpleNamespace(
        sample=sample,
        client=client,
        operations=operations,
        conversation=conversation,
        audio=audio,
        recording=recording,
        items=items,
        run=run,
        item_bytes=item_bytes,
        merged_bytes=merged_bytes,
        asynchronous=asynchronous,
    )


@pytest.mark.asyncio
async def test_live_rest_samples_are_read_only_by_default(rest_sample, tmp_path, capsys, monkeypatch):
    for variable in ("FOUNDRY_VOICE_AGENT_MODEL", "FOUNDRY_MODEL_NAME", "FOUNDRY_VOICE_AUDIO_INPUT_PATH"):
        monkeypatch.delenv(variable, raising=False)
    await rest_sample.run()

    operations = rest_sample.operations
    operations.get.assert_called_once_with("stored-agent-test", "conversation-test")
    operations.list.assert_called_once_with("stored-agent-test", limit=5, order="desc")
    operations.list_items.assert_called_once_with("stored-agent-test", "conversation-test", limit=20, order="asc")
    assert operations.get_item.call_count == 2
    operations.get_audio_item.assert_called_once_with("stored-agent-test", "conversation-test", "speech-test")
    operations.get_audio.assert_called_once_with("stored-agent-test", "conversation-test")
    operations.download_audio.assert_not_called()
    operations.download_audio_item.assert_not_called()
    operations.delete.assert_not_called()
    rest_sample.client.agents.create_version.assert_not_called()
    rest_sample.client.agents.delete_version.assert_not_called()
    rest_sample.client.beta.voice_agents.live.connect.assert_not_called()
    rest_sample.client.beta.voice_agents.conversations.get.assert_not_called()
    assert not list(tmp_path.iterdir())
    output = capsys.readouterr().out
    assert "A synthetic transcript." in output
    assert "Non-speech item" in output
    assert "Read-only run" in output


@pytest.mark.asyncio
async def test_live_rest_samples_download_both_recordings_and_delete_only_when_requested(rest_sample, tmp_path, capsys):
    rest_sample.operations.get.side_effect = [rest_sample.conversation, ResourceNotFoundError("deleted")]

    await rest_sample.run(output_directory=tmp_path, delete=True)

    assert (tmp_path / "item-0001.wav").read_bytes() == rest_sample.item_bytes
    assert (tmp_path / "conversation.wav").read_bytes() == rest_sample.merged_bytes
    rest_sample.operations.download_audio_item.assert_called_once_with(
        "stored-agent-test", "conversation-test", "speech-test"
    )
    rest_sample.operations.download_audio.assert_called_once_with("stored-agent-test", "conversation-test")
    rest_sample.operations.delete.assert_called_once_with("stored-agent-test", "conversation-test")
    assert rest_sample.operations.get.call_count == 2
    if rest_sample.asynchronous:
        for name in ("get_item", "get_audio_item", "get_audio", "download_audio_item", "download_audio", "delete"):
            method = getattr(rest_sample.operations, name)
            assert method.await_count == method.call_count
    assert "confirmed HTTP 404" in capsys.readouterr().out


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [404, 409, 500])
async def test_live_rest_samples_surface_service_failures_without_fallback_or_deletion(rest_sample, status, capsys):
    failure = HttpResponseError("service failure")
    failure.status_code = status
    rest_sample.operations.get.side_effect = failure

    with pytest.raises(HttpResponseError) as caught:
        await rest_sample.run(delete=True)

    assert caught.value is failure
    rest_sample.operations.delete.assert_not_called()
    assert not rest_sample.client.beta.voice_agents.conversations.mock_calls
    assert f"HTTP {status}" in capsys.readouterr().out
    if rest_sample.asynchronous:
        rest_sample.client.__aexit__.assert_awaited_once()
    else:
        rest_sample.client.__exit__.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("status", ["in_progress", "failed"])
async def test_live_rest_samples_require_successful_session_finalization(rest_sample, status):
    rest_sample.conversation.status = status

    with pytest.raises(RuntimeError, match="must finish successfully"):
        await rest_sample.run(delete=True)

    rest_sample.operations.list_items.assert_not_called()
    rest_sample.operations.download_audio.assert_not_called()
    rest_sample.operations.delete.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,filename",
    [
        ("download_audio_item", "item-0001.wav"),
        ("download_audio", "conversation.wav"),
    ],
)
@pytest.mark.parametrize("empty", [True, False], ids=["empty-stream", "failed-stream"])
async def test_live_rest_download_failures_remove_incomplete_files_and_do_not_delete(
    rest_sample, tmp_path, method, filename, empty
):
    async def async_chunks():
        if not empty:
            yield b"partial"
            raise ConnectionError("stream failed")

    def sync_chunks():
        if not empty:
            yield b"partial"
            raise ConnectionError("stream failed")

    getattr(rest_sample.operations, method).side_effect = lambda *args: (
        async_chunks() if rest_sample.asynchronous else sync_chunks()
    )

    with pytest.raises(RuntimeError if empty else ConnectionError, match="no bytes|stream failed"):
        await rest_sample.run(output_directory=tmp_path, delete=True)

    assert not (tmp_path / filename).exists()
    rest_sample.operations.delete.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "filename,method",
    [
        ("item-0001.wav", "download_audio_item"),
        ("conversation.wav", "download_audio"),
    ],
)
async def test_live_rest_samples_never_overwrite_an_existing_recording(rest_sample, tmp_path, filename, method):
    path = tmp_path / filename
    path.write_bytes(b"keep existing audio")

    with pytest.raises(FileExistsError):
        await rest_sample.run(output_directory=tmp_path, delete=True)

    assert path.read_bytes() == b"keep existing audio"
    getattr(rest_sample.operations, method).assert_not_called()
    rest_sample.operations.delete.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("level", ["item", "merged"])
@pytest.mark.parametrize("download", [False, True], ids=["metadata-only", "download-requested"])
async def test_live_rest_samples_explain_byos_without_proxying_downloads(
    rest_sample, tmp_path, capsys, level, download
):
    metadata = rest_sample.audio if level == "item" else rest_sample.recording
    metadata.blob_uri = "https://example.invalid/private-recording"
    if download:
        with pytest.raises(RuntimeError, match="not BYOS audio"):
            await rest_sample.run(output_directory=tmp_path, delete=True)
        rest_sample.operations.delete.assert_not_called()
    else:
        await rest_sample.run()
    method = "download_audio_item" if level == "item" else "download_audio"
    getattr(rest_sample.operations, method).assert_not_called()
    output = capsys.readouterr().out
    assert "BYOS" in output and "https://example.invalid/private-recording" not in output


@pytest.mark.asyncio
async def test_live_rest_samples_reject_repeated_paging_items(rest_sample):
    rest_sample.items.append(rest_sample.items[0])

    with pytest.raises(RuntimeError, match="pager repeated an item"):
        await rest_sample.run(delete=True)

    rest_sample.operations.delete.assert_not_called()


@pytest.mark.asyncio
async def test_live_rest_samples_report_a_delete_that_did_not_take_effect(rest_sample):
    with pytest.raises(RuntimeError, match="remains readable after deletion"):
        await rest_sample.run(delete=True)

    rest_sample.operations.delete.assert_called_once_with("stored-agent-test", "conversation-test")


@pytest.mark.asyncio
@pytest.mark.parametrize("variable", ["FOUNDRY_VOICE_AGENT_NAME", "FOUNDRY_VOICE_CONVERSATION_ID"])
async def test_live_rest_samples_reject_blank_resource_identifiers(rest_sample, monkeypatch, variable):
    monkeypatch.setenv(variable, " ")

    with pytest.raises(ValueError, match="nonblank"):
        await rest_sample.run(delete=True)

    rest_sample.operations.get.assert_not_called()
    rest_sample.operations.delete.assert_not_called()
