# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for ``SearchIndexingBufferedSender`` patched behavior."""

from __future__ import annotations

from unittest import mock

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ServiceResponseTimeoutError

from azure.search.documents import RequestEntityTooLargeError, SearchIndexingBufferedSender
from azure.search.documents.models import IndexingResult

SEARCH_ENDPOINT = "https://my-search-service.search.windows.net"
INDEX_NAME = "hotel-index"
API_KEY = "fake-api-key"
DOCUMENT_KEY = "1"
REPLACEMENT_DOCUMENT_KEY = "2"
API_VERSION = "2026-04-01"
NON_POSITIVE_AUTO_FLUSH_INTERVAL = 0

CREDENTIAL = AzureKeyCredential(API_KEY)


def create_sender(**kwargs):
    kwargs.setdefault("auto_flush", False)
    return SearchIndexingBufferedSender(SEARCH_ENDPOINT, INDEX_NAME, CREDENTIAL, **kwargs)


def create_hotel_document(document_key=DOCUMENT_KEY, hotel_name="Northwind Lodge"):
    return {
        "HotelId": document_key,
        "HotelName": hotel_name,
        "Category": "Hotel",
        "Rating": 4.0,
        "Rooms": [],
    }


def create_indexing_result(document_key=DOCUMENT_KEY, *, succeeded=True, status_code=200):
    result = IndexingResult()
    result.key = document_key
    result.status_code = status_code
    result.succeeded = succeeded
    return result


class TestSearchIndexingBufferedSenderConstructor:
    def test_constructor_uses_default_buffering_settings(self):
        sender = SearchIndexingBufferedSender(SEARCH_ENDPOINT, INDEX_NAME, CREDENTIAL, window=100)
        try:
            assert sender._batch_action_count == 512
            assert sender._max_retries_per_action == 3
            assert sender._auto_flush_interval == 60
            assert sender._auto_flush is True
        finally:
            sender._timer.cancel()

    def test_constructor_uses_public_settings_and_creates_inner_client(self):
        sender = create_sender(
            api_version=API_VERSION,
            initial_batch_action_count=32,
            max_retries_per_action=5,
            auto_flush_interval=120,
        )

        assert sender._endpoint == SEARCH_ENDPOINT
        assert sender._index_name == INDEX_NAME
        assert sender._api_version == API_VERSION
        assert sender._batch_action_count == 32
        assert sender._max_retries_per_action == 5
        assert sender._auto_flush_interval == 120
        assert sender._auto_flush is False
        assert sender._client._config.api_version == API_VERSION
        assert repr(sender) == (
            "<SearchIndexingBufferedSender "
            f"[endpoint='{SEARCH_ENDPOINT}', index='{INDEX_NAME}']>"
        )

    def test_constructor_rejects_non_positive_auto_flush_interval(self):
        with pytest.raises(ValueError, match="auto_flush_interval must be a positive number"):
            create_sender(auto_flush_interval=NON_POSITIVE_AUTO_FLUSH_INTERVAL)


