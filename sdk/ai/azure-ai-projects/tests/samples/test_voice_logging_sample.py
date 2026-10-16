# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline coverage for the synchronous Voice Agent diagnostic logging sample."""

import importlib
import json
import logging
from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from azure.core.credentials import AccessToken
from azure.ai.projects import AIProjectClient


_PRIVATE = "SENSITIVE-PAYLOAD-DO-NOT-LOG"


@pytest.fixture(name="sample")
def _sample(monkeypatch, tmp_path):
    endpoint = "https://example.test/api/projects/project-test"
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", endpoint)
    monkeypatch.setenv("FOUNDRY_VOICE_AGENT_NAME", "agent-test")
    monkeypatch.setattr("dotenv.load_dotenv", MagicMock())
    credential = MagicMock()
    credential.__enter__.return_value = credential
    credential.get_token.return_value = AccessToken(_PRIVATE, 4_102_444_800)
    client = AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True)
    create_version = MagicMock(return_value=SimpleNamespace(version="1"))
    delete_version = MagicMock()
    monkeypatch.setattr(client.agents, "create_version", create_version)
    monkeypatch.setattr(client.agents, "delete_version", delete_version)
    monkeypatch.setattr("azure.identity.DefaultAzureCredential", MagicMock(return_value=credential))
    monkeypatch.setattr("azure.ai.projects.AIProjectClient", MagicMock(return_value=client))

    import websockets.sync.client

    socket = MagicMock()
    socket.recv.side_effect = [
        json.dumps({"type": "session.created", "session": {"id": "session-test"}}),
        json.dumps({"type": "response.output_text.delta", "delta": _PRIVATE}),
        json.dumps({"type": "response.done", "response": {"id": "response-test", "status": "completed"}}),
    ]
    connect = MagicMock(return_value=socket)
    monkeypatch.setattr(websockets.sync.client, "connect", connect)
    path = Path(__file__).parents[2] / "samples" / "logs" / "sample_log_from_voice_agent.py"
    monkeypatch.syspath_prepend(str(path.parent))
    log_file = tmp_path / "voice-agent.log"
    monkeypatch.setattr(
        importlib.import_module("log_utils"), "create_timestamped_temp_log_file", MagicMock(return_value=log_file)
    )
    namespace = runpy.run_path(str(path))
    logger = logging.getLogger("azure.ai.projects.realtime")
    return SimpleNamespace(
        main=namespace["main"],
        create_version=create_version,
        delete_version=delete_version,
        connect=connect,
        socket=socket,
        log_file=log_file,
        logger=logger,
        previous_level=logger.level,
        previous_propagate=logger.propagate,
        previous_handlers=list(logger.handlers),
    )


def _assert_logger_restored(sample):
    assert sample.logger.level == sample.previous_level
    assert sample.logger.propagate == sample.previous_propagate
    assert sample.logger.handlers == sample.previous_handlers
    sample.log_file.unlink()


def test_sample_captures_sdk_transport_logs_without_payloads(sample, capsys):
    sample.main()
    log = sample.log_file.read_text(encoding="utf-8")
    for message in (
        "WebSocket CONNECT target=",
        "WebSocket CONNECTED target=",
        "WebSocket SEND type=conversation.item.create bytes=",
        "WebSocket SEND type=response.create bytes=",
        "WebSocket RECEIVE type=session.created bytes=",
        "WebSocket RECEIVE type=response.output_text.delta bytes=",
        "WebSocket RECEIVE type=response.done bytes=",
        "WebSocket CLOSE code=1000",
    ):
        assert message in log
    assert _PRIVATE not in log
    assert "Authorization" not in log and "Bearer" not in log
    assert "What is two plus three?" not in log
    assert f"Voice Agent realtime logs written to {sample.log_file}" in capsys.readouterr().out
    definition = sample.create_version.call_args.kwargs["definition"]
    assert definition.kind == "voice" and definition.store is False
    assert definition.output_modalities == ["text"]
    sample.delete_version.assert_called_once_with(agent_name="agent-test", agent_version="1")
    sample.socket.close.assert_called_once_with(code=1000, reason="")
    _assert_logger_restored(sample)


@pytest.mark.parametrize("failure", ["create", "connect", "receive", "server-error", "response-failed", "cleanup"])
def test_sample_cleans_up_after_failures(sample, failure, capsys):
    if failure == "create":
        sample.create_version.side_effect = RuntimeError("Agent creation failed.")
    elif failure == "connect":
        sample.connect.side_effect = RuntimeError("Connection failed.")
    elif failure == "receive":
        sample.socket.recv.side_effect = RuntimeError("Receive failed.")
    elif failure in ("server-error", "response-failed"):
        event = (
            {"type": "error", "error": {"type": "server_error", "message": _PRIVATE}}
            if failure == "server-error"
            else {"type": "response.done", "response": {"id": "response-test", "status": "failed"}}
        )
        sample.socket.recv.side_effect = [json.dumps(event)]
    else:
        sample.delete_version.side_effect = RuntimeError("Version deletion failed.")
    with pytest.raises(RuntimeError):
        sample.main()
    if failure == "create":
        sample.delete_version.assert_not_called()
        sample.connect.assert_not_called()
    else:
        sample.delete_version.assert_called_once_with(agent_name="agent-test", agent_version="1")
    assert "logs written" not in capsys.readouterr().out
    assert _PRIVATE not in sample.log_file.read_text(encoding="utf-8")
    _assert_logger_restored(sample)
