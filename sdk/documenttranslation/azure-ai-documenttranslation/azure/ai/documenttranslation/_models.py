# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import
from typing import Any, List
from ._generated.models import (
    BatchRequest as _BatchRequest,
    SourceInput as _SourceInput,
    DocumentFilter as _DocumentFilter,
    TargetInput as _TargetInput,
    Glossary as _Glossary
)


class TranslationGlossary(object):  # pylint: disable=useless-object-inheritance
    """Glossary / translation memory to apply to the translation.

    :param str glossary_url: Required. Location of the glossary file. This should be a SAS URL to
        the glossary file in the storage blob container. If the translation language pair is
        not present in the glossary, it will not be applied.
    :param str file_format: Required. Format of the glossary file. To see supported formats,
        call the :func:`~DocumentTranslationClient.get_glossary_formats()` client method.
    :keyword str format_version: File format version. If not specified, the service will
        use the default_version for the file format returned from the
        :func:`~DocumentTranslationClient.get_glossary_formats()` client method.
    :keyword str storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.
    """

    def __init__(
            self,
            glossary_url,
            file_format,
            **kwargs
    ):
        # type: (str, str, **Any) -> None
        self.glossary_url = glossary_url
        self.file_format = file_format
        self.format_version = kwargs.get("format_version", None)
        self.storage_source = kwargs.get("storage_source", None)

    def _to_generated(self):
        return _Glossary(
                glossary_url=self.glossary_url,
                format=self.file_format,
                version=self.format_version,
                storage_source=self.storage_source
            )

    @staticmethod
    def _to_generated_list(glossaries):
        return [glossary._to_generated() for glossary in glossaries]  # pylint: disable=protected-access


class TranslationTarget(object):  # pylint: disable=useless-object-inheritance
    """Destination for the finished translated documents.

    :param str target_url: Required. The target location for your translated documents.
        This should be a container SAS URL to your target container.
    :param str language_code: Required. Target Language Code. This is the language
        you want your documents to be translated to. See supported languages here:
        https://docs.microsoft.com/azure/cognitive-services/translator/language-support#translate
    :keyword str category_id: Category / custom model ID for using custom translation.
    :keyword glossaries: Glossaries to apply to translation.
    :paramtype glossaries: list[~azure.ai.documenttranslation.TranslationGlossary]
    :keyword str storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.
    """

    def __init__(
        self,
        target_url,
        language_code,
        **kwargs
    ):
        # type: (str, str, **Any) -> None
        self.target_url = target_url
        self.language_code = language_code
        self.category_id = kwargs.get("category_id", None)
        self.glossaries = kwargs.get("glossaries", None)
        self.storage_source = kwargs.get("storage_source", None)

    def _to_generated(self):
        return _TargetInput(
            target_url=self.target_url,
            category=self.category_id,
            language=self.language_code,
            storage_source=self.storage_source,
            glossaries=TranslationGlossary._to_generated_list(self.glossaries)  # pylint: disable=protected-access
            if self.glossaries else None
        )

    @staticmethod
    def _to_generated_list(targets):
        return [target._to_generated() for target in targets]  # pylint: disable=protected-access


class DocumentTranslationInput(object):  # pylint: disable=useless-object-inheritance
    # pylint: disable=C0301
    """Input for translation. This requires that you have your source document or
    documents in an Azure Blob Storage container. Provide a SAS URL to the source file or
    source container containing the documents for translation. The source document(s) are
    translated and written to the location provided by the TranslationTargets.

    :param str source_url: Required. Location of the folder / container or single file with your
        documents.
    :param targets: Required. Location of the destination for the output. This is a list of
        TranslationTargets. Note that a TranslationTarget is required for each language code specified.
    :type targets: list[~azure.ai.documenttranslation.TranslationTarget]
    :keyword str source_language_code: Language code for the source documents.
        If none is specified, the source language will be auto-detected for each document.
    :keyword str prefix: A case-sensitive prefix string to filter documents in the source path for
        translation. For example, when using a Azure storage blob Uri, use the prefix to restrict
        sub folders for translation.
    :keyword str suffix: A case-sensitive suffix string to filter documents in the source path for
        translation. This is most often use for file extensions.
    :keyword storage_type: Storage type of the input documents source string. Possible values
        include: "Folder", "File".
    :paramtype storage_type: str or ~azure.ai.documenttranslation.StorageInputType
    :keyword str storage_source: Storage Source. Default value: "AzureBlob".
        Currently only "AzureBlob" is supported.
    """

    def __init__(
        self,
        source_url,
        targets,
        **kwargs
    ):
        # type: (str, List[TranslationTarget], **Any) -> None
        self.source_url = source_url
        self.targets = targets
        self.source_language_code = kwargs.get("source_language_code", None)
        self.storage_type = kwargs.get("storage_type", None)
        self.storage_source = kwargs.get("storage_source", None)
        self.prefix = kwargs.get("prefix", None)
        self.suffix = kwargs.get("suffix", None)

    def _to_generated(self):
        return _BatchRequest(
            source=_SourceInput(
                source_url=self.source_url,
                filter=_DocumentFilter(
                    prefix=self.prefix,
                    suffix=self.suffix
                ),
                language=self.source_language_code,
                storage_source=self.storage_source
            ),
            targets=TranslationTarget._to_generated_list(self.targets),  # pylint: disable=protected-access
            storage_type=self.storage_type
        )

    @staticmethod
    def _to_generated_list(batch_document_inputs):
        return [
            batch_document_input._to_generated()  # pylint: disable=protected-access
            for batch_document_input in batch_document_inputs
        ]


