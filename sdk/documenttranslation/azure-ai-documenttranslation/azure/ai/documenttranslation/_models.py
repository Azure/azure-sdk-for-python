# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Any, List


class StorageSourceInput(object):
    """Source of the input documents.

    :param source_url: Required. Location of the folder / container or single file with your
     documents.
    :type source_url: str
    :param str language: Language code
     If none is specified, we will perform auto detect on the document.
    :keyword str prefix: A case-sensitive prefix string to filter documents in the source path for
     translation. For example, when using a Azure storage blob Uri, use the prefix to restrict sub folders for
     translation.
    :keyword str suffix: A case-sensitive suffix string to filter documents in the source path for
     translation. This is most often use for file extensions.
    :ivar storage_source: Storage Source. Default value: "AzureBlob".
    :vartype storage_source: str
    """

    def __init__(
        self,
        source_url,
        language,
        **kwargs
    ):
        # type: (str, str, **Any) -> None
        self.storage_source = "AzureBlob"
        self.source_url = source_url
        self.language = language
        self.prefix = kwargs.get("prefix", None)
        self.suffix = kwargs.get("suffix", None)


class TranslationGlossary(object):
    """Glossary / translation memory for the request.

    :param glossary_url: Required. Location of the glossary.
     We will use the file extension to extract the formatting if the format parameter is not
     supplied.
     If the translation language pair is not present in the glossary, it will not be applied.
    :type glossary_url: str
    :keyword str format: Format.
    :keyword str version: Version.
    :ivar storage_source: Storage Source. Default value: "AzureBlob".
    :vartype storage_source: str
    """

    def __init__(
            self,
            glossary_url,
            **kwargs
    ):
        # type: (str, **Any) -> None
        self.storage_source = "AzureBlob"
        self.glossary_url = glossary_url
        self.format = kwargs.get("format", None)
        self.version = kwargs.get("version", None)


class StorageTargetInput(object):
    """Destination for the finished translated documents.

    :param target_url: Required. Location of the folder / container with your documents.
    :type target_url: str
    :param language: Required. Target Language.
    :type language: str
    :keyword str custom_model_id: Category / custom system for translation request.
    :keyword glossaries: List of TranslationGlossary.
    :paramtype glossaries: Union[list[str], list[~azure.ai.documenttranslation.TranslationGlossary]]
    :ivar storage_source: Storage Source. Default value: "AzureBlob".
    :vartype storage_source: str
    """

    def __init__(
        self,
        target_url,
        language,
        **kwargs
    ):
        # type: (str, str, **Any) -> None
        self.storage_source = "AzureBlob"
        self.target_url = target_url
        self.language = language
        self.custom_model_id = kwargs.get("custom_model_id", None)
        self.glossaries = kwargs.get("glossaries", None)


class BatchDocumentInput(object):
    """Definition for the input batch translation request.

    :param source: Required. Source of the input documents.
    :type source: ~azure.ai.documenttranslation.StorageSourceInput
    :param targets: Required. Location of the destination for the output.
    :type targets: list[StorageTargetInput]
    :keyword storage_type: Storage type of the input documents source string. Possible values
     include: "Folder", "File".
    :paramtype storage_type: str or ~azure.ai.documenttranslation.StorageInputType
    """

    def __init__(
        self,
        source,
        targets,
        **kwargs
    ):
        # type: (StorageSourceInput, List[StorageTargetInput], **Any) -> None
        self.source = source
        self.targets = targets
        self.storage_type = kwargs.get("storage_type", None)


