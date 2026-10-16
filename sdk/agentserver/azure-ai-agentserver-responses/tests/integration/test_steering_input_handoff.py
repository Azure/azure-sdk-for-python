# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Queued steering inputs must pass durable admission and execute."""

from __future__ import annotations

import asyncio
import threading
import time
from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.core.tasks import set_resilient_tasks_enabled
from azure.ai.agentserver.responses import (
    CreateResponse,
    ResponseContext,
    ResponseEventStream,
    ResponsesAgentServerHost,
    ResponsesServerOptions,
)


@pytest.mark.parametrize("resilient_background", [False, True], ids=["resilience-off", "resilience-on"])
@pytest.mark.parametrize("chain", ["conversation", "previous-response"])
@pytest.mark.parametrize("first_terminal", ["return", "completed"])
def test_queued_turn_executes_after_steering_cancellation(
    monkeypatch: pytest.MonkeyPatch, resilient_background: bool, chain: str, first_terminal: str
) -> None:
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)
    monkeypatch.setenv("AGENTSERVER_TASKS_BACKEND", "local")
    set_resilient_tasks_enabled(True)
    host = ResponsesAgentServerHost(
        options=ResponsesServerOptions(
            resilient_background=resilient_background,
            steerable_conversations=True,
            shutdown_grace_period_seconds=1,
        )
    )
    cancelled = threading.Event()
    entries: list[tuple[str, bool]] = []
    active = 0
    max_active = 0

    @host.response_handler
    async def handler(request: CreateResponse, context: ResponseContext, cancellation_signal: asyncio.Event):
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        entries.append((context.response_id, context.is_steered_turn))
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        try:
            yield stream.emit_created()
            yield stream.emit_in_progress()
            if len(entries) == 1:
                await asyncio.wait_for(cancellation_signal.wait(), timeout=10)
                cancelled.set()
                if first_terminal == "return":
                    return
            yield stream.emit_completed()
        finally:
            active -= 1

    payload: dict[str, Any] = {
        "model": "test-model",
        "agent_session_id": "steering_handoff_session",
        "input": "first",
        "store": True,
        "background": True,
        "stream": False,
    }
    if chain == "conversation":
        payload["conversation"] = "conv_steering_handoff"

    with TestClient(host) as client:
        first = client.post("/responses", json=payload)
        assert first.status_code == 200, first.text
        first_id = first.json()["id"]
        second = client.post(
            "/responses",
            json={**payload, "input": "second", "previous_response_id": first_id},
        )
        assert second.status_code == 200, second.text
        assert second.json()["status"] == "queued", second.text
        second_id = second.json()["id"]

        deadline = time.monotonic() + 5
        observed: dict[str, Any] = {}
        while time.monotonic() < deadline:
            response = client.get(f"/responses/{second_id}")
            assert response.status_code == 200, response.text
            observed = response.json()
            if observed["status"] in {"completed", "failed", "cancelled", "incomplete"}:
                break
            time.sleep(0.01)

        assert cancelled.is_set()
        assert observed["status"] == "completed", observed
        assert entries == [(first_id, False), (second_id, True)]
        assert max_active == 1

        third = client.post(
            "/responses",
            json={**payload, "input": "third", "previous_response_id": second_id},
        )
        assert third.status_code == 200, third.text
        third_id = third.json()["id"]
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            response = client.get(f"/responses/{third_id}")
            assert response.status_code == 200, response.text
            observed = response.json()
            if observed["status"] in {"completed", "failed", "cancelled", "incomplete"}:
                break
            time.sleep(0.01)
        assert observed["status"] == "completed", observed
        assert entries == [(first_id, False), (second_id, True), (third_id, False)]
