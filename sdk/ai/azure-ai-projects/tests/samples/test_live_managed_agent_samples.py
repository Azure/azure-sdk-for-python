# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline workflow and cleanup checks for the managed prompt-agent Live sample."""

import asyncio
import base64
from collections import deque
import importlib.util
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call
import wave

import pytest

from azure.ai.projects import models


_SAMPLES = Path(__file__).resolve().parents[2] / "samples" / "agents" / "voice"
_BACKEND = "owned-managed-backend-test"
_VOICE = "owned-managed-frontend-test"
_INPUT_PCM = b"\x00\x08" * 2400
_OUTPUT_PCM = b"\x00\x09" * 1200


def _load_module(monkeypatch, filename):
    name = Path(filename).stem
    spec = importlib.util.spec_from_file_location(name, _SAMPLES / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    return module


def _wav_bytes(pcm=_INPUT_PCM, *, channels=1, rate=24000, sample_width=2):
    stream = io.BytesIO()
    with wave.open(stream, "wb") as recording:
        recording.setnchannels(channels)
        recording.setsampwidth(sample_width)
        recording.setframerate(rate)
        recording.writeframes(pcm)
    return stream.getvalue()


def _snapshot(owner=None):
    return {
        "id": "session-managed-test",
        "model": "gpt-live-1",
        "expires_at": 2000000000,
        "status": "active",
        "delegation": (
            owner
            if owner is not None
            else {"type": "foundry_managed_agent", "agent_name": _BACKEND, "agent_version": "7"}
        ),
    }


def _started(owner=None):
    return models.LiveServerEventLiveSessionStarted(
        json.loads(json.dumps({"type": "session.started", "event_id": "started-test", "session": _snapshot(owner)}))
    )


def _closed(reason="close_requested"):
    return models.LiveServerEventLiveSessionClosed(
        json.loads(
            json.dumps(
                {
                    "type": "session.closed",
                    "event_id": "closed-test",
                    "session": _snapshot(),
                    "reason": reason,
                    "usage": {"seconds": 1},
                }
            )
        )
    )


def _delegated(target="foundry_managed_agent", delegation_id="delegation-test"):
    return models.LiveServerEventLiveDelegationCreated(
        json.loads(
            json.dumps(
                {
                    "type": "session.delegation.created",
                    "event_id": "delegated-test",
                    "offset_ms": 50,
                    "delegation": {"type": "delegation", "id": delegation_id, "target": target},
                }
            )
        )
    )


def _response(event_type="response.completed", *, delegation_id="delegation-test", **kwargs):
    if event_type == "response.completed" and not kwargs:
        kwargs = {"response": {"status": "completed", "output": []}}
    return models.LiveServerEventLiveResponseEvent(
        json.loads(
            json.dumps(
                {
                    "type": "response.event",
                    "event_id": "response-test",
                    "delegation_id": delegation_id,
                    "event": {"type": event_type, **kwargs},
                }
            )
        )
    )


def _audio(pcm=_OUTPUT_PCM):
    return models.LiveOutputAudioDelta(delta=base64.b64encode(pcm).decode("ascii"))


def _transcript(text="Seattle has frequent rain."):
    return models.LiveServerEventLiveOutputTranscriptDelta(
        event_id="transcript-test", start_ms=100, end_ms=150, delta=text
    )


def _success_events():
    return [
        _delegated(),
        # A server-owned backend tool event is observational, not a client request to execute it.
        _response(
            "response.output_item.added",
            item={"type": "function_call", "name": "server_owned_tool", "call_id": "call-test"},
        ),
        _response(
            "response.output_text.delta",
            item_id="backend-message-test",
            content_index=0,
            delta="[thinking]Preparing an answer.[commentary]Seattle has frequent rain.",
        ),
        _response(),
        models.LiveServerEventLiveInputTranscriptDelta(
            event_id="input-test", start_ms=0, end_ms=50, delta="Why does it rain in Seattle?"
        ),
        _audio(),
        _transcript(),
    ]


def _version(name, definition):
    return models.AgentVersionDetails(
        {
            "object": "agent.version",
            "id": f"{name}:7" if name == _BACKEND else f"{name}:11",
            "name": name,
            "version": "7" if name == _BACKEND else "11",
            "created_at": 1700000000,
            "metadata": {},
            "definition": definition.as_dict(),
        }
    )


class _Clock:
    def __init__(self):
        self.now = 100.0

    def monotonic(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def managed_sample(monkeypatch):
    monkeypatch.syspath_prepend(str(_SAMPLES))
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.invalid/api/projects/offline")
    monkeypatch.setenv("FOUNDRY_VOICE_AGENT_MODEL", "live-deployment-test")
    monkeypatch.setenv("FOUNDRY_MODEL_NAME", "prompt-deployment-test")
    monkeypatch.setenv("FOUNDRY_VOICE_AUDIO_INPUT_PATH", "offline-managed-input.wav")
    monkeypatch.setenv("FOUNDRY_VOICE_AGENT_NAME", "existing-agent-never-delete")
    monkeypatch.setattr("dotenv.load_dotenv", lambda: False)

    shared = _load_module(monkeypatch, "live_sample_utils.py")
    helper = _load_module(monkeypatch, "managed_agent_sample_utils.py")
    clock = _Clock()
    monkeypatch.setattr(shared, "time", clock)
    monkeypatch.setattr(helper, "time", clock)
    environment = SimpleNamespace(
        is_async=True,
        helper=helper,
        clock=clock,
        wav=_wav_bytes(),
        events=deque([_started(), *_success_events()]),
        sent=[],
        received_during_input=[],
        input_path="offline-managed-input.wav",
    )
    real_wave_open = wave.open

    def open_input(path, mode):
        assert path == environment.input_path and mode == "rb"
        return real_wave_open(io.BytesIO(environment.wav), mode)

    monkeypatch.setattr(helper, "wave", SimpleNamespace(open=open_input, Error=wave.Error))
    connection = MagicMock()

    def send_audio(*, audio):
        environment.sent.append((clock.monotonic(), audio))

    def receive(timeout=0.05):
        if environment.events:
            clock.advance(0.005)
            event = environment.events.popleft()
            if isinstance(event, BaseException):
                raise event
            if environment.sent:
                environment.received_during_input.append(
                    sum(len(chunk) for _, chunk in environment.sent) < len(_INPUT_PCM)
                )
            return event
        clock.advance(timeout)
        raise TimeoutError("offline receive idle")

    def close():
        environment.events.append(_closed())

    client = MagicMock()
    credential = MagicMock()
    manager = client.beta.voice_agents.live.connect.return_value
    if environment.is_async:
        client.__aenter__.return_value = client
        credential.__aenter__.return_value = credential
        manager.__aenter__.return_value = connection
        client.agents.create_version = AsyncMock(side_effect=lambda **kw: _version(kw["agent_name"], kw["definition"]))
        client.agents.delete_version = AsyncMock()
        connection.recv = AsyncMock(side_effect=receive)
        connection.session.input_audio.append = AsyncMock(side_effect=send_audio)
        connection.session.close = AsyncMock(side_effect=close)
        client_path = "azure.ai.projects.aio.AIProjectClient"
        credential_path = "azure.identity.aio.DefaultAzureCredential"
    else:
        client.__enter__.return_value = client
        credential.__enter__.return_value = credential
        manager.__enter__.return_value = connection
        client.agents.create_version.side_effect = lambda **kw: _version(kw["agent_name"], kw["definition"])
        connection.recv.side_effect = receive
        connection.session.input_audio.append.side_effect = send_audio
        connection.session.close.side_effect = close
        client_path = "azure.ai.projects.AIProjectClient"
        credential_path = "azure.identity.DefaultAzureCredential"
    client_factory = MagicMock(return_value=client)
    credential_factory = MagicMock(return_value=credential)
    monkeypatch.setattr(client_path, client_factory)
    monkeypatch.setattr(credential_path, credential_factory)
    suffix = "_async" if environment.is_async else ""
    sample = _load_module(monkeypatch, f"sample_voice_agent_live_managed_agent{suffix}.py")
    monkeypatch.setattr(
        sample, "sample_agent_name", lambda scenario: _BACKEND if scenario == "managed-backend" else _VOICE
    )
    environment.sample = sample
    environment.client = client
    environment.client_factory = client_factory
    environment.credential_factory = credential_factory
    environment.connection = connection
    environment.manager = manager
    return environment


async def _run(environment):
    if environment.is_async:
        await environment.sample.main()
    else:
        environment.sample.main()


def _assert_deleted(environment, expected):
    operation = environment.client.agents.delete_version
    actual = operation.await_args_list if environment.is_async else operation.call_args_list
    assert actual == [call(agent_name=name, agent_version=version) for name, version in expected]
    environment.client.agents.delete.assert_not_called()


def _assert_no_client_delegation(environment):
    connection = environment.connection
    connection.response.item.create.assert_not_called()
    connection.response.create.assert_not_called()
    connection.response.cancel.assert_not_called()
    connection.session.commentary.append.assert_not_called()
    connection.session.thinking.append.assert_not_called()
    connection.session.start.assert_not_called()
    connection.session.update.assert_not_called()
    connection.send.assert_not_called()
    environment.client.beta.voice_agents.realtime.connect.assert_not_called()


@pytest.mark.asyncio
async def test_managed_samples_run_pinned_same_project_audio_workflow(managed_sample, capsys):
    environment = managed_sample
    await _run(environment)

    created = environment.client.agents.create_version.call_args_list
    assert len(created) == 2
    backend = created[0].kwargs["definition"]
    voice = created[1].kwargs["definition"]
    assert created[0].kwargs["agent_name"] == _BACKEND
    assert isinstance(backend, models.PromptAgentDefinition)
    assert backend.model == "prompt-deployment-test"
    assert "[thinking]" in backend.instructions and "[commentary]" in backend.instructions
    assert created[1].kwargs["agent_name"] == _VOICE
    assert isinstance(voice, models.VoiceAgentLiveDefinition)
    assert voice.sub_protocol == "live" and voice.model_type == "self_deployed"
    assert voice.model == "live-deployment-test" and voice.store is False
    assert isinstance(voice.delegation, models.VoiceAgentLiveManagedAgentDelegation)
    assert voice.delegation.as_dict() == {
        "type": "foundry_managed_agent",
        "agent_name": _BACKEND,
        "agent_version": "7",
    }
    assert voice.audio.format.rate == 24000 and voice.audio.output.voice == "marin"
    environment.client_factory.assert_called_once_with(
        endpoint="https://example.invalid/api/projects/offline",
        credential=environment.credential_factory.return_value,
        allow_preview=True,
    )
    environment.client.beta.voice_agents.live.connect.assert_called_once_with(
        agent_name=_VOICE, agent_version="11", store=False
    )
    sent = environment.sent
    assert b"".join(chunk for _, chunk in sent[:2]) == _INPUT_PCM
    assert len(sent) > 2 and all(not any(chunk) for _, chunk in sent[2:])
    assert all(not chunk.startswith(b"RIFF") for _, chunk in sent)
    for (previous, chunk), (following, _) in zip(sent, sent[1:]):
        assert following - previous >= len(chunk) / 48000 - 1e-8
    assert any(environment.received_during_input)
    _assert_no_client_delegation(environment)
    _assert_deleted(environment, [(_VOICE, "11"), (_BACKEND, "7")])
    environment.connection.session.close.assert_called_once()
    if environment.is_async:
        environment.connection.session.close.assert_awaited_once()
        environment.manager.__aexit__.assert_awaited_once()
        environment.client.__aexit__.assert_awaited_once()
    else:
        environment.manager.__exit__.assert_called_once()
        environment.client.__exit__.assert_called_once()
    text = capsys.readouterr().out
    assert "target=foundry_managed_agent" in text
    assert f"prompt agent {_BACKEND}, version 7" in text
    assert "Output transcript: Seattle has frequent rain." in text
    assert f"Received {len(_OUTPUT_PCM)} PCM16 bytes" in text
    assert "not a playback-complete event" in text


@pytest.mark.asyncio
async def test_managed_sample_uses_bundled_audio_without_an_input_path_setting(managed_sample, monkeypatch):
    monkeypatch.delenv("FOUNDRY_VOICE_AUDIO_INPUT_PATH", raising=False)
    managed_sample.input_path = str(_SAMPLES / "audio" / "question.wav")

    await _run(managed_sample)

    assert managed_sample.sent
    _assert_deleted(managed_sample, [(_VOICE, "11"), (_BACKEND, "7")])


@pytest.mark.asyncio
async def test_managed_samples_clock_silence_after_actual_input_send_finishes(managed_sample, monkeypatch):
    environment = managed_sample
    monkeypatch.setattr(environment.helper, "OUTPUT_IDLE_SECONDS", 0)
    append = environment.connection.session.input_audio.append
    original_send = append.side_effect

    def delayed_send(*, audio):
        if len(environment.sent) < 2:
            environment.clock.advance(0.75)
        original_send(audio=audio)

    append.side_effect = delayed_send
    await _run(environment)

    last_input_sent, last_input_chunk = environment.sent[1]
    assert environment.clock.monotonic() >= last_input_sent + len(last_input_chunk) / 48000 + 1
    assert len(environment.sent) > 2
    assert all(not any(chunk) for _, chunk in environment.sent[2:])
    _assert_no_client_delegation(environment)
    _assert_deleted(environment, [(_VOICE, "11"), (_BACKEND, "7")])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid",
    ["stereo", "silent", "truncated"],
)
async def test_managed_samples_validate_complete_wav_before_resource_creation(managed_sample, invalid):
    environment = managed_sample
    environment.wav = {
        "stereo": lambda: _wav_bytes(channels=2),
        "wrong-rate": lambda: _wav_bytes(rate=16000),
        "wrong-width": lambda: _wav_bytes(sample_width=1),
        "empty": lambda: _wav_bytes(b""),
        "silent": lambda: _wav_bytes(bytes(4800)),
        "truncated": lambda: _wav_bytes()[:-2],
        "partial-frame": lambda: _wav_bytes(b"\x00\x08\x00"),
        "too-long": lambda: _wav_bytes(b"\x00\x08" * (24000 * 31)),
        "not-wav": lambda: b"not a WAV recording",
    }[invalid]()

    with pytest.raises(ValueError, match="WAV|PCM16|audible"):
        await _run(environment)

    environment.credential_factory.assert_not_called()
    environment.client_factory.assert_not_called()
    environment.client.agents.create_version.assert_not_called()
    _assert_deleted(environment, [])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "owner",
    [
        pytest.param({"type": "client"}, id="client-owner"),
        pytest.param(
            {"type": "foundry_managed_agent", "agent_name": _BACKEND, "agent_version": "8"},
            id="wrong-version",
        ),
    ],
)
async def test_managed_samples_check_effective_owner_before_sending_audio(managed_sample, owner):
    environment = managed_sample
    environment.events[0] = _started(owner)
    with pytest.raises(RuntimeError, match="pin the expected"):
        await _run(environment)
    assert not environment.sent
    _assert_no_client_delegation(environment)
    _assert_deleted(environment, [(_VOICE, "11"), (_BACKEND, "7")])


