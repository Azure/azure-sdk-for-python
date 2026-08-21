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

    async def test_client_wraps_generated_stream_and_composes_cls(self):
        require_capability(
            "azure.search.documents.knowledgebases.aio.KnowledgeBaseRetrievalClient.retrieve_stream",
            "AsyncKnowledgeBaseRetrievalStream",
        )
        from azure.search.documents.knowledgebases.aio import (
            AsyncKnowledgeBaseRetrievalStream,
            KnowledgeBaseRetrievalClient,
        )
        from azure.search.documents.knowledgebases.models import KnowledgeBaseRetrievalRequest

        response = _AsyncResponse()
        raw_stream = _AsyncRawStream([_frame("response.completed", {"statusCode": 200, "response": {}})])
        pipeline_response = SimpleNamespace(http_response=response)
        generated_kwargs = {}

        async def generated_retrieve_stream(_self, _request, **kwargs):
            generated_kwargs.update(kwargs)
            return kwargs["cls"](pipeline_response, raw_stream, {"content-type": "text/event-stream"})

        client = KnowledgeBaseRetrievalClient(
            ENDPOINT, AzureKeyCredential(KEY), knowledge_base_name=KNOWLEDGE_BASE_NAME
        )
        with mock.patch(
            "azure.search.documents.knowledgebases.aio._patch._KnowledgeBaseRetrievalClient.retrieve_stream",
            new=generated_retrieve_stream,
        ):
            stream = await client.retrieve_stream(
                KnowledgeBaseRetrievalRequest(),
                query_work_iq_source_authorization="work-iq-token",
            )
        assert isinstance(stream, AsyncKnowledgeBaseRetrievalStream)
        assert generated_kwargs["query_work_iq_source_authorization"] == "work-iq-token"
        await stream.close()

        observed = {}

        def custom_cls(received_pipeline_response, typed_stream, headers):
            observed.update(pipeline_response=received_pipeline_response, stream=typed_stream, headers=headers)
            return "custom-result"

        response = _AsyncResponse()
        raw_stream = _AsyncRawStream([])
        pipeline_response = SimpleNamespace(http_response=response)
        with mock.patch(
            "azure.search.documents.knowledgebases.aio._patch._KnowledgeBaseRetrievalClient.retrieve_stream",
            new=generated_retrieve_stream,
        ):
            result = await client.retrieve_stream(KnowledgeBaseRetrievalRequest(), cls=custom_cls)
        assert result == "custom-result"
        assert isinstance(observed["stream"], AsyncKnowledgeBaseRetrievalStream)
        await observed["stream"].close()

        response = _AsyncResponse()
        raw_stream = _AsyncRawStream([])
        pipeline_response = SimpleNamespace(http_response=response)

        def raising_cls(_pipeline_response, _typed_stream, _headers):
            raise RuntimeError("custom callback failed")

        with mock.patch(
            "azure.search.documents.knowledgebases.aio._patch._KnowledgeBaseRetrievalClient.retrieve_stream",
            new=generated_retrieve_stream,
        ):
            with pytest.raises(RuntimeError, match="custom callback failed"):
                await client.retrieve_stream(KnowledgeBaseRetrievalRequest(), cls=raising_cls)
        assert response.closed
        assert raw_stream.closed
        await client.close()
