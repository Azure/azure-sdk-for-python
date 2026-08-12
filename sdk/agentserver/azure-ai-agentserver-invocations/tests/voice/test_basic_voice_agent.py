# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Behavior tests for the developer-owned lifecycle in the basic Voice sample."""

import asyncio
import importlib
import sys
from pathlib import Path

import pytest
import yaml

import azure.ai.agentserver.invocations.voice as voice
from azure.ai.agentserver.invocations.voice import (
    InputTextPart,
    ResponseTimeouts,
    SessionDisconnected,
    SessionEnd,
    SessionReady,
    SessionRejected,
    SessionStart,
    UserMessage,
)

_SAMPLE_ROOT = Path(__file__).parents[2] / "samples" / "basic_voice_agent"


class _CapturingSession:
    def __init__(self):
        self.messages = []

    async def send(self, message):
        self.messages.append(message)


@pytest.fixture
def sample_module(monkeypatch):
    class QuietVoiceAgentServerHost(voice.VoiceAgentServerHost):
        def __init__(self, **kwargs):
            kwargs["configure_observability"] = None
            super().__init__(**kwargs)

    monkeypatch.setattr(voice, "VoiceAgentServerHost", QuietVoiceAgentServerHost)
    module_name = "samples.basic_voice_agent.basic_voice_agent"
    sys.modules.pop(module_name, None)
    module = importlib.import_module(module_name)
    yield module
    module.generations.clear()
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

    sample_module.on_connection_terminating(session)

    with pytest.raises(asyncio.CancelledError):
        await generation.task
    await asyncio.sleep(0)

    assert generation.task.cancelled()
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
    assert not sample_module.generations
    assert not sample_module.input_generations

    await sample_module.on_disconnect(session, SessionDisconnected(code=1000))
    sample_module.on_connection_terminating(session)

    assert not sample_module.generations
    assert not sample_module.input_generations
