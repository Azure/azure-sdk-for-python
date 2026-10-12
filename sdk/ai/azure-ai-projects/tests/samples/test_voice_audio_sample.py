# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline guards for Voice Agent audio accounting and the conversation deletion snippet."""

import asyncio
from concurrent.futures import Future
from pathlib import Path
import runpy
import sys
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def sample(monkeypatch):
    pyaudio = ModuleType("pyaudio")
    setattr(pyaudio, "PyAudio", MagicMock())
    monkeypatch.setitem(sys.modules, "pyaudio", pyaudio)
    path = Path(__file__).parents[2] / "samples" / "agents" / "voice"
    return runpy.run_path(str(path / "sample_voice_agent_realtime_audio_conversation_async.py"))


@pytest.mark.asyncio
async def test_input_audio_counts_only_completed_payloads(sample) -> None:
    connection = MagicMock()
    connection.input_audio_buffer.append = AsyncMock()
    processor = sample["_AudioProcessor"](connection)
    payload = b"\x01\x00" * 1200

    await processor._append_input_audio(payload)

    connection.input_audio_buffer.append.assert_awaited_once_with(audio=payload)
    assert processor.input_bytes_sent == len(payload)
    assert processor.input_seconds == len(payload) / 48000


@pytest.mark.asyncio
async def test_failed_input_audio_send_is_not_counted(sample) -> None:
    connection = MagicMock()
    connection.input_audio_buffer.append = AsyncMock(side_effect=ConnectionResetError("Connection closed."))
    processor = sample["_AudioProcessor"](connection)

    with pytest.raises(ConnectionResetError, match="Connection closed"):
        await processor._append_input_audio(b"\x01\x00" * 1200)

    assert processor.input_bytes_sent == 0


@pytest.mark.asyncio
async def test_capture_shutdown_waits_for_the_last_send(sample) -> None:
    processor = sample["_AudioProcessor"](MagicMock())
    stream = MagicMock()
    processor._input_stream = stream
    pending: Future[None] = Future()
    processor._pending_send = pending

    shutdown = asyncio.create_task(processor.stop_capture())
    await asyncio.sleep(0)

    stream.stop_stream.assert_called_once()
    stream.close.assert_called_once()
    assert processor._input_stream is None
    assert not shutdown.done()
    pending.set_result(None)
    await shutdown

    assert processor._pending_send is None


@pytest.mark.asyncio
async def test_capture_shutdown_surfaces_failed_send(sample) -> None:
    processor = sample["_AudioProcessor"](MagicMock())
    completed: Future[None] = Future()
    completed.set_exception(ConnectionResetError("Last audio send failed."))
    processor._pending_send = completed

    with pytest.raises(ConnectionResetError, match="Last audio send failed"):
        await processor.stop_capture()


def test_output_audio_counts_received_payload_not_playback_estimate(sample) -> None:
    processor = sample["_AudioProcessor"](MagicMock())
    first = b"\x01\x00" * 1200
    second = b"\x02\x00" * 2400

    processor.queue_audio(first)
    processor.queue_audio(second)
    processor.skip_pending_audio()

    assert processor.output_bytes_received == len(first) + len(second)
    assert processor.seconds == (len(first) + len(second)) / 48000


def test_conversation_delete_snippet_accepts_no_content_result(capsys) -> None:
    path = Path(__file__).parents[2] / "samples" / "agents" / "voice" / "sample_voice_agent_read_conversation.py"
    lines = [
        line.strip()[2:]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith(("# conversations.delete(", '# print(f"Deleted conversation'))
    ]
    assert len(lines) == 2
    conversations = MagicMock()
    conversations.delete.return_value = None

    exec(
        compile("\n".join(lines), str(path), "exec"),
        {"conversations": conversations, "agent_name": "agent-test", "conversation_id": "conversation-test"},
    )

    conversations.delete.assert_called_once_with("agent-test", "conversation-test")
    assert "Deleted conversation conversation-test" in capsys.readouterr().out
