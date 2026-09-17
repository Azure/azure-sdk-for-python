# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Contract test: streaming spans are flushed AFTER the stream body is drained.

For streaming requests the handler runs lazily while Starlette iterates the
``StreamingResponse`` body, which happens *after* ``handle_create`` returns.  The
outer ``handle_create`` ``finally`` therefore flushes spans before any streaming
span exists.  The streaming body iterator flushes again once it is fully drained
so streaming spans are not stranded until the next request's flush.

Regression test for: span flush located only in the outer ``finally`` (fires
before the stream body is consumed).
"""

from __future__ import annotations

from typing import Any
from unittest import mock

from starlette.testclient import TestClient

from azure.ai.agentserver.responses import ResponsesAgentServerHost, ResponsesServerOptions
from azure.ai.agentserver.responses.hosting import _endpoint_handler as eh
from azure.ai.agentserver.responses.store._memory import InMemoryResponseProvider
from azure.ai.agentserver.responses.streaming import ResponseEventStream


def _build_streaming_client() -> TestClient:
    async def _handler(request: Any, context: Any, cancellation_signal: Any) -> Any:
        stream = ResponseEventStream(response_id=context.response_id, model=getattr(request, "model", None))
        yield stream.emit_created()
        yield stream.emit_completed()

    app = ResponsesAgentServerHost(
        options=ResponsesServerOptions(),
        store=InMemoryResponseProvider(),
    )
    app.response_handler(_handler)
    return TestClient(app)


class TestStreamingFlushAfterDrain:
    def test_streaming_request_flushes_twice_nonstreaming_once(self) -> None:
        """A streaming request flushes twice — the outer ``handle_create``
        ``finally`` (before the body is consumed) plus a second flush once the
        stream body is fully drained — whereas a non-streaming request, whose
        spans all exist by the time ``handle_create`` returns, flushes once.

        (Starlette's ``TestClient`` drives the app to completion on the portal
        thread, so the two streaming flushes are both observed here; the extra
        streaming flush is the behaviour under test.)
        """
        client = _build_streaming_client()

        with mock.patch.object(eh, "_flush_spans_for_mode", new_callable=mock.AsyncMock) as m_flush:
            with client.stream(
                "POST",
                "/responses",
                json={"model": "m", "input": "hi", "stream": True, "store": False},
            ) as r:
                assert r.status_code == 200
                for _ in r.iter_lines():
                    pass
            streaming_flushes = m_flush.await_count

        with mock.patch.object(eh, "_flush_spans_for_mode", new_callable=mock.AsyncMock) as m_flush:
            r2 = client.post(
                "/responses",
                json={"model": "m", "input": "hi", "stream": False, "store": False},
            )
            assert r2.status_code == 200
            nonstreaming_flushes = m_flush.await_count

        # The stream-drain flush is the added behaviour: streaming flushes once
        # more than non-streaming.
        assert nonstreaming_flushes == 1
        assert streaming_flushes == nonstreaming_flushes + 1
