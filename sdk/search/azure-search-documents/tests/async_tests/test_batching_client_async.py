# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
try:
    from unittest import mock
except ImportError:
    import mock

from azure.search.documents.aio import (
    SearchIndexDocumentBatchingClient,
)
from azure.core.credentials import AzureKeyCredential

CREDENTIAL = AzureKeyCredential(key="test_api_key")

class TestSearchBatchingClientAsync(object):
    async def test_search_index_document_batching_client_kwargs(self):
        client = SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL, window=100, batch_size=100)

        assert client.batch_size == 100
        assert client._window == 100
        assert client._auto_flush
        await client.close()


    async def test_batch_queue(self):
        client = SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL)

        assert client._index_documents_batch
        await client.add_upload_actions(["upload1"])
        await client.add_delete_actions(["delete1", "delete2"])
        await client.add_merge_actions(["merge1", "merge2", "merge3"])
        await client.add_merge_or_upload_actions(["merge_or_upload1"])
        assert len(client.actions) == 7
        actions = await client._index_documents_batch.dequeue_actions()
        assert len(client.actions) == 0
        await client._index_documents_batch.enqueue_actions(actions)
        assert len(client.actions) == 7


    async def test_succeeded_queue(self):
        client = SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL)

        assert client._index_documents_batch
        await client.add_upload_actions(["upload1"])
        await client.add_delete_actions(["delete1", "delete2"])
        await client.add_merge_actions(["merge1", "merge2", "merge3"])
        await client.add_merge_or_upload_actions(["merge_or_upload1"])
        actions = await client._index_documents_batch.dequeue_actions()
        await client._index_documents_batch.enqueue_succeeded_actions(actions)
        assert len(client.succeeded_actions) == 7


    async def test_failed_queue(self):
        client = SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL)

        assert client._index_documents_batch
        await client.add_upload_actions(["upload1"])
        await client.add_delete_actions(["delete1", "delete2"])
        await client.add_merge_actions(["merge1", "merge2", "merge3"])
        await client.add_merge_or_upload_actions(["merge_or_upload1"])
        actions = await client._index_documents_batch.dequeue_actions()
        await client._index_documents_batch.enqueue_failed_actions(actions)
        assert len(client.failed_actions) == 7


    @mock.patch(
        "azure.search.documents._internal.aio._search_index_document_batching_client_async.SearchIndexDocumentBatchingClient.flush"
    )
    async def test_flush_if_needed(self, mock_flush):
        client = SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL, window=1000, batch_size=2)

        await client.add_upload_actions(["upload1"])
        await client.add_delete_actions(["delete1", "delete2"])
        assert mock_flush.called
        await client.close()


    @mock.patch(
        "azure.search.documents._internal.aio._search_index_document_batching_client_async.SearchIndexDocumentBatchingClient._cleanup"
    )
    async def test_context_manager(self, mock_cleanup):
        async with SearchIndexDocumentBatchingClient("endpoint", "index name", CREDENTIAL) as client:
            await client.add_upload_actions(["upload1"])
            await client.add_delete_actions(["delete1", "delete2"])
        assert mock_cleanup.called
