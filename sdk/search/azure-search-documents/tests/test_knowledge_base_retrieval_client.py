# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for the public knowledge base client and generated streaming integration."""

import datetime
import json
from types import SimpleNamespace
from unittest import mock

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient

from _capabilities import require_capability

ENDPOINT = "https://my-search-service.search.windows.net"
KEY = "fake-api-key"
KNOWLEDGE_BASE_NAME = "hotel-kb"
AUDIENCE = "https://search.azure.com/"


class _Response:
    status_code = 200
    headers = {"Content-Type": "text/event-stream"}

    def __init__(self, chunks, error=None):
        self._chunks = chunks
        self._error = error
        self.closed = False

    def iter_bytes(self):
        if self._error is not None:
            raise self._error
        yield from self._chunks

    def close(self):
        self.closed = True


def _frame(event_type, payload):
    return f"event: {event_type}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n".encode()


@pytest.fixture
def client():
    require_capability("azure.search.documents.knowledgebases.KnowledgeBaseRetrievalClient.retrieve_stream")
    with KnowledgeBaseRetrievalClient(
        ENDPOINT, AzureKeyCredential(KEY), knowledge_base_name=KNOWLEDGE_BASE_NAME
    ) as retrieval_client:
        yield retrieval_client


def _retrieve_stream(client, response, **kwargs):
    from azure.search.documents.knowledgebases.models import KnowledgeBaseRetrievalRequest

    with mock.patch.object(
        client._client._pipeline, "run", return_value=SimpleNamespace(http_response=response)
    ) as run:
        stream = client.retrieve_stream(KnowledgeBaseRetrievalRequest(), **kwargs)
    return stream, run


class TestKnowledgeBaseRetrievalClientConstructor:
    def test_constructor_translates_audience_to_credential_scope(self):
        require_capability("KnowledgeBaseRetrievalClient")
        with KnowledgeBaseRetrievalClient(
            ENDPOINT,
            AzureKeyCredential(KEY),
            knowledge_base_name=KNOWLEDGE_BASE_NAME,
            audience=AUDIENCE,
        ) as client:
            assert client._config.endpoint == ENDPOINT
            assert client._config.knowledge_base_name == KNOWLEDGE_BASE_NAME
            assert client._config.credential_scopes == ["https://search.azure.com/.default"]


class TestKnowledgeBaseRetrievalResources:
    @pytest.mark.parametrize("wait_for_active", [False, True])
    def test_retrieve_resources_seed_documents_only_when_requested(self, wait_for_active):
        import _search_helpers as helpers

        test = SimpleNamespace(is_live=False, get_resource_name=lambda name: name)
        index_client = mock.Mock()
        index_client.get_knowledge_source_status.return_value = SimpleNamespace(synchronization_status="active")
        search_client = mock.MagicMock()
        search_client.__enter__.return_value = search_client
        search_client.index_documents.return_value = [SimpleNamespace(succeeded=True)]
        search_client.get_document_count.return_value = len(helpers.KNOWLEDGE_BASE_DOCUMENTS)

        with mock.patch.object(helpers, "get_credential"), mock.patch.object(
            helpers, "make_index_client", return_value=index_client
        ), mock.patch.object(helpers, "make_search_client", return_value=search_client) as create_search:
            with helpers.knowledge_base_resources(test, ENDPOINT, wait_for_active=wait_for_active) as resources:
                assert resources.index_name == "search-index"
                if wait_for_active:
                    batch = search_client.index_documents.call_args.args[0]
                    assert [action["id"] for action in batch.actions] == ["hotel-1", "hotel-2"]
                    assert all("wireless internet" in action["content"] for action in batch.actions)
                    search_client.get_document_count.assert_called_once()
                    index_client.get_knowledge_source_status.assert_called_once()
                else:
                    create_search.assert_not_called()
                    index_client.get_knowledge_source_status.assert_not_called()

        index_client.delete_knowledge_base.assert_called_once_with("search-base")
        index_client.delete_knowledge_source.assert_called_once_with("search-source")
        index_client.delete_index.assert_called_once_with("search-index")
        index_client.close.assert_called_once()


