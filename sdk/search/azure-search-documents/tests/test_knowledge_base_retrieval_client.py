# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for ``KnowledgeBaseRetrievalClient`` patched public behavior."""

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


class _Response:
    def __init__(self):
        self.closed = False
        self.status_code = 200
        self.headers = {"Content-Type": "text/event-stream"}
        self.raw_stream = None

    def iter_bytes(self):
        return self.raw_stream

    def close(self):
        self.closed = True


class _RawStream:
    def __init__(self, chunks):
        self._chunks = iter(chunks)
        self.closed = False

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._chunks)

    def close(self):
        self.closed = True


def _frame(event_type, payload):
    return f"event: {event_type}\ndata: {json.dumps(payload)}\n\n".encode()


class TestKnowledgeBaseRetrievalClientConstructor:
    def test_constructor_translates_audience_to_credential_scope(self):
        require_capability("KnowledgeBaseRetrievalClient")
        from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient

        client = KnowledgeBaseRetrievalClient(
            ENDPOINT,
            AzureKeyCredential(KEY),
            knowledge_base_name=KNOWLEDGE_BASE_NAME,
            audience=AUDIENCE,
        )

        assert client._config.endpoint == ENDPOINT
        assert client._config.knowledge_base_name == KNOWLEDGE_BASE_NAME
        assert client._config.credential_scopes == ["https://search.azure.com/.default"]


class TestKnowledgeBaseRetrievalStream:
    def test_stream_deserializes_all_known_event_types(self):
        require_capability("KnowledgeBaseRetrievalEvent", "KnowledgeBaseRetrievalStream")
        from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalStream
        from azure.search.documents.knowledgebases.models import (
            KnowledgeBaseActivityStartedEvent,
            KnowledgeBaseAnswerCompletedEvent,
            KnowledgeBaseResponseCompletedEvent,
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
            _frame(
                "activity.started",
                {"id": 1, "type": "searchIndex", "startedAt": "2026-08-10T00:00:00Z"},
            ),
            _frame("activity.completed", {"id": 1, "type": "searchIndex"}),
            _frame("answer.completed", {"messageIndex": 0, "message": {"role": "assistant", "content": []}}),
            _frame("references.completed", [{"type": "searchIndex", "id": "doc-1", "activitySource": 1}]),
            _frame("error", {"error": {"code": "Failed", "message": "retrieval failed"}}),
            _frame("response.completed", {"statusCode": 200, "response": {}}),
        ]
        response = _Response()
        raw_stream = _RawStream(chunks)
        stream = KnowledgeBaseRetrievalStream(response=response, raw_stream=raw_stream)

        events = list(stream)

        assert [event.event_type for event in events] == [
            "retrieval.started",
            "activity.started",
            "activity.completed",
            "answer.completed",
            "references.completed",
            "error",
        ]
        assert isinstance(events[0].data, KnowledgeBaseRetrievalStartedEvent)
        assert isinstance(events[1].data, KnowledgeBaseActivityStartedEvent)
        assert isinstance(events[2].data, KnowledgeBaseSearchIndexActivityRecord)
        assert isinstance(events[3].data, KnowledgeBaseAnswerCompletedEvent)
        assert isinstance(events[4].data[0], KnowledgeBaseSearchIndexReference)
        assert isinstance(events[5].data, KnowledgeBaseStreamErrorEvent)
        assert response.closed
        assert raw_stream.closed

        success_stream = KnowledgeBaseRetrievalStream(
            response=_Response(),
            raw_stream=_RawStream([_frame("response.completed", {"statusCode": 200, "response": {}})]),
        )
        assert isinstance(next(success_stream).data, KnowledgeBaseResponseCompletedEvent)

    @pytest.mark.parametrize("chunk_size", [1, 2, 5, 512])
    def test_stream_handles_fragmented_utf8_line_endings_comments_and_unknown_events(self, chunk_size):
        from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalStream

        payload = (
            b"\xef\xbb\xbf: keep-alive\r\n"
            b"event: future.event\r"
            b'data: {"message":\r\n'
            b'data: "caf\xc3\xa9"}\r\n\r\n'
        )
        chunks = [payload[index : index + chunk_size] for index in range(0, len(payload), chunk_size)]
        response = _Response()

        with KnowledgeBaseRetrievalStream(response=response, raw_stream=_RawStream(chunks)) as stream:
            event = next(stream)

        assert event.event_type == "future.event"
        assert event.data == {"message": "caf\u00e9"}
        assert response.closed

    def test_stream_closes_on_malformed_json_and_explicit_close(self):
        from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalStream

        response = _Response()
        raw_stream = _RawStream([b"event: retrieval.started\ndata: {invalid}\n\n"])
        stream = KnowledgeBaseRetrievalStream(response=response, raw_stream=raw_stream)

        with pytest.raises(json.JSONDecodeError):
            next(stream)
        assert response.closed
        assert raw_stream.closed

        response = _Response()
        raw_stream = _RawStream([])
        stream = KnowledgeBaseRetrievalStream(response=response, raw_stream=raw_stream)
        stream.close()
        stream.close()
        assert response.closed
        assert raw_stream.closed

    @pytest.mark.parametrize("terminal", ["response.completed", "error"])
    @pytest.mark.parametrize("use_cls", [False, True])
    def test_retrieve_stream_yields_ga_payloads_and_preserves_november_options(self, terminal, use_cls):
        require_capability(
            "azure.search.documents.knowledgebases.KnowledgeBaseRetrievalClient.retrieve_stream",
        )
        from azure.search.documents.knowledgebases import KnowledgeBaseRetrievalClient
        from azure.search.documents._utils.streaming_base import Stream
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

        response = _Response()
        terminal_payload = (
            {"statusCode": 200, "response": {}}
            if terminal == "response.completed"
            else {"error": {"code": "Failed", "message": "retrieval failed"}}
        )
        response.raw_stream = _RawStream(
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

        with KnowledgeBaseRetrievalClient(
            ENDPOINT, AzureKeyCredential(KEY), knowledge_base_name=KNOWLEDGE_BASE_NAME
        ) as client:
            with mock.patch.object(client._client._pipeline, "run", return_value=pipeline_response) as run:
                options = {"cls": custom_cls} if use_cls else {}
                with client.retrieve_stream(
                    KnowledgeBaseRetrievalRequest(),
                    query_source_authorization="query-token",
                    query_work_iq_source_authorization="work-iq-token",
                    **options,
                ) as stream:
                    assert isinstance(stream, Stream)
                    events = list(stream)
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
