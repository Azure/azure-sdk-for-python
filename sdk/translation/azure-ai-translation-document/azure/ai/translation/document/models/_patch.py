# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any, List, Mapping, Optional, Union, overload, TYPE_CHECKING
import datetime
from ._models import (
    DocumentStatus as GeneratedDocumentStatus,
    TranslationStatus as GeneratedTranslationStatus,
    TranslationGlossary as GeneratedTranslationGlossary,
    TranslationTarget as GeneratedTranslationTarget,
    DocumentBatch,
    SourceInput,
    DocumentFilter,
)
from ._enums import StorageInputType


if TYPE_CHECKING:
    from .. import models as _models


def convert_status(status, ll=False):
    if ll is False:
        if status.lower() == "cancelled":
            return "Canceled"
        if status.lower() == "cancelling":
            return "Canceling"
    elif ll is True:
        if status.lower() == "canceled":
            return "Cancelled"
        if status.lower() == "canceling":
            return "Cancelling"
    return status


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
    targets: List["TranslationTarget"]
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
        targets: List["TranslationTarget"],
        *,
        source_language: Optional[str] = None,
        storage_type: Optional[Union[str, StorageInputType]] = None,
        storage_source: Optional[str] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
    ) -> None:
        self.source_url = source_url
        self.targets = targets
        self.source_language = source_language
        self.storage_type = storage_type
        self.storage_source = storage_source
        self.prefix = prefix
        self.suffix = suffix

    def _to_generated(self):
        return DocumentBatch(
            source=SourceInput(
                source_url=self.source_url,
                filter=DocumentFilter(prefix=self.prefix, suffix=self.suffix),
                language=self.source_language,
                storage_source=self.storage_source,
            ),
            targets=self.targets,
            storage_type=self.storage_type,
        )

    def __repr__(self) -> str:
        return (
            "DocumentTranslationInput(source_url={}, targets={}, "
            "source_language={}, storage_type={}, "
            "storage_source={}, prefix={}, suffix={})".format(
                self.source_url,
                repr(self.targets),
                self.source_language,
                repr(self.storage_type),
                self.storage_source,
                self.prefix,
                self.suffix,
            )[:1024]
        )


