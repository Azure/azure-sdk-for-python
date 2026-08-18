# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Behavior tests for the developer-owned lifecycle in the basic Voice sample."""

import asyncio
import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

import azure.ai.agentserver.invocations.voice as voice
from azure.ai.agentserver.invocations.voice import (
    InputTextPart,
    ResponseNone,
    ResponseTimeouts,
    SessionDisconnected,
    SessionEnd,
    SessionReady,
    SessionRejected,
    SessionStart,
    SessionTermination,
    TargetTurnOutcome,
    UserMessage,
)

_SAMPLE_ROOT = Path(__file__).parents[2] / "samples" / "basic_voice_agent"


class _Activation:
    def __init__(self, turn):
        self.turn = turn

    def __enter__(self):
        self.turn.activation_count += 1

    def __exit__(self, _exc_type, _exc_value, _traceback):
        return None


class _CapturingTurn:
    def __init__(self, origin, input_count):
        self.origin = origin
        self.input_count = input_count
        self.activation_count = 0
        self.completions = []

    def activate(self):
        return _Activation(self)

    def complete(self, **kwargs):
        if not self.completions:
            self.completions.append(kwargs)

    @property
    def is_completed(self):
        return bool(self.completions)


class _CapturingSession:
    def __init__(self):
        self.messages = []
        self.turns = []
        self.termination = None

    async def send(self, message):
        self.messages.append(message)

    def start_target_turn(self, *, origin, input_count, trigger_context=None):
        del trigger_context
        turn = _CapturingTurn(origin, input_count)
        self.turns.append(turn)
        return turn


@pytest.fixture
def sample_module(monkeypatch):
    class QuietVoiceAgentServerHost(voice.VoiceAgentServerHost):
        def __init__(self, **kwargs):
            kwargs["configure_observability"] = None
            super().__init__(**kwargs)

    monkeypatch.setattr(voice, "VoiceAgentServerHost", QuietVoiceAgentServerHost)
    module_name = "_basic_voice_agent_sample"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, _SAMPLE_ROOT / "basic_voice_agent.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load the basic Voice sample")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        if hasattr(module, "generations"):
            module.generations.clear()
        if hasattr(module, "input_generations"):
            module.input_generations.clear()
        sys.modules.pop(module_name, None)


def _session_start(protocol_version):
    return SessionStart(
        id="m_start",
        ts="2026-08-12T00:00:00Z",
        protocol_version=protocol_version,
        reconnect=False,
        response_timeouts=ResponseTimeouts(first_output_ms=1, idle_ms=2, max_duration_ms=3),
    )


