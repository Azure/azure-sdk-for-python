# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING
from threading import Lock

from ._generated.models import IndexAction

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import List


def _flatten_args(args):
    # type (Union[List[dict], List[List[dict]]]) -> List[dict]
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        return args[0]
    return args


class IndexDocumentsBatch(object):
    """Represent a batch of upate operations for documents in an Azure
    Search index.

    Index operations are performed in the order in which they are added
    to the batch.

    """

    def __init__(self):
        # type: () -> None
        self._actions = []  # type: List[IndexAction]
        self._lock = Lock()

    def __repr__(self):
        # type: () -> str
        return "<IndexDocumentsBatch [{} actions]>".format(len(self.actions))[:1024]

    def add_upload_actions(self, *documents):
        # type (Union[List[dict], List[List[dict]]]) -> List[IndexAction]
        """Add documents to upload to the Azure search index.

        An upload action is similar to an "upsert" where the document will be
        inserted if it is new and updated/replaced if it exists. All fields are
        replaced in the update case.

        :param documents: Documents to upload to an Azure search index. May be
         a single list of documents, or documents as individual parameters.
        :type documents: dict or list[dict]
        :return: the added actions
        :rtype: List[IndexAction]
        """
        return self._extend_batch(_flatten_args(documents), "upload")

    def add_delete_actions(self, *documents, **kwargs):  # pylint: disable=unused-argument
        # type (Union[List[dict], List[List[dict]]]) -> List[IndexAction]
        """Add documents to delete to the Azure search index.

        Delete removes the specified document from the index. Any field you
        specify in a delete operation, other than the key field, will be
        ignored. If you want to remove an individual field from a document, use
        `merge_documents` instead and set the field explicitly to None.

        Delete operations are idempotent. That is, even if a document key does
        not exist in the index, attempting a delete operation with that key will
        result in a 200 status code.

        :param documents: Documents to delete from an Azure search index. May be
         a single list of documents, or documents as individual parameters.
        :type documents: dict or list[dict]
        :return: the added actions
        :rtype: List[IndexAction]
        """
        return self._extend_batch(_flatten_args(documents), "delete")

    def add_merge_actions(self, *documents, **kwargs):  # pylint: disable=unused-argument
        # type (Union[List[dict], List[List[dict]]]) -> List[IndexAction]
        """Add documents to merge in to existing documets in the Azure search
        index.

        Merge updates an existing document with the specified fields. If the
        document doesn't exist, the merge will fail. Any field you specify in a
        merge will replace the existing field in the document. This also applies
        to collections of primitive and complex types.

        :param documents: Documents to merge into an Azure search index. May be
         a single list of documents, or documents as individual parameters.
        :type documents: dict or list[dict]
        :return: the added actions
        :rtype: List[IndexAction]
        """
        return self._extend_batch(_flatten_args(documents), "merge")

    def add_merge_or_upload_actions(self, *documents, **kwargs):  # pylint: disable=unused-argument
        # type (Union[List[dict], List[List[dict]]]) -> List[IndexAction]
        """Add documents to merge in to existing documets in the Azure search
        index, or upload if they do not yet exist.

        This action behaves like *merge* if a document with the given key
        already exists in the index. If the document does not exist, it behaves
        like *upload* with a new document.

        :param documents: Documents to merge or uplaod into an Azure search
         index. May be a single list of documents, or documents as individual
         parameters.
        :type documents: dict or list[dict]
        :return: the added actions
        :rtype: List[IndexAction]
        """
        return self._extend_batch(_flatten_args(documents), "mergeOrUpload")

    @property
    def actions(self):
        # type: () -> List[IndexAction]
        """The list of currently index actions to index.

        :rtype: List[IndexAction]
        """
        return list(self._actions)

    def dequeue_actions(self, **kwargs):  # pylint: disable=unused-argument
        # type: () -> List[IndexAction]
        """Get the list of currently configured index actions and clear it.

        :rtype: List[IndexAction]
        """
        with self._lock:
            result = list(self._actions)
            self._actions = []
        return result

    def enqueue_actions(self, new_actions, **kwargs):  # pylint: disable=unused-argument
        # type: (Union[IndexAction, List[IndexAction]]) -> None
        """Enqueue a list of index actions to index.
        """
        if isinstance(new_actions, IndexAction):
            with self._lock:
                self._actions.append(new_actions)
        else:
            with self._lock:
                self._actions.extend(new_actions)

    def _extend_batch(self, documents, action_type):
        # type: (List[dict], str) -> List[IndexAction]
        new_actions = [
            IndexAction(additional_properties=document, action_type=action_type)
            for document in documents
        ]
        with self._lock:
            self._actions.extend(new_actions)
        return new_actions
