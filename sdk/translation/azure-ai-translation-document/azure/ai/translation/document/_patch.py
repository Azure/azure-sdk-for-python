# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# mypy: disable-error-code="attr-defined"

from typing import Any, List, Union, overload, Optional, cast, Mapping, IO, MutableMapping
from enum import Enum
import json
import datetime
from io import IOBase
from azure.core import CaseInsensitiveEnumMeta
from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline.policies import HttpLoggingPolicy

from ._operations._patch import DocumentTranslationLROPoller, DocumentTranslationLROPollingMethod, TranslationPolling
from ._client import DocumentTranslationClient as GeneratedDocumentTranslationClient
from .models import (
    DocumentBatch,
    SourceInput,
    TranslationTarget,
    DocumentFilter,
    TranslationGlossary,
    DocumentStatus,
    StartTranslationDetails,
    StorageInputType,
    DocumentTranslationFileFormat,
    TranslationStatus,
    DocumentTranslationError,
    DocumentTranslationInput,
)
from .models._patch import convert_status

JSON = MutableMapping[str, Any]

POLLING_INTERVAL = 1


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


class DocumentTranslationApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Document Translation API versions supported by this package"""

    #: This is the default version
    V2024_05_01 = "2024-05-01"


def get_translation_input(args, kwargs, continuation_token):
    if continuation_token:
        return None

    inputs = kwargs.pop("inputs", None)
    if not inputs:
        try:
            inputs = args[0]
        except IndexError:
            inputs = args

    if isinstance(inputs, StartTranslationDetails):
        request = inputs
    elif isinstance(inputs, (Mapping, IOBase, bytes)):
        request = inputs
    # backcompatibility
    elif len(inputs) > 0 and isinstance(inputs[0], DocumentTranslationInput):
        # pylint: disable=protected-access
        request = StartTranslationDetails(inputs=[input._to_generated() for input in inputs])
    else:
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

            request = StartTranslationDetails(
                inputs=[
                    DocumentBatch(
                        source=SourceInput(
                            source_url=source_url,
                            filter=DocumentFilter(prefix=prefix, suffix=suffix),
                            language=source_language,
                        ),
                        targets=[
                            TranslationTarget(
                                target_url=target_url,
                                language=target_language,
                                glossaries=glossaries,
                                category_id=category_id,
                            )
                        ],
                        storage_type=storage_type,
                    )
                ]
            )
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


class DocumentTranslationClient(GeneratedDocumentTranslationClient):
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
        super().__init__(
            endpoint=self._endpoint,
            credential=credential,
            http_logging_policy=kwargs.pop("http_logging_policy", get_http_logging_policy()),
            polling_interval=polling_interval,
            **kwargs
        )

    def __enter__(self) -> "DocumentTranslationClient":
        self._client.__enter__()
        return self

    def __exit__(self, *args) -> None:
        self._client.__exit__(*args)

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
        in the given language.

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
        self, inputs: StartTranslationDetails, **kwargs: Any
    ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param inputs: A StartTranslationDetails including translation inputs. Each individual input has a single
            source URL to documents and can contain multiple TranslationTargets (one for each language)
            for the destination to write translated documents.
        :type inputs: ~azure.ai.translation.document.models.StartTranslationDetails
        :return: An instance of a DocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: DocumentTranslationLROPoller[~azure.core.paging.ItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def begin_translation(self, inputs: JSON, **kwargs: Any) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param inputs: JSON including translation inputs. Each individual input has a single
            source URL to documents and can contain multiple targets (one for each language)
            for the destination to write translated documents.
        :type inputs: JSON
        :return: An instance of a DocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: DocumentTranslationLROPoller[~azure.core.paging.ItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                body = {
                    "inputs": [
                        {
                            "source": {
                                "sourceUrl": "str",
                                "filter": {
                                    "prefix": "str",
                                    "suffix": "str"
                                },
                                "language": "str",
                                "storageSource": "str"
                            },
                            "targets": [
                                {
                                    "language": "str",
                                    "targetUrl": "str",
                                    "category": "str",
                                    "glossaries": [
                                        {
                                            "format": "str",
                                            "glossaryUrl": "str",
                                            "storageSource": "str",
                                            "version": "str"
                                        }
                                    ],
                                    "storageSource": "str"
                                }
                            ],
                            "storageType": "str"
                        }
                    ]
                }
        """

    @overload
    def begin_translation(
        self, inputs: IO[bytes], **kwargs: Any
    ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param inputs: The translation inputs. Each individual input has a single
            source URL to documents and can contain multiple targets (one for each language)
            for the destination to write translated documents.
        :type inputs: IO[bytes]
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
        in the given language.

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
    def begin_translation(  # pylint: disable=docstring-missing-param,docstring-should-be-keyword,docstring-keyword-should-match-keyword-only
        self, *args: Union[str, List[DocumentTranslationInput], StartTranslationDetails, IO[bytes], JSON], **kwargs: Any
    ) -> DocumentTranslationLROPoller[ItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param inputs: The translation inputs. Each individual input has a single
            source URL to documents and can contain multiple targets (one for each language)
            for the destination to write translated documents.
        :type inputs: List[~azure.ai.translation.document.DocumentTranslationInput] or
            IO[bytes] or JSON or ~azure.ai.translation.document.models.StartTranslationDetails
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
            self._config.polling_interval,
        )

        pipeline_response = None
        if continuation_token:
            pipeline_response = self.get_translation_status(
                continuation_token,
                cls=lambda pipeline_response, _, response_headers: pipeline_response,
            )

        callback = kwargs.pop("cls", deserialization_callback)
        return cast(
            DocumentTranslationLROPoller[ItemPaged[DocumentStatus]],
            super()._begin_translation(
                body=inputs,
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
    def cancel_translation(self, translation_id: str, **kwargs: Any) -> None:  # type: ignore[override]
        """Cancel a currently processing or queued translation operation.
        A translation will not be canceled if it is already completed, failed, or canceling.
        All documents that have completed translation will not be canceled and will be charged.
        If possible, all pending documents will be canceled.
        :param str translation_id: The translation operation ID.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError or ~azure.core.exceptions.ResourceNotFoundError:
        """

        super().cancel_translation(translation_id, **kwargs)

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

        return cast(
            ItemPaged[TranslationStatus],
            super().list_translation_statuses(
                created_date_time_utc_start=created_after,
                created_date_time_utc_end=created_before,
                translation_ids=translation_ids,
                orderby=order_by,
                statuses=statuses,
                top=top,
                skip=skip,
                **kwargs
            ),
        )

    @distributed_trace
    def list_document_statuses(  # type: ignore[override]
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

        return cast(
            ItemPaged[DocumentStatus],
            super().list_document_statuses(
                translation_id=translation_id,
                created_date_time_utc_start=created_after,
                created_date_time_utc_end=created_before,
                document_ids=document_ids,
                orderby=order_by,
                statuses=statuses,
                top=top,
                skip=skip,
                **kwargs
            ),
        )

    @distributed_trace
    def get_supported_glossary_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]:
        """Get the list of the glossary formats supported by the Document Translation service.

        :return: A list of supported glossary formats.
        :rtype: List[DocumentTranslationFileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return super()._get_supported_formats(type="glossary", **kwargs).value

    @distributed_trace
    def get_supported_document_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]:
        """Get the list of the document formats supported by the Document Translation service.

        :return: A list of supported document formats for translation.
        :rtype: List[DocumentTranslationFileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return super()._get_supported_formats(type="document", **kwargs).value


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
