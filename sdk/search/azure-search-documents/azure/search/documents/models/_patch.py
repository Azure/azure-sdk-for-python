# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Dict, List, Union
from azure.core.exceptions import HttpResponseError

from ._models import IndexDocumentsBatch as IndexDocumentsBatchGenerated
from ._models import IndexAction
from ._enums import IndexActionType


class RequestEntityTooLargeError(HttpResponseError):
    """An error response with status code 413 - Request Entity Too Large"""


class IndexDocumentsBatch(IndexDocumentsBatchGenerated):
    """Contains a batch of document write actions to send to the index."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._actions_queue: List[IndexAction] = []

    def add_upload_actions(self, documents: List[Dict[str, Any]]) -> List[IndexAction]:
        """Add upload actions for documents.

        An upload action is similar to an "upsert" where the document will be
        inserted if it is new and updated/replaced if it exists. All fields are
        replaced in the update case.

        :param documents: A list of documents to upload.
        :type documents: list[dict[str, Any]]
        :return: The list of actions added
        :rtype: list[~azure.search.documents.models.IndexAction]
        """
        if not hasattr(self, "actions") or self.actions is None:
            self.actions = []

        actions = []
        for doc in documents:
            # Create a mapping that includes both the action type and document fields
            action_dict = {"@search.action": IndexActionType.UPLOAD}
            action_dict.update(doc)
            action = IndexAction(action_dict)
            self.actions.append(action)
            actions.append(action)
        return actions

    def add_delete_actions(self, documents: List[Dict[str, Any]]) -> List[IndexAction]:
        """Add delete actions for documents.

        Delete removes the specified documents from the index.

        :param documents: A list of documents to delete.
        :type documents: list[dict[str, Any]]
        :return: The list of actions added
        :rtype: list[~azure.search.documents.models.IndexAction]
        """
        if not hasattr(self, "actions") or self.actions is None:
            self.actions = []

        actions = []
        for doc in documents:
            # Create a mapping that includes both the action type and document fields
            action_dict = {"@search.action": IndexActionType.DELETE}
            action_dict.update(doc)
            action = IndexAction(action_dict)
            self.actions.append(action)
            actions.append(action)
        return actions

    def add_merge_actions(self, documents: List[Dict[str, Any]]) -> List[IndexAction]:
        """Add merge actions for documents.

        Merge updates an existing document with the specified fields. If the document
        doesn't exist, the merge will fail. Any field you specify in a merge will
        replace the existing field in the document.

        :param documents: A list of documents to merge.
        :type documents: list[dict[str, Any]]
        :return: The list of actions added
        :rtype: list[~azure.search.documents.models.IndexAction]
        """
        if not hasattr(self, "actions") or self.actions is None:
            self.actions = []

        actions = []
        for doc in documents:
            # Create a mapping that includes both the action type and document fields
            action_dict = {"@search.action": IndexActionType.MERGE}
            action_dict.update(doc)
            action = IndexAction(action_dict)
            self.actions.append(action)
            actions.append(action)
        return actions

    def add_merge_or_upload_actions(self, documents: List[Dict[str, Any]]) -> List[IndexAction]:
        """Add merge or upload actions for documents.

        Merge or upload behaves like merge if a document with the given key already
        exists in the index. If the document does not exist, it behaves like upload
        with a new document.

        :param documents: A list of documents to merge or upload.
        :type documents: list[dict[str, Any]]
        :return: The list of actions added
        :rtype: list[~azure.search.documents.models.IndexAction]
        """
        if not hasattr(self, "actions") or self.actions is None:
            self.actions = []

        actions = []
        for doc in documents:
            # Create a mapping that includes both the action type and document fields
            action_dict = {"@search.action": IndexActionType.MERGE_OR_UPLOAD}
            action_dict.update(doc)
            action = IndexAction(action_dict)
            self.actions.append(action)
            actions.append(action)
        return actions

    def dequeue_actions(self) -> List[IndexAction]:
        """Get and remove the actions from the batch.

        :return: The actions that were dequeued
        :rtype: list[~azure.search.documents.models.IndexAction]
        """
        if not hasattr(self, "actions") or self.actions is None:
            return []

        actions = self.actions
        self.actions = []
        return actions

    def enqueue_actions(self, actions: Union[IndexAction, List[IndexAction]]) -> None:
        """Add actions back to the batch.

        :param actions: The action(s) to enqueue
        :type actions: ~azure.search.documents.models.IndexAction or list[~azure.search.documents.models.IndexAction]
        """
        if not hasattr(self, "actions") or self.actions is None:
            self.actions = []

        if isinstance(actions, list):
            self.actions.extend(actions)
        else:
            self.actions.append(actions)


__all__: list[str] = [
    "IndexDocumentsBatch",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
