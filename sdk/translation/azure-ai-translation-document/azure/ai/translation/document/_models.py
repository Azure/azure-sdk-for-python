# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, List, Optional, Union
from ._generated.models import (
    BatchRequest as _BatchRequest,
    SourceInput as _SourceInput,
    DocumentFilter as _DocumentFilter,
    TargetInput as _TargetInput,
    Glossary as _Glossary,
    StorageInputType
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
    :keyword str format_version: File format version. If not specified, the service will
        use the default_version for the file format returned from the
        :func:`~DocumentTranslationClient.get_supported_glossary_formats()` client method.
    :keyword str storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.

    :ivar str glossary_url: Required. Location of the glossary file. This should be a URL to
        the glossary file in the storage blob container. The URL can be a SAS URL (see the
        service documentation for the supported SAS permissions for accessing storage
        containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions) or a managed identity
        can be created and used to access documents in your storage account
        (see https://aka.ms/azsdk/documenttranslation/managed-identity). Note that if the translation
        language pair is not present in the glossary, it will not be applied.
    :ivar str file_format: Required. Format of the glossary file. To see supported formats,
        call the :func:`~DocumentTranslationClient.get_supported_glossary_formats()` client method.
    :ivar str format_version: File format version. If not specified, the service will
        use the default_version for the file format returned from the
        :func:`~DocumentTranslationClient.get_supported_glossary_formats()` client method.
    :ivar str storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.
    """

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
        return [
            glossary._to_generated()  # pylint: disable=protected-access
            for glossary in glossaries
        ]

    def __repr__(self):
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
    :param str language_code: Required. Target Language Code. This is the language
        you want your documents to be translated to. See supported languages here:
        https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate
    :keyword str category_id: Category / custom model ID for using custom translation.
    :keyword glossaries: Glossaries to apply to translation.
    :paramtype glossaries: list[~azure.ai.translation.document.TranslationGlossary]
    :keyword str storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.

    :ivar str target_url: Required. The target location for your translated documents.
        This can be a SAS URL (see the service documentation for the supported SAS permissions
        for accessing target storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions)
        or a managed identity can be created and used to access documents in your storage account
        (see https://aka.ms/azsdk/documenttranslation/managed-identity).
    :ivar str language_code: Required. Target Language Code. This is the language
        you want your documents to be translated to. See supported languages here:
        https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate
    :ivar str category_id: Category / custom model ID for using custom translation.
    :ivar glossaries: Glossaries to apply to translation.
    :vartype glossaries: list[~azure.ai.translation.document.TranslationGlossary]
    :ivar str storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.
    """

    def __init__(
        self,
        target_url: str,
        language_code: str,
        *,
        category_id: Optional[str] = None,
        glossaries: Optional[List[TranslationGlossary]] = None,
        storage_source: Optional[str] = None
    ) -> None:
        self.target_url = target_url
        self.language_code = language_code
        self.category_id = category_id
        self.glossaries = glossaries
        self.storage_source = storage_source

    def _to_generated(self):
        return _TargetInput(
            target_url=self.target_url,
            category=self.category_id,
            language=self.language_code,
            storage_source=self.storage_source,
            glossaries=TranslationGlossary._to_generated_list(  # pylint: disable=protected-access
                self.glossaries
            )
            if self.glossaries
            else None,
        )

    @staticmethod
    def _to_generated_list(targets):
        return [
            target._to_generated()  # pylint: disable=protected-access
            for target in targets
        ]

    def __repr__(self):
        return (
            "TranslationTarget(target_url={}, language_code={}, "
            "category_id={}, glossaries={}, storage_source={})".format(
                self.target_url,
                self.language_code,
                self.category_id,
                self.glossaries.__repr__(),
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
    :keyword str source_language_code: Language code for the source documents.
        If none is specified, the source language will be auto-detected for each document.
    :keyword str prefix: A case-sensitive prefix string to filter documents in the source path for
        translation. For example, when using a Azure storage blob Uri, use the prefix to restrict
        sub folders for translation.
    :keyword str suffix: A case-sensitive suffix string to filter documents in the source path for
        translation. This is most often use for file extensions.
    :keyword storage_type: Storage type of the input documents source string. Possible values
        include: "Folder", "File".
    :paramtype storage_type: str or ~azure.ai.translation.document.StorageInputType
    :keyword str storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.

    :ivar str source_url: Required. Location of the folder / container or single file with your
        documents. This can be a SAS URL (see the service documentation for the supported SAS permissions
        for accessing source storage containers/blobs: https://aka.ms/azsdk/documenttranslation/sas-permissions)
        or a managed identity can be created and used to access documents in your storage account
        (see https://aka.ms/azsdk/documenttranslation/managed-identity).
    :ivar targets: Required. Location of the destination for the output. This is a list of
        TranslationTargets. Note that a TranslationTarget is required for each language code specified.
    :vartype targets: list[~azure.ai.translation.document.TranslationTarget]
    :ivar str source_language_code: Language code for the source documents.
        If none is specified, the source language will be auto-detected for each document.
    :ivar str prefix: A case-sensitive prefix string to filter documents in the source path for
        translation. For example, when using a Azure storage blob Uri, use the prefix to restrict
        sub folders for translation.
    :ivar str suffix: A case-sensitive suffix string to filter documents in the source path for
        translation. This is most often use for file extensions.
    :ivar storage_type: Storage type of the input documents source string. Possible values
        include: "Folder", "File".
    :vartype storage_type: str or ~azure.ai.translation.document.StorageInputType
    :ivar str storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.
    """

    def __init__(
        self,
        source_url: str,
        targets: List[TranslationTarget],
        *,
        source_language_code: Optional[str] = None,
        storage_type: Optional[Union[str, StorageInputType]] = None,
        storage_source: Optional[str] = None,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None
    ) -> None:
        self.source_url = source_url
        self.targets = targets
        self.source_language_code = source_language_code
        self.storage_type = storage_type
        self.storage_source = storage_source
        self.prefix = prefix
        self.suffix = suffix

    def _to_generated(self):
        return _BatchRequest(
            source=_SourceInput(
                source_url=self.source_url,
                filter=_DocumentFilter(prefix=self.prefix, suffix=self.suffix),
                language=self.source_language_code,
                storage_source=self.storage_source,
            ),
            targets=TranslationTarget._to_generated_list(  # pylint: disable=protected-access
                self.targets
            ),
            storage_type=self.storage_type,
        )

    @staticmethod
    def _to_generated_list(batch_document_inputs):
        return [
            batch_document_input._to_generated()  # pylint: disable=protected-access
            for batch_document_input in batch_document_inputs
        ]

    def __repr__(self):
        return (
            "DocumentTranslationInput(source_url={}, targets={}, "
            "source_language_code={}, storage_type={}, "
            "storage_source={}, prefix={}, suffix={})".format(
                self.source_url,
                self.targets.__repr__(),
                self.source_language_code,
                self.storage_type.__repr__(),
                self.storage_source,
                self.prefix,
                self.suffix,
            )[:1024]
        )


class TranslationStatus:  # pylint: disable=too-many-instance-attributes
    """Status information about the translation operation.

    :ivar str id: Id of the translation operation.
    :ivar created_on: The date time when the translation operation was created.
    :vartype created_on: ~datetime.datetime
    :ivar last_updated_on: The date time when the translation operation's status was last updated.
    :vartype last_updated_on: ~datetime.datetime
    :ivar str status: Status for a translation operation.

        * `NotStarted` - the operation has not begun yet.
        * `Running` - translation is in progress.
        * `Succeeded` - at least one document translated successfully within the operation.
        * `Canceled` - the operation was canceled.
        * `Canceling` - the operation is being canceled.
        * `ValidationFailed` - the input failed validation. E.g. there was insufficient permissions on blob containers.
        * `Failed` - all the documents within the operation failed.

    :ivar error: Returned if there is an error with the translation operation.
        Includes error code, message, target.
    :vartype error: ~azure.ai.translation.document.DocumentTranslationError
    :ivar int documents_total_count: Number of translations to be made on documents in the operation.
    :ivar int documents_failed_count: Number of documents that failed translation.
    :ivar int documents_succeeded_count: Number of successful translations on documents.
    :ivar int documents_in_progress_count: Number of translations on documents in progress.
    :ivar int documents_not_yet_started_count: Number of documents that have not yet started being translated.
    :ivar int documents_canceled_count: Number of documents that were canceled for translation.
    :ivar int total_characters_charged: Total characters charged across all documents within the translation operation.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id")
        self.created_on = kwargs.get("created_on")
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.status = kwargs.get("status", None)
        self.error = kwargs.get("error", None)
        self.documents_total_count = kwargs.get("documents_total_count", None)
        self.documents_failed_count = kwargs.get("documents_failed_count", None)
        self.documents_succeeded_count = kwargs.get("documents_succeeded_count", None)
        self.documents_in_progress_count = kwargs.get(
            "documents_in_progress_count", None
        )
        self.documents_not_yet_started_count = kwargs.get(
            "documents_not_yet_started_count", None
        )
        self.documents_canceled_count = kwargs.get("documents_canceled_count", None)
        self.total_characters_charged = kwargs.get("total_characters_charged", None)

    @classmethod
    def _from_generated(cls, batch_status_details):
        if not batch_status_details:
            return cls()

        return cls(
            id=batch_status_details.id,
            created_on=batch_status_details.created_date_time_utc,
            last_updated_on=batch_status_details.last_action_date_time_utc,
            status=convert_status(batch_status_details.status),
            error=DocumentTranslationError._from_generated(  # pylint: disable=protected-access
                batch_status_details.error
            )
            if batch_status_details.error
            else None,
            documents_total_count=batch_status_details.summary.total,
            documents_failed_count=batch_status_details.summary.failed,
            documents_succeeded_count=batch_status_details.summary.success,
            documents_in_progress_count=batch_status_details.summary.in_progress,
            documents_not_yet_started_count=batch_status_details.summary.not_yet_started,
            documents_canceled_count=batch_status_details.summary.cancelled,
            total_characters_charged=batch_status_details.summary.total_character_charged,
        )

    def __repr__(self):
        return (
            "TranslationStatus(id={}, created_on={}, "
            "last_updated_on={}, status={}, error={}, documents_total_count={}, "
            "documents_failed_count={}, documents_succeeded_count={}, "
            "documents_in_progress_count={}, documents_not_yet_started_count={}, "
            "documents_canceled_count={}, total_characters_charged={})".format(
                self.id,
                self.created_on,
                self.last_updated_on,
                self.status,
                self.error.__repr__(),
                self.documents_total_count,
                self.documents_failed_count,
                self.documents_succeeded_count,
                self.documents_in_progress_count,
                self.documents_not_yet_started_count,
                self.documents_canceled_count,
                self.total_characters_charged,
            )[:1024]
        )


class DocumentStatus:
    """Status information about a particular document within a translation operation.

    :ivar str source_document_url: Location of the source document in the source
        container. Note that any SAS tokens are removed from this path.
    :ivar str translated_document_url: Location of the translated document in the target
        container. Note that any SAS tokens are removed from this path.
    :ivar created_on: The date time when the document was created.
    :vartype created_on: ~datetime.datetime
    :ivar last_updated_on: The date time when the document's status was last updated.
    :vartype last_updated_on: ~datetime.datetime
    :ivar str status: Status for a document.

        * `NotStarted` - the document has not been translated yet.
        * `Running` - translation is in progress for document
        * `Succeeded` - translation succeeded for the document
        * `Failed` - the document failed to translate. Check the error property.
        * `Canceled` - the operation was canceled, the document was not translated.
        * `Canceling` - the operation is canceling, the document will not be translated.
    :ivar str translated_to: The language code of the language the document was translated to,
        if successful.
    :ivar error: Returned if there is an error with the particular document.
        Includes error code, message, target.
    :vartype error: ~azure.ai.translation.document.DocumentTranslationError
    :ivar float translation_progress: Progress of the translation if available.
        Value is between [0.0, 1.0].
    :ivar str id: Document Id.
    :ivar int characters_charged: Characters charged for the document.
    """

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
            error=DocumentTranslationError._from_generated(  # pylint: disable=protected-access
                doc_status.error
            )
            if doc_status.error
            else None,
            translation_progress=doc_status.progress,
            id=doc_status.id,
            characters_charged=doc_status.character_charged,
        )

    def __repr__(self):
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
                self.error.__repr__(),
                self.translation_progress,
                self.characters_charged,
            )[:1024]
        )


class DocumentTranslationError:
    """This contains the error code, message, and target with descriptive details on why
    a translation operation or particular document failed.

    :ivar str code: The error code. Possible high level values include:
        "InvalidRequest", "InvalidArgument", "InternalServerError", "ServiceUnavailable",
        "ResourceNotFound", "Unauthorized", "RequestRateTooHigh".
    :ivar str message: The error message associated with the failure.
    :ivar str target: The source of the error.
        For example it would be "documents" or "document id" in case of invalid document.
    """

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
                target=inner_error.target
                if inner_error.target is not None
                else error.target,
            )
        return cls(code=error.code, message=error.message, target=error.target)

    def __repr__(self):
        return "DocumentTranslationError(code={}, message={}, target={}".format(
            self.code, self.message, self.target
        )[:1024]


class DocumentTranslationFileFormat:
    """Possible file formats supported by the Document Translation service.

    :ivar file_format: Name of the format.
    :vartype file_format: str
    :ivar file_extensions: Supported file extension for this format.
    :vartype file_extensions: list[str]
    :ivar content_types: Supported Content-Types for this format.
    :vartype content_types: list[str]
    :ivar format_versions: Supported Version.
    :vartype format_versions: list[str]
    :ivar default_format_version: Default format version if none is specified.
    :vartype default_format_version: str
    """

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
        return [
            DocumentTranslationFileFormat._from_generated(file_formats) for file_formats in file_formats
        ]

    def __repr__(self):
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
