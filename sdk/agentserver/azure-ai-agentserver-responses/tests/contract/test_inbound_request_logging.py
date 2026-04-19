# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract tests for inbound request logging middleware and handler diagnostic logging.

Validates that:
- InboundRequestLoggingMiddleware logs request start and completion at INFO.
- Status >= 400 triggers WARNING on completion.
- Correlation headers (x-request-id, x-ms-client-request-id) appear in log.
- Query strings are NOT logged (path only).
- Handler-level diagnostic logs fire at INFO for each endpoint.
- Orchestrator logs handler invocation with handler name.
"""

from __future__ import annotations

import asyncio
import json as _json
import logging
from typing import Any

import pytest

from azure.ai.agentserver.responses import ResponsesAgentServerHost


# ── Helpers ───────────────────────────────────────────────

LOGGER_NAME = "azure.ai.agentserver"

# A valid-format response ID that will never exist in state/storage.
_NONEXISTENT_ID = "caresp_00000000000000000000000000000000000000000000000000"


def _make_app(handler=None):
    """Create a host with a simple handler."""
    app = ResponsesAgentServerHost(configure_observability=None)

    @app.response_handler
    def _default_handler(request: Any, context: Any, cancellation_signal: Any):
        async def _events():
            if False:  # pragma: no cover
                yield None
        return _events()

    if handler is not None:
        app.response_handler(handler)
    return app


class _AsgiResponse:
    def __init__(self, status_code: int, body: bytes, headers: list[tuple[bytes, bytes]]) -> None:
        self.status_code = status_code
        self.body = body
        self.headers = headers

    def json(self) -> Any:
        return _json.loads(self.body)


class _AsyncAsgiClient:
    def __init__(self, app: Any) -> None:
        self._app = app

    @staticmethod
    def _build_scope(
        method: str, path: str, body: bytes,
        headers: list[tuple[bytes, bytes]] | None = None,
    ) -> dict[str, Any]:
        hdr: list[tuple[bytes, bytes]] = list(headers or [])
        query_string = b""
        if "?" in path:
            path, qs = path.split("?", 1)
            query_string = qs.encode()
        if body:
            hdr += [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode()),
            ]
        return {
            "type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
            "method": method, "headers": hdr, "scheme": "http",
            "path": path, "raw_path": path.encode(),
            "query_string": query_string,
            "server": ("localhost", 80), "client": ("127.0.0.1", 123),
            "root_path": "",
        }

    async def request(
        self, method: str, path: str, *,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> _AsgiResponse:
        body = _json.dumps(json_body).encode() if json_body else b""
        raw_headers = (
            [(k.lower().encode(), v.encode()) for k, v in headers.items()]
            if headers else []
        )
        scope = self._build_scope(method, path, body, raw_headers)
        status_code: int | None = None
        response_headers: list[tuple[bytes, bytes]] = []
        body_parts: list[bytes] = []
        request_sent = False
        response_done = asyncio.Event()

        async def receive() -> dict[str, Any]:
            nonlocal request_sent
            if not request_sent:
                request_sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            await response_done.wait()
            return {"type": "http.disconnect"}

        async def send(message: dict[str, Any]) -> None:
            nonlocal status_code, response_headers
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = message.get("headers", [])
            elif message["type"] == "http.response.body":
                chunk = message.get("body", b"")
                if chunk:
                    body_parts.append(chunk)
                if not message.get("more_body", False):
                    response_done.set()

        await self._app(scope, receive, send)
        assert status_code is not None
        return _AsgiResponse(status_code=status_code, body=b"".join(body_parts), headers=response_headers)

    async def get(self, path: str, *, headers: dict[str, str] | None = None) -> _AsgiResponse:
        return await self.request("GET", path, headers=headers)

    async def post(
        self, path: str, *, json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> _AsgiResponse:
        return await self.request("POST", path, json_body=json_body, headers=headers)

    async def delete(self, path: str, *, headers: dict[str, str] | None = None) -> _AsgiResponse:
        return await self.request("DELETE", path, headers=headers)


# ── Middleware Tests ──────────────────────────────────────


class TestInboundRequestLoggingMiddleware:
    """Inbound request logging middleware tests."""

    @pytest.mark.asyncio
    async def test_logs_request_start_and_completion_info(self, caplog: pytest.LogCaptureFixture):
        """Middleware logs start and completion at INFO for successful requests."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            resp = await client.post("/responses", json_body={"model": "m"})
        assert resp.status_code == 200

        messages = [r.message for r in caplog.records if r.name == LOGGER_NAME]
        start_msgs = [m for m in messages if "Inbound POST /responses started" in m]
        assert len(start_msgs) >= 1, f"Expected start log, got: {messages}"

        completion_msgs = [m for m in messages if "Inbound POST /responses completed" in m]
        assert len(completion_msgs) >= 1, f"Expected completion log, got: {messages}"
        assert "200" in completion_msgs[0]

    @pytest.mark.asyncio
    async def test_logs_warning_for_4xx_status(self, caplog: pytest.LogCaptureFixture):
        """Middleware logs WARNING for 4xx responses."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            resp = await client.get(f"/responses/{_NONEXISTENT_ID}")
        assert resp.status_code == 404

        warning_records = [
            r for r in caplog.records
            if r.name == LOGGER_NAME
            and r.levelno == logging.WARNING
            and "Inbound" in r.message
            and "completed" in r.message
        ]
        assert len(warning_records) >= 1, "Expected WARNING for 404"
        assert "404" in warning_records[0].message

    @pytest.mark.asyncio
    async def test_correlation_headers_in_log(self, caplog: pytest.LogCaptureFixture):
        """Middleware includes x-request-id and x-ms-client-request-id in log."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            resp = await client.post(
                "/responses",
                json_body={"model": "m"},
                headers={
                    "x-request-id": "req-abc-123",
                    "x-ms-client-request-id": "client-xyz",
                },
            )
        assert resp.status_code == 200

        messages = [r.message for r in caplog.records if r.name == LOGGER_NAME]
        start_msgs = [m for m in messages if "Inbound" in m and "started" in m]
        assert len(start_msgs) >= 1
        assert "x-request-id: req-abc-123" in start_msgs[0]
        assert "x-ms-client-request-id: client-xyz" in start_msgs[0]

    @pytest.mark.asyncio
    async def test_trace_id_extracted_from_traceparent(self, caplog: pytest.LogCaptureFixture):
        """Middleware extracts trace-id from traceparent header when no OTel span is active."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        trace_id = "0af7651916cd43dd8448eb211c80319c"
        traceparent = f"00-{trace_id}-b7ad6b7169203331-01"
        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            resp = await client.post(
                "/responses",
                json_body={"model": "m"},
                headers={"traceparent": traceparent},
            )
        assert resp.status_code == 200

        messages = [r.message for r in caplog.records if r.name == LOGGER_NAME]
        start_msgs = [m for m in messages if "Inbound" in m and "started" in m]
        assert len(start_msgs) >= 1
        assert f"trace-id: {trace_id}" in start_msgs[0]

    @pytest.mark.asyncio
    async def test_query_string_not_logged(self, caplog: pytest.LogCaptureFixture):
        """Middleware logs path only, not query string."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            resp = await client.get(f"/responses/{_NONEXISTENT_ID}?stream=true")
        # The response should be 404 but that's fine — we're checking the logs
        messages = [r.message for r in caplog.records if r.name == LOGGER_NAME and "Inbound" in r.message]
        assert len(messages) >= 1
        for msg in messages:
            assert "stream=true" not in msg, f"Query string leaked into log: {msg}"
            # Path should be present
            assert "/responses/" in msg

    @pytest.mark.asyncio
    async def test_duration_in_completion_log(self, caplog: pytest.LogCaptureFixture):
        """Middleware includes duration in completion log."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            await client.post("/responses", json_body={"model": "m"})

        completion_msgs = [
            r.message for r in caplog.records
            if r.name == LOGGER_NAME and "Inbound" in r.message and "completed" in r.message
        ]
        assert len(completion_msgs) >= 1
        assert "ms" in completion_msgs[0], f"Expected duration in ms: {completion_msgs[0]}"


# ── Handler Diagnostic Logging Tests ──────────────────────


class TestHandlerDiagnosticLogging:
    """Handler-level diagnostic logging tests."""

    @pytest.mark.asyncio
    async def test_create_logs_parameters(self, caplog: pytest.LogCaptureFixture):
        """POST /responses logs creation parameters."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            resp = await client.post("/responses", json_body={"model": "test-model"})
        assert resp.status_code == 200

        messages = [r.message for r in caplog.records if r.name == LOGGER_NAME]
        create_msgs = [m for m in messages if "Creating response" in m]
        assert len(create_msgs) >= 1, f"Expected 'Creating response' log, got: {messages}"
        msg = create_msgs[0]
        assert "streaming=" in msg
        assert "background=" in msg
        assert "store=" in msg
        assert "model=" in msg

    @pytest.mark.asyncio
    async def test_create_sync_logs_completion(self, caplog: pytest.LogCaptureFixture):
        """Synchronous POST /responses logs response completion."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            resp = await client.post("/responses", json_body={"model": "m"})
        assert resp.status_code == 200

        messages = [r.message for r in caplog.records if r.name == LOGGER_NAME]
        completed_msgs = [m for m in messages if "completed: status=" in m]
        assert len(completed_msgs) >= 1, f"Expected completion log, got: {messages}"
        assert "output_count=" in completed_msgs[0]

    @pytest.mark.asyncio
    async def test_get_logs_response_retrieval(self, caplog: pytest.LogCaptureFixture):
        """GET /responses/{id} logs entry and retrieval."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        # Create a response first
        create_resp = await client.post("/responses", json_body={"model": "m"})
        assert create_resp.status_code == 200
        response_id = create_resp.json()["id"]

        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            resp = await client.get(f"/responses/{response_id}")
        assert resp.status_code == 200

        messages = [r.message for r in caplog.records if r.name == LOGGER_NAME]
        get_msgs = [m for m in messages if f"Getting response {response_id}" in m]
        assert len(get_msgs) >= 1, f"Expected GET log, got: {messages}"

        retrieved_msgs = [m for m in messages if f"Retrieved response {response_id}" in m]
        assert len(retrieved_msgs) >= 1, f"Expected retrieval log, got: {messages}"

    @pytest.mark.asyncio
    async def test_get_sse_replay_logs(self, caplog: pytest.LogCaptureFixture):
        """GET /responses/{id}?stream=true logs SSE replay entry."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            # Non-existent but valid format — just check the log message
            await client.get(f"/responses/{_NONEXISTENT_ID}?stream=true")

        messages = [r.message for r in caplog.records if r.name == LOGGER_NAME]
        sse_msgs = [m for m in messages if "with SSE replay" in m]
        assert len(sse_msgs) >= 1, f"Expected SSE replay log, got: {messages}"

    @pytest.mark.asyncio
    async def test_delete_logs_entry_and_success(self, caplog: pytest.LogCaptureFixture):
        """DELETE /responses/{id} logs entry and success."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        create_resp = await client.post("/responses", json_body={"model": "m"})
        assert create_resp.status_code == 200
        response_id = create_resp.json()["id"]

        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            resp = await client.delete(f"/responses/{response_id}")
        assert resp.status_code == 200

        messages = [r.message for r in caplog.records if r.name == LOGGER_NAME]
        delete_entry = [m for m in messages if f"Deleting response {response_id}" in m]
        assert len(delete_entry) >= 1, f"Expected delete entry log, got: {messages}"

        delete_success = [m for m in messages if f"Deleted response {response_id}" in m]
        assert len(delete_success) >= 1, f"Expected delete success log, got: {messages}"

    @pytest.mark.asyncio
    async def test_cancel_logs_entry(self, caplog: pytest.LogCaptureFixture):
        """POST /responses/{id}/cancel logs cancellation entry."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            # Cancel on a non-existent response — just verify the entry log fires
            await client.post(f"/responses/{_NONEXISTENT_ID}/cancel")

        messages = [r.message for r in caplog.records if r.name == LOGGER_NAME]
        cancel_msgs = [m for m in messages if "Cancelling response" in m]
        assert len(cancel_msgs) >= 1, f"Expected cancel entry log, got: {messages}"

    @pytest.mark.asyncio
    async def test_input_items_logs_entry(self, caplog: pytest.LogCaptureFixture):
        """GET /responses/{id}/input_items logs entry."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            await client.get(f"/responses/{_NONEXISTENT_ID}/input_items")

        messages = [r.message for r in caplog.records if r.name == LOGGER_NAME]
        input_msgs = [m for m in messages if "Getting input items" in m]
        assert len(input_msgs) >= 1, f"Expected input items log, got: {messages}"


# ── Orchestrator Handler Invocation Logging Tests ─────────


class TestOrchestratorHandlerLogging:
    """Orchestrator-level handler invocation logging."""

    @pytest.mark.asyncio
    async def test_invoking_handler_logged(self, caplog: pytest.LogCaptureFixture):
        """Orchestrator logs 'Invoking handler' with handler name."""
        app = _make_app()
        client = _AsyncAsgiClient(app)

        with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
            resp = await client.post("/responses", json_body={"model": "m"})
        assert resp.status_code == 200

        messages = [r.message for r in caplog.records if r.name == LOGGER_NAME]
        handler_msgs = [m for m in messages if "Invoking handler" in m]
        assert len(handler_msgs) >= 1, f"Expected handler invocation log, got: {messages}"
        # Should include the response ID
        response_id = resp.json()["id"]
        assert response_id in handler_msgs[0]
