# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# mypy: disable-error-code="attr-defined"
# pylint: disable=too-many-lines

from typing import Any, List, Union, overload, Optional, cast, Tuple, TypeVar, Dict
from enum import Enum
import json
import datetime

from azure.core import CaseInsensitiveEnumMeta
from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline.policies import HttpLoggingPolicy
from azure.core.exceptions import HttpResponseError, ODataV4Format
from azure.core.pipeline import PipelineResponse
from azure.core.rest import (
    HttpResponse,
    AsyncHttpResponse,
    HttpRequest,
)
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import (
    LROBasePolling,
    OperationResourcePolling,
    _is_empty,
    _as_json,
    BadResponse,
    OperationFailed,
    _raise_if_bad_http_status_and_method,
)

from .models._models import (
    BatchRequest as _BatchRequest,
    SourceInput as _SourceInput,
    TargetInput as _TargetInput,
    DocumentFilter as _DocumentFilter,
    StartTranslationDetails as _StartTranslationDetails,
    Glossary as _Glossary,
    TranslationStatus as _TranslationStatus,
    DocumentStatus as _DocumentStatus,
)
from .models._enums import StorageInputType

COGNITIVE_KEY_HEADER = "Ocp-Apim-Subscription-Key"
POLLING_INTERVAL = 1

ResponseType = Union[HttpResponse, AsyncHttpResponse]
PipelineResponseType = PipelineResponse[HttpRequest, ResponseType]
PollingReturnType_co = TypeVar("PollingReturnType_co", covariant=True)

_FINISHED = frozenset(["succeeded", "cancelled", "cancelling", "failed"])
_FAILED = frozenset(["validationfailed"])


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


class TranslationGlossary:
    """Glossary / translation memory to apply to the translation.

    :param str glossary_url: Required. Location of the glossary file. This should be a URL to
        the glossary file in the storage blob container. The URL can be a SAS URL (see the
        service documentation for the supported SAS permissions for accessing storage
        containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions) or a managed identity
        can be created and used to access documents in your storage account
        (see https://aka.ms/azsdk/documenttranslation/managed-identity). Note that if the translation
        language pair is not present in the glossary, it will not be applied.
    :param str file_format: Required. Format of the glossary file. To see supported formats,
        call the :func:`~DocumentTranslationClient.get_supported_glossary_formats()` client method.
    :keyword Optional[str] format_version: File format version. If not specified, the service will
        use the default_version for the file format returned from the
        :func:`~DocumentTranslationClient.get_supported_glossary_formats()` client method.
    :keyword Optional[str] storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.
    """

    glossary_url: str
    """Location of the glossary file. This should be a URL to
        the glossary file in the storage blob container. The URL can be a SAS URL (see the
        service documentation for the supported SAS permissions for accessing storage
        containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions) or a managed identity
        can be created and used to access documents in your storage account
        (see https://aka.ms/azsdk/documenttranslation/managed-identity). Note that if the translation
        language pair is not present in the glossary, it will not be applied."""
    file_format: str
    """Format of the glossary file. To see supported formats,
        call the :func:`~DocumentTranslationClient.get_supported_glossary_formats()` client method."""
    format_version: Optional[str] = None
    """File format version. If not specified, the service will
        use the default_version for the file format returned from the
        :func:`~DocumentTranslationClient.get_supported_glossary_formats()` client method."""
    storage_source: Optional[str] = None
    """Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported."""

    def __init__(
        self,
        glossary_url: str,
        file_format: str,
        *,
        format_version: Optional[str] = None,
        storage_source: Optional[str] = None
    ) -> None:
        self.glossary_url = glossary_url
        self.file_format = file_format
        self.format_version = format_version
        self.storage_source = storage_source

    def _to_generated(self):
        return _Glossary(
            glossary_url=self.glossary_url,
            format=self.file_format,
            version=self.format_version,
            storage_source=self.storage_source,
        )

    @staticmethod
    def _to_generated_list(glossaries):
        return [glossary._to_generated() for glossary in glossaries]  # pylint: disable=protected-access

    def __repr__(self) -> str:
        return (
            "TranslationGlossary(glossary_url={}, "
            "file_format={}, format_version={}, storage_source={})".format(
                self.glossary_url,
                self.file_format,
                self.format_version,
                self.storage_source,
            )[:1024]
        )


