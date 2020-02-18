# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING

from ._generated.models import IndexAction

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import List


def flatten_args(args):
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        return args[0]
    return args


class IndexBatch(object):
    """Represent a batch of upate operations for documents in an Azure
    Search index.

    Index operations are performed in the order in which they are added
    to the batch.

    """

    def __init__(self):
        # type: () -> None
        self._actions = []  # type: List[IndexAction]

    def __repr__(self):
        # type: () -> str
        return "<IndexBatch [{} actions]>".format(len(self.actions))[:1024]

    def add_upload_documents(self, *documents):
        # type (Union[List[dict], List[List[dict]]]) -> None
        """Add documents to upload to the Azure search index.

        """
        self._extend_batch(flatten_args(documents), "upload")

    def add_delete_documents(self, *documents):
        # type (Union[List[dict], List[List[dict]]]) -> None
        """Add documents to delete to the Azure search index.

        """
        self._extend_batch(flatten_args(documents), "delete")

    def add_merge_documents(self, *documents):
        # type (Union[List[dict], List[List[dict]]]) -> None
        """Add documents to merge in to existing documets in the Azure search
        index.

        """
        self._extend_batch(flatten_args(documents), "merge")

    def add_merge_or_upload_documents(self, *documents):
        # type (Union[List[dict], List[List[dict]]]) -> None
        """Add documents to merge in to existing documets in the Azure search
        index, or upload if they do not yet exist.

        """
        self._extend_batch(flatten_args(documents), "mergeOrUpload")

    @property
    def actions(self):
        # type: () -> List[IndexAction]
        """The list of currently configured index actions.
        """
        return list(self._actions)

    def _extend_batch(self, documents, action_type):
        # type: (List[dict], str) -> None
        new_actions = [
            IndexAction(additional_properties=document, action_type=action_type)
            for document in documents
        ]
        self._actions.extend(new_actions)