class TranslationTarget(GeneratedTranslationTarget):
    """Destination for the finished translated documents.

    All required parameters must be populated in order to send to server.

    :ivar target_url: Location of the folder / container with your documents. Required.
    :vartype target_url: str
    :ivar category_id: Category / custom system for translation request.
    :vartype category_id: str
    :ivar language: Target Language. Required.
    :vartype language: str
    :ivar glossaries: List of Glossary.
    :vartype glossaries: list[~azure.ai.translation.document.models.TranslationGlossary]
    :ivar storage_source: Storage Source. "AzureBlob"
    :vartype storage_source: str or ~azure.ai.translation.document.models.TranslationStorageSource
    """

    target_url: str
    """Location of the folder / container with your documents. Required."""
    category_id: Optional[str]
    """Category / custom system for translation request."""
    language: str
    """Target Language. Required."""
    glossaries: Optional[List["TranslationGlossary"]]
    """List of Glossary."""
    storage_source: Optional[Union[str, "_models.TranslationStorageSource"]]
    """Storage Source. \"AzureBlob\""""

    @overload
    def __init__(
        self,
        target_url: str,
        language: str,
        *,
        category_id: Optional[str] = None,
        glossaries: Optional[List["TranslationGlossary"]] = None,
        storage_source: Optional[Union[str, "_models.TranslationStorageSource"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        target = kwargs.get("mapping")
        if not target and len(args) == 2:
            kwargs["target_url"] = args[0]
            kwargs["language"] = args[1]

        super().__init__(*args, **kwargs)


class TranslationGlossary(GeneratedTranslationGlossary):
    """Glossary / translation memory for the request.

    All required parameters must be populated in order to send to server.

    :ivar glossary_url: Location of the glossary.
     We will use the file extension to extract the
     formatting if the format parameter is not supplied.

     If the translation
     language pair is not present in the glossary, it will not be applied. Required.
    :vartype glossary_url: str
    :ivar file_format: Format. Required.
    :vartype file_format: str
    :ivar format_version: Optional Version.  If not specified, default is used.
    :vartype format_version: str
    :ivar storage_source: Storage Source. "AzureBlob"
    :vartype storage_source: str or ~azure.ai.translation.document.models.TranslationStorageSource
    """

    glossary_url: str
    """Location of the glossary.
     We will use the file extension to extract the
     formatting if the format parameter is not supplied.
     
     If the translation
     language pair is not present in the glossary, it will not be applied. Required."""
    file_format: str
    """Format. Required."""
    format_version: Optional[str]
    """Optional Version.  If not specified, default is used."""
    storage_source: Optional[Union[str, "_models.TranslationStorageSource"]]
    """Storage Source. \"AzureBlob\""""

    @overload
    def __init__(
        self,
        glossary_url: str,
        file_format: str,
        *,
        format_version: Optional[str] = None,
        storage_source: Optional[Union[str, "_models.TranslationStorageSource"]] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        glossary = kwargs.get("mapping")
        if not glossary and len(args) == 2:
            kwargs["glossary_url"] = args[0]
            kwargs["file_format"] = args[1]

        super().__init__(*args, **kwargs)


class DocumentStatus(GeneratedDocumentStatus):
    """Document Status Response.

    :ivar translated_document_url: Location of the document or folder.
    :vartype translated_document_url: str
    :ivar source_document_url: Location of the source document. Required.
    :vartype source_document_url: str
    :ivar created_on: Operation created date time. Required.
    :vartype created_on: ~datetime.datetime
    :ivar last_updated_on: Date time in which the operation's status has been updated. Required.
    :vartype last_updated_on: ~datetime.datetime
    :ivar status: List of possible statuses for job or document. Required. Known values are:
     "NotStarted", "Running", "Succeeded", "Failed", "Cancelled", "Cancelling", and
     "ValidationFailed".
    :vartype status: str or ~azure.ai.translation.document.models.Status
    :ivar translated_to: To language. Required.
    :vartype translated_to: str
    :ivar error: This contains an outer error with error code, message, details, target and an
     inner error with more descriptive details.
    :vartype error: ~azure.ai.translation.document.models.DocumentTranslationError
    :ivar translation_progress: Progress of the translation if available. Required.
    :vartype translation_progress: float
    :ivar id: Document Id. Required.
    :vartype id: str
    :ivar characters_charged: Character charged by the API.
    :vartype characters_charged: int
    """

    translated_document_url: Optional[str]
    """Location of the document or folder."""
    source_document_url: str
    """Location of the source document. Required."""
    created_on: datetime.datetime
    """Operation created date time. Required."""
    last_updated_on: datetime.datetime
    """Date time in which the operation's status has been updated. Required."""
    status: Union[str, "_models.Status"]
    """List of possible statuses for job or document. Required. Known values are: \"NotStarted\",
     \"Running\", \"Succeeded\", \"Failed\", \"Cancelled\", \"Cancelling\", and
     \"ValidationFailed\"."""
    translated_to: str
    """To language. Required."""
    error: Optional["_models.DocumentTranslationError"]
    """This contains an outer error with error code, message, details, target and an
     inner error with more descriptive details."""
    translation_progress: float
    """Progress of the translation if available. Required."""
    id: str
    """Document Id. Required."""
    characters_charged: Optional[int]
    """Character charged by the API."""

    @overload
    def __init__(
        self,
        *,
        source_document_url: str,
        created_on: datetime.datetime,
        last_updated_on: datetime.datetime,
        status: Union[str, "_models.Status"],
        translated_to: str,
        translation_progress: float,
        id: str,  # pylint: disable=redefined-builtin
        translated_document_url: Optional[str] = None,
        error: Optional["_models.DocumentTranslationError"] = None,
        characters_charged: Optional[int] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        status = kwargs.get("mapping")
        if not status and args:
            status = args[0]
        else:
            status = kwargs

        if status.get("status"):
            status["status"] = convert_status(status["status"])
        if status.get("error"):
            status["error"]["code"] = status["error"].get("innerError", {}).get("code")
        super().__init__(*args, **kwargs)


class TranslationStatus(GeneratedTranslationStatus):
    """Translation job status response.

    :ivar id: Id of the operation. Required.
    :vartype id: str
    :ivar created_on: Operation created date time. Required.
    :vartype created_on: ~datetime.datetime
    :ivar last_updated_on: Date time in which the operation's status has been updated. Required.
    :vartype last_updated_on: ~datetime.datetime
    :ivar status: List of possible statuses for job or document. Required. Known values are:
     "NotStarted", "Running", "Succeeded", "Failed", "Cancelled", "Cancelling", and
     "ValidationFailed".
    :vartype status: str or ~azure.ai.translation.document.models.Status
    :ivar error: This contains an outer error with error code, message, details, target and an
     inner error with more descriptive details.
    :vartype error: ~azure.ai.translation.document.models.DocumentTranslationError
    :ivar summary: Status Summary. Required.
    :vartype summary: ~azure.ai.translation.document.models.TranslationStatusSummary
    """

    id: str
    """Id of the operation. Required."""
    created_on: datetime.datetime
    """Operation created date time. Required."""
    last_updated_on: datetime.datetime
    """Date time in which the operation's status has been updated. Required."""
    status: Union[str, "_models.Status"]
    """List of possible statuses for job or document. Required. Known values are: \"NotStarted\",
     \"Running\", \"Succeeded\", \"Failed\", \"Cancelled\", \"Cancelling\", and
     \"ValidationFailed\"."""
    error: Optional["_models.DocumentTranslationError"]
    """This contains an outer error with error code, message, details, target and an
     inner error with more descriptive details."""
    summary: "_models.TranslationStatusSummary"
    """Status Summary. Required."""

    # pylint: disable=too-many-return-statements
    def __getattr__(self, name: str) -> Any:
        backcompat_attrs = [
            "documents_total_count",
            "documents_failed_count",
            "documents_in_progress_count",
            "documents_succeeded_count",
            "documents_not_started_count",
            "documents_canceled_count",
            "total_characters_charged",
        ]
        if name in backcompat_attrs:
            try:
                if name == "documents_succeeded_count":
                    return self.summary["success"]
                if name == "documents_failed_count":
                    return self.summary["failed"]
                if name == "documents_total_count":
                    return self.summary["total"]
                if name == "documents_in_progress_count":
                    return self.summary["inProgress"]
                if name == "documents_not_started_count":
                    return self.summary["notYetStarted"]
                if name == "documents_canceled_count":
                    return self.summary["cancelled"]
                if name == "total_characters_charged":
                    return self.summary["totalCharacterCharged"]
            except KeyError:
                return None
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    @overload
    def __init__(
        self,
        *,
        id: str,  # pylint: disable=redefined-builtin
        created_on: datetime.datetime,
        last_updated_on: datetime.datetime,
        status: Union[str, "_models.Status"],
        summary: "_models.TranslationStatusSummary",
        error: Optional["_models.DocumentTranslationError"] = None,
    ): ...

    @overload
    def __init__(self, mapping: Mapping[str, Any]):
        """
        :param mapping: raw JSON to initialize the model.
        :type mapping: Mapping[str, Any]
        """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        status = kwargs.get("mapping")
        if not status and args:
            status = args[0]
        else:
            status = kwargs

        if status.get("status"):
            status["status"] = convert_status(status["status"])
        if status.get("error"):
            status["error"]["code"] = status["error"].get("innerError", {}).get("code")
        super().__init__(*args, **kwargs)


__all__: List[str] = [
    "DocumentStatus",
    "TranslationStatus",
    "DocumentTranslationInput",
    "TranslationTarget",
    "TranslationGlossary",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