class TranslationTarget:
    """Destination for the finished translated documents.

    :param str target_url: Required. The target location for your translated documents.
        This can be a SAS URL (see the service documentation for the supported SAS permissions
        for accessing target storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions)
        or a managed identity can be created and used to access documents in your storage account
        (see https://aka.ms/azsdk/documenttranslation/managed-identity).
    :param str language: Required. Target Language Code. This is the language
        you want your documents to be translated to. See supported languages here:
        https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate
    :keyword Optional[str] category_id: Category / custom model ID for using custom translation.
    :keyword glossaries: Glossaries to apply to translation.
    :paramtype glossaries: Optional[list[~azure.ai.translation.document.TranslationGlossary]]
    :keyword Optional[str] storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.
    """

    target_url: str
    """The target location for your translated documents.
        This can be a SAS URL (see the service documentation for the supported SAS permissions
        for accessing target storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions)
        or a managed identity can be created and used to access documents in your storage account
        (see https://aka.ms/azsdk/documenttranslation/managed-identity)."""
    language: str
    """Target Language Code. This is the language
        you want your documents to be translated to. See supported languages here:
        https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate"""
    category_id: Optional[str] = None
    """Category / custom model ID for using custom translation."""
    glossaries: Optional[List[TranslationGlossary]] = None
    """Glossaries to apply to translation."""
    storage_source: Optional[str] = None
    """Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported."""

    def __init__(
        self,
        target_url: str,
        language: str,
        *,
        category_id: Optional[str] = None,
        glossaries: Optional[List[TranslationGlossary]] = None,
        storage_source: Optional[str] = None
    ) -> None:
        self.target_url = target_url
        self.language = language
        self.category_id = category_id
        self.glossaries = glossaries
        self.storage_source = storage_source

    def _to_generated(self):
        return _TargetInput(
            target_url=self.target_url,
            category=self.category_id,
            language=self.language,
            storage_source=self.storage_source,
            glossaries=(
                TranslationGlossary._to_generated_list(self.glossaries)  # pylint: disable=protected-access
                if self.glossaries
                else None
            ),
        )

    @staticmethod
    def _to_generated_list(targets):
        return [target._to_generated() for target in targets]  # pylint: disable=protected-access

    def __repr__(self) -> str:
        return (
            "TranslationTarget(target_url={}, language={}, "
            "category_id={}, glossaries={}, storage_source={})".format(
                self.target_url,
                self.language,
                self.category_id,
                repr(self.glossaries),
                self.storage_source,
            )[:1024]
        )


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
        return _BatchRequest(
            source=_SourceInput(
                source_url=self.source_url,
                filter=_DocumentFilter(prefix=self.prefix, suffix=self.suffix),
                language=self.source_language,
                storage_source=self.storage_source,
            ),
            targets=TranslationTarget._to_generated_list(self.targets),  # pylint: disable=protected-access
            storage_type=self.storage_type,
        )

    @staticmethod
    def _to_generated_list(batch_document_inputs):
        return [
            batch_document_input._to_generated()  # pylint: disable=protected-access
            for batch_document_input in batch_document_inputs
        ]

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


