# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""All POST modes reuse one validated ID lookup, without dropping storage writes."""

import asyncio
import threading
from unittest.mock import AsyncMock

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses._id_generator import IdGenerator
from azure.ai.agentserver.responses.store._file import FileResponseStore
from azure.ai.agentserver.responses.streaming import ResponseEventStream


@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("background", [False, True])
@pytest.mark.parametrize("resilient", [False, True])
@pytest.mark.parametrize("empty", [False, True])
@pytest.mark.parametrize("read_history", [False, True])
def test_all_modes_share_history_ids_and_keep_materialization_scoped(
    monkeypatch, tmp_path, streaming, background, resilient, empty, read_history
):
    provider = FileResponseStore(tmp_path / "responses")
    history = AsyncMock(return_value=[] if empty else ["history"])
    items = AsyncMock(return_value=[])
    create = AsyncMock(wraps=provider.create_response)
    update = AsyncMock(wraps=provider.update_response)
    finished = threading.Event()
    monkeypatch.setattr(provider, "get_history_item_ids", history)
    monkeypatch.setattr(provider, "get_items", items)
    monkeypatch.setattr(provider, "create_response", create)

    async def terminal_update(*args, **kwargs):
        await update(*args, **kwargs)
        finished.set()

    monkeypatch.setattr(provider, "update_response", terminal_update)
    app = ResponsesAgentServerHost(
        options=ResponsesServerOptions(resilient_background=resilient),
        store=provider,
    )

    async def handler(request, context, cancellation_signal):
        if read_history:
            histories = await asyncio.gather(context.get_history(), context.get_history())
            assert histories[0] is histories[1]
        events = ResponseEventStream(response_id=context.response_id, model="m")
        yield events.emit_created()
        yield events.emit_completed()

    app.response_handler(handler)
    with TestClient(app) as client:
        response = client.post(
            "/responses",
            json={
                "model": "m",
                "input": "hi",
                "previous_response_id": IdGenerator.new_response_id(),
                "stream": streaming,
                "background": background,
                "store": True,
            },
            headers={"x-agent-user-id": "user", "x-agent-foundry-call-id": "call"},
        )
        assert response.status_code == 200
        if streaming:
            assert "response.completed" in response.text
        if background:
            assert finished.wait(5), "background terminal write did not complete"
        history.assert_awaited_once()
        assert history.await_args.kwargs["context"].user_id_key == "user"
        assert history.await_args.kwargs["context"].call_id == "call"
        assert items.await_count == (1 if read_history and not empty else 0)
        create.assert_awaited_once()
        assert create.await_args.args[2] == ([] if empty else ["history"])
        update.assert_awaited_once()
