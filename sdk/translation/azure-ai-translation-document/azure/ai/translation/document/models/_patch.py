# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List
from typing import Any, List, Mapping, Optional, TYPE_CHECKING, Union, overload

from ._models import (
    DocumentStatus as GeneratedDocumentStatus,
    TranslationStatus as GeneratedTranslationStatus,
    TranslationTarget,
    BatchRequest,
    SourceInput,
    DocumentFilter,
)
from ._enums import StorageInputType


class DocumentTranslationInput:
    """Input for translation. This requires that you have your source document or
    documents in an Azure Blob Storage container. Provide a URL to the source file or
    source container containing the documents for translation. The source document(s) are
    translated and written to the location provided by the TranslationTargets.

    :param str source_url: Required. Location of the folder / container or single file with your
        documents. This can be a SAS URL (see the service documentation for the supported SAS permissions
        for accessing source storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions)
        or a managed identity can be created and used to access documents in your storage account
        (see https://aka.ms/azsdk/documenttranslation/managed-identity).
    :param targets: Required. Location of the destination for the output. This is a list of
        TranslationTargets. Note that a TranslationTarget is required for each language code specified.
    :type targets: list[~azure.ai.translation.document.TranslationTarget]
    :keyword Optional[str] source_language: Language code for the source documents.
        If none is specified, the source language will be auto-detected for each document.
    :keyword Optional[str] prefix: A case-sensitive prefix string to filter documents in the source path for
        translation. For example, when using a Azure storage blob Uri, use the prefix to restrict
        sub folders for translation.
    :keyword Optional[str] suffix: A case-sensitive suffix string to filter documents in the source path for
        translation. This is most often use for file extensions.
    :keyword storage_type: Storage type of the input documents source string. Possible values
        include: "Folder", "File".
    :paramtype storage_type: Optional[str or ~azure.ai.translation.document.StorageInputType]
    :keyword Optional[str] storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.
    """

    source_url: str
    """Location of the folder / container or single file with your
        documents. This can be a SAS URL (see the service documentation for the supported SAS permissions
        for accessing source storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions)
        or a managed identity can be created and used to access documents in your storage account
        (see https://aka.ms/azsdk/documenttranslation/managed-identity)."""
    targets: List[TranslationTarget]
    """Location of the destination for the output. This is a list of
        TranslationTargets. Note that a TranslationTarget is required for each language code specified."""
    source_language: Optional[str] = None
    """Language code for the source documents.
        If none is specified, the source language will be auto-detected for each document."""
    storage_type: Optional[Union[str, StorageInputType]] = None
    """Storage type of the input documents source string. Possible values
        include: "Folder", "File"."""
    storage_source: Optional[str] = None
    """Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported."""
    prefix: Optional[str] = None
    """A case-sensitive prefix string to filter documents in the source path for
        translation. For example, when using a Azure storage blob Uri, use the prefix to restrict
        sub folders for translation."""
    suffix: Optional[str] = None
    """A case-sensitive suffix string to filter documents in the source path for
        translation. This is most often use for file extensions."""

    def __init__(
        self,
        source_url: str,
        targets: List[TranslationTarget],
        *,
        source_language: Optional[str] = None,
        storage_type: Optional[Union[str, StorageInputType]] = None,
        storage_source: Optional[str] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None
    ) -> None:
        self.source_url = source_url
        self.targets = targets
        self.source_language = source_language
        self.storage_type = storage_type
        self.storage_source = storage_source
        self.prefix = prefix
        self.suffix = suffix

    def _to_generated(self):
        return BatchRequest(
            source=SourceInput(
                source_url=self.source_url,
                filter=DocumentFilter(prefix=self.prefix, suffix=self.suffix),
                language=self.source_language,
                storage_source=self.storage_source,
            ),
            targets=self.targets,
            storage_type=self.storage_type,
        )


def convert_status(status, ll=False):
    if ll is False:
        if status == "Cancelled":
            return "Canceled"
        if status == "Cancelling":
            return "Canceling"
    elif ll is True:
        if status == "Canceled":
            return "Cancelled"
        if status == "Canceling":
            return "Cancelling"
    return status


class DocumentStatus(GeneratedDocumentStatus):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        doc_status = kwargs.get("mapping")
        if not doc_status:
            doc_status = args[0]
        try:
            doc_status["status"] = convert_status(doc_status["status"])
        except KeyError:
            kwargs["status"] = convert_status(kwargs["status"])
        super().__init__(*args, **kwargs)


class TranslationStatus(GeneratedTranslationStatus):
    def __getattr__(self, name: str) -> Any:
        backcompat_attrs = [
            "documents_total_count",
            "documents_failed_count",
            "documents_in_progress_count",
            "documents_succeeded_count",
            "documents_not_started_count",
            "documents_canceled_count",
        ]
        if name in backcompat_attrs:
            return self.summary[name.split("documents_")[1].split("_count")[0]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        translation_status = kwargs.get("mapping")
        if not translation_status:
            translation_status = args[0]
        try:
            translation_status["status"] = convert_status(translation_status["status"])
        except KeyError:
            kwargs["status"] = convert_status(kwargs["status"])
        super().__init__(*args, **kwargs)


__all__: List[str] = [
    "DocumentStatus",
    "TranslationStatus",
    "DocumentTranslationInput",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
