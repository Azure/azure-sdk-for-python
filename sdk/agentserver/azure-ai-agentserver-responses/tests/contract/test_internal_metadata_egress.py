# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests: internal_metadata never leaks to clients (spec 025 §A.2).

Verifies the HTTP egress surfaces (POST sync body, GET response, GET
input_items, SSE frames) strip both the item-level ``internal_metadata`` bag
and the response-level reserved ``_internal_metadata`` key, and that the POST
ingress strips a client-supplied reserved key before metadata validation.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponseEventStream, ResponsesAgentServerHost


async def _stamping_handler(request: Any, context: Any, cancellation_signal: asyncio.Event):
    """Emit one message item stamped with internal_metadata + a response-level bag."""

    async def _events():
        stream = ResponseEventStream(response_id=context.response_id, request=request)
        stream.internal_metadata["completed_phases"] = 2  # response-level
        yield stream.emit_created()
        yield stream.emit_in_progress()
        msg = stream.add_output_item_message()
        msg.internal_metadata["phase"] = "gather"  # item-level
        yield msg.emit_added()
        text = msg.add_text_content()
        yield text.emit_added()
        yield text.emit_delta("hello")
        yield text.emit_text_done("hello")
        yield text.emit_done()
        yield msg.emit_done()
        yield stream.emit_completed()

    return _events()


def _client() -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(_stamping_handler)
    return TestClient(app)


def _assert_no_internal_metadata(blob: Any) -> None:
    text = json.dumps(blob)
    assert "internal_metadata" not in text, f"internal_metadata leaked: {text}"
    assert "_internal_metadata" not in text


def test_post_sync_body_strips_internal_metadata():
    client = _client()
    r = client.post(
        "/responses",
        json={"model": "m", "input": "hi", "stream": False, "store": True, "background": False},
    )
    assert r.status_code == 200
    body = r.json()
    _assert_no_internal_metadata(body)
    # The item content is still present — only the internal bag is gone.
    assert body["output"], "expected output items in the response body"


def test_get_response_strips_internal_metadata():
    client = _client()
    rid = client.post(
        "/responses",
        json={"model": "m", "input": "hi", "stream": False, "store": True, "background": False},
    ).json()["id"]
    g = client.get(f"/responses/{rid}")
    assert g.status_code == 200
    _assert_no_internal_metadata(g.json())


def test_get_input_items_strips_internal_metadata():
    client = _client()
    rid = client.post(
        "/responses",
        json={
            "model": "m",
            "input": [{"type": "message", "role": "user", "content": "hi"}],
            "stream": False,
            "store": True,
            "background": False,
        },
    ).json()["id"]
    g = client.get(f"/responses/{rid}/input_items")
    assert g.status_code == 200
    _assert_no_internal_metadata(g.json())


def test_sse_frames_strip_internal_metadata():
    client = _client()
    with client.stream(
        "POST",
        "/responses",
        json={"model": "m", "input": "hi", "stream": True, "store": True, "background": False},
    ) as resp:
        assert resp.status_code == 200
        body = "".join(chunk for chunk in resp.iter_text())
    assert "internal_metadata" not in body, f"internal_metadata leaked on SSE: {body}"
    assert "_internal_metadata" not in body


def test_t15r_response_level_client_key_coexistence_on_egress():
    """Client metadata key survives egress; reserved key never appears."""
    client = _client()
    r = client.post(
        "/responses",
        json={
            "model": "m",
            "input": "hi",
            "stream": False,
            "store": True,
            "background": False,
            "metadata": {"user": "alice"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("metadata", {}).get("user") == "alice"
    _assert_no_internal_metadata(body)


def test_t8r_ingress_strips_client_supplied_reserved_key():
    """A client-supplied _internal_metadata key is stripped before validation."""
    client = _client()
    r = client.post(
        "/responses",
        json={
            "model": "m",
            "input": "hi",
            "stream": False,
            "store": True,
            "background": False,
            "metadata": {"user": "alice", "_internal_metadata": '{"evil":1}'},
        },
    )
    assert r.status_code == 200
    body = r.json()
    # Client cannot inject — reserved key absent on egress, client key intact.
    assert body.get("metadata", {}).get("user") == "alice"
    _assert_no_internal_metadata(body)


def test_t6r2_ingress_16_keys_including_reserved_passes_validation():
    """16 metadata keys where one is the (stripped) reserved key must validate."""
    client = _client()
    md = {f"k{i}": "v" for i in range(15)}
    md["_internal_metadata"] = '{"evil":1}'  # 16th key — stripped before the 16-key check
    r = client.post(
        "/responses",
        json={
            "model": "m",
            "input": "hi",
            "stream": False,
            "store": True,
            "background": False,
            "metadata": md,
        },
    )
    assert r.status_code == 200, r.text