class TestSearchIndexingBufferedSenderQueueing:
    @pytest.mark.parametrize(
        ("method_name", "documents"),
        [
            ("upload_documents", [create_hotel_document(DOCUMENT_KEY)]),
            ("delete_documents", [create_hotel_document(DOCUMENT_KEY)]),
            ("merge_documents", [{"HotelId": DOCUMENT_KEY, "Rating": 4.5}]),
            ("merge_or_upload_documents", [{"HotelId": DOCUMENT_KEY, "HotelName": "Northwind Lodge"}]),
        ],
    )
    def test_document_methods_trigger_processing_check(self, method_name, documents):
        sender = create_sender()

        with mock.patch.object(sender, "_process_if_needed", return_value=False) as mock_process:
            getattr(sender, method_name)(documents)

        mock_process.assert_called_once_with()

    def test_document_methods_enqueue_expected_actions_without_auto_flush(self):
        sender = create_sender()

        sender.upload_documents([create_hotel_document(DOCUMENT_KEY, "Northwind Lodge")])
        sender.delete_documents([create_hotel_document(REPLACEMENT_DOCUMENT_KEY, "Contoso Suites")])
        sender.merge_documents([{"HotelId": DOCUMENT_KEY, "Rating": 4.5}])
        sender.merge_or_upload_documents([{"HotelId": REPLACEMENT_DOCUMENT_KEY, "HotelName": "Contoso Suites"}])

        assert [action.as_dict() for action in sender.actions] == [
            {
                "@search.action": "upload",
                "HotelId": DOCUMENT_KEY,
                "HotelName": "Northwind Lodge",
                "Category": "Hotel",
                "Rating": 4.0,
                "Rooms": [],
            },
            {
                "@search.action": "delete",
                "HotelId": REPLACEMENT_DOCUMENT_KEY,
                "HotelName": "Contoso Suites",
                "Category": "Hotel",
                "Rating": 4.0,
                "Rooms": [],
            },
            {"@search.action": "merge", "HotelId": DOCUMENT_KEY, "Rating": 4.5},
            {"@search.action": "mergeOrUpload", "HotelId": REPLACEMENT_DOCUMENT_KEY, "HotelName": "Contoso Suites"},
        ]

    def test_on_new_callback_receives_each_added_action(self):
        on_new = mock.Mock()
        sender = create_sender(on_new=on_new)

        sender.upload_documents(
            [
                create_hotel_document(DOCUMENT_KEY),
                create_hotel_document(REPLACEMENT_DOCUMENT_KEY, "Contoso Suites"),
            ]
        )

        assert [call.args[0].as_dict()["HotelId"] for call in on_new.call_args_list] == [
            DOCUMENT_KEY,
            REPLACEMENT_DOCUMENT_KEY,
        ]

    def test_upload_documents_auto_flushes_when_batch_threshold_is_reached(self):
        with mock.patch.object(SearchIndexingBufferedSender, "_process", return_value=False) as mock_process:
            sender = SearchIndexingBufferedSender(
                SEARCH_ENDPOINT,
                INDEX_NAME,
                CREDENTIAL,
                auto_flush=True,
                auto_flush_interval=3600,
                initial_batch_action_count=2,
            )
            try:
                sender.upload_documents(
                    [
                        create_hotel_document(DOCUMENT_KEY),
                        create_hotel_document(REPLACEMENT_DOCUMENT_KEY, "Contoso Suites"),
                    ]
                )
            finally:
                sender._timer.cancel()

        mock_process.assert_called_once_with(raise_error=False)


class TestSearchIndexingBufferedSenderProcessing:
    def test_flush_detects_key_field_and_reports_success_callbacks(self):
        on_progress = mock.Mock()
        on_remove = mock.Mock()
        sender = create_sender(on_progress=on_progress, on_remove=on_remove)
        sender.upload_documents([create_hotel_document(DOCUMENT_KEY)])
        key_field = mock.Mock(key=True)
        key_field.name = "HotelId"
        index = mock.Mock(fields=[key_field])

        with mock.patch("azure.search.documents._patch.SearchIndexClient") as mock_index_client, mock.patch.object(
            sender, "_index_documents_actions", return_value=[create_indexing_result()]
        ):
            mock_index_client.return_value.get_index.return_value = index
            has_error = sender.flush()

        assert has_error is False
        assert sender._index_key == "HotelId"
        on_progress.assert_called_once()
        on_remove.assert_called_once()
        assert on_progress.call_args.args[0].as_dict()["HotelId"] == DOCUMENT_KEY

    def test_flush_retries_retryable_result_and_reports_error_at_retry_limit(self):
        on_error = mock.Mock()
        on_remove = mock.Mock()
        sender = create_sender(max_retries_per_action=1, on_error=on_error, on_remove=on_remove)
        sender._index_key = "HotelId"
        sender.upload_documents([create_hotel_document(DOCUMENT_KEY)])

        with mock.patch.object(
            sender,
            "_index_documents_actions",
            return_value=[create_indexing_result(succeeded=False, status_code=503)],
        ):
            has_error = sender.flush()

        assert has_error is True
        assert sender.actions == []
        on_error.assert_called_once()
        on_remove.assert_called_once()

    def test_flush_reports_non_retryable_result_to_error_callback(self):
        on_error = mock.Mock()
        sender = create_sender(on_error=on_error)
        sender._index_key = "HotelId"
        sender.upload_documents([create_hotel_document(DOCUMENT_KEY)])

        with mock.patch.object(
            sender,
            "_index_documents_actions",
            return_value=[create_indexing_result(succeeded=False, status_code=400)],
        ):
            has_error = sender.flush()

        assert has_error is True
        on_error.assert_called_once()
        assert on_error.call_args.args[0].as_dict()["HotelId"] == DOCUMENT_KEY

    def test_flush_retries_then_clears_actions_when_indexing_raises(self):
        sender = create_sender(max_retries_per_action=1)
        sender._index_key = "HotelId"
        sender.upload_documents([create_hotel_document(DOCUMENT_KEY)])

        with mock.patch.object(
            sender,
            "_index_documents_actions",
            side_effect=HttpResponseError("indexing request failed"),
        ):
            has_error = sender.flush()

        assert has_error is True
        assert sender.actions == []

    def test_flush_timeout_reports_each_queued_action(self):
        on_error = mock.Mock()
        sender = create_sender(on_error=on_error)
        sender.upload_documents(
            [
                create_hotel_document(DOCUMENT_KEY),
                create_hotel_document(REPLACEMENT_DOCUMENT_KEY, "Contoso Suites"),
            ]
        )

        with pytest.raises(ServiceResponseTimeoutError):
            sender.flush(timeout=-1)

        assert on_error.call_count == 2
        assert sender.actions == []


