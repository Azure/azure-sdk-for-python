# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import Union, List, Dict, Any, Tuple, cast
from threading import Lock

from ._generated.models import IndexAction


def _flatten_args(args: Tuple[Union[List[Dict[Any, Any]], List[List[Dict[Any, Any]]]], ...]) -> List[Dict]:
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        return cast(List[Dict], args[0])
    return cast(List[Dict], args)


class IndexDocumentsBatch:
    """Represent a batch of update operations for documents in an Azure
    Search index.

    Index operations are performed in the order in which they are added
    to the batch.

    """

    def __init__(self) -> None:
        self._actions: List[IndexAction] = []
        self._lock = Lock()

    def __repr__(self) -> str:
        return "<IndexDocumentsBatch [{} actions]>".format(len(self.actions))[:1024]

    def add_upload_actions(self, *documents: Union[List[Dict], List[List[Dict]]]) -> List[IndexAction]:
        """Add documents to upload to the Azure search index.

        An upload action is similar to an "upsert" where the document will be
        inserted if it is new and updated/replaced if it exists. All fields are
        replaced in the update case.

        :param documents: Documents to upload to an Azure search index. May be
            a single list of documents, or documents as individual parameters.
        :type documents: dict or list[dict]
        :return: the added actions
        :rtype: list[IndexAction]
        """
        return self._extend_batch(_flatten_args(documents), "upload")

    def add_delete_actions(self, *documents: Union[List[Dict], List[List[Dict]]], **kwargs: Any) -> List[IndexAction]:
        # pylint: disable=unused-argument
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
        :rtype: list[IndexAction]
        """
        return self._extend_batch(_flatten_args(documents), "delete")

    def add_merge_actions(self, *documents: Union[List[Dict], List[List[Dict]]], **kwargs: Any) -> List[IndexAction]:
        # pylint: disable=unused-argument
        """Add documents to merge in to existing documents in the Azure search
        index.

        Merge updates an existing document with the specified fields. If the
        document doesn't exist, the merge will fail. Any field you specify in a
        merge will replace the existing field in the document. This also applies
        to collections of primitive and complex types.

        :param documents: Documents to merge into an Azure search index. May be
            a single list of documents, or documents as individual parameters.
        :type documents: dict or list[dict]
        :return: the added actions
        :rtype: list[IndexAction]
        """
        return self._extend_batch(_flatten_args(documents), "merge")

    def add_merge_or_upload_actions(
        self, *documents: Union[List[Dict], List[List[Dict]]], **kwargs: Any
    ) -> List[IndexAction]:
        # pylint: disable=unused-argument
        """Add documents to merge in to existing documents in the Azure search
        index, or upload if they do not yet exist.

        This action behaves like *merge* if a document with the given key
        already exists in the index. If the document does not exist, it behaves
        like *upload* with a new document.

        :param documents: Documents to merge or upload into an Azure search
            index. May be a single list of documents, or documents as individual
            parameters.
        :type documents: dict or list[dict]
        :return: the added actions
        :rtype: list[IndexAction]
        """
        return self._extend_batch(_flatten_args(documents), "mergeOrUpload")

    @property
    def actions(self) -> List[IndexAction]:
        """The list of currently index actions to index.

        :rtype: list[IndexAction]
        """
        return list(self._actions)

    def dequeue_actions(self, **kwargs: Any) -> List[IndexAction]:  # pylint: disable=unused-argument
        """Get the list of currently configured index actions and clear it.

        :return: the current actions
        :rtype: list[IndexAction]
        """
        with self._lock:
            result = list(self._actions)
            self._actions = []
        return result

    def enqueue_actions(self, new_actions: Union[IndexAction, List[IndexAction]], **kwargs: Any) -> None:
        # pylint: disable=unused-argument
        """Enqueue a list of index actions to index.

        :param new_actions: the actions to enqueue
        :type new_actions: IndexAction or list[IndexAction]
        """
        if isinstance(new_actions, IndexAction):
            with self._lock:
                self._actions.append(new_actions)
        else:
            with self._lock:
                self._actions.extend(new_actions)

    def _extend_batch(self, documents: List[Dict], action_type: str) -> List[IndexAction]:
        new_actions = [IndexAction(additional_properties=document, action_type=action_type) for document in documents]
        with self._lock:
            self._actions.extend(new_actions)
        return new_actions
