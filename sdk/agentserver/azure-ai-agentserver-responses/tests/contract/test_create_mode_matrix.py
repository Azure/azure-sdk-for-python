# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract matrix tests for POST /responses store/background/stream combinations.

These cases mirror C1-C8 in docs/api-behaviour-contract.md.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost


def _noop_response_handler(request: Any, context: Any, cancellation_signal: Any):
    """Minimal handler used to wire contract matrix tests."""

    async def _events():
        if False:  # pragma: no cover - keep async generator shape.
            yield None

    return _events()


class _CreateModeCase:
    def __init__(
        self,
        id: str,
        store: bool,
        background: bool,
        stream: bool,
        expected_http: int,
        expected_content_prefix: str,
        expected_get_status: int | None = None,
    ) -> None:
        self.id = id
        self.store = store
        self.background = background
        self.stream = stream
        self.expected_http = expected_http
        self.expected_content_prefix = expected_content_prefix
        self.expected_get_status = expected_get_status


def _build_client() -> TestClient:
    app = ResponsesAgentServerHost()
    app.response_handler(_noop_response_handler)
    return TestClient(app)


def _collect_sse_events(response: Any) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    current_type: str | None = None
    current_data: str | None = None

    for line in response.iter_lines():
        if not line:
            if current_type is not None:
                payload = json.loads(current_data) if current_data else {}
                events.append({"type": current_type, "data": payload})
            current_type = None
            current_data = None
            continue

        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()

    if current_type is not None:
        payload = json.loads(current_data) if current_data else {}
        events.append({"type": current_type, "data": payload})

    return events


def _extract_response_id_from_sse_text(raw_text: str) -> str | None:
    current_type: str | None = None
    current_data: str | None = None

    for line in raw_text.splitlines():
        if not line:
            if current_type is not None and current_data:
                payload = json.loads(current_data)
                candidate = payload.get("response", {}).get("id")
                if isinstance(candidate, str) and candidate:
                    return candidate
            current_type = None
            current_data = None
            continue

        if line.startswith("event:"):
            current_type = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            current_data = line.split(":", 1)[1].strip()

    if current_type is not None and current_data:
        payload = json.loads(current_data)
        candidate = payload.get("response", {}).get("id")
        if isinstance(candidate, str) and candidate:
            return candidate

    return None


_CASES: tuple[_CreateModeCase, ...] = (
    _CreateModeCase(
        id="C1",
        store=True,
        background=False,
        stream=False,
        expected_http=200,
        expected_content_prefix="application/json",
        expected_get_status=200,
    ),
    _CreateModeCase(
        id="C2",
        store=True,
        background=False,
        stream=True,
        expected_http=200,
        expected_content_prefix="text/event-stream",
        expected_get_status=200,
    ),
    _CreateModeCase(
        id="C3",
        store=True,
        background=True,
        stream=False,
        expected_http=200,
        expected_content_prefix="application/json",
        expected_get_status=200,
    ),
    _CreateModeCase(
        id="C4",
        store=True,
        background=True,
        stream=True,
        expected_http=200,
        expected_content_prefix="text/event-stream",
        expected_get_status=200,
    ),
    _CreateModeCase(
        id="C5",
        store=False,
        background=False,
        stream=False,
        expected_http=200,
        expected_content_prefix="application/json",
        expected_get_status=404,
    ),
    _CreateModeCase(
        id="C6",
        store=False,
        background=False,
        stream=True,
        expected_http=200,
        expected_content_prefix="text/event-stream",
        expected_get_status=404,
    ),
    _CreateModeCase(
        id="C7",
        store=False,
        background=True,
        stream=False,
        expected_http=400,
        expected_content_prefix="application/json",
        expected_get_status=None,
    ),
    _CreateModeCase(
        id="C8",
        store=False,
        background=True,
        stream=True,
        expected_http=400,
        expected_content_prefix="application/json",
        expected_get_status=None,
    ),
)


@pytest.mark.parametrize(
    "case",
    [
        *_CASES,
    ],
    ids=[case.id for case in _CASES],
)
def test_create_mode_matrix__http_and_content_type(case: _CreateModeCase) -> None:
    client = _build_client()
    payload = {
        "model": "gpt-4o-mini",
        "input": "hello",
        "stream": case.stream,
        "store": case.store,
        "background": case.background,
    }

    response = client.post("/responses", json=payload)

    assert response.status_code == case.expected_http
    assert response.headers.get("content-type", "").startswith(case.expected_content_prefix)
    # Contract: C7/C8 (store=false, background=true) → error.code="unsupported_parameter", error.param="background"
    if case.id in {"C7", "C8"}:
        error = response.json().get("error", {})
        assert error.get("code") == "unsupported_parameter"
        assert error.get("param") == "background"

    if case.expected_http == 400:
        body = response.json()
        assert isinstance(body.get("error"), dict)
        assert body["error"].get("type") == "invalid_request_error"


@pytest.mark.parametrize(
    "case",
    [case for case in _CASES if case.expected_http == 200 and case.expected_get_status is not None],
    ids=[case.id for case in _CASES if case.expected_http == 200 and case.expected_get_status is not None],
)
def test_create_mode_matrix__get_visibility(case: _CreateModeCase) -> None:
    client = _build_client()
    payload = {
        "model": "gpt-4o-mini",
        "input": "hello",
        "stream": case.stream,
        "store": case.store,
        "background": case.background,
    }

    create_response = client.post("/responses", json=payload)
    assert create_response.status_code == 200
    content_type = create_response.headers.get("content-type", "")

    if content_type.startswith("text/event-stream"):
        response_id = _extract_response_id_from_sse_text(create_response.text)
    else:
        body = create_response.json()
        response_id = body.get("id")

    assert isinstance(response_id, str) and response_id

    get_response = client.get(f"/responses/{response_id}")
    assert get_response.status_code == case.expected_get_status
