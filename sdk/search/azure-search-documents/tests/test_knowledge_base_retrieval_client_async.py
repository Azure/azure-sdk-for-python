# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async unit tests for ``KnowledgeBaseRetrievalClient`` patched public behavior."""

import asyncio
import json
from types import SimpleNamespace
from unittest import mock

import pytest
from azure.core.credentials import AzureKeyCredential

from _capabilities import require_capability

ENDPOINT = "https://my-search-service.search.windows.net"
KEY = "fake-api-key"
KNOWLEDGE_BASE_NAME = "hotel-kb"
AUDIENCE = "https://search.azure.com/"


class _AsyncResponse:
    def __init__(self):
        self.closed = False
        self.status_code = 200
        self.headers = {"Content-Type": "text/event-stream"}
        self.raw_stream = None

    def iter_bytes(self):
        return self.raw_stream

    async def close(self):
        self.closed = True


class _AsyncRawStream:
    def __init__(self, chunks, error=None):
        self._chunks = iter(chunks)
        self._error = error
        self.closed = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._error is not None:
            error = self._error
            self._error = None
            raise error
        try:
            return next(self._chunks)
        except StopIteration as exc:
            raise StopAsyncIteration from exc

    async def aclose(self):
        self.closed = True


def _frame(event_type, payload):
    return f"event: {event_type}\ndata: {json.dumps(payload)}\n\n".encode()


@pytest.mark.asyncio
class TestKnowledgeBaseRetrievalClientConstructorAsync:
    async def test_constructor_translates_audience_to_credential_scope(self):
        require_capability("KnowledgeBaseRetrievalClient.aio")
        from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient

        client = KnowledgeBaseRetrievalClient(
            ENDPOINT,
            AzureKeyCredential(KEY),
            knowledge_base_name=KNOWLEDGE_BASE_NAME,
            audience=AUDIENCE,
        )

        assert client._config.endpoint == ENDPOINT
        assert client._config.knowledge_base_name == KNOWLEDGE_BASE_NAME
        assert client._config.credential_scopes == ["https://search.azure.com/.default"]
        await client.close()


