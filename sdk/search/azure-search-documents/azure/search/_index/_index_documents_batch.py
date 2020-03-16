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

    def __repr__(self):
        # type: () -> str
        return "<IndexDocumentsBatch [{} actions]>".format(len(self.actions))[:1024]

    def add_upload_documents(self, *documents):
        # type (Union[List[dict], List[List[dict]]]) -> None
        """Add documents to upload to the Azure search index.

        An upload action is similar to an "upsert" where the document will be
        inserted if it is new and updated/replaced if it exists. All fields are
        replaced in the update case.

        :param documents: Documents to upload to an Azure search index. May be
         a single list of documents, or documents as individual parameters.
        :type documents: dict or list[dict]
        """
        self._extend_batch(flatten_args(documents), "upload")

    def add_delete_documents(self, *documents):
        # type (Union[List[dict], List[List[dict]]]) -> None
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
        """
        self._extend_batch(flatten_args(documents), "delete")

    def add_merge_documents(self, *documents):
        # type (Union[List[dict], List[List[dict]]]) -> None
        """Add documents to merge in to existing documets in the Azure search
        index.

        Merge updates an existing document with the specified fields. If the
        document doesn't exist, the merge will fail. Any field you specify in a
        merge will replace the existing field in the document. This also applies
        to collections of primitive and complex types.

        :param documents: Documents to merge into an Azure search index. May be
         a single list of documents, or documents as individual parameters.
        :type documents: dict or list[dict]
        """
        self._extend_batch(flatten_args(documents), "merge")

    def add_merge_or_upload_documents(self, *documents):
        # type (Union[List[dict], List[List[dict]]]) -> None
        """Add documents to merge in to existing documets in the Azure search
        index, or upload if they do not yet exist.

        This action behaves like *merge* if a document with the given key
        already exists in the index. If the document does not exist, it behaves
        like *upload* with a new document.

        :param documents: Documents to merge or uplaod into an Azure search
         index. May be a single list of documents, or documents as individual
         parameters.
        :type documents: dict or list[dict]
        """
        self._extend_batch(flatten_args(documents), "mergeOrUpload")

    @property
    def actions(self):
        # type: () -> List[IndexAction]
        """The list of currently configured index actions.

        :rtype: List[IndexAction]
        """
        return list(self._actions)

    def _extend_batch(self, documents, action_type):
        # type: (List[dict], str) -> None
        new_actions = [
            IndexAction(additional_properties=document, action_type=action_type)
            for document in documents
        ]
        self._actions.extend(new_actions)
