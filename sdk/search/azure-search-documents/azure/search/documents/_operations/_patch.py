# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Dict, List, cast

from ._operations import _SearchClientOperationsMixin as _SearchClientOperationsMixinGenerated
from .. import models as _models


class _SearchClientOperationsMixin(_SearchClientOperationsMixinGenerated):
    """SearchClient operations mixin customizations."""

    def upload_documents(self, documents: List[Dict], **kwargs: Any) -> List[_models.IndexingResult]:
        """Upload documents to the Azure search index.

        An upload action is similar to an "upsert" where the document will be
        inserted if it is new and updated/replaced if it exists. All fields are
        replaced in the update case.

        :param documents: A list of documents to upload.
        :type documents: list[dict]
        :return: List of IndexingResult
        :rtype: list[~azure.search.documents.models.IndexingResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_crud_operations.py
                :start-after: [START upload_document]
                :end-before: [END upload_document]
                :language: python
                :dedent: 4
                :caption: Upload new documents to an index
        """
        batch = _models.IndexDocumentsBatch()
        batch.add_upload_actions(documents)

        result = self.index_documents(batch, **kwargs)
        return cast(List[_models.IndexingResult], result.results)

    def delete_documents(self, documents: List[Dict], **kwargs: Any) -> List[_models.IndexingResult]:
        """Delete documents from the Azure search index.

        Delete removes the specified documents from the index. Any field you
        specify in a delete operation, other than the key field, will be ignored.
        If you want to remove a field from a document, use merge instead and
        set the field explicitly to None.

        :param documents: A list of documents to delete.
        :type documents: list[dict]
        :return: List of IndexingResult
        :rtype: list[~azure.search.documents.models.IndexingResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_crud_operations.py
                :start-after: [START delete_document]
                :end-before: [END delete_document]
                :language: python
                :dedent: 4
                :caption: Delete documents from an index
        """
        batch = _models.IndexDocumentsBatch()
        batch.add_delete_actions(documents)

        result = self.index_documents(batch, **kwargs)
        return cast(List[_models.IndexingResult], result.results)

    def merge_documents(self, documents: List[Dict], **kwargs: Any) -> List[_models.IndexingResult]:
        """Merge documents in the Azure search index.

        Merge updates an existing document with the specified fields. If the
        document doesn't exist, the merge will fail. Any field you specify in
        a merge will replace the existing field in the document. This also
        applies to collections of primitive and complex types.

        :param documents: A list of documents to merge.
        :type documents: list[dict]
        :return: List of IndexingResult
        :rtype: list[~azure.search.documents.models.IndexingResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_crud_operations.py
                :start-after: [START merge_document]
                :end-before: [END merge_document]
                :language: python
                :dedent: 4
                :caption: Merge documents in an index
        """
        batch = _models.IndexDocumentsBatch()
        batch.add_merge_actions(documents)

        result = self.index_documents(batch, **kwargs)
        return cast(List[_models.IndexingResult], result.results)

    def merge_or_upload_documents(self, documents: List[Dict], **kwargs: Any) -> List[_models.IndexingResult]:
        """Merge or upload documents to the Azure search index.

        Merge or upload behaves like merge if a document with the given key
        already exists in the index. If the document does not exist, it behaves
        like upload with a new document.

        :param documents: A list of documents to merge or upload.
        :type documents: list[dict]
        :return: List of IndexingResult
        :rtype: list[~azure.search.documents.models.IndexingResult]

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_crud_operations.py
                :start-after: [START merge_or_upload_document]
                :end-before: [END merge_or_upload_document]
                :language: python
                :dedent: 4
                :caption: Merge or upload documents to an index
        """
        batch = _models.IndexDocumentsBatch()
        batch.add_merge_or_upload_actions(documents)

        result = self.index_documents(batch, **kwargs)
        return cast(List[_models.IndexingResult], result.results)


__all__: list[str] = [
    "_SearchClientOperationsMixin",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