_ERROR_EVENTS = [
    *[
        pytest.param(
            _response(f"response.{status}", response={"status": status, "error": {"message": "Backend stopped"}}),
            RuntimeError,
            "Responses backend",
            id=status,
        )
        for status in ("failed", "incomplete", "cancelled")
    ]
]


@pytest.mark.asyncio
@pytest.mark.parametrize("event,error_type,message", _ERROR_EVENTS)
async def test_managed_samples_propagate_backend_and_protocol_failures(managed_sample, event, error_type, message):
    environment = managed_sample
    environment.events = deque([_started(), _delegated(), event])
    with pytest.raises(error_type, match=message):
        await _run(environment)
    _assert_no_client_delegation(environment)
    _assert_deleted(environment, [(_VOICE, "11"), (_BACKEND, "7")])
    environment.connection.session.close.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "events",
    [
        pytest.param([_delegated(), _response()], id="backend-completion-only"),
        pytest.param([_delegated(), _response(), _audio(bytes(2400)), _transcript()], id="silent-output"),
        pytest.param([_delegated(), _response(), _audio()], id="missing-transcript"),
    ],
)
async def test_managed_samples_never_treat_backend_completion_as_frontend_success(
    managed_sample, monkeypatch, events, capsys
):
    environment = managed_sample
    monkeypatch.setattr(environment.helper, "RESPONSE_TIMEOUT", 2)
    monkeypatch.setattr(environment.helper, "OUTPUT_IDLE_SECONDS", 0.1)
    environment.events = deque([_started(), *events])
    with pytest.raises(TimeoutError, match="managed backend completion and nonempty Live audio/transcript"):
        await _run(environment)
    assert "Deleted only the Live and prompt-agent versions" not in capsys.readouterr().out
    _assert_no_client_delegation(environment)
    _assert_deleted(environment, [(_VOICE, "11"), (_BACKEND, "7")])
    assert any(not any(chunk) for _, chunk in environment.sent[2:])


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["backend", "voice"])
async def test_managed_samples_clean_only_successfully_created_versions(managed_sample, stage):
    environment = managed_sample
    error = RuntimeError(f"{stage} create failed")
    results = [error] if stage == "backend" else [_version(_BACKEND, models.PromptAgentDefinition(model="test")), error]
    environment.client.agents.create_version.side_effect = results
    with pytest.raises(RuntimeError, match=f"{stage} create failed"):
        await _run(environment)
    environment.client.beta.voice_agents.live.connect.assert_not_called()
    _assert_deleted(environment, [] if stage == "backend" else [(_BACKEND, "7")])


@pytest.mark.asyncio
@pytest.mark.parametrize("stage", ["stream"])
async def test_managed_samples_cleanup_on_cancellation_without_swallowing_it(managed_sample, stage):
    environment = managed_sample
    cancellation = asyncio.CancelledError() if environment.is_async else KeyboardInterrupt()
    if stage == "voice-create":
        environment.client.agents.create_version.side_effect = [
            _version(_BACKEND, models.PromptAgentDefinition(model="test")),
            cancellation,
        ]
    else:
        environment.events = deque([_started(), _delegated(), cancellation])
    with pytest.raises(type(cancellation)):
        await _run(environment)
    _assert_deleted(environment, [(_BACKEND, "7")] if stage == "voice-create" else [(_VOICE, "11"), (_BACKEND, "7")])
    _assert_no_client_delegation(environment)