class TranslationStatus:  # pylint: disable=too-many-instance-attributes
    """Status information about the translation operation."""

    id: str  # pylint: disable=redefined-builtin
    """Id of the translation operation."""
    created_on: datetime.datetime
    """The date time when the translation operation was created."""
    last_updated_on: datetime.datetime
    """The date time when the translation operation's status was last updated."""
    status: str
    """Status for a translation operation.

        * `NotStarted` - the operation has not begun yet.
        * `Running` - translation is in progress.
        * `Succeeded` - at least one document translated successfully within the operation.
        * `Canceled` - the operation was canceled.
        * `Canceling` - the operation is being canceled.
        * `ValidationFailed` - the input failed validation. E.g. there was insufficient permissions on blob containers.
        * `Failed` - all the documents within the operation failed.
    """
    documents_total_count: int
    """Number of translations to be made on documents in the operation."""
    documents_failed_count: int
    """Number of documents that failed translation."""
    documents_succeeded_count: int
    """Number of successful translations on documents."""
    documents_in_progress_count: int
    """Number of translations on documents in progress."""
    documents_not_started_count: int
    """Number of documents that have not started being translated."""
    documents_canceled_count: int
    """Number of documents that were canceled for translation."""
    total_characters_charged: int
    """Total characters charged across all documents within the translation operation."""
    error: Optional["DocumentTranslationError"] = None
    """Returned if there is an error with the translation operation.
        Includes error code, message, target."""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", None)
        self.created_on = kwargs.get("created_on", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.status = kwargs.get("status", None)
        self.error = kwargs.get("error", None)
        self.documents_total_count = kwargs.get("documents_total_count", None)
        self.documents_failed_count = kwargs.get("documents_failed_count", None)
        self.documents_succeeded_count = kwargs.get("documents_succeeded_count", None)
        self.documents_in_progress_count = kwargs.get("documents_in_progress_count", None)
        self.documents_not_started_count = kwargs.get("documents_not_started_count", None)
        self.documents_canceled_count = kwargs.get("documents_canceled_count", None)
        self.total_characters_charged = kwargs.get("total_characters_charged", None)

    @classmethod
    def _from_generated(cls, batch_status_details):
        return cls(
            id=batch_status_details.id,
            created_on=batch_status_details.created_date_time_utc,
            last_updated_on=batch_status_details.last_action_date_time_utc,
            status=convert_status(batch_status_details.status),
            error=(
                DocumentTranslationError._from_generated(batch_status_details.error)  # pylint: disable=protected-access
                if batch_status_details.error
                else None
            ),
            documents_total_count=batch_status_details.summary.total,
            documents_failed_count=batch_status_details.summary.failed,
            documents_succeeded_count=batch_status_details.summary.success,
            documents_in_progress_count=batch_status_details.summary.in_progress,
            documents_not_started_count=batch_status_details.summary.not_yet_started,
            documents_canceled_count=batch_status_details.summary.cancelled,
            total_characters_charged=batch_status_details.summary.total_character_charged,
        )

    def __repr__(self) -> str:
        return (
            "TranslationStatus(id={}, created_on={}, "
            "last_updated_on={}, status={}, error={}, documents_total_count={}, "
            "documents_failed_count={}, documents_succeeded_count={}, "
            "documents_in_progress_count={}, documents_not_started_count={}, "
            "documents_canceled_count={}, total_characters_charged={})".format(
                self.id,
                self.created_on,
                self.last_updated_on,
                self.status,
                repr(self.error),
                self.documents_total_count,
                self.documents_failed_count,
                self.documents_succeeded_count,
                self.documents_in_progress_count,
                self.documents_not_started_count,
                self.documents_canceled_count,
                self.total_characters_charged,
            )[:1024]
        )


class DocumentStatus:
    """Status information about a particular document within a translation operation."""

    id: str  # pylint: disable=redefined-builtin
    """Document Id."""
    source_document_url: str
    """Location of the source document in the source
        container. Note that any SAS tokens are removed from this path."""
    created_on: datetime.datetime
    """The date time when the document was created."""
    last_updated_on: datetime.datetime
    """The date time when the document's status was last updated."""
    status: str
    """Status for a document.

        * `NotStarted` - the document has not been translated yet.
        * `Running` - translation is in progress for document
        * `Succeeded` - translation succeeded for the document
        * `Failed` - the document failed to translate. Check the error property.
        * `Canceled` - the operation was canceled, the document was not translated.
        * `Canceling` - the operation is canceling, the document will not be translated."""
    translated_to: str
    """The language code of the language the document was translated to,
        if successful."""
    translation_progress: float
    """Progress of the translation if available.
        Value is between [0.0, 1.0]."""
    translated_document_url: Optional[str] = None
    """Location of the translated document in the target
        container. Note that any SAS tokens are removed from this path."""
    characters_charged: Optional[int] = None
    """Characters charged for the document."""
    error: Optional["DocumentTranslationError"] = None
    """Returned if there is an error with the particular document.
        Includes error code, message, target."""

    def __init__(self, **kwargs: Any) -> None:
        self.source_document_url = kwargs.get("source_document_url", None)
        self.translated_document_url = kwargs.get("translated_document_url", None)
        self.created_on = kwargs["created_on"]
        self.last_updated_on = kwargs["last_updated_on"]
        self.status = kwargs["status"]
        self.translated_to = kwargs["translated_to"]
        self.error = kwargs.get("error", None)
        self.translation_progress = kwargs.get("translation_progress", None)
        self.id = kwargs.get("id", None)
        self.characters_charged = kwargs.get("characters_charged", None)

    @classmethod
    def _from_generated(cls, doc_status):
        return cls(
            source_document_url=doc_status.source_path,
            translated_document_url=doc_status.path,
            created_on=doc_status.created_date_time_utc,
            last_updated_on=doc_status.last_action_date_time_utc,
            status=convert_status(doc_status.status),
            translated_to=doc_status.to,
            error=(
                DocumentTranslationError._from_generated(doc_status.error)  # pylint: disable=protected-access
                if doc_status.error
                else None
            ),
            translation_progress=doc_status.progress,
            id=doc_status.id,
            characters_charged=doc_status.character_charged,
        )

    def __repr__(self) -> str:
        return (
            "DocumentStatus(id={}, source_document_url={}, "
            "translated_document_url={}, created_on={}, last_updated_on={}, "
            "status={}, translated_to={}, error={}, translation_progress={}, "
            "characters_charged={})".format(
                self.id,
                self.source_document_url,
                self.translated_document_url,
                self.created_on,
                self.last_updated_on,
                self.status,
                self.translated_to,
                repr(self.error),
                self.translation_progress,
                self.characters_charged,
            )[:1024]
        )


class DocumentTranslationError:
    """This contains the error code, message, and target with descriptive details on why
    a translation operation or particular document failed.
    """

    code: str
    """The error code. Possible high level values include:
        "InvalidRequest", "InvalidArgument", "InternalServerError", "ServiceUnavailable",
        "ResourceNotFound", "Unauthorized", "RequestRateTooHigh"."""
    message: str
    """The error message associated with the failure."""
    target: Optional[str] = None
    """The source of the error.
        For example it would be "documents" or "document id" in case of invalid document."""

    def __init__(self, **kwargs: Any) -> None:
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)
        self.target = kwargs.get("target", None)

    @classmethod
    def _from_generated(cls, error):
        if error.inner_error:
            inner_error = error.inner_error
            return cls(
                code=inner_error.code,
                message=inner_error.message,
                target=inner_error.target if inner_error.target is not None else error.target,
            )
        return cls(code=error.code, message=error.message, target=error.target)

    def __repr__(self) -> str:
        return "DocumentTranslationError(code={}, message={}, target={}".format(self.code, self.message, self.target)[
            :1024
        ]


