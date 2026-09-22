# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract test: streaming spans are flushed AFTER the stream body is drained.

For streaming requests the handler runs lazily while Starlette iterates the
``StreamingResponse`` body, which happens *after* ``handle_create`` returns.  The
outer ``handle_create`` ``finally`` must skip flushing for streaming requests.
The stream finalizer dispatches exactly one flush after draining the body.
"""

from __future__ import annotations

from typing import Any
from unittest import mock

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses.hosting import _endpoint_handler as eh
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider
from azure.ai.agentserver.responses.streaming import ResponseEventStream


def _build_streaming_client(events: list[str]) -> TestClient:
    async def _handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
        events.append("handler-started")
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_completed()
        events.append("handler-ended")

    app = ResponsesAgentServerHost(
        options=ResponsesServerOptions(),
        store=InMemoryResponseProvider(),
    )
    app.response_handler(_handler)
    return TestClient(app)


class TestStreamingFlushAfterDrain:
    @pytest.mark.parametrize("streaming", [False, True])
    @pytest.mark.parametrize(
        "mode, expected_helper",
        [
            (None, "flush_spans_async"),
            ("async", "flush_spans_async"),
            ("background", "schedule_flush_spans"),
            ("sync", "flush_spans"),
        ],
    )
    def test_request_flushes_once_after_handler_in_configured_mode(
        self, monkeypatch: pytest.MonkeyPatch, streaming: bool, mode: str | None, expected_helper: str
    ) -> None:
        """Both paths use the selected helper exactly once, after handler work."""
        if mode is None:
            monkeypatch.delenv("AGENTSERVER_FLUSH_MODE", raising=False)
        else:
            monkeypatch.setenv("AGENTSERVER_FLUSH_MODE", mode)
        events: list[str] = []
        with mock.patch.object(
            eh, "flush_spans", side_effect=lambda: events.append("flush_spans")
        ) as sync_flush, mock.patch.object(
            eh, "schedule_flush_spans", side_effect=lambda: events.append("schedule_flush_spans")
        ) as background_flush, mock.patch.object(
            eh,
            "flush_spans_async",
            new_callable=mock.AsyncMock,
            side_effect=lambda: events.append("flush_spans_async"),
        ) as async_flush:
            with _build_streaming_client(events) as client:
                response = client.post(
                    "/responses", json={"model": "m", "input": "hi", "stream": streaming, "store": False}
                )
                assert response.status_code == 200
            helpers = {
                "flush_spans": sync_flush,
                "schedule_flush_spans": background_flush,
                "flush_spans_async": async_flush,
            }
            for name, helper in helpers.items():
                assert helper.call_count == (1 if name == expected_helper else 0)
            assert async_flush.await_count == (1 if expected_helper == "flush_spans_async" else 0)
        assert events == ["handler-started", "handler-ended", expected_helper]
