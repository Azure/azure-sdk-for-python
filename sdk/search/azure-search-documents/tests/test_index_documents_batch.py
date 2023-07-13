# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest

from azure.search.documents.models import IndexAction

from azure.search.documents import IndexDocumentsBatch

METHOD_NAMES = [
    "add_upload_actions",
    "add_delete_actions",
    "add_merge_actions",
    "add_merge_or_upload_actions",
]

METHOD_MAP = dict(zip(METHOD_NAMES, ["upload", "delete", "merge", "mergeOrUpload"]))


class TestIndexDocumentsBatch:
    def test_init(self):
        batch = IndexDocumentsBatch()
        assert batch.actions == []

    def test_repr(self):
        batch = IndexDocumentsBatch()
        assert repr(batch) == "<IndexDocumentsBatch [0 actions]>"

        batch._actions = [1, 2, 3]
        assert repr(batch) == "<IndexDocumentsBatch [3 actions]>"

        # a strict length test here would require constructing an actions list
        # with a length of ~10**24, so settle for this simple sanity check on
        # an extreme case.
        batch_actions = list(range(2000))
        assert len(repr(batch)) <= 1024

    def test_actions_returns_list_copy(self):
        batch = IndexDocumentsBatch()
        batch.actions.extend([1, 2, 3])
        assert type(batch.actions) is list
        assert batch.actions == []
        assert batch.actions is not batch._actions

    @pytest.mark.parametrize("method_name", METHOD_NAMES)
    def test_add_method(self, method_name):
        batch = IndexDocumentsBatch()

        method = getattr(batch, method_name)

        method("doc1")
        assert len(batch.actions) == 1

        method("doc2", "doc3")
        assert len(batch.actions) == 3

        method(["doc4", "doc5"])
        assert len(batch.actions) == 5

        method(("doc6", "doc7"))
        assert len(batch.actions) == 7

        assert all(action.action_type == METHOD_MAP[method_name] for action in batch.actions)
        assert all(type(action) == IndexAction for action in batch.actions)

        expected = ["doc{}".format(i) for i in range(1, 8)]
        assert [action.additional_properties for action in batch.actions] == expected
