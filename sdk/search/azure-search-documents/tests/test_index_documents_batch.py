# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for ``IndexDocumentsBatch`` action helpers."""

from __future__ import annotations

import pytest

from azure.search.documents import IndexDocumentsBatch
from azure.search.documents.models import IndexAction

METHOD_NAMES = [
    "add_upload_actions",
    "add_delete_actions",
    "add_merge_actions",
    "add_merge_or_upload_actions",
]

METHOD_MAP = dict(zip(METHOD_NAMES, ["upload", "delete", "merge", "mergeOrUpload"]))


class TestIndexDocumentsBatch:
    @pytest.mark.parametrize("method_name", METHOD_NAMES)
    def test_add_method_returns_new_actions_and_preserves_batch_order(self, method_name):
        batch = IndexDocumentsBatch()
        method = getattr(batch, method_name)

        first_actions = method([{"id": "1", "HotelName": "One"}])
        second_actions = method([{"id": "2", "HotelName": "Two"}, {"id": "3", "HotelName": "Three"}])

        assert [action.as_dict() for action in first_actions] == [
            {"@search.action": METHOD_MAP[method_name], "id": "1", "HotelName": "One"}
        ]
        assert [action.as_dict() for action in second_actions] == [
            {"@search.action": METHOD_MAP[method_name], "id": "2", "HotelName": "Two"},
            {"@search.action": METHOD_MAP[method_name], "id": "3", "HotelName": "Three"},
        ]
        assert [action.as_dict() for action in batch.actions] == [
            {"@search.action": METHOD_MAP[method_name], "id": "1", "HotelName": "One"},
            {"@search.action": METHOD_MAP[method_name], "id": "2", "HotelName": "Two"},
            {"@search.action": METHOD_MAP[method_name], "id": "3", "HotelName": "Three"},
        ]
        assert all(type(action) is IndexAction for action in batch.actions)

    @pytest.mark.parametrize("method_name", METHOD_NAMES)
    def test_add_method_accepts_variadic_documents(self, method_name):
        batch = IndexDocumentsBatch()
        method = getattr(batch, method_name)

        added_actions = method({"id": "1"}, {"id": "2"})

        assert [action.as_dict() for action in added_actions] == [
            {"@search.action": METHOD_MAP[method_name], "id": "1"},
            {"@search.action": METHOD_MAP[method_name], "id": "2"},
        ]
        assert [action.as_dict() for action in batch.actions] == [
            {"@search.action": METHOD_MAP[method_name], "id": "1"},
            {"@search.action": METHOD_MAP[method_name], "id": "2"},
        ]

    def test_add_merge_or_upload_actions_is_public_helper(self):
        batch = IndexDocumentsBatch()

        added_actions = batch.add_merge_or_upload_actions(
            {"id": "1", "HotelName": "Northwind Lodge"},
            {"id": "2", "HotelName": "Contoso Suites"},
        )

        expected = [
            {"@search.action": "mergeOrUpload", "id": "1", "HotelName": "Northwind Lodge"},
            {"@search.action": "mergeOrUpload", "id": "2", "HotelName": "Contoso Suites"},
        ]
        assert [action.as_dict() for action in added_actions] == expected
        assert [action.as_dict() for action in batch.actions] == expected

    def test_constructor_accepts_existing_actions(self):
        actions = [
            IndexAction({"@search.action": "upload", "id": "1"}),
            IndexAction({"@search.action": "delete", "id": "2"}),
        ]

        batch = IndexDocumentsBatch(actions=actions)

        assert batch.actions == actions
        assert batch.as_dict() == {
            "value": [
                {"@search.action": "upload", "id": "1"},
                {"@search.action": "delete", "id": "2"},
            ]
        }

    def test_actions_returns_copy(self):
        batch = IndexDocumentsBatch()
        batch.add_upload_actions([{"id": "1"}])

        actions = batch.actions
        actions.clear()

        assert [action.as_dict() for action in batch.actions] == [{"@search.action": "upload", "id": "1"}]

    def test_actions_setter_replaces_current_actions(self):
        batch = IndexDocumentsBatch()
        batch.add_upload_actions([{"id": "old"}])
        replacement = [IndexAction({"@search.action": "merge", "id": "new"})]

        batch.actions = replacement

        assert batch.actions == replacement

    def test_dequeue_actions_returns_copy_and_clears_batch(self):
        batch = IndexDocumentsBatch()
        batch.add_upload_actions([{"id": "1"}])
        batch.add_delete_actions([{"id": "2"}])

        dequeued = batch.dequeue_actions()

        assert [action.as_dict() for action in dequeued] == [
            {"@search.action": "upload", "id": "1"},
            {"@search.action": "delete", "id": "2"},
        ]
        assert batch.actions == []
        assert batch.dequeue_actions() == []

    def test_enqueue_actions_accepts_single_action_and_action_list(self):
        upload = IndexAction({"@search.action": "upload", "id": "1"})
        delete = IndexAction({"@search.action": "delete", "id": "2"})
        merge = IndexAction({"@search.action": "merge", "id": "3"})
        batch = IndexDocumentsBatch()

        batch.enqueue_actions(upload)
        batch.enqueue_actions([delete, merge])

        assert batch.actions == [upload, delete, merge]

    def test_repr_includes_action_count(self):
        batch = IndexDocumentsBatch()
        batch.add_upload_actions([{"id": "1"}, {"id": "2"}])

        assert repr(batch) == "<IndexDocumentsBatch [2 actions]>"
