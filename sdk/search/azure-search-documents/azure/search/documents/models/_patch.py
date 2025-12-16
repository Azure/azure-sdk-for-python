# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Dict, List, Tuple, Union, cast
from azure.core.exceptions import HttpResponseError

from ._models import IndexDocumentsBatch as IndexDocumentsBatchGenerated
from ._models import IndexAction
from ._enums import IndexActionType


def _flatten_args(args: Tuple[Union[List[Dict[Any, Any]], List[List[Dict[Any, Any]]]], ...]) -> List[Dict]:
    """Flatten variadic arguments into a single list of documents.

    Supports both:
    - add_upload_actions([doc1, doc2])  # single list
    - add_upload_actions(doc1, doc2)    # multiple args
    """
    if len(args) == 1 and isinstance(args[0], (list, tuple)):
        return cast(List[Dict], args[0])
    return cast(List[Dict], args)


class RequestEntityTooLargeError(HttpResponseError):
    """An error response with status code 413 - Request Entity Too Large"""


class IndexDocumentsBatch(IndexDocumentsBatchGenerated):
    """Represent a batch of update operations for documents in an Azure
    Search index.

    Index operations are performed in the order in which they are added
    to the batch.
    """

    def __init__(self) -> None:
        self._actions: List[IndexAction] = []

    def __repr__(self) -> str:
        return "<IndexDocumentsBatch [{} actions]>".format(len(self.actions) if self.actions else 0)[:1024]

    def add_upload_actions(self, *documents: Union[List[Dict], List[List[Dict]]], **kwargs: Any) -> List[IndexAction]:
        # pylint: disable=unused-argument
        """Add documents to upload to the Azure search index.

        An upload action is similar to an "upsert" where the document will be
        inserted if it is new and updated/replaced if it exists. All fields are
        replaced in the update case.

        :param documents: Documents to upload to an Azure search index. May be
            a single list of documents, or documents as individual parameters.
        :type documents: dict or list[dict]
        :return: the added actions
        :rtype: list[~azure.search.documents.models.IndexAction]
        """
        return self._extend_batch(_flatten_args(documents), IndexActionType.UPLOAD)

    def add_delete_actions(self, *documents: Union[List[Dict], List[List[Dict]]], **kwargs: Any) -> List[IndexAction]:
        # pylint: disable=unused-argument
        """Add documents to delete from the Azure search index.

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
        :rtype: list[~azure.search.documents.models.IndexAction]
        """
        return self._extend_batch(_flatten_args(documents), IndexActionType.DELETE)

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
        :rtype: list[~azure.search.documents.models.IndexAction]
        """
        return self._extend_batch(_flatten_args(documents), IndexActionType.MERGE)

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
        :rtype: list[~azure.search.documents.models.IndexAction]
        """
        return self._extend_batch(_flatten_args(documents), IndexActionType.MERGE_OR_UPLOAD)

    @property
    def actions(self) -> List[IndexAction]:
        """The list of currently index actions to index.

        :rtype: list[~azure.search.documents.models.IndexAction]
        """
        if not hasattr(self, "_actions") or self._actions is None:
            self._actions = []
        return list(self._actions)

    # @actions.setter
    # def actions(self, value: List[IndexAction]) -> None:
    #     """Set the list of index actions.

    #     :param value: The list of index actions
    #     :type value: list[~azure.search.documents.models.IndexAction]
    #     """
    #     self._actions = value if value is not None else []

    def dequeue_actions(self, **kwargs: Any) -> List[IndexAction]:
        # pylint: disable=unused-argument
        """Get the list of currently configured index actions and clear it.

        :return: the current actions
        :rtype: list[~azure.search.documents.models.IndexAction]
        """
        if not hasattr(self, "_actions") or self._actions is None:
            return []
        result = list(self._actions)
        self._actions = []
        return result

    def enqueue_actions(self, new_actions: Union[IndexAction, List[IndexAction]], **kwargs: Any) -> None:
        # pylint: disable=unused-argument
        """Enqueue a list of index actions to index.

        :param new_actions: the actions to enqueue
        :type new_actions: ~azure.search.documents.models.IndexAction or list[~azure.search.documents.models.IndexAction]
        """
        if not hasattr(self, "_actions") or self._actions is None:
            self._actions = []

        if isinstance(new_actions, IndexAction):
            self._actions.append(new_actions)
        else:
            self._actions.extend(new_actions)

    def _extend_batch(self, documents: List[Dict], action_type: str) -> List[IndexAction]:
        """Internal helper to extend the batch with new actions.

        :param documents: The documents to add
        :type documents: list[dict]
        :param action_type: The action type for these documents
        :type action_type: str
        :return: The list of actions added
        :rtype: list[~azure.search.documents.models.IndexAction]
        """
        if not hasattr(self, "_actions") or self._actions is None:
            self._actions = []

        new_actions = []
        for doc in documents:
            action_dict = {"@search.action": action_type}
            action_dict.update(doc)
            action = IndexAction(action_dict)
            new_actions.append(action)

        self._actions.extend(new_actions)
        return new_actions


__all__: list[str] = [
    "IndexDocumentsBatch",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
