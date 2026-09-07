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
    ResponseCancel,
    ResponseCreated,
    ResponseDone,
    ResponseNone,
    ResponseOutputTextDelta,
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


@pytest.mark.parametrize(
    ("termination", "expected"),
    [
        pytest.param(None, TargetTurnOutcome.CANCELLED, id="local-cancellation"),
        pytest.param(SessionTermination.CANCELLED, TargetTurnOutcome.CANCELLED, id="connection-cancelled"),
        pytest.param(SessionTermination.COMPLETED, TargetTurnOutcome.ABANDONED, id="clean-peer-close"),
        pytest.param(SessionTermination.PROTOCOL_ERROR, TargetTurnOutcome.TRANSPORT_ERROR, id="protocol-error"),
        pytest.param(SessionTermination.TRANSPORT_ERROR, TargetTurnOutcome.TRANSPORT_ERROR, id="transport-error"),
        pytest.param(SessionTermination.ACCEPT_ERROR, TargetTurnOutcome.ERROR, id="accept-error"),
        pytest.param(SessionTermination.CALLBACK_ERROR, TargetTurnOutcome.ERROR, id="callback-error"),
        pytest.param(SessionTermination.INTERNAL_ERROR, TargetTurnOutcome.ERROR, id="internal-error"),
    ],
)
def test_termination_outcome_preserves_source_semantics(sample_module, termination, expected):
    assert sample_module.termination_outcome(termination) is expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("termination", "expected"),
    [
        pytest.param(None, TargetTurnOutcome.CANCELLED, id="local-cancellation-negative-control"),
        pytest.param(
            SessionTermination.TRANSPORT_ERROR,
            TargetTurnOutcome.TRANSPORT_ERROR,
            id="committed-transport-error",
        ),
        pytest.param(SessionTermination.CALLBACK_ERROR, TargetTurnOutcome.ERROR, id="committed-callback-error"),
    ],
)
async def test_no_response_cancellation_preserves_committed_termination(
    sample_module,
    termination,
    expected,
):
    session = _CapturingSession()
    send_attempts = []

    async def cancel_send(message):
        send_attempts.append(message)
        session.termination = termination
        raise asyncio.CancelledError()

    session.send = cancel_send

    with pytest.raises(asyncio.CancelledError):
        await sample_module.send_no_response(session, ("in_1",), "no_reply_needed")

    assert len(send_attempts) == 1
    assert len(session.turns) == 1
    turn = session.turns[0]
    assert turn.completions == [
        {
            "outcome": expected,
            "output_item_count": 0,
        }
    ]
    assert not sample_module.generations
    assert not sample_module.input_generations

    sample_module.on_connection_terminating(session)
    assert len(turn.completions) == 1