class BatchStatusDetail(object):
    """Job status response.

    :ivar id: Required. Id of the operation.
    :vartype id: str
    :ivar created_on: Required. Operation created date time.
    :vartype created_on: ~datetime.datetime
    :ivar last_updated_on: Required. Date time in which the operation's status has been
     updated.
    :vartype last_updated_on: ~datetime.datetime
    :ivar status: Required. List of possible statuses for job or document. Possible values
     include: "NotStarted", "Running", "Succeeded", "Failed", "Cancelled", "Cancelling",
     "ValidationFailed".
    :vartype status: str
    :ivar summary: Required.
    :vartype summary: ~azure.ai.documenttranslation.StatusSummary
    :ivar error: This contains an outer error with error code, message, details, target and an
     inner error with more descriptive details.
    :vartype error: ~azure.ai.documenttranslation.DocumentTranslationError
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
        self.summary = kwargs['summary']
        self.error = kwargs.get("error", None)


class DocumentStatusDetail(object):
    """DocumentStatusDetail.

    :ivar url: Required. Location of the document or folder.
    :vartype url: str
    :ivar created_on: Required. Operation created date time.
    :vartype created_on: ~datetime.datetime
    :ivar last_updated_on: Required. Date time in which the operation's status has been
     updated.
    :vartype last_updated_on: ~datetime.datetime
    :ivar status: Required. List of possible statuses for job or document. Possible values
     include: "NotStarted", "Running", "Succeeded", "Failed", "Cancelled", "Cancelling",
     "ValidationFailed".
    :vartype status: str
    :ivar translate_to: Required. To language.
    :vartype translate_to: str
    :ivar error: This contains an outer error with error code, message, details, target and an
     inner error with more descriptive details.
    :vartype error: ~azure.ai.documenttranslation.DocumentTranslationError
    :ivar progress: Progress of the translation if available.
    :vartype progress: float
    :ivar id: Document Id.
    :vartype id: str
    :ivar int characters_charged: Character charged by the API.
    """

    def __init__(
        self,
        **kwargs
    ):
        # type: (**Any) -> None
        self.url = kwargs['url']
        self.created_on = kwargs['created_on']
        self.last_updated_on = kwargs['last_updated_on']
        self.status = kwargs['status']
        self.translate_to = kwargs['translate_to']
        self.error = kwargs.get('error', None)
        self.progress = kwargs.get('progress', None)
        self.id = kwargs.get('id', None)
        self.characters_charged = kwargs.get('characters_charged', None)


class DocumentTranslationError(object):
    """This contains an outer error with error code, message, details, target and an
    inner error with more descriptive details.

    :ivar code: Enums containing high level error codes. Possible values include:
     "InvalidRequest", "InvalidArgument", "InternalServerError", "ServiceUnavailable",
     "ResourceNotFound", "Unauthorized", "RequestRateTooHigh".
    :vartype code: str
    :ivar message: Gets high level error message.
    :vartype message: str
    :ivar target: Gets the source of the error.
     For example it would be "documents" or "document id" in case of invalid document.
    :vartype target: str
    """

    def __init__(
        self,
        **kwargs
    ):
        # type: (**Any) -> None
        self.code = kwargs.get('code', None)
        self.message = None
        self.target = None


class StatusSummary(object):
    """StatusSummary.

    :ivar total: Total count.
    :vartype total: int
    :ivar failed: Failed count.
    :vartype failed: int
    :ivar succeeded: Number of Success.
    :vartype succeeded: int
    :ivar in_progress: Number of in progress.
    :vartype in_progress: int
    :ivar not_yet_started: Count of not yet started.
    :vartype not_yet_started: int
    :ivar cancelled: Number of cancelled.
    :vartype cancelled: int
    :ivar int total_characters_charged: Required. Total characters charged by the API.
    """

    def __init__(
        self,
        **kwargs
    ):
        # type: (**Any) -> None
        self.total = kwargs.get('total', None)
        self.failed = kwargs.get('failed', None)
        self.succeeded = kwargs.get('succeeded', None)
        self.in_progress = kwargs.get('in_progress', None)
        self.not_yet_started = kwargs.get('not_yet_started', None)
        self.cancelled = kwargs.get('cancelled', None)
        self.total_characters_charged = kwargs.get('total_characters_charged', None)


class FileFormat(object):
    """FileFormat.

    :ivar format: Name of the format.
    :vartype format: str
    :ivar file_extensions: Supported file extension for this format.
    :vartype file_extensions: list[str]
    :ivar content_types: Supported Content-Types for this format.
    :vartype content_types: list[str]
    :ivar versions: Supported Version.
    :vartype versions: list[str]
    """

    def __init__(
        self,
        **kwargs
    ):
        # type: (**Any) -> None
        self.format = kwargs.get('format', None)
        self.file_extensions = kwargs.get('file_extensions', None)
        self.content_types = kwargs.get('content_types', None)
        self.versions = kwargs.get('versions', None)
