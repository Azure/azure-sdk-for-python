# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""A failed turn must not poison the conversation for later turns.

End-to-end through ``ResponsesAgentServerHost``: a handler fails when its
input carries a ``function_call_output`` that matches no call. The input of
that failed turn must not be replayed into the history of later turns in
the same conversation, or of turns chained through ``previous_response_id``,
in synchronous, streaming and background modes. The failed response and its
input items remain retrievable for diagnostics.

Regression coverage for https://github.com/Azure/azure-sdk-for-python/issues/48929.
"""

from __future__ import annotations

import asyncio
import json as _json
import time
from typing import Any
from uuid import uuid4

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost
from azure.ai.agentserver.responses.models._helpers import get_input_expanded
from azure.ai.agentserver.responses.streaming._event_stream import ResponseEventStream

_BAD_CALL_ID = "call_that_does_not_exist"


# ════════════════════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════════════════════


class _RecordingHandler:
    """Records the history each turn saw; fails a turn whose input carries an unmatched ``function_call_output``."""

    def __init__(self) -> None:
        self.histories: list[list[dict[str, Any]]] = []

    def as_handler(self):
        recorder = self

        async def handler(request: Any, context: Any, cancellation_signal: asyncio.Event):
            history = [dict(item) for item in await context.get_history()]
            recorder.histories.append(history)
            input_items = [dict(item) for item in get_input_expanded(request)]
            unmatched = any(
                item.get("type") == "function_call_output" and item.get("call_id") == _BAD_CALL_ID
                for item in input_items
            )

            async def _events():
                stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
                yield stream.emit_created()
                if unmatched:
                    yield stream.emit_failed(
                        code="invalid_request",
                        message=f"No tool call found for function call output with call_id {_BAD_CALL_ID}.",
                    )
                else:
                    yield stream.emit_completed()

            return _events()

        return handler


def _build_client() -> tuple[TestClient, _RecordingHandler]:
    recorder = _RecordingHandler()
    app = ResponsesAgentServerHost()
    app.response_handler(recorder.as_handler())
    return TestClient(app), recorder


def _poison_input() -> list[dict[str, Any]]:
    return [
        {"role": "user", "content": "Hello"},
        {"type": "function_call_output", "call_id": _BAD_CALL_ID, "output": "invalid output"},
    ]


def _collect_sse_events(response: Any) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None
    for line in response.iter_lines():
        if not line:
            if current_type is not None:
                events.append({"type": current_type, "data": _json.loads(current_data) if current_data else {}})
            current_type = None
            current_data = None
            continue
        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()
    if current_type is not None:
        events.append({"type": current_type, "data": _json.loads(current_data) if current_data else {}})
    return events


def _post(client: TestClient, **body: Any) -> dict[str, Any]:
    resp = client.post("/responses", json={"model": "test", **body})
    assert resp.status_code == 200, resp.text
    return resp.json()


def _post_stream(client: TestClient, **body: Any) -> dict[str, Any]:
    with client.stream("POST", "/responses", json={"model": "test", "stream": True, **body}) as resp:
        assert resp.status_code == 200
        events = _collect_sse_events(resp)
    terminal = [e for e in events if e["type"] in ("response.completed", "response.failed")]
    assert terminal, [e["type"] for e in events]
    return terminal[-1]["data"]["response"]


def _wait_terminal(client: TestClient, response_id: str, timeout: float = 5.0) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while True:
        body = client.get(f"/responses/{response_id}").json()
        if body.get("status") in ("completed", "failed", "cancelled", "incomplete"):
            return body
        assert time.monotonic() < deadline, f"response {response_id} did not reach a terminal state: {body}"
        time.sleep(0.05)


def _conv() -> str:
    """Unique conversation id: the host's default file store is shared within a process."""
    return f"conv_{uuid4().hex}"


def _history_types(history: list[dict[str, Any]]) -> list[str]:
    return [str(item.get("type")) for item in history]


# ════════════════════════════════════════════════════════════
# conversation scope
# ════════════════════════════════════════════════════════════


def test_failed_turn_input_is_not_replayed_into_conversation() -> None:
    """Issue #48929 repro: a failed turn must not make the next valid turn in the conversation fail."""
    client, handler = _build_client()
    conv = _conv()

    failed = _post(client, conversation=conv, input=_poison_input())
    assert failed["status"] == "failed"
    assert failed["error"]["code"] == "invalid_request"

    ok = _post(client, conversation=conv, input="Hello, how are you?")
    assert ok["status"] == "completed"

    # The second turn saw no history from the failed turn.
    assert handler.histories[1] == []

    # A third turn sees only the successful second turn.
    third = _post(client, conversation=conv, input="And now?")
    assert third["status"] == "completed"
    assert _history_types(handler.histories[2]) == ["message"]
    assert all(item.get("call_id") != _BAD_CALL_ID for item in handler.histories[2])


def test_successful_turns_before_and_after_a_failure_are_kept() -> None:
    client, handler = _build_client()
    conv = _conv()

    first = _post(client, conversation=conv, input="first")
    assert first["status"] == "completed"
    failed = _post(client, conversation=conv, input=_poison_input())
    assert failed["status"] == "failed"
    third = _post(client, conversation=conv, input="third")
    assert third["status"] == "completed"

    # The third turn's history is exactly the first turn's input: no poison, nothing dropped.
    history = handler.histories[2]
    assert _history_types(history) == ["message"]
    assert history[0]["role"] == "user"
    assert all(item.get("call_id") != _BAD_CALL_ID for item in history)


def test_failed_response_and_its_input_items_remain_retrievable() -> None:
    """Exclusion from history is not deletion: diagnostics still work."""
    client, _handler = _build_client()
    conv = _conv()

    failed = _post(client, conversation=conv, input=_poison_input())
    response_id = failed["id"]

    stored = client.get(f"/responses/{response_id}")
    assert stored.status_code == 200
    assert stored.json()["status"] == "failed"

    items = client.get(f"/responses/{response_id}/input_items").json()
    types = [item.get("type") for item in items.get("data", [])]
    assert "function_call_output" in types


# ════════════════════════════════════════════════════════════
# previous_response_id scope
# ════════════════════════════════════════════════════════════


def test_chaining_from_failed_response_does_not_replay_its_input() -> None:
    client, handler = _build_client()

    ok = _post(client, input="first")
    failed = _post(client, previous_response_id=ok["id"], input=_poison_input())
    assert failed["status"] == "failed"

    chained = _post(client, previous_response_id=failed["id"], input="Hello again")
    assert chained["status"] == "completed"

    # Only the successful first turn is inherited through the failed response.
    history = handler.histories[2]
    assert _history_types(history) == ["message"]
    assert all(item.get("call_id") != _BAD_CALL_ID for item in history)


# ════════════════════════════════════════════════════════════
# streaming and background modes
# ════════════════════════════════════════════════════════════


def test_streaming_failed_turn_input_is_not_replayed() -> None:
    client, handler = _build_client()
    conv = _conv()

    failed = _post_stream(client, conversation=conv, input=_poison_input())
    assert failed["status"] == "failed"

    ok = _post_stream(client, conversation=conv, input="Hello, how are you?")
    assert ok["status"] == "completed"
    assert handler.histories[1] == []


def test_background_failed_turn_input_is_not_replayed() -> None:
    client, handler = _build_client()
    conv = _conv()

    started = _post(client, conversation=conv, background=True, input=_poison_input())
    failed = _wait_terminal(client, started["id"])
    assert failed["status"] == "failed"

    ok = _post(client, conversation=conv, input="Hello, how are you?")
    assert ok["status"] == "completed"
    assert handler.histories[1] == []
