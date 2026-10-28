# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Smoke tests for the actual runnable SDK samples and their native client."""

import importlib.util
import logging
from pathlib import Path
from unittest.mock import patch

import pytest
from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import get_artifact_text, new_text_message
from a2a.types import GetTaskRequest, Role, SendMessageRequest, TaskState

_SAMPLES = Path(__file__).resolve().parents[1] / "samples"
_EXAMPLES = [
    ("01-hello-world/hello_world.py", "Hello from Foundry"),
    ("02-multi-protocol/multi_protocol.py", "Hello over A2A"),
    ("03-streaming/streaming.py", "Hello from streaming A2A!"),
]


@pytest.fixture
def load_sample(monkeypatch, tmp_path):
    monkeypatch.setenv("OTEL_INSTRUMENTATION_A2A_SDK_ENABLED", "false")
    monkeypatch.delenv("A2A_AGENT_URL", raising=False)
    monkeypatch.setenv("PORT", "8088")
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)

    def load(relative_path):
        path = _SAMPLES / relative_path
        spec = importlib.util.spec_from_file_location(f"a2a_sample_{path.stem}", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        root = logging.getLogger()
        level, handlers = root.level, list(root.handlers)
        try:
            with patch("azure.ai.agentserver.core._tracing._configure_tracing"):
                spec.loader.exec_module(module)
        finally:
            root.setLevel(level)
            for handler in list(root.handlers):
                if handler not in handlers:
                    root.removeHandler(handler)
                    handler.close()
        return module

    return load


async def _native_client(http_client, *, streaming=False):
    http_client.headers["A2A-Version"] = "1.0"
    card = await A2ACardResolver(http_client, "http://testserver").get_agent_card(
        relative_card_path="a2a/.well-known/agent-card.json",
    )
    return await create_client(card, ClientConfig(streaming=streaming, httpx_client=http_client))


def _text(task):
    return "".join(get_artifact_text(artifact, delimiter="") for artifact in task.artifacts)


@pytest.mark.asyncio
@pytest.mark.parametrize("relative_path,expected", _EXAMPLES)
async def test_sample_task_lookup_and_context_reuse(load_sample, client_factory, relative_path, expected):
    module = load_sample(relative_path)
    async with client_factory(module.host) as http_client:
        assert (await http_client.get("/readiness")).status_code == 200
        client = await _native_client(http_client)
        try:
            responses = [
                response
                async for response in client.send_message(
                    SendMessageRequest(message=new_text_message("hello", role=Role.ROLE_USER))
                )
            ]
            assert len(responses) == 1 and responses[0].HasField("task")
            task = responses[0].task
            assert task.id and task.context_id
            assert task.status.state == TaskState.TASK_STATE_COMPLETED
            assert _text(task) == expected

            stored = await client.get_task(GetTaskRequest(id=task.id))
            assert stored.id == task.id
            assert stored.context_id == task.context_id
            assert stored.status.state == TaskState.TASK_STATE_COMPLETED
            assert _text(stored) == expected

            followup = [
                response
                async for response in client.send_message(
                    SendMessageRequest(
                        message=new_text_message("hello again", role=Role.ROLE_USER, context_id=task.context_id)
                    )
                )
            ]
            assert followup[0].task.context_id == task.context_id
            assert followup[0].task.id != task.id
            assert _text(followup[0].task) == expected
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_multi_protocol_sample_serves_invocations(load_sample, client_factory):
    module = load_sample("02-multi-protocol/multi_protocol.py")
    async with client_factory(module.host) as client:
        response = await client.post("/invocations", json={"message": "hello"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello over Invocations"}


@pytest.mark.asyncio
async def test_streaming_sample_appends_one_artifact(load_sample, client_factory):
    module = load_sample("03-streaming/streaming.py")
    assert module.card.capabilities.streaming
    async with client_factory(module.host) as http_client:
        client = await _native_client(http_client, streaming=True)
        try:
            responses = [
                response
                async for response in client.send_message(
                    SendMessageRequest(message=new_text_message("hello", role=Role.ROLE_USER))
                )
            ]
            updates = [response.artifact_update for response in responses if response.HasField("artifact_update")]
            states = [
                response.status_update.status.state for response in responses if response.HasField("status_update")
            ]
            assert len(updates) == 4
            assert len({update.artifact.artifact_id for update in updates}) == 1
            assert [update.append for update in updates] == [False, True, True, True]
            assert [update.last_chunk for update in updates] == [False, False, False, True]
            assert "".join(get_artifact_text(update.artifact, delimiter="") for update in updates) == (
                "Hello from streaming A2A!"
            )
            assert TaskState.TASK_STATE_WORKING in states
            assert states[-1] == TaskState.TASK_STATE_COMPLETED
            task_id = next(response.task.id for response in responses if response.HasField("task"))
            assert _text(await client.get_task(GetTaskRequest(id=task_id))) == "Hello from streaming A2A!"
        finally:
            await client.close()


@pytest.mark.asyncio
async def test_new_sample_process_has_no_previous_tasks(load_sample, client_factory):
    module = load_sample("01-hello-world/hello_world.py")
    async with client_factory(module.host) as http_client:
        client = await _native_client(http_client)
        try:
            responses = [
                response
                async for response in client.send_message(
                    SendMessageRequest(message=new_text_message("hello", role=Role.ROLE_USER))
                )
            ]
            task_id = responses[0].task.id
        finally:
            await client.close()

    restarted = load_sample("01-hello-world/hello_world.py")
    async with client_factory(restarted.host) as http_client:
        response = await http_client.post(
            "/a2a",
            headers={"A2A-Version": "1.0"},
            json={"jsonrpc": "2.0", "id": "lookup", "method": "GetTask", "params": {"id": task_id}},
        )
    assert response.status_code == 200
    assert response.json()["error"]["code"] == -32001


@pytest.mark.asyncio
async def test_state_store_sample_retrieves_task_after_host_recreation(load_sample, client_factory):
    module = load_sample("04-state-store/state_store.py")
    async with client_factory(module.host) as http_client:
        client = await _native_client(http_client)
        try:
            responses = [
                response
                async for response in client.send_message(
                    SendMessageRequest(message=new_text_message("remember this", role=Role.ROLE_USER))
                )
            ]
            task = responses[0].task
            assert task.status.state == TaskState.TASK_STATE_COMPLETED
            assert _text(task) == "Persisted: remember this"
        finally:
            await client.close()
    await module.host._dispatch_shutdown()

    restarted = load_sample("04-state-store/state_store.py")
    try:
        async with client_factory(restarted.host) as http_client:
            client = await _native_client(http_client)
            try:
                stored = await client.get_task(GetTaskRequest(id=task.id))
                assert stored.id == task.id
                assert stored.context_id == task.context_id
                assert stored.status.state == TaskState.TASK_STATE_COMPLETED
                assert _text(stored) == "Persisted: remember this"
            finally:
                await client.close()
    finally:
        await restarted.host._dispatch_shutdown()


@pytest.mark.parametrize("relative_path,_expected", _EXAMPLES)
def test_sample_card_respects_port_and_url(load_sample, monkeypatch, relative_path, _expected):
    monkeypatch.setenv("PORT", "8093")
    assert load_sample(relative_path).card.supported_interfaces[0].url == "http://localhost:8093/a2a"
    monkeypatch.setenv("A2A_AGENT_URL", "http://localhost:8094/a2a")
    assert load_sample(relative_path).card.supported_interfaces[0].url == "http://localhost:8094/a2a"


@pytest.mark.asyncio
async def test_sample_client_streams_then_fetches_task(load_sample, client_factory, capsys):
    server = load_sample("03-streaming/streaming.py")
    example = load_sample("sample_client.py")

    def create_http_client(**kwargs):
        client = client_factory(server.host)
        client.headers.update(kwargs.get("headers", {}))
        return client

    with patch.object(example.httpx, "AsyncClient", side_effect=create_http_client):
        await example._run(example._parse_args(["--stream"]))
        output = capsys.readouterr().out
        assert "TASK_STATE_WORKING" in output and "TASK_STATE_COMPLETED" in output
        assert output.count("Artifact chunk") == 4
        task_id = next(line.removeprefix("Task: ") for line in output.splitlines() if line.startswith("Task: "))
        await example._run(example._parse_args(["--get-task", task_id]))
    output = capsys.readouterr().out
    assert f"Task: {task_id}" in output
    assert "TASK_STATE_COMPLETED" in output
    assert "Artifact: Hello from streaming A2A!" in output


@pytest.mark.asyncio
async def test_sample_client_rejects_unadvertised_streaming(load_sample, client_factory):
    server = load_sample("01-hello-world/hello_world.py")
    example = load_sample("sample_client.py")
    with patch.object(example.httpx, "AsyncClient", return_value=client_factory(server.host)):
        with pytest.raises(ValueError, match="does not advertise streaming"):
            await example._run(example._parse_args(["--stream"]))