def test_sample_includes_setup_run_and_bridge_manifest():
    readme = (_SAMPLE_ROOT / "README.md").read_text(encoding="utf-8")
    requirements = (_SAMPLE_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    assert "python -m pip install -r requirements.txt" in readme
    assert "python basic_voice_agent.py" in readme
    assert "/invocations_ws" in readme
    assert requirements == ["azure-ai-agentserver-invocations>=1.2.0b1,<2.0.0"]

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
@pytest.mark.parametrize(
    ("termination", "expected"),
    [
        pytest.param(SessionTermination.COMPLETED, TargetTurnOutcome.ABANDONED, id="clean-peer-close"),
        pytest.param(SessionTermination.CALLBACK_ERROR, TargetTurnOutcome.ERROR, id="callback-error"),
        pytest.param(SessionTermination.PROTOCOL_ERROR, TargetTurnOutcome.TRANSPORT_ERROR, id="protocol-error"),
    ],
)
async def test_connection_cleanup_projects_source_aware_outcome_once(
    sample_module,
    monkeypatch,
    termination,
    expected,
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
    sent_count = len(session.messages)

    session.termination = termination
    sample_module.on_connection_terminating(session)
    sample_module.on_connection_terminating(session)

    with pytest.raises(asyncio.CancelledError):
        await generation.task
    await asyncio.sleep(0)

    assert generation.turn.completions == [
        {
            "outcome": expected,
            "response_id": generation.response_id,
            "output_item_count": 0,
        }
    ]
    assert len(session.messages) == sent_count
    assert not sample_module.generations
    assert not sample_module.input_generations

    sample_module.on_connection_terminating(session)
    assert len(generation.turn.completions) == 1


@pytest.mark.asyncio
async def test_explicit_end_call_hint_wins_later_completed_connection(sample_module, monkeypatch):
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

    sample_module.cancel_session_generation_tasks(session, TargetTurnOutcome.END_CALL)
    session.termination = SessionTermination.COMPLETED
    sample_module.on_connection_terminating(session)

    with pytest.raises(asyncio.CancelledError):
        await generation.task
    await asyncio.sleep(0)

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
    assert sum(isinstance(message, ResponseDone) for message in session.messages) == 1
    assert not any(isinstance(message, ResponseCancel) for message in session.messages)
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
    cancellations = [message for message in session.messages if isinstance(message, ResponseCancel)]
    assert len(cancellations) == 1
    assert cancellations[0].response_id == generation.response_id
    assert cancellations[0].reason == "output_limit_exceeded"
    assert [type(message) for message in session.messages] == [
        ResponseCreated,
        ResponseOutputTextDelta,
        ResponseCancel,
    ]
    assert not any(isinstance(message, ResponseDone) for message in session.messages)
    assert not sample_module.generations
    assert not sample_module.input_generations

    async def bounded_generation(_text):
        yield "ok"

    monkeypatch.setattr(sample_module, "generate_answer", bounded_generation)
    sent_count = len(session.messages)
    await sample_module.on_user_message(
        session,
        UserMessage(
            id="m_retry",
            ts="2026-08-12T00:00:01Z",
            item_id="in_2",
            content=(InputTextPart(text="retry"),),
        ),
    )
    retried_generation = next(iter(sample_module.generations.values()))
    await retried_generation.task
    await asyncio.sleep(0)

    retried_messages = session.messages[sent_count:]
    assert sum(isinstance(message, ResponseDone) for message in retried_messages) == 1
    assert not any(isinstance(message, ResponseCancel) for message in retried_messages)
    assert retried_generation.turn.completions == [
        {
            "outcome": TargetTurnOutcome.RESPONSE,
            "response_id": retried_generation.response_id,
            "output_item_count": 1,
        }
    ]
    assert not sample_module.generations
    assert not sample_module.input_generations


@pytest.mark.asyncio
async def test_model_failure_cancels_started_response(sample_module, monkeypatch):
    async def failing_generation(_text):
        yield "partial"
        raise ValueError("model failed")

    monkeypatch.setattr(sample_module, "generate_answer", failing_generation)
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

    with pytest.raises(ValueError, match="model failed"):
        await generation.task
    await asyncio.sleep(0)

    assert [type(message) for message in session.messages] == [
        ResponseCreated,
        ResponseOutputTextDelta,
        ResponseCancel,
    ]
    cancellation = session.messages[-1]
    assert cancellation.response_id == generation.response_id
    assert cancellation.reason == "generation_failed"
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
async def test_response_cancel_failure_preserves_generation_error(sample_module, monkeypatch):
    async def failing_generation(_text):
        yield "partial"
        raise ValueError("model failed")

    monkeypatch.setattr(sample_module, "generate_answer", failing_generation)
    session = _CapturingSession()

    async def fail_response_cancel(message):
        session.messages.append(message)
        if isinstance(message, ResponseCancel):
            raise OSError("cancel send failed")

    session.send = fail_response_cancel
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

    with pytest.raises(ValueError, match="model failed"):
        await generation.task
    await asyncio.sleep(0)

    assert [type(message) for message in session.messages] == [
        ResponseCreated,
        ResponseOutputTextDelta,
        ResponseCancel,
    ]
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
async def test_response_cancel_task_cancellation_remains_cancellation(sample_module, monkeypatch):
    cancel_send_started = asyncio.Event()

    async def failing_generation(_text):
        yield "partial"
        raise ValueError("model failed")

    monkeypatch.setattr(sample_module, "generate_answer", failing_generation)
    session = _CapturingSession()

    async def block_response_cancel(message):
        session.messages.append(message)
        if isinstance(message, ResponseCancel):
            cancel_send_started.set()
            await asyncio.Future()

    session.send = block_response_cancel
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
    await asyncio.wait_for(cancel_send_started.wait(), timeout=1)

    sample_module.cancel_generation(session, generation.response_id, TargetTurnOutcome.CANCELLED)
    with pytest.raises(asyncio.CancelledError):
        await generation.task
    await asyncio.sleep(0)

    assert [type(message) for message in session.messages] == [
        ResponseCreated,
        ResponseOutputTextDelta,
        ResponseCancel,
    ]
    assert generation.turn.completions == [
        {
            "outcome": TargetTurnOutcome.CANCELLED,
            "response_id": generation.response_id,
            "output_item_count": 0,
        }
    ]
    assert not sample_module.generations
    assert not sample_module.input_generations


@pytest.mark.asyncio
async def test_committed_connection_termination_prevents_response_cancel(sample_module, monkeypatch):
    session = _CapturingSession()

    async def terminated_generation(_text):
        yield "partial"
        session.termination = SessionTermination.TRANSPORT_ERROR
        raise OSError("connection lost")

    monkeypatch.setattr(sample_module, "generate_answer", terminated_generation)
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

    with pytest.raises(OSError, match="connection lost"):
        await generation.task
    await asyncio.sleep(0)

    assert [type(message) for message in session.messages] == [
        ResponseCreated,
        ResponseOutputTextDelta,
    ]
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
async def test_bare_task_cancellation_only_records_local_outcome(
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
    assert not any(isinstance(message, ResponseCancel) for message in session.messages)


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
