# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest import mock
import pytest
from azure.search.documents.aio import (
    SearchIndexingBufferedSender,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ServiceResponseTimeoutError
from azure.search.documents.models import IndexingResult
from test_search_index_client_async import await_prepared_test

CREDENTIAL = AzureKeyCredential(key="test_api_key")


class TestSearchBatchingClientAsync:
    @await_prepared_test
    async def test_search_indexing_buffered_sender_kwargs(self):
        async with SearchIndexingBufferedSender("endpoint", "index name", CREDENTIAL, window=100) as client:
            assert client._batch_action_count == 512
            assert client._max_retries_per_action == 3
            assert client._auto_flush_interval == 60
            assert client._auto_flush

    @await_prepared_test
    async def test_batch_queue(self):
        async with SearchIndexingBufferedSender("endpoint", "index name", CREDENTIAL, auto_flush=False) as client:
            assert client._index_documents_batch
            await client.upload_documents(["upload1"])
            await client.delete_documents(["delete1", "delete2"])
            await client.merge_documents(["merge1", "merge2", "merge3"])
            await client.merge_or_upload_documents(["merge_or_upload1"])
            assert len(client.actions) == 7
            actions = await client._index_documents_batch.dequeue_actions()
            assert len(client.actions) == 0
            await client._index_documents_batch.enqueue_actions(actions)
            assert len(client.actions) == 7

    @await_prepared_test
    @mock.patch(
        "azure.search.documents.aio._search_indexing_buffered_sender_async.SearchIndexingBufferedSender._process_if_needed"
    )
    async def test_process_if_needed(self, mock_process_if_needed):
        async with SearchIndexingBufferedSender("endpoint", "index name", CREDENTIAL) as client:
            await client.upload_documents(["upload1"])
            await client.delete_documents(["delete1", "delete2"])
        assert mock_process_if_needed.called

    @await_prepared_test
    @mock.patch(
        "azure.search.documents.aio._search_indexing_buffered_sender_async.SearchIndexingBufferedSender._cleanup"
    )
    async def test_context_manager(self, mock_cleanup):
        async with SearchIndexingBufferedSender("endpoint", "index name", CREDENTIAL, auto_flush=False) as client:
            await client.upload_documents(["upload1"])
            await client.delete_documents(["delete1", "delete2"])
        assert mock_cleanup.called

    @await_prepared_test
    async def test_flush(self):
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
            async with SearchIndexingBufferedSender("endpoint", "index name", CREDENTIAL, auto_flush=False) as client:
                client._index_key = "hotelId"
                await client.upload_documents([DOCUMENT])
                await client.flush()
                assert len(client.actions) == 0

    @await_prepared_test
    async def test_callback_new(self):
        on_new = mock.AsyncMock()
        async with SearchIndexingBufferedSender(
            "endpoint", "index name", CREDENTIAL, auto_flush=False, on_new=on_new
        ) as client:
            await client.upload_documents(["upload1"])
            assert on_new.called

    @await_prepared_test
    async def test_callback_error(self):
        async def mock_fail_index_documents(actions, timeout=86400):
            if len(actions) > 0:
                result = IndexingResult()
                result.key = actions[0].additional_properties.get("id")
                result.status_code = 400
                result.succeeded = False
                self.uploaded = self.uploaded + len(actions) - 1
                return [result]

        on_error = mock.AsyncMock()
        async with SearchIndexingBufferedSender(
            "endpoint", "index name", CREDENTIAL, auto_flush=False, on_error=on_error
        ) as client:
            client._index_documents_actions = mock_fail_index_documents
            client._index_key = "id"
            await client.upload_documents({"id": 0})
            await client.flush()
            assert on_error.called

    @await_prepared_test
    async def test_callback_error_on_timeout(self):
        async def mock_fail_index_documents(actions, timeout=86400):
            if len(actions) > 0:
                result = IndexingResult()
                result.key = actions[0].additional_properties.get("id")
                result.status_code = 400
                result.succeeded = False
                self.uploaded = self.uploaded + len(actions) - 1
                time.sleep(1)
                return [result]

        on_error = mock.AsyncMock()
        async with SearchIndexingBufferedSender(
            "endpoint", "index name", CREDENTIAL, auto_flush=False, on_error=on_error
        ) as client:
            client._index_documents_actions = mock_fail_index_documents
            client._index_key = "id"
            await client.upload_documents([{"id": 0}, {"id": 1}])
            with pytest.raises(ServiceResponseTimeoutError):
                await client.flush(timeout=-1)
            assert on_error.call_count == 2

    @await_prepared_test
    async def test_callback_progress(self):
        async def mock_successful_index_documents(actions, timeout=86400):
            if len(actions) > 0:
                result = IndexingResult()
                result.key = actions[0].additional_properties.get("id")
                result.status_code = 200
                result.succeeded = True
                return [result]

        on_progress = mock.AsyncMock()
        on_remove = mock.AsyncMock()
        async with SearchIndexingBufferedSender(
            "endpoint",
            "index name",
            CREDENTIAL,
            auto_flush=False,
            on_progress=on_progress,
            on_remove=on_remove,
        ) as client:
            client._index_documents_actions = mock_successful_index_documents
            client._index_key = "id"
            await client.upload_documents({"id": 0})
            await client.flush()
            assert on_progress.called
            assert on_remove.called
