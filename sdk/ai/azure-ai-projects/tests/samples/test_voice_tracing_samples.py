# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline guards for the runnable REST/realtime tracing sample pair."""

import asyncio
import base64
from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.ai.projects import models


@pytest.fixture(name="setup_sample")
def _setup_sample(monkeypatch):
    def setup(is_async: bool):
        monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.test/api/projects/project-test")
        monkeypatch.setenv("FOUNDRY_VOICE_AGENT_NAME", "agent-test")
        monkeypatch.setattr("dotenv.load_dotenv", MagicMock())
        provider = MagicMock()
        instrumentor = MagicMock()
        instrumentor.is_instrumented.return_value = True
        instrumentor.is_content_recording_enabled.return_value = False
        monkeypatch.setattr("opentelemetry.sdk.trace.TracerProvider", MagicMock(return_value=provider))
        monkeypatch.setattr("opentelemetry.trace.set_tracer_provider", MagicMock())
        tracer = MagicMock()
        tracer.start_as_current_span.return_value.__enter__.return_value.get_span_context.return_value.trace_id = 1
        monkeypatch.setattr("opentelemetry.trace.get_tracer", MagicMock(return_value=tracer))
        monkeypatch.setattr("azure.ai.projects.telemetry.AIProjectInstrumentor", MagicMock(return_value=instrumentor))
        client = MagicMock()
        client.__enter__.return_value = client
        client.__aenter__.return_value = client
        connection = MagicMock()
        connection.__enter__.return_value = connection
        connection.__aenter__.return_value = connection
        client.beta.voice_agents.realtime.connect.return_value = connection
        version = SimpleNamespace(name="agent-test", version="1", definition=SimpleNamespace(kind="voice"))
        for method in ("create_version", "get_version", "delete_version"):
            value = None if method == "delete_version" else version
            setattr(client.agents, method, AsyncMock(return_value=value) if is_async else MagicMock(return_value=value))
        conversations = client.beta.voice_agents.conversations
        conversation = SimpleNamespace(id="conversation-test", status="completed")
        conversations.get = AsyncMock(return_value=conversation) if is_async else MagicMock(return_value=conversation)
        conversations.delete = AsyncMock() if is_async else MagicMock()
        events = [
            models.RealtimeServerEventSessionCreated({"conversation_id": "conversation-test"}),
            models.RealtimeServerEventResponseAudioDelta({"delta": base64.b64encode(b"\x01\x00" * 120).decode()}),
            models.RealtimeServerEventResponseAudioTranscriptDone({"transcript": "Two plus three is five."}),
            models.RealtimeServerEventResponseDone({"response": {"id": "response-test", "status": "completed"}}),
        ]
        connection.recv = AsyncMock(side_effect=events) if is_async else MagicMock(side_effect=events)
        if is_async:
            connection.conversation.item.create = AsyncMock()
            connection.response.create = AsyncMock()
        module = "azure.ai.projects.aio" if is_async else "azure.ai.projects"
        identity = "azure.identity.aio" if is_async else "azure.identity"
        monkeypatch.setattr(module + ".AIProjectClient", MagicMock(return_value=client))
        monkeypatch.setattr(identity + ".DefaultAzureCredential", MagicMock())
        suffix = "_async" if is_async else ""
        path = (
            Path(__file__).parents[2]
            / "samples"
            / "agents"
            / "telemetry"
            / f"sample_voice_agent_with_tracing{suffix}.py"
        )
        namespace = runpy.run_path(str(path))
        return SimpleNamespace(
            namespace=namespace, client=client, connection=connection, provider=provider, instrumentor=instrumentor
        )

    return setup


def _execute(sample, is_async):
    if is_async:
        asyncio.run(sample.namespace["main"]())
    else:
        sample.namespace["main"]()


@pytest.mark.parametrize("is_async", [False, True])
def test_samples_cover_rest_realtime_and_exact_audio_size(setup_sample, is_async, capsys):
    sample = setup_sample(is_async)
    _execute(sample, is_async)
    output = capsys.readouterr().out
    assert "Retrieved version 1: kind=voice" in output
    assert "Transcript: Two plus three is five." in output
    assert "Output audio: 240 bytes" in output
    assert "Total audio: 240 bytes" in output
    assert "Deleted conversation conversation-test" in output
    assert "Deleted voice agent version 1" in output
    sample.client.agents.delete_version.assert_called_once_with(agent_name="agent-test", agent_version="1")
    sample.client.beta.voice_agents.conversations.delete.assert_called_once_with("agent-test", "conversation-test")
    if is_async:
        sample.client.agents.delete_version.assert_awaited_once()
        sample.client.beta.voice_agents.conversations.delete.assert_awaited_once()
    definition = sample.client.agents.create_version.call_args.kwargs["definition"]
    assert definition.kind == "voice" and definition.store is True
    sample.instrumentor.instrument.assert_called_once_with()
    sample.instrumentor.uninstrument.assert_called_once_with()
    sample.provider.force_flush.assert_called_once()
    sample.provider.shutdown.assert_called_once()


@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("failure", ["get", "recv", "response-failed"])
def test_samples_clean_up_on_rest_or_realtime_failure(setup_sample, is_async, failure):
    sample = setup_sample(is_async)
    if failure == "get":
        sample.client.agents.get_version.side_effect = RuntimeError("REST failure")
    elif failure == "recv":
        sample.connection.recv.side_effect = RuntimeError("Transport failure")
    else:
        sample.connection.recv.side_effect = [
            models.RealtimeServerEventResponseDone({"response": {"id": "response-test", "status": "failed"}})
        ]
    with pytest.raises(RuntimeError):
        _execute(sample, is_async)
    sample.client.agents.delete_version.assert_called_once_with(agent_name="agent-test", agent_version="1")
    if is_async:
        sample.client.agents.delete_version.assert_awaited_once()
    sample.client.beta.voice_agents.conversations.delete.assert_not_called()
    sample.instrumentor.uninstrument.assert_called_once()
    sample.provider.shutdown.assert_called_once()


@pytest.mark.parametrize("is_async", [False, True])
def test_http_status_callback_does_not_print_request_secrets(setup_sample, is_async, capsys):
    sample = setup_sample(is_async)
    sample.namespace["_print_http_status"](
        SimpleNamespace(
            http_request=SimpleNamespace(method="DELETE", url="https://example.test/?secret=do-not-print"),
            http_response=SimpleNamespace(status_code=204),
        )
    )
    output = capsys.readouterr().out
    assert output.strip() == "HTTP DELETE -> 204"
    assert "secret" not in output