class TestKnowledgeBaseRetrievalClientStreaming:
    def test_retrieve_stream_inherits_generated_operation(self, client):
        from azure.search.documents.knowledgebases._operations._operations import (
            _KnowledgeBaseRetrievalClientOperationsMixin,
        )

        assert "retrieve_stream" not in KnowledgeBaseRetrievalClient.__dict__
        assert client.retrieve_stream.__func__ is _KnowledgeBaseRetrievalClientOperationsMixin.retrieve_stream

    @pytest.mark.parametrize("status_code", [200, 206, "error"])
    def test_retrieve_stream_deserializes_lifecycle_payloads(self, client, status_code):
        from azure.search.documents.knowledgebases.models import (
            KnowledgeBaseActivityStartedEvent,
            KnowledgeBaseAnswerCompletedEvent,
            KnowledgeBaseResponseCompletedEvent,
            KnowledgeBaseRetrievalResponse,
            KnowledgeBaseRetrievalStartedEvent,
            KnowledgeBaseSearchIndexActivityRecord,
            KnowledgeBaseSearchIndexReference,
            KnowledgeBaseStreamErrorEvent,
        )

        chunks = [
            _frame(
                "retrieval.started",
                {
                    "requestId": "request-id",
                    "knowledgeBaseName": KNOWLEDGE_BASE_NAME,
                    "outputMode": "extractiveData",
                    "reasoningEffort": {"kind": "minimal"},
                },
            ),
            _frame("activity.started", {"id": 1, "type": "searchIndex", "startedAt": "2026-10-01T00:00:00Z"}),
            _frame("activity.completed", {"id": 1, "type": "searchIndex", "elapsedMs": 12}),
            _frame(
                "answer.completed",
                {"messageIndex": 0, "message": {"role": "assistant", "content": [{"type": "text", "text": "answer"}]}},
            ),
            _frame("references.completed", [{"type": "searchIndex", "id": "doc-1", "activitySource": 1}]),
        ]
        if status_code == "error":
            chunks.append(
                _frame(
                    "error",
                    {
                        "error": {"code": "Failed", "message": "retrieval failed"},
                        "activity": [{"id": 1, "type": "searchIndex"}],
                    },
                )
            )
        else:
            chunks.append(_frame("response.completed", {"statusCode": status_code, "response": {"references": []}}))
        chunks.append(b"event: unexpected\ndata: {invalid}\n\n")
        response = _Response(chunks)
        stream, _ = _retrieve_stream(client, response)

        with stream:
            events = list(stream)

        assert len(events) == 6
        assert isinstance(events[0], KnowledgeBaseRetrievalStartedEvent)
        assert events[0].request_id == "request-id"
        assert events[0].knowledge_base_name == KNOWLEDGE_BASE_NAME
        assert events[0].output_mode == "extractiveData"
        assert events[0].reasoning_effort.kind == "minimal"
        assert isinstance(events[1], KnowledgeBaseActivityStartedEvent)
        assert events[1].started_at == datetime.datetime(2026, 10, 1, tzinfo=datetime.timezone.utc)
        assert isinstance(events[2], KnowledgeBaseSearchIndexActivityRecord)
        assert events[2].elapsed_ms == 12
        assert isinstance(events[3], KnowledgeBaseAnswerCompletedEvent)
        assert events[3].message_index == 0
        assert events[3].message.content[0].text == "answer"
        assert isinstance(events[4][0], KnowledgeBaseSearchIndexReference)
        assert events[4][0].id == "doc-1"
        if status_code == "error":
            assert isinstance(events[5], KnowledgeBaseStreamErrorEvent)
            assert events[5].error.code == "Failed"
            assert isinstance(events[5].activity[0], KnowledgeBaseSearchIndexActivityRecord)
        else:
            assert isinstance(events[5], KnowledgeBaseResponseCompletedEvent)
            assert events[5].status_code == status_code
            assert isinstance(events[5].response, KnowledgeBaseRetrievalResponse)
        assert response.closed

    @pytest.mark.parametrize("chunk_size", [1, 2, 5, 512])
    def test_retrieve_stream_handles_fragmented_utf8_and_sse_framing(self, client, chunk_size):
        payload = (
            b"\xef\xbb\xbf: keep-alive\r\n"
            b"event: answer.completed\r"
            b'data: {"messageIndex":0,\r\n'
            b'data: "message":{"role":"assistant","content":[{"type":"text","text":"caf\xc3\xa9"}]}}\r\n\r\n'
            + _frame("response.completed", {"statusCode": 200, "response": {}})
        )
        response = _Response([payload[index : index + chunk_size] for index in range(0, len(payload), chunk_size)])
        stream, _ = _retrieve_stream(client, response)
        with stream:
            events = list(stream)
        assert events[0].message.content[0].text == "caf\u00e9"
        assert len(events) == 2
        assert response.closed

    @pytest.mark.parametrize(
        "payload,exception",
        [
            (b"event: retrieval.started\ndata: {invalid}\n\n", json.JSONDecodeError),
            (_frame("future.event", {"message": "value"}), ValueError),
        ],
    )
    def test_retrieve_stream_closes_on_invalid_events(self, client, payload, exception):
        response = _Response([payload])
        stream, _ = _retrieve_stream(client, response)
        with pytest.raises(exception):
            next(stream)
        assert response.closed

    @pytest.mark.parametrize("consume", [False, True])
    def test_retrieve_stream_closes_on_explicit_close_and_context_exit(self, client, consume):
        response = _Response([_frame("answer.completed", {"messageIndex": 0, "message": {"content": []}})])
        stream, _ = _retrieve_stream(client, response)
        with stream:
            if consume:
                next(stream)
        stream.close()
        assert response.closed

    def test_retrieve_stream_forwards_request_options(self, client):
        response = _Response([])
        stream, run = _retrieve_stream(
            client, response, query_source_authorization="query-token", headers={"x-custom": "value"}
        )
        stream.close()
        request = run.call_args.args[0]
        assert request.method == "POST"
        assert "/knowledgebases('hotel-kb')/retrieve" in request.url
        assert "api-version=2026-10-01" in request.url
        assert request.headers["Accept"] == "text/event-stream"
        assert request.headers["x-ms-query-source-authorization"] == "query-token"
        assert request.headers["x-custom"] == "value"
        assert run.call_args.kwargs["stream"] is True

    def test_retrieve_stream_passes_native_stream_to_cls(self, client):
        response = _Response([_frame("response.completed", {"statusCode": 206, "response": {}})])
        observed = {}

        def custom_cls(pipeline_response, stream, headers):
            observed.update(pipeline_response=pipeline_response, headers=headers)
            with stream:
                observed["payloads"] = list(stream)
            return mock.sentinel.result

        result, _ = _retrieve_stream(client, response, cls=custom_cls)
        assert result is mock.sentinel.result
        assert observed["pipeline_response"].http_response is response
        assert observed["payloads"][0].status_code == 206
        assert response.closed