class JobStatusResult(object):  # pylint: disable=useless-object-inheritance, too-many-instance-attributes
    """Status information about the translation job.

    :ivar str id: Id of the job.
    :ivar created_on: The date time when the translation job was created.
    :vartype created_on: ~datetime.datetime
    :ivar last_updated_on: The date time when the translation job's status was last updated.
    :vartype last_updated_on: ~datetime.datetime
    :ivar str status: Status for a job.

        * `NotStarted` - the job has not begun yet.
        * `Running` - translation is in progress.
        * `Succeeded` - at least one document translated successfully within the job.
        * `Cancelled` - the job was cancelled.
        * `Cancelling` - the job is being cancelled.
        * `ValidationFailed` - the input failed validation. E.g. there was insufficient permissions on blob containers.
        * `Failed` - all the documents within the job failed. To understand the reason for each document failure,
         call the :func:`~DocumentTranslationClient.list_all_document_statuses()` client method and inspect the error.

    :ivar error: Returned if there is an error with the translation job.
        Includes error code, message, target.
    :vartype error: ~azure.ai.documenttranslation.DocumentTranslationError
    :ivar int documents_total_count: Number of translations to be made on documents in the job.
    :ivar int documents_failed_count: Number of documents that failed translation.
        More details can be found by calling the :func:`~DocumentTranslationClient.list_all_document_statuses`
        client method.
    :ivar int documents_succeeded_count: Number of successful translations on documents.
    :ivar int documents_in_progress_count: Number of translations on documents in progress.
    :ivar int documents_not_yet_started_count: Number of documents that have not yet started being translated.
    :ivar int documents_cancelled_count: Number of documents that were cancelled for translation.
    :ivar int total_characters_charged: Total characters charged across all documents within the job.
    """

    def __init__(
        self,
        **kwargs
    ):
        # type: (**Any) -> None
        self.id = kwargs['id']
        self.created_on = kwargs['created_on']
        self.last_updated_on = kwargs['last_updated_on']
        self.status = kwargs.get('status', None)
        self.error = kwargs.get("error", None)
        self.documents_total_count = kwargs.get('documents_total_count', None)
        self.documents_failed_count = kwargs.get('documents_failed_count', None)
        self.documents_succeeded_count = kwargs.get('documents_succeeded_count', None)
        self.documents_in_progress_count = kwargs.get('documents_in_progress_count', None)
        self.documents_not_yet_started_count = kwargs.get('documents_not_yet_started_count', None)
        self.documents_cancelled_count = kwargs.get('documents_cancelled_count', None)
        self.total_characters_charged = kwargs.get('total_characters_charged', None)

    @classmethod
    def _from_generated(cls, batch_status_details):
        return cls(
            id=batch_status_details.id,
            created_on=batch_status_details.created_date_time_utc,
            last_updated_on=batch_status_details.last_action_date_time_utc,
            status=batch_status_details.status,
            error=DocumentTranslationError._from_generated(batch_status_details.error)  # pylint: disable=protected-access
            if batch_status_details.error else None,
            documents_total_count=batch_status_details.summary.total,
            documents_failed_count=batch_status_details.summary.failed,
            documents_succeeded_count=batch_status_details.summary.success,
            documents_in_progress_count=batch_status_details.summary.in_progress,
            documents_not_yet_started_count=batch_status_details.summary.not_yet_started,
            documents_cancelled_count=batch_status_details.summary.cancelled,
            total_characters_charged=batch_status_details.summary.total_character_charged
        )