@pytest.mark.asyncio
class TestKnowledgeBaseRetrievalStreamAsync:
    async def test_stream_deserializes_all_known_event_types(self):
        require_capability("AsyncKnowledgeBaseRetrievalStream", "KnowledgeBaseRetrievalEvent")
        from azure.search.documents.knowledgebases.aio import AsyncKnowledgeBaseRetrievalStream
        from azure.search.documents.knowledgebases.models import (
            KnowledgeBaseActivityStartedEvent,
            KnowledgeBaseAnswerCompletedEvent,
            KnowledgeBaseRetrievalStartedEvent,
            KnowledgeBaseSearchIndexActivityRecord,
            KnowledgeBaseSearchIndexReference,
            KnowledgeBaseStreamErrorEvent,
        )

        raw_stream = _AsyncRawStream(
            [
                _frame(
                    "retrieval.started",
                    {
                        "requestId": "request-id",
                        "knowledgeBaseName": KNOWLEDGE_BASE_NAME,
                        "outputMode": "extractiveData",
                        "reasoningEffort": {"kind": "minimal"},
                    },
                ),
                _frame("activity.started", {"id": 1, "type": "searchIndex", "startedAt": "2026-08-10T00:00:00Z"}),
                _frame("activity.completed", {"id": 1, "type": "searchIndex"}),
                _frame("answer.completed", {"messageIndex": 0, "message": {"role": "assistant", "content": []}}),
                _frame("references.completed", [{"type": "searchIndex", "id": "doc-1", "activitySource": 1}]),
                _frame("error", {"error": {"code": "Failed", "message": "retrieval failed"}}),
            ]
        )
        stream = AsyncKnowledgeBaseRetrievalStream(response=_AsyncResponse(), raw_stream=raw_stream)
        events = [event async for event in stream]

        assert isinstance(events[0].data, KnowledgeBaseRetrievalStartedEvent)
        assert isinstance(events[1].data, KnowledgeBaseActivityStartedEvent)
        assert isinstance(events[2].data, KnowledgeBaseSearchIndexActivityRecord)
        assert isinstance(events[3].data, KnowledgeBaseAnswerCompletedEvent)
        assert isinstance(events[4].data[0], KnowledgeBaseSearchIndexReference)
        assert isinstance(events[5].data, KnowledgeBaseStreamErrorEvent)
        assert AsyncKnowledgeBaseRetrievalStream.__module__ == "azure.search.documents.knowledgebases.aio"

    async def test_stream_handles_fragmented_events_and_terminal_cleanup(self):
        require_capability("AsyncKnowledgeBaseRetrievalStream", "KnowledgeBaseRetrievalEvent")
        from azure.search.documents.knowledgebases.aio import AsyncKnowledgeBaseRetrievalStream
        from azure.search.documents.knowledgebases.models import KnowledgeBaseResponseCompletedEvent

        payload = (
            b": keep-alive\r\n"
            b"event: response.completed\r\n"
            b'data: {"statusCode":200,"response":{}}\r\n\r\nignored'
        )
        raw_stream = _AsyncRawStream([payload[index : index + 2] for index in range(0, len(payload), 2)])
        response = _AsyncResponse()
        stream = AsyncKnowledgeBaseRetrievalStream(response=response, raw_stream=raw_stream)

        event = await stream.__anext__()

        assert event.event_type == "response.completed"
        assert isinstance(event.data, KnowledgeBaseResponseCompletedEvent)
        assert response.closed
        assert raw_stream.closed
        with pytest.raises(StopAsyncIteration):
            await stream.__anext__()

    async def test_stream_closes_on_cancellation_malformed_json_and_context_exit(self):
        from azure.search.documents.knowledgebases.aio import AsyncKnowledgeBaseRetrievalStream

        response = _AsyncResponse()
        raw_stream = _AsyncRawStream([], error=asyncio.CancelledError())
        stream = AsyncKnowledgeBaseRetrievalStream(response=response, raw_stream=raw_stream)
        with pytest.raises(asyncio.CancelledError):
            await stream.__anext__()
        assert response.closed
        assert raw_stream.closed

        response = _AsyncResponse()
        raw_stream = _AsyncRawStream([b"event: error\ndata: {invalid}\n\n"])
        stream = AsyncKnowledgeBaseRetrievalStream(response=response, raw_stream=raw_stream)
        with pytest.raises(json.JSONDecodeError):
            await stream.__anext__()
        assert response.closed
        assert raw_stream.closed

        response = _AsyncResponse()
        raw_stream = _AsyncRawStream([])
        async with AsyncKnowledgeBaseRetrievalStream(response=response, raw_stream=raw_stream):
            pass
        assert response.closed
        assert raw_stream.closed

    @pytest.mark.parametrize("terminal", ["response.completed", "error"])
    @pytest.mark.parametrize("use_cls", [False, True])
    async def test_retrieve_stream_yields_ga_payloads_and_preserves_november_options(self, terminal, use_cls):
        require_capability(
            "azure.search.documents.knowledgebases.aio.KnowledgeBaseRetrievalClient.retrieve_stream",
        )
        from azure.search.documents.knowledgebases.aio import KnowledgeBaseRetrievalClient
        from azure.search.documents._utils.streaming_base import AsyncStream
        from azure.search.documents.knowledgebases.models import (
            KnowledgeBaseActivityStartedEvent,
            KnowledgeBaseAnswerCompletedEvent,
            KnowledgeBaseResponseCompletedEvent,
            KnowledgeBaseRetrievalRequest,
            KnowledgeBaseRetrievalStartedEvent,
            KnowledgeBaseSearchIndexActivityRecord,
            KnowledgeBaseSearchIndexReference,
            KnowledgeBaseStreamErrorEvent,
        )

        response = _AsyncResponse()
        terminal_payload = (
            {"statusCode": 200, "response": {}}
            if terminal == "response.completed"
            else {"error": {"code": "Failed", "message": "retrieval failed"}}
        )
        response.raw_stream = _AsyncRawStream(
            [
                _frame("retrieval.started", {"requestId": "request-id", "knowledgeBaseName": KNOWLEDGE_BASE_NAME}),
                _frame("activity.started", {"id": 1, "type": "searchIndex"}),
                _frame("activity.completed", {"id": 1, "type": "searchIndex"}),
                _frame("answer.completed", {"messageIndex": 0, "message": {"role": "assistant", "content": []}}),
                _frame("references.completed", [{"type": "searchIndex", "id": "doc-1", "activitySource": 1}]),
                _frame(terminal, terminal_payload),
                _frame("must.not.be.consumed", {}),
            ]
        )
        pipeline_response = SimpleNamespace(http_response=response)
        observed = {}

        def custom_cls(received_pipeline_response, typed_stream, headers):
            observed.update(pipeline_response=received_pipeline_response, stream=typed_stream, headers=headers)
            return typed_stream

        async with KnowledgeBaseRetrievalClient(
            ENDPOINT, AzureKeyCredential(KEY), knowledge_base_name=KNOWLEDGE_BASE_NAME
        ) as client:
            with mock.patch.object(
                client._client._pipeline, "run", new_callable=mock.AsyncMock, return_value=pipeline_response
            ) as run:
                options = {"cls": custom_cls} if use_cls else {}
                stream = await client.retrieve_stream(
                    KnowledgeBaseRetrievalRequest(),
                    query_source_authorization="query-token",
                    query_work_iq_source_authorization="work-iq-token",
                    **options,
                )
                async with stream:
                    assert isinstance(stream, AsyncStream)
                    events = [event async for event in stream]
        if use_cls:
            assert observed["pipeline_response"] is pipeline_response
            assert observed["stream"] is stream
        assert isinstance(events[0], KnowledgeBaseRetrievalStartedEvent)
        assert isinstance(events[1], KnowledgeBaseActivityStartedEvent)
        assert isinstance(events[2], KnowledgeBaseSearchIndexActivityRecord)
        assert isinstance(events[3], KnowledgeBaseAnswerCompletedEvent)
        assert isinstance(events[4][0], KnowledgeBaseSearchIndexReference)
        expected_terminal = (
            KnowledgeBaseResponseCompletedEvent if terminal == "response.completed" else KnowledgeBaseStreamErrorEvent
        )
        assert isinstance(events[5], expected_terminal)
        assert len(events) == 6
        request = run.call_args.args[0]
        assert request.headers["x-ms-query-source-authorization"] == "query-token"
        assert request.headers["x-ms-query-work-iq-source-authorization"] == "work-iq-token"
        assert response.closed
