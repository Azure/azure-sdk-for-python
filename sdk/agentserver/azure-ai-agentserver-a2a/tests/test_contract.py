# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Language-neutral request and storage contracts exercised through native APIs."""

import base64
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from a2a.helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor
from a2a.server.context import ServerCallContext
from a2a.server.routes import ServerCallContextBuilder
from a2a.types import AgentCard, ListTasksRequest, Task, TaskState, TaskStatus
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from azure.ai.agentserver.a2a import A2AAgentServerHost, FoundryTaskStore

CONTRACT = json.loads((Path(__file__).parent / "fixtures" / "a2a-contract.json").read_text())


class _Executor(AgentExecutor):
    async def execute(self, context, event_queue):
        await event_queue.enqueue_event(new_text_message("contract reply"))

    async def cancel(self, context, event_queue):
        raise NotImplementedError


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/a2a", "/invocations/a2a"])
@pytest.mark.parametrize("case", CONTRACT["protocol_version_cases"], ids=lambda case: case["name"])
async def test_protocol_selection_matches_dispatch_and_tracing(client_factory, monkeypatch, path, case):
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    with patch("azure.ai.agentserver.a2a._tracing.trace.get_tracer", provider.get_tracer):
        host = A2AAgentServerHost(
            agent_card=AgentCard(name="contract", version="1"),
            agent_executor=_Executor(),
            configure_observability=None,
        )
        try:
            async with client_factory(host) as client:
                response = await client.post(
                    path,
                    headers=case["headers"],
                    params=case["query"],
                    json={
                        "jsonrpc": "2.0",
                        "id": case["name"],
                        "method": "SendMessage",
                        "params": {
                            "message": {"messageId": case["name"], "role": "ROLE_USER", "parts": [{"text": "test"}]},
                        },
                    },
                )
            assert response.status_code == 200
            body = response.json()
            assert body["id"] == case["name"]
            if "error_code" in case:
                assert body["error"]["code"] == case["error_code"]
            else:
                assert body["result"]["message"]["parts"][0]["text"] == "contract reply"
            spans = [
                span
                for span in exporter.get_finished_spans()
                if span.instrumentation_scope.name == "Azure.AI.AgentServer.A2A"
            ]
            assert len(spans) == 1
            assert spans[0].attributes.get("a2a.protocol.version") == case.get("effective_version")
            if "error_code" in case:
                assert spans[0].attributes["error.type"] == str(case["error_code"])
        finally:
            await host._dispatch_shutdown()
            provider.shutdown()


@pytest.mark.asyncio
async def test_query_version_preserves_custom_context_builder(client_factory, monkeypatch):
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    calls = []

    class Builder(ServerCallContextBuilder):
        def build(self, request):
            context = ServerCallContext(state={"custom": "kept"}, tenant="tenant")
            calls.append(context)
            return context

    host = A2AAgentServerHost(
        agent_card=AgentCard(name="contract", version="1"),
        agent_executor=_Executor(),
        context_builder=Builder(),
        configure_observability=None,
    )
    try:
        async with client_factory(host) as client:
            response = await client.post(
                "/a2a?a2a-version=1.0",
                json={
                    "jsonrpc": "2.0",
                    "id": "custom",
                    "method": "SendMessage",
                    "params": {
                        "message": {"messageId": "custom", "role": "ROLE_USER", "parts": [{"text": "test"}]},
                    },
                },
            )
        assert "result" in response.json()
        assert len(calls) == 1
        assert calls[0].state["custom"] == "kept"
        assert calls[0].state["headers"]["a2a-version"] == "1.0"
    finally:
        await host._dispatch_shutdown()


@pytest.fixture
def local_store_root(monkeypatch, tmp_path):
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    monkeypatch.setenv("AGENTSERVER_STATE_ROOT", str(tmp_path))


def test_long_item_keys_retain_owner_scope_and_identifier_uniqueness():
    first = FoundryTaskStore._key("\u00e9" * 200, "a" * 64)
    assert len(first) == 64
    assert first != FoundryTaskStore._key("\u00e9" * 200, "b" * 64)
    assert first != FoundryTaskStore._key("\u00e9" * 199 + "x", "a" * 64)


@pytest.mark.asyncio
@pytest.mark.parametrize("case", CONTRACT["storage_tag_cases"], ids=lambda case: case["name"])
async def test_storage_tag_bound_preserves_full_task_and_listing(local_store_root, case):
    task = Task(
        id="t" * case["task_id_length"],
        context_id="c" * case["context_id_length"],
        status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED),
    )
    task.status.timestamp.FromNanoseconds(10000000001)
    context = ServerCallContext()
    async with FoundryTaskStore(case["name"]) as store:
        backend = await store._store(create=True)
        original_set = backend.set_item

        async def bounded_set(key, value, **kwargs):
            assert len(key) <= 128
            assert all(len(value) <= 256 for value in kwargs["tags"].values())
            return await original_set(key, value, **kwargs)

        with patch.object(backend, "set_item", side_effect=bounded_set) as write:
            await store.save(task, context)
        tags = write.call_args.kwargs["tags"]
        if "key_chars" in case:
            assert len(write.call_args.args[0]) == case["key_chars"]
        assert ("a2a_list" in tags) is case["summary_tag"]
        if "summary_chars" in case:
            assert len(tags["a2a_list"]) == case["summary_chars"]
        assert await store.get(task.id, context) == task
        assert list((await store.list(ListTasksRequest(), context)).tasks) == [task]
        if not case["summary_tag"]:
            decoded = Task.FromString(
                base64.b64decode(
                    (
                        await backend.get_item(
                            store._key(task.id, store._owner(context)),
                        )
                    ).value["task"]
                )
            )
            assert decoded == task
        await store.delete(task.id, context)
        assert await store.get(task.id, context) is None


@pytest.mark.asyncio
@pytest.mark.parametrize("case", CONTRACT["list_cases"], ids=lambda case: case["name"])
async def test_portable_task_list_contract(local_store_root, case):
    context = ServerCallContext()
    async with FoundryTaskStore(case["name"]) as store:
        for item in case["tasks"]:
            task = Task(id=item["id"], status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED))
            task.status.timestamp.FromNanoseconds(item["timestamp_ns"])
            await store.save(task, context)
        request = ListTasksRequest(page_size=case["page_size"])
        if "cutoff_ns" in case:
            request.status_timestamp_after.FromNanoseconds(case["cutoff_ns"])
        for index, expected in enumerate(case["expected_pages"]):
            page = await store.list(request, context)
            assert [task.id for task in page.tasks] == expected
            assert page.page_size == case["page_size"]
            assert page.total_size == case["expected_total_sizes"][index]
            assert bool(page.next_page_token) == (index < len(case["expected_pages"]) - 1)
            if index == 0:
                for task_id in case.get("delete_after_first", []):
                    await store.delete(task_id, context)
            request.page_token = page.next_page_token
