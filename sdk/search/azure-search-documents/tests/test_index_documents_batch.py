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
    @pytest.mark.parametrize("method_name", METHOD_NAMES)
    def test_add_method(self, method_name):
        batch = IndexDocumentsBatch()

        method = getattr(batch, method_name)

        method([{"doc1": "doc"}])
        assert len(batch.actions) == 1

        method([{"doc2": "doc"}, {"doc3": "doc"}])
        assert len(batch.actions) == 3

        method([{"doc4": "doc"}, {"doc5": "doc"}])
        assert len(batch.actions) == 5

        method([{"doc6": "doc"}, {"doc7": "doc"}])
        assert len(batch.actions) == 7

        assert all(action.action_type == METHOD_MAP[method_name] for action in batch.actions)
        assert all(type(action) == IndexAction for action in batch.actions)