class DocumentTranslationFileFormat:
    """Possible file formats supported by the Document Translation service."""

    file_format: str
    """Name of the format."""
    file_extensions: List[str]
    """Supported file extension for this format."""
    content_types: List[str]
    """Supported Content-Types for this format."""
    format_versions: List[str]
    """Supported Version."""
    default_format_version: Optional[str] = None
    """Default format version if none is specified."""

    def __init__(self, **kwargs: Any) -> None:
        self.file_format = kwargs.get("file_format", None)
        self.file_extensions = kwargs.get("file_extensions", None)
        self.content_types = kwargs.get("content_types", None)
        self.format_versions = kwargs.get("format_versions", None)
        self.default_format_version = kwargs.get("default_format_version", None)

    @classmethod
    def _from_generated(cls, file_format):
        return cls(
            file_format=file_format.format,
            file_extensions=file_format.file_extensions,
            content_types=file_format.content_types,
            format_versions=file_format.versions,
            default_format_version=file_format.default_version,
        )

    @staticmethod
    def _from_generated_list(file_formats):
        return [DocumentTranslationFileFormat._from_generated(file_formats) for file_formats in file_formats]

    def __repr__(self) -> str:
        return (
            "DocumentTranslationFileFormat(file_format={}, file_extensions={}, "
            "content_types={}, format_versions={}, default_format_version={}".format(
                self.file_format,
                self.file_extensions,
                self.content_types,
                self.format_versions,
                self.default_format_version,
            )[:1024]
        )


class DocumentTranslationLROPoller(LROPoller[PollingReturnType_co]):
    """A custom poller implementation for Document Translation. Call `result()` on the poller to return
    a pageable of :class:`~azure.ai.translation.document.DocumentStatus`."""

    @property
    def id(self) -> str:
        """The ID for the translation operation

        :return: The str ID for the translation operation.
        :rtype: str
        """
        if self._polling_method._current_body:  # pylint: disable=protected-access
            return self._polling_method._current_body.id  # pylint: disable=protected-access
        return self._polling_method._get_id_from_headers()  # pylint: disable=protected-access

    @property
    def details(self) -> TranslationStatus:
        """The details for the translation operation

        :return: The details for the translation operation.
        :rtype: ~azure.ai.translation.document.TranslationStatus
        """
        if self._polling_method._current_body:  # pylint: disable=protected-access
            return TranslationStatus._from_generated(  # pylint: disable=protected-access
                self._polling_method._current_body  # pylint: disable=protected-access
            )
        return TranslationStatus(id=self._polling_method._get_id_from_headers())  # pylint: disable=protected-access

    @classmethod
    def from_continuation_token(  # pylint: disable=docstring-missing-return,docstring-missing-param,docstring-missing-rtype
        cls, polling_method, continuation_token, **kwargs: Any
    ):
        """
        :meta private:
        """
        (
            client,
            initial_response,
            deserialization_callback,
        ) = polling_method.from_continuation_token(continuation_token, **kwargs)

        return cls(client, initial_response, deserialization_callback, polling_method)