class DocumentStatusResult(object):  # pylint: disable=useless-object-inheritance, R0903
    """Status information about a particular document within a translation job.

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
        * `Cancelled` - the job was cancelled, the document was not translated.
        * `Cancelling` - the job is cancelling, the document will not be translated.
    :ivar str translate_to: The language code of the language the document was translated to,
        if successful.
    :ivar error: Returned if there is an error with the particular document.
        Includes error code, message, target.
    :vartype error: ~azure.ai.documenttranslation.DocumentTranslationError
    :ivar float translation_progress: Progress of the translation if available.
        Value is between [0.0, 1.0].
    :ivar str id: Document Id.
    :ivar int characters_charged: Characters charged for the document.
    """

    def __init__(
        self,
        **kwargs
    ):
        # type: (**Any) -> None
        self.translated_document_url = kwargs.get('translated_document_url', None)
        self.created_on = kwargs['created_on']
        self.last_updated_on = kwargs['last_updated_on']
        self.status = kwargs['status']
        self.translate_to = kwargs['translate_to']
        self.error = kwargs.get('error', None)
        self.translation_progress = kwargs.get('translation_progress', None)
        self.id = kwargs.get('id', None)
        self.characters_charged = kwargs.get('characters_charged', None)


    @classmethod
    def _from_generated(cls, doc_status):
        return cls(
            translated_document_url=doc_status.path,
            created_on=doc_status.created_date_time_utc,
            last_updated_on=doc_status.last_action_date_time_utc,
            status=doc_status.status,
            translate_to=doc_status.to,
            error=DocumentTranslationError._from_generated(doc_status.error) if doc_status.error else None,  # pylint: disable=protected-access
            translation_progress=doc_status.progress,
            id=doc_status.id,
            characters_charged=doc_status.character_charged
        )


class DocumentTranslationError(object):  # pylint: disable=useless-object-inheritance, R0903
    """This contains the error code, message, and target with descriptive details on why
    a translation job or particular document failed.

    :ivar str code: The error code. Possible high level values include:
        "InvalidRequest", "InvalidArgument", "InternalServerError", "ServiceUnavailable",
        "ResourceNotFound", "Unauthorized", "RequestRateTooHigh".
    :ivar str message: The error message associated with the failure.
    :ivar str target: The source of the error.
        For example it would be "documents" or "document id" in case of invalid document.
    """

    def __init__(
        self,
        **kwargs
    ):
        # type: (**Any) -> None
        self.code = kwargs.get('code', None)
        self.message = kwargs.get('message', None)
        self.target = kwargs.get('target', None)

    @classmethod
    def _from_generated(cls, error):
        if error.inner_error:
            inner_error = error.inner_error
            return cls(
                code=inner_error.code,
                message=inner_error.message,
                target=inner_error.target if inner_error.target is not None else error.target
            )
        return cls(
            code=error.code,
            message=error.message,
            target=error.target
        )


class FileFormat(object):  # pylint: disable=useless-object-inheritance, R0903
    """Possible file formats supported by the Document Translation service.

    :ivar file_format: Name of the format.
    :vartype file_format: str
    :ivar file_extensions: Supported file extension for this format.
    :vartype file_extensions: list[str]
    :ivar content_types: Supported Content-Types for this format.
    :vartype content_types: list[str]
    :ivar format_versions: Supported Version.
    :vartype format_versions: list[str]
    """

    def __init__(
        self,
        **kwargs
    ):
        # type: (**Any) -> None
        self.file_format = kwargs.get('file_format', None)
        self.file_extensions = kwargs.get('file_extensions', None)
        self.content_types = kwargs.get('content_types', None)
        self.format_versions = kwargs.get('format_versions', None)

    @classmethod
    def _from_generated(cls, file_format):
        return cls(
            file_format=file_format.format,
            file_extensions=file_format.file_extensions,
            content_types=file_format.content_types,
            format_versions=file_format.versions
        )

    @staticmethod
    def _from_generated_list(file_formats):
        return [FileFormat._from_generated(file_formats) for file_formats in file_formats]
