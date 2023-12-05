# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest import mock
import pytest
from azure.search.documents import (
    SearchIndexingBufferedSender,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ServiceResponseTimeoutError
from azure.search.documents.models import IndexingResult

CREDENTIAL = AzureKeyCredential(key="test_api_key")


class TestSearchBatchingClient:
    def test_search_indexing_buffered_sender_kwargs(self):
        with SearchIndexingBufferedSender("endpoint", "index name", CREDENTIAL, window=100) as client:
            assert client._batch_action_count == 512
            assert client._max_retries_per_action == 3
            assert client._auto_flush_interval == 60
            assert client._auto_flush

    def test_batch_queue(self):
        with SearchIndexingBufferedSender("endpoint", "index name", CREDENTIAL, auto_flush=False) as client:
            assert client._index_documents_batch
            client.upload_documents(["upload1"])
            client.delete_documents(["delete1", "delete2"])
            client.merge_documents(["merge1", "merge2", "merge3"])
            client.merge_or_upload_documents(["merge_or_upload1"])
            assert len(client.actions) == 7
            actions = client._index_documents_batch.dequeue_actions()
            assert len(client.actions) == 0
            client._index_documents_batch.enqueue_actions(actions)
            assert len(client.actions) == 7
            actions = client._index_documents_batch.dequeue_actions()
            assert len(client.actions) == 0
            for action in actions:
                client._index_documents_batch.enqueue_actions(action)
            assert len(client.actions) == 7

    @mock.patch(
        "azure.search.documents._search_indexing_buffered_sender.SearchIndexingBufferedSender._process_if_needed"
    )
    def test_process_if_needed(self, mock_process_if_needed):
        with SearchIndexingBufferedSender("endpoint", "index name", CREDENTIAL) as client:
            client.upload_documents(["upload1"])
            client.delete_documents(["delete1", "delete2"])
        assert mock_process_if_needed.called

    @mock.patch("azure.search.documents._search_indexing_buffered_sender.SearchIndexingBufferedSender._cleanup")
    def test_context_manager(self, mock_cleanup):
        with SearchIndexingBufferedSender("endpoint", "index name", CREDENTIAL, auto_flush=False) as client:
            client.upload_documents(["upload1"])
            client.delete_documents(["delete1", "delete2"])
        assert mock_cleanup.called

    def test_flush(self):
        DOCUMENT = {
            "category": "Hotel",
            "hotelId": "1000",
            "rating": 4.0,
            "rooms": [],
            "hotelName": "Azure Inn",
        }
        with mock.patch.object(
            SearchIndexingBufferedSender,
            "_index_documents_actions",
            side_effect=HttpResponseError("Error"),
        ):
            with SearchIndexingBufferedSender("endpoint", "index name", CREDENTIAL, auto_flush=False) as client:
                client._index_key = "hotelId"
                client.upload_documents([DOCUMENT])
                client.flush()
                assert len(client.actions) == 0

    def test_callback_new(self):
        on_new = mock.Mock()
        with SearchIndexingBufferedSender(
            "endpoint", "index name", CREDENTIAL, auto_flush=False, on_new=on_new
        ) as client:
            client.upload_documents(["upload1"])
            assert on_new.called

    def test_callback_error(self):
        def mock_fail_index_documents(actions, timeout=86400):
            if len(actions) > 0:
                result = IndexingResult()
                result.key = actions[0].additional_properties.get("id")
                result.status_code = 400
                result.succeeded = False
                self.uploaded = self.uploaded + len(actions) - 1
                return [result]

        on_error = mock.Mock()
        with SearchIndexingBufferedSender(
            "endpoint", "index name", CREDENTIAL, auto_flush=False, on_error=on_error
        ) as client:
            client._index_documents_actions = mock_fail_index_documents
            client._index_key = "id"
            client.upload_documents({"id": 0})
            client.flush()
            assert on_error.called

    def test_callback_error_on_timeout(self):
        def mock_fail_index_documents(actions, timeout=86400):
            import time

            if len(actions) > 0:
                result = IndexingResult()
                result.key = actions[0].additional_properties.get("id")
                result.status_code = 400
                result.succeeded = False
                self.uploaded = self.uploaded + len(actions) - 1
                time.sleep(1)
                return [result]

        on_error = mock.Mock()
        with SearchIndexingBufferedSender(
            "endpoint", "index name", CREDENTIAL, auto_flush=False, on_error=on_error
        ) as client:
            client._index_documents_actions = mock_fail_index_documents
            client._index_key = "id"
            client.upload_documents([{"id": 0}, {"id": 1}])
            with pytest.raises(ServiceResponseTimeoutError):
                client.flush(timeout=-1)
            assert on_error.call_count == 2

    def test_callback_progress(self):
        def mock_successful_index_documents(actions, timeout=86400):
            if len(actions) > 0:
                result = IndexingResult()
                result.key = actions[0].additional_properties.get("id")
                result.status_code = 200
                result.succeeded = True
                return [result]

        on_progress = mock.Mock()
        on_remove = mock.Mock()
        with SearchIndexingBufferedSender(
            "endpoint",
            "index name",
            CREDENTIAL,
            auto_flush=False,
            on_progress=on_progress,
            on_remove=on_remove,
        ) as client:
            client._index_documents_actions = mock_successful_index_documents
            client._index_key = "id"
            client.upload_documents({"id": 0})
            client.flush()
            assert on_progress.called
            assert on_remove.called