class DocumentTranslationLROPollingMethod(LROBasePolling):
    """A custom polling method implementation for Document Translation."""

    def __init__(self, *args, **kwargs):
        self._cont_token_response = kwargs.pop("cont_token_response")
        super().__init__(*args, **kwargs)

    @property
    def _current_body(self) -> _TranslationStatus:
        try:
            return _TranslationStatus(self._pipeline_response.http_response.json())
        except json.decoder.JSONDecodeError:
            return _TranslationStatus()  # type: ignore[call-overload]

    def _get_id_from_headers(self) -> str:
        return (
            self._initial_response.http_response.headers["Operation-Location"]
            .split("/batches/")[1]
            .split("?api-version")[0]
        )

    def finished(self) -> bool:
        """Is this polling finished?

        :return: True/False for whether polling is complete.
        :rtype: bool
        """
        return self._finished(self.status())

    @staticmethod
    def _finished(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FINISHED

    @staticmethod
    def _failed(status) -> bool:
        if hasattr(status, "value"):
            status = status.value
        return str(status).lower() in _FAILED

    def get_continuation_token(self) -> str:
        if self._current_body:
            return self._current_body.id
        return self._get_id_from_headers()

    # pylint: disable=arguments-differ
    def from_continuation_token(self, continuation_token: str, **kwargs: Any) -> Tuple:  # type: ignore[override]
        try:
            client = kwargs["client"]
        except KeyError as exc:
            raise ValueError("Need kwarg 'client' to be recreated from continuation_token") from exc

        try:
            deserialization_callback = kwargs["deserialization_callback"]
        except KeyError as exc:
            raise ValueError("Need kwarg 'deserialization_callback' to be recreated from continuation_token") from exc

        return client, self._cont_token_response, deserialization_callback

    def _poll(self) -> None:
        """Poll status of operation so long as operation is incomplete and
        we have an endpoint to query.

        :raises: OperationFailed if operation status 'Failed' or 'Canceled'.
        :raises: BadStatus if response status invalid.
        :raises: BadResponse if response invalid.
        """

        while not self.finished():
            self.update_status()
        while not self.finished():
            self._delay()
            self.update_status()

        if self._failed(self.status()):
            raise OperationFailed("Operation failed or canceled")

        final_get_url = self._operation.get_final_get_url(self._pipeline_response)
        if final_get_url:
            self._pipeline_response = self.request_status(final_get_url)
            _raise_if_bad_http_status_and_method(self._pipeline_response.http_response)


class TranslationPolling(OperationResourcePolling):
    """Implements a Location polling."""

    def can_poll(self, pipeline_response: PipelineResponseType) -> bool:
        """Answer if this polling method could be used.

        :param pipeline_response: The PipelineResponse type
        :type pipeline_response: PipelineResponseType
        :return: Whether polling should be performed.
        :rtype: bool
        """
        response = pipeline_response.http_response
        can_poll = self._operation_location_header in response.headers
        if can_poll:
            return True

        if not _is_empty(response):
            body = _as_json(response)
            status = body.get("status")
            if status:
                return True
        return False

    def _set_async_url_if_present(self, response: ResponseType) -> None:
        location_header = response.headers.get(self._operation_location_header)
        if location_header:
            self._async_url = location_header
        else:
            self._async_url = response.request.url

    def get_status(self, pipeline_response: PipelineResponseType) -> str:
        """Process the latest status update retrieved from a 'location' header.

        :param azure.core.pipeline.PipelineResponse pipeline_response: latest REST call response.
        :return: The current operation status
        :rtype: str
        :raises: BadResponse if response has no body and not status 202.
        """
        response = pipeline_response.http_response
        if not _is_empty(response):
            body = _as_json(response)
            status = body.get("status")
            if status:
                return self._map_nonstandard_statuses(status, body)
            raise BadResponse("No status found in body")
        raise BadResponse("The response from long running operation does not contain a body.")

    def _map_nonstandard_statuses(self, status: str, body: Dict[str, Any]) -> str:
        """Map non-standard statuses.

        :param str status: lro process status.
        :param str body: pipeline response body.
        :return: The current operation status.
        :rtype: str
        """
        if status == "ValidationFailed":
            self.raise_error(body)
        return status

    def raise_error(self, body: Dict[str, Any]) -> None:
        error = body["error"]
        if body["error"].get("innerError", None):
            error = body["error"]["innerError"]
        http_response_error = HttpResponseError(message="({}): {}".format(error["code"], error["message"]))
        http_response_error.error = ODataV4Format(error)  # set error.code
        raise http_response_error


class DocumentTranslationApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Document Translation API versions supported by this package"""

    #: This is the default version
    V2024_05_01 = "2024-05-01"


def get_translation_input(args, kwargs, continuation_token):
    try:
        inputs = kwargs.pop("inputs", None)
        if not inputs:
            inputs = args[0]
        request = (
            DocumentTranslationInput._to_generated_list(inputs)  # pylint: disable=protected-access
            if not continuation_token
            else None
        )
    except (AttributeError, TypeError, IndexError):
        try:
            source_url = kwargs.pop("source_url", None)
            if not source_url:
                source_url = args[0]
            target_url = kwargs.pop("target_url", None)
            if not target_url:
                target_url = args[1]
            target_language = kwargs.pop("target_language", None)
            if not target_language:
                target_language = args[2]

            # Additional kwargs
            source_language = kwargs.pop("source_language", None)
            prefix = kwargs.pop("prefix", None)
            suffix = kwargs.pop("suffix", None)
            storage_type = kwargs.pop("storage_type", None)
            category_id = kwargs.pop("category_id", None)
            glossaries = kwargs.pop("glossaries", None)

            request = [
                _BatchRequest(
                    source=_SourceInput(
                        source_url=source_url,
                        filter=_DocumentFilter(prefix=prefix, suffix=suffix),
                        language=source_language,
                    ),
                    targets=[
                        _TargetInput(
                            target_url=target_url,
                            language=target_language,
                            glossaries=(
                                [g._to_generated() for g in glossaries]  # pylint: disable=protected-access
                                if glossaries
                                else None
                            ),
                            category=category_id,
                        )
                    ],
                    storage_type=storage_type,
                )
            ]
        except (AttributeError, TypeError, IndexError) as exc:
            raise ValueError(
                "Pass 'inputs' for multiple inputs or 'source_url', 'target_url', "
                "and 'target_language' for a single input."
            ) from exc

    return request


def get_http_logging_policy(**kwargs):
    http_logging_policy = HttpLoggingPolicy(**kwargs)
    http_logging_policy.allowed_header_names.update(
        {
            "Operation-Location",
            "Content-Encoding",
            "Vary",
            "apim-request-id",
            "X-RequestId",
            "Set-Cookie",
            "X-Powered-By",
            "Strict-Transport-Security",
            "x-content-type-options",
        }
    )
    http_logging_policy.allowed_query_params.update(
        {
            "top",
            "skip",
            "maxpagesize",
            "ids",
            "statuses",
            "createdDateTimeUtcStart",
            "createdDateTimeUtcEnd",
            "orderby",
        }
    )
    return http_logging_policy


def convert_datetime(date_time: Union[str, datetime.datetime]) -> datetime.datetime:
    if isinstance(date_time, datetime.datetime):
        return date_time
    if isinstance(date_time, str):
        try:
            return datetime.datetime.strptime(date_time, "%Y-%m-%d")
        except ValueError:
            try:
                return datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                return datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    raise TypeError("Bad datetime type")


def convert_order_by(orderby: Optional[List[str]]) -> Optional[List[str]]:
    if orderby:
        orderby = [order.replace("created_on", "createdDateTimeUtc") for order in orderby]
    return orderby


class DocumentTranslationClient:
    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        """DocumentTranslationClient is your interface to the Document Translation service.
        Use the client to translate whole documents while preserving source document
        structure and text formatting.

        :param str endpoint: Supported Document Translation endpoint (protocol and hostname, for example:
            https://<resource-name>.cognitiveservices.azure.com/).
        :param credential: Credentials needed for the client to connect to Azure.
            This is an instance of AzureKeyCredential if using an API key or a token
            credential from :mod:`azure.identity`.
        :type credential: :class:`~azure.core.credentials.AzureKeyCredential` or
            :class:`~azure.core.credentials.TokenCredential`
        :keyword api_version:
            The API version of the service to use for requests. It defaults to the latest service version.
            Setting to an older version may result in reduced feature compatibility.
        :paramtype api_version: str or ~azure.ai.translation.document.DocumentTranslationApiVersion

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_authentication.py
                :start-after: [START create_dt_client_with_key]
                :end-before: [END create_dt_client_with_key]
                :language: python
                :dedent: 4
                :caption: Creating the DocumentTranslationClient with an endpoint and API key.

            .. literalinclude:: ../samples/sample_authentication.py
                :start-after: [START create_dt_client_with_aad]
                :end-before: [END create_dt_client_with_aad]
                :language: python
                :dedent: 4
                :caption: Creating the DocumentTranslationClient with a token credential.
        """
        try:
            self._endpoint = endpoint.rstrip("/")
        except AttributeError as exc:
            raise ValueError("Parameter 'endpoint' must be a string.") from exc
        self._credential = credential
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)

        from ._client import DocumentTranslationClient as _BatchDocumentTranslationClient

        self._client = _BatchDocumentTranslationClient(
            endpoint=self._endpoint,
            credential=credential,
            http_logging_policy=kwargs.pop("http_logging_policy", get_http_logging_policy()),
            polling_interval=polling_interval,
            **kwargs
        )

    def __enter__(self) -> "DocumentTranslationClient":
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args) -> None:
        self._client.__exit__(*args)  # pylint:disable=no-member

    def close(self) -> None:
        """Close the :class:`~azure.ai.translation.document.DocumentTranslationClient` session."""
        return self._client.close()

    @overload
    def begin_translation(
        self,
        source_url: str,
        target_url: str,
        target_language: str,
        *,
        source_language: Optional[str] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        storage_type: Optional[Union[str, StorageInputType]] = None,
        category_id: Optional[str] = None,
        glossaries: Optional[List[TranslationGlossary]] = None,
        **kwargs: Any
    ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language. There are two ways to call this method:

        1) To perform translation on documents from a single source container to a single target container, pass the
        `source_url`, `target_url`, and `target_language` parameters including any optional keyword arguments.

        2) To pass multiple inputs for translation (multiple sources or targets), pass the `inputs` parameter
        as a list of :class:`~azure.ai.translation.document.DocumentTranslationInput`.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param str source_url: The source SAS URL to the Azure Blob container containing the documents
            to be translated. See the service documentation for the supported SAS permissions for accessing
            source storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions
        :param str target_url: The target SAS URL to the Azure Blob container where the translated documents
            should be written. See the service documentation for the supported SAS permissions for accessing
            target storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions
        :param str target_language: This is the language code you want your documents to be translated to.
            See supported language codes here:
            https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate
        :keyword str source_language: Language code for the source documents.
            If none is specified, the source language will be auto-detected for each document.
        :keyword str prefix: A case-sensitive prefix string to filter documents in the source path for
            translation. For example, when using a Azure storage blob Uri, use the prefix to restrict
            sub folders for translation.
        :keyword str suffix: A case-sensitive suffix string to filter documents in the source path for
            translation. This is most often use for file extensions.
        :keyword storage_type: Storage type of the input documents source string. Possible values
            include: "Folder", "File".
        :paramtype storage_type: str or ~azure.ai.translation.document.StorageInputType
        :keyword str category_id: Category / custom model ID for using custom translation.
        :keyword glossaries: Glossaries to apply to translation.
        :paramtype glossaries: list[~azure.ai.translation.document.TranslationGlossary]
        :return: An instance of a DocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: DocumentTranslationLROPoller[~azure.core.paging.ItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_translation(
        self, inputs: List[DocumentTranslationInput], **kwargs: Any
    ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language. There are two ways to call this method:

        1) To perform translation on documents from a single source container to a single target container, pass the
        `source_url`, `target_url`, and `target_language` parameters including any optional keyword arguments.

        2) To pass multiple inputs for translation (multiple sources or targets), pass the `inputs` parameter
        as a list of :class:`~azure.ai.translation.document.DocumentTranslationInput`.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param inputs: A list of translation inputs. Each individual input has a single
            source URL to documents and can contain multiple TranslationTargets (one for each language)
            for the destination to write translated documents.
        :type inputs: List[~azure.ai.translation.document.DocumentTranslationInput]
        :return: An instance of a DocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: DocumentTranslationLROPoller[~azure.core.paging.ItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace
    def begin_translation(  # pylint: disable=docstring-missing-param
        self, *args: Union[str, List[DocumentTranslationInput]], **kwargs: Any
    ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language. There are two ways to call this method:

        1) To perform translation on documents from a single source container to a single target container, pass the
        `source_url`, `target_url`, and `target_language` parameters including any optional keyword arguments.

        2) To pass multiple inputs for translation (multiple sources or targets), pass the `inputs` parameter
        as a list of :class:`~azure.ai.translation.document.DocumentTranslationInput`.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :return: An instance of a DocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: DocumentTranslationLROPoller[~azure.core.paging.ItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_begin_translation.py
                :start-after: [START begin_translation]
                :end-before: [END begin_translation]
                :language: python
                :dedent: 4
                :caption: Translate the documents in your storage container.
        """

        continuation_token = kwargs.pop("continuation_token", None)

        inputs = get_translation_input(args, kwargs, continuation_token)

        def deserialization_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            translation_status = json.loads(raw_response.http_response.text())
            return self.list_document_statuses(translation_status["id"])

        polling_interval = kwargs.pop(
            "polling_interval",
            self._client._config.polling_interval,  # pylint: disable=protected-access
        )

        pipeline_response = None
        if continuation_token:
            pipeline_response = self._client.get_translation_status(
                continuation_token,
                cls=lambda pipeline_response, _, response_headers: pipeline_response,
            )

        callback = kwargs.pop("cls", deserialization_callback)
        return cast(
            DocumentTranslationLROPoller[ItemPaged[DocumentStatus]],
            self._client.begin_start_translation(
                body=_StartTranslationDetails(inputs=inputs),
                polling=DocumentTranslationLROPollingMethod(
                    timeout=polling_interval,
                    lro_algorithms=[TranslationPolling()],
                    cont_token_response=pipeline_response,
                    **kwargs
                ),
                cls=callback,
                continuation_token=continuation_token,
                **kwargs
            ),
        )

    @distributed_trace
    def get_translation_status(self, translation_id: str, **kwargs: Any) -> TranslationStatus:
        """Gets the status of the translation operation.

        Includes the overall status, as well as a summary of
        the documents that are being translated as part of that translation operation.

        :param str translation_id: The translation operation ID.
        :return: A TranslationStatus with information on the status of the translation operation.
        :rtype: ~azure.ai.translation.document.TranslationStatus
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        translation_status = self._client.get_translation_status(translation_id, **kwargs)
        return TranslationStatus._from_generated(  # pylint: disable=protected-access
            _TranslationStatus(translation_status)  # type: ignore[call-overload]
        )

    @distributed_trace
    def cancel_translation(self, translation_id: str, **kwargs: Any) -> None:
        """Cancel a currently processing or queued translation operation.

        A translation will not be canceled if it is already completed, failed, or canceling.
        All documents that have completed translation will not be canceled and will be charged.
        If possible, all pending documents will be canceled.

        :param str translation_id: The translation operation ID.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        self._client.cancel_translation(translation_id, **kwargs)

    @distributed_trace
    def list_translation_statuses(
        self,
        *,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        translation_ids: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        created_after: Optional[Union[str, datetime.datetime]] = None,
        created_before: Optional[Union[str, datetime.datetime]] = None,
        order_by: Optional[List[str]] = None,
        **kwargs: Any
    ) -> ItemPaged[TranslationStatus]:
        """List all the submitted translation operations under the Document Translation resource.

        :keyword int top: The total number of operations to return (across all pages) from all submitted translations.
        :keyword int skip: The number of operations to skip (from beginning of all submitted operations).
            By default, we sort by all submitted operations in descending order by start time.
        :keyword list[str] translation_ids: Translation operations ids to filter by.
        :keyword list[str] statuses: Translation operation statuses to filter by. Options include
            'NotStarted', 'Running', 'Succeeded', 'Failed', 'Canceled', 'Canceling',
            and 'ValidationFailed'.
        :keyword created_after: Get operations created after a certain datetime.
        :paramtype created_after: str or ~datetime.datetime
        :keyword created_before: Get operations created before a certain datetime.
        :paramtype created_before: str or ~datetime.datetime
        :keyword list[str] order_by: The sorting query for the operations returned. Currently only
            'created_on' supported.
            format: ["param1 asc/desc", "param2 asc/desc", ...]
            (ex: 'created_on asc', 'created_on desc').
        :return: A pageable of TranslationStatus.
        :rtype: ~azure.core.paging.ItemPaged[TranslationStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_list_translations.py
                :start-after: [START list_translations]
                :end-before: [END list_translations]
                :language: python
                :dedent: 4
                :caption: List all submitted translations under the resource.
        """

        if statuses:
            statuses = [convert_status(status, ll=True) for status in statuses]
        order_by = convert_order_by(order_by)
        created_after = convert_datetime(created_after) if created_after else None
        created_before = convert_datetime(created_before) if created_before else None

        def _convert_from_generated_model(
            generated_model,
        ):  # pylint: disable=protected-access
            return TranslationStatus._from_generated(
                _TranslationStatus(generated_model)
            )  # pylint: disable=protected-access

        model_conversion_function = kwargs.pop(
            "cls",
            lambda translation_statuses: [_convert_from_generated_model(status) for status in translation_statuses],
        )

        return cast(
            ItemPaged[TranslationStatus],
            self._client.get_translations_status(
                cls=model_conversion_function,
                created_date_time_utc_start=created_after,
                created_date_time_utc_end=created_before,
                ids=translation_ids,
                orderby=order_by,
                statuses=statuses,
                top=top,
                skip=skip,
                **kwargs
            ),
        )

    @distributed_trace
    def list_document_statuses(
        self,
        translation_id: str,
        *,
        top: Optional[int] = None,
        skip: Optional[int] = None,
        document_ids: Optional[List[str]] = None,
        statuses: Optional[List[str]] = None,
        created_after: Optional[Union[str, datetime.datetime]] = None,
        created_before: Optional[Union[str, datetime.datetime]] = None,
        order_by: Optional[List[str]] = None,
        **kwargs: Any
    ) -> ItemPaged[DocumentStatus]:
        """List all the document statuses for a given translation operation.

        :param str translation_id: ID of translation operation to list documents for.
        :keyword int top: The total number of documents to return (across all pages).
        :keyword int skip: The number of documents to skip (from beginning).
            By default, we sort by all documents in descending order by start time.
        :keyword list[str] document_ids: Document IDs to filter by.
        :keyword list[str] statuses: Document statuses to filter by. Options include
            'NotStarted', 'Running', 'Succeeded', 'Failed', 'Canceled', 'Canceling',
            and 'ValidationFailed'.
        :keyword created_after: Get documents created after a certain datetime.
        :paramtype created_after: str or ~datetime.datetime
        :keyword created_before: Get documents created before a certain datetime.
        :paramtype created_before: str or ~datetime.datetime
        :keyword list[str] order_by: The sorting query for the documents. Currently only
            'created_on' is supported.
            format: ["param1 asc/desc", "param2 asc/desc", ...]
            (ex: 'created_on asc', 'created_on desc').
        :return: A pageable of DocumentStatus.
        :rtype: ~azure.core.paging.ItemPaged[DocumentStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_check_document_statuses.py
                :start-after: [START list_document_statuses]
                :end-before: [END list_document_statuses]
                :language: python
                :dedent: 4
                :caption: List all the document statuses as they are being translated.
        """

        if statuses:
            statuses = [convert_status(status, ll=True) for status in statuses]
        order_by = convert_order_by(order_by)
        created_after = convert_datetime(created_after) if created_after else None
        created_before = convert_datetime(created_before) if created_before else None

        def _convert_from_generated_model(generated_model):
            return DocumentStatus._from_generated(_DocumentStatus(generated_model))  # pylint: disable=protected-access

        model_conversion_function = kwargs.pop(
            "cls",
            lambda doc_statuses: [_convert_from_generated_model(doc_status) for doc_status in doc_statuses],
        )

        return cast(
            ItemPaged[DocumentStatus],
            self._client.get_documents_status(
                id=translation_id,
                cls=model_conversion_function,
                created_date_time_utc_start=created_after,
                created_date_time_utc_end=created_before,
                ids=document_ids,
                orderby=order_by,
                statuses=statuses,
                top=top,
                skip=skip,
                **kwargs
            ),
        )

    @distributed_trace
    def get_document_status(self, translation_id: str, document_id: str, **kwargs: Any) -> DocumentStatus:
        """Get the status of an individual document within a translation operation.

        :param str translation_id: The translation operation ID.
        :param str document_id: The ID for the document.
        :return: A DocumentStatus with information on the status of the document.
        :rtype: ~azure.ai.translation.document.DocumentStatus
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        document_status = self._client.get_document_status(translation_id, document_id, **kwargs)
        return DocumentStatus._from_generated(_DocumentStatus(document_status))  # type: ignore[call-overload] # pylint: disable=protected-access

    @distributed_trace
    def get_supported_glossary_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]:
        """Get the list of the glossary formats supported by the Document Translation service.

        :return: A list of supported glossary formats.
        :rtype: List[DocumentTranslationFileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        glossary_formats = self._client.get_supported_formats(type="glossary", **kwargs)
        return DocumentTranslationFileFormat._from_generated_list(  # pylint: disable=protected-access
            glossary_formats.value
        )

    @distributed_trace
    def get_supported_document_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]:
        """Get the list of the document formats supported by the Document Translation service.

        :return: A list of supported document formats for translation.
        :rtype: List[DocumentTranslationFileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        document_formats = self._client.get_supported_formats(type="document", **kwargs)
        return DocumentTranslationFileFormat._from_generated_list(  # pylint: disable=protected-access
            document_formats.value
        )


__all__: List[str] = [
    "DocumentTranslationClient",
    "DocumentTranslationApiVersion",
    "DocumentTranslationLROPoller",
    # re-export models at this level for backwards compatibility
    "TranslationGlossary",
    "TranslationTarget",
    "DocumentTranslationInput",
    "TranslationStatus",
    "DocumentStatus",
    "DocumentTranslationError",
    "DocumentTranslationFileFormat",
    "StorageInputType",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