class TestSearchIndexingBufferedSenderIndexing:
    def test_context_manager_enters_client_and_closes_on_exit(self):
        sender = create_sender()

        with mock.patch.object(sender._client, "__enter__", return_value=sender._client) as mock_enter, mock.patch.object(
            sender._client, "__exit__", return_value=None
        ) as mock_exit, mock.patch.object(sender, "close") as mock_close:
            with sender as result:
                assert result is sender

        mock_enter.assert_called_once_with()
        mock_close.assert_called_once_with()
        mock_exit.assert_called_once_with(None, None, None)

    def test_index_documents_uses_inner_client_and_returns_results(self):
        sender = create_sender()
        sender.upload_documents([create_hotel_document(DOCUMENT_KEY)])
        expected = [create_indexing_result()]

        with mock.patch.object(sender._client, "index_documents", return_value=expected) as mock_index_documents:
            results = sender.index_documents(sender._index_documents_batch, request_id="request-1")

        assert results == expected
        batch = mock_index_documents.call_args.kwargs["batch"]
        assert [action.as_dict() for action in batch.actions] == [
            {"@search.action": "upload", **create_hotel_document(DOCUMENT_KEY)}
        ]
        assert mock_index_documents.call_args.kwargs["request_id"] == "request-1"

    def test_index_documents_splits_oversized_batches_and_combines_results(self):
        sender = create_sender(initial_batch_action_count=1)
        actions = sender._index_documents_batch.add_upload_actions(
            [
                create_hotel_document(DOCUMENT_KEY),
                create_hotel_document(REPLACEMENT_DOCUMENT_KEY, "Contoso Suites"),
            ]
        )
        first_result = create_indexing_result(DOCUMENT_KEY)
        second_result = create_indexing_result(REPLACEMENT_DOCUMENT_KEY)

        with mock.patch.object(
            sender._client,
            "index_documents",
            side_effect=[RequestEntityTooLargeError("request body too large"), [first_result], [second_result]],
        ) as mock_index_documents:
            results = sender._index_documents_actions(actions)

        assert results == [first_result, second_result]
        assert [len(call.kwargs["batch"].actions) for call in mock_index_documents.call_args_list] == [2, 1, 1]

    def test_index_documents_raises_request_too_large_for_single_action(self):
        sender = create_sender()
        actions = sender._index_documents_batch.add_upload_actions([create_hotel_document(DOCUMENT_KEY)])

        with mock.patch.object(
            sender._client,
            "index_documents",
            side_effect=RequestEntityTooLargeError("request body too large"),
        ):
            with pytest.raises(RequestEntityTooLargeError):
                sender._index_documents_actions(actions)

    def test_close_runs_cleanup_and_closes_inner_client(self):
        sender = create_sender()

        with mock.patch.object(sender, "_cleanup") as mock_cleanup, mock.patch.object(
            sender._client, "close"
        ) as mock_close:
            sender.close()

        mock_cleanup.assert_called_once_with(flush=True)
        mock_close.assert_called_once_with()