def test_sample_includes_setup_run_and_bridge_manifest():
    readme = (_SAMPLE_ROOT / "README.md").read_text(encoding="utf-8")
    requirements = (_SAMPLE_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    assert "python -m pip install -r requirements.txt" in readme
    assert "python basic_voice_agent.py" in readme
    assert "/invocations_ws" in readme
    assert requirements == ["azure-ai-agentserver-invocations>=1.1.0b2"]

    manifest = yaml.safe_load((_SAMPLE_ROOT / "agent.manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["protocols"] == ["invocations_ws"]
    assert manifest["voiceLiveCompatible"] == "true"
    assert manifest["bridgeProtocolVersion"] == "1.0"


@pytest.mark.asyncio
async def test_session_start_accepts_only_the_supported_protocol(sample_module):
    unsupported_session = _CapturingSession()
    await sample_module.on_session_start(unsupported_session, _session_start("2.0"))
    assert len(unsupported_session.messages) == 1
    rejection = unsupported_session.messages[0]
    assert isinstance(rejection, SessionRejected)
    assert rejection.code == "protocol_mismatch"
    assert rejection.retriable is False

    supported_session = _CapturingSession()
    await sample_module.on_session_start(supported_session, _session_start("1.0"))
    assert len(supported_session.messages) == 1
    assert isinstance(supported_session.messages[0], SessionReady)


@pytest.mark.asyncio
async def test_connection_termination_cancels_sample_owned_generation(sample_module, monkeypatch):
    generation_started = asyncio.Event()
    generation_release = asyncio.Event()

    async def blocked_generation(_text):
        generation_started.set()
        await generation_release.wait()
        yield "not reached"

    monkeypatch.setattr(sample_module, "generate_answer", blocked_generation)
    session = _CapturingSession()
    await sample_module.on_user_message(
        session,
        UserMessage(
            id="m_user",
            ts="2026-08-12T00:00:00Z",
            item_id="in_1",
            content=(InputTextPart(text="hello"),),
        ),
    )
    await asyncio.wait_for(generation_started.wait(), timeout=1)
    generation = next(iter(sample_module.generations.values()))

    await sample_module.on_disconnect(session, SessionDisconnected(code=1006))
    assert not generation.task.done()

    session.termination = SessionTermination.TRANSPORT_ERROR
    sample_module.on_connection_terminating(session)

    with pytest.raises(asyncio.CancelledError):
        await generation.task
    await asyncio.sleep(0)

    assert generation.task.cancelled()
    assert generation.turn.activation_count == 1
    assert generation.turn.completions == [
        {
            "outcome": TargetTurnOutcome.TRANSPORT_ERROR,
            "response_id": generation.response_id,
            "output_item_count": 0,
        }
    ]
    assert not sample_module.generations
    assert not sample_module.input_generations


@pytest.mark.asyncio
async def test_session_end_joins_cleanup_before_later_termination_signals(sample_module, monkeypatch):
    generation_started = asyncio.Event()
    cleanup_finished = asyncio.Event()

    async def blocked_generation(_text):
        generation_started.set()
        try:
            await asyncio.Future()
        finally:
            cleanup_finished.set()
        yield "not reached"

    monkeypatch.setattr(sample_module, "generate_answer", blocked_generation)
    session = _CapturingSession()
    await sample_module.on_user_message(
        session,
        UserMessage(
            id="m_user",
            ts="2026-08-12T00:00:00Z",
            item_id="in_1",
            content=(InputTextPart(text="hello"),),
        ),
    )
    await asyncio.wait_for(generation_started.wait(), timeout=1)
    generation = next(iter(sample_module.generations.values()))

    await sample_module.on_session_end(
        session,
        SessionEnd(id="m_end", ts="2026-08-12T00:00:01Z", reason="completed"),
    )

    assert cleanup_finished.is_set()
    assert generation.task.cancelled()
    assert generation.turn.completions == [
        {
            "outcome": TargetTurnOutcome.END_CALL,
            "response_id": generation.response_id,
            "output_item_count": 0,
        }
    ]
    assert not sample_module.generations
    assert not sample_module.input_generations


@pytest.mark.asyncio
async def test_successful_generation_completes_declared_target_turn(sample_module, monkeypatch):
    async def immediate_generation(_text):
        yield "hello"

    monkeypatch.setattr(sample_module, "generate_answer", immediate_generation)
    session = _CapturingSession()
    await sample_module.on_user_message(
        session,
        UserMessage(
            id="m_user",
            ts="2026-08-12T00:00:00Z",
            item_id="in_1",
            content=(InputTextPart(text="hello"),),
        ),
    )
    generation = next(iter(sample_module.generations.values()))
    await generation.task
    await asyncio.sleep(0)

    assert generation.turn.activation_count == 1
    assert generation.turn.completions == [
        {
            "outcome": TargetTurnOutcome.RESPONSE,
            "response_id": generation.response_id,
            "output_item_count": 1,
        }
    ]
    assert not sample_module.generations
    assert not sample_module.input_generations


@pytest.mark.asyncio
async def test_send_side_transport_failure_preserves_physical_outcome(sample_module):
    session = _CapturingSession()

    async def fail_send(message):
        session.messages.append(message)
        session.termination = SessionTermination.TRANSPORT_ERROR
        raise OSError("peer transport failed")

    session.send = fail_send
    await sample_module.on_user_message(
        session,
        UserMessage(
            id="m_user",
            ts="2026-08-12T00:00:00Z",
            item_id="in_1",
            content=(InputTextPart(text="hello"),),
        ),
    )
    generation = next(iter(sample_module.generations.values()))

    with pytest.raises(OSError, match="peer transport failed"):
        await generation.task
    await asyncio.sleep(0)

    assert generation.turn.completions == [
        {
            "outcome": TargetTurnOutcome.TRANSPORT_ERROR,
            "response_id": None,
            "output_item_count": 0,
        }
    ]
    assert not sample_module.generations
    assert not sample_module.input_generations


@pytest.mark.asyncio
async def test_generation_capacity_replies_none_without_retaining_another_task(sample_module, monkeypatch):
    generation_started = asyncio.Event()

    async def blocked_generation(_text):
        generation_started.set()
        await asyncio.Future()
        yield "not reached"

    monkeypatch.setattr(sample_module, "MAX_ACTIVE_GENERATIONS_PER_SESSION", 1)
    monkeypatch.setattr(sample_module, "generate_answer", blocked_generation)
    session = _CapturingSession()
    await sample_module.on_user_message(
        session,
        UserMessage(
            id="m_first",
            ts="2026-08-12T00:00:00Z",
            item_id="in_1",
            content=(InputTextPart(text="first"),),
        ),
    )
    await asyncio.wait_for(generation_started.wait(), timeout=1)
    generation = next(iter(sample_module.generations.values()))

    await sample_module.on_user_message(
        session,
        UserMessage(
            id="m_second",
            ts="2026-08-12T00:00:01Z",
            item_id="in_2",
            content=(InputTextPart(text="second"),),
        ),
    )

    assert len(sample_module.generations) == 1
    assert len(sample_module.input_generations) == 1
    refusal = session.messages[-1]
    assert isinstance(refusal, ResponseNone)
    assert refusal.in_reply_to == ("in_2",)
    assert refusal.reason == "capacity_exceeded"
    assert session.turns[-1].completions == [
        {
            "outcome": TargetTurnOutcome.NONE,
            "output_item_count": 0,
        }
    ]

    generation.task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await generation.task
    await asyncio.sleep(0)
    assert not sample_module.generations
    assert not sample_module.input_generations


@pytest.mark.asyncio
async def test_generation_output_retention_is_bounded(sample_module, monkeypatch):
    async def oversized_generation(_text):
        yield "abc"
        yield "def"

    monkeypatch.setattr(sample_module, "MAX_OUTPUT_CHUNKS", 1)
    monkeypatch.setattr(sample_module, "MAX_OUTPUT_UTF8_BYTES", 5)
    monkeypatch.setattr(sample_module, "generate_answer", oversized_generation)
    session = _CapturingSession()
    await sample_module.on_user_message(
        session,
        UserMessage(
            id="m_user",
            ts="2026-08-12T00:00:00Z",
            item_id="in_1",
            content=(InputTextPart(text="hello"),),
        ),
    )
    generation = next(iter(sample_module.generations.values()))

    with pytest.raises(RuntimeError, match="output exceeded sample limits"):
        await generation.task
    await asyncio.sleep(0)

    assert generation.turn.completions == [
        {
            "outcome": TargetTurnOutcome.ERROR,
            "response_id": generation.response_id,
            "output_item_count": 0,
        }
    ]
    assert not sample_module.generations
    assert not sample_module.input_generations


@pytest.mark.asyncio
async def test_ordinary_application_cancellation_is_not_transport_error(
    sample_module,
    monkeypatch,
):
    generation_started = asyncio.Event()

    async def blocked_generation(_text):
        generation_started.set()
        await asyncio.Future()
        yield "not reached"

    monkeypatch.setattr(sample_module, "generate_answer", blocked_generation)
    session = _CapturingSession()
    await sample_module.on_user_message(
        session,
        UserMessage(
            id="m_user",
            ts="2026-08-12T00:00:00Z",
            item_id="in_1",
            content=(InputTextPart(text="hello"),),
        ),
    )
    await asyncio.wait_for(generation_started.wait(), timeout=1)
    generation = next(iter(sample_module.generations.values()))

    generation.task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await generation.task
    await asyncio.sleep(0)

    assert generation.turn.completions == [
        {
            "outcome": TargetTurnOutcome.CANCELLED,
            "response_id": generation.response_id,
            "output_item_count": 0,
        }
    ]


@pytest.mark.asyncio
async def test_pre_start_cancellation_completes_and_releases_turn(sample_module):
    session = _CapturingSession()
    await sample_module.on_user_message(
        session,
        UserMessage(
            id="m_user",
            ts="2026-08-12T00:00:00Z",
            item_id="in_1",
            content=(InputTextPart(text="hello"),),
        ),
    )
    generation = next(iter(sample_module.generations.values()))

    generation.task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await generation.task
    await asyncio.sleep(0)

    assert generation.turn.activation_count == 0
    assert generation.turn.completions == [
        {
            "outcome": TargetTurnOutcome.CANCELLED,
            "response_id": None,
            "output_item_count": 0,
        }
    ]
    assert not sample_module.generations
    assert not sample_module.input_generations

    await sample_module.on_disconnect(session, SessionDisconnected(code=1000))
    sample_module.on_connection_terminating(session)

    assert not sample_module.generations
    assert not sample_module.input_generations
