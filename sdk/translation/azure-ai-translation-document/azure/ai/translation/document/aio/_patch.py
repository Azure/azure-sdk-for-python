# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# mypy: disable-error-code="attr-defined"

import json
import datetime
from typing import Any, List, Union, overload, Optional, cast, IO, MutableMapping

from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.tracing.decorator import distributed_trace
from azure.core.async_paging import AsyncItemPaged
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential

from ._operations._patch import AsyncDocumentTranslationLROPoller, AsyncDocumentTranslationLROPollingMethod
from .._operations._patch import TranslationPolling
from ._client import DocumentTranslationClient as GeneratedDocumentTranslationClient
from ..models import (
    DocumentStatus,
    TranslationStatus,
    StartTranslationDetails,
    StorageInputType,
    TranslationGlossary,
    DocumentTranslationInput,
    DocumentTranslationFileFormat,
)
from ...document._patch import (
    get_http_logging_policy,
    get_translation_input,
    convert_datetime,
    convert_order_by,
    convert_status,
)

JSON = MutableMapping[str, Any]
POLLING_INTERVAL = 1


class DocumentTranslationClient(GeneratedDocumentTranslationClient):
    """DocumentTranslationClient.

    :param endpoint: Supported document Translation endpoint, protocol and hostname, for example:
     https://{TranslatorResourceName}.cognitiveservices.azure.com/translator. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: The API version to use for this operation. Default value is "2024-05-01".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
        **kwargs: Any
    ) -> None:
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

            .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
                :start-after: [START create_dt_client_with_key_async]
                :end-before: [END create_dt_client_with_key_async]
                :language: python
                :dedent: 4
                :caption: Creating the DocumentTranslationClient with an endpoint and API key.

            .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
                :start-after: [START create_dt_client_with_aad_async]
                :end-before: [END create_dt_client_with_aad_async]
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

    async def __aenter__(self) -> "DocumentTranslationClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.ai.translation.document.aio.DocumentTranslationClient` session."""
        await self._client.__aexit__()

    @overload
    async def begin_translation(
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
    ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]:
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
        :return: An instance of an AsyncDocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: AsyncDocumentTranslationLROPoller[~azure.core.async_paging.AsyncItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_translation(
        self, inputs: StartTranslationDetails, **kwargs: Any
    ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param inputs: A StartTranslationDetails including translation inputs. Each individual input has a single
            source URL to documents and can contain multiple TranslationTargets (one for each language)
            for the destination to write translated documents.
        :type inputs: ~azure.ai.translation.document.models.StartTranslationDetails
        :return: An instance of a AsyncDocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: AsyncDocumentTranslationLROPoller[~azure.core.async_paging.AsyncItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_translation(
        self, inputs: JSON, **kwargs: Any
    ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param inputs: JSON including translation inputs. Each individual input has a single
            source URL to documents and can contain multiple targets (one for each language)
            for the destination to write translated documents.
        :type inputs: JSON
        :return: An instance of a AsyncDocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: AsyncDocumentTranslationLROPoller[~azure.core.async_paging.AsyncItemPaged[DocumentStatus]]
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
    async def begin_translation(
        self, inputs: IO[bytes], **kwargs: Any
    ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param inputs: The translation inputs. Each individual input has a single
            source URL to documents and can contain multiple targets (one for each language)
            for the destination to write translated documents.
        :type inputs: IO[bytes]
        :return: An instance of a AsyncDocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: AsyncDocumentTranslationLROPoller[~azure.core.async_paging.AsyncItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def begin_translation(
        self, inputs: List[DocumentTranslationInput], **kwargs: Any
    ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :param inputs: A list of translation inputs. Each individual input has a single
            source URL to documents and can contain multiple TranslationTargets (one for each language)
            for the destination to write translated documents.
        :type inputs: List[~azure.ai.translation.document.DocumentTranslationInput]
        :return: An instance of a AsyncDocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: AsyncDocumentTranslationLROPoller[~azure.core.async_paging.AsyncItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_translation(  # pylint: disable=docstring-missing-param,docstring-should-be-keyword,docstring-keyword-should-match-keyword-only
        self, *args: Union[str, List[DocumentTranslationInput], IO[bytes], JSON], **kwargs: Any
    ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]:
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
        :rtype: AsyncDocumentTranslationLROPoller[~azure.core.async_paging.AsyncItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_begin_translation_async.py
                :start-after: [START begin_translation_async]
                :end-before: [END begin_translation_async]
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
            pipeline_response = await self.get_translation_status(
                continuation_token,
                cls=lambda pipeline_response, _, response_headers: pipeline_response,
            )

        callback = kwargs.pop("cls", deserialization_callback)
        return cast(
            AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]],
            await super()._begin_translation(
                body=inputs,
                polling=AsyncDocumentTranslationLROPollingMethod(
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
    ) -> AsyncItemPaged[TranslationStatus]:
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
        :rtype: ~azure.core.async_paging.AsyncItemPaged[TranslationStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_list_translations_async.py
                :start-after: [START list_translations_async]
                :end-before: [END list_translations_async]
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
            AsyncItemPaged[TranslationStatus],
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
    ) -> AsyncItemPaged[DocumentStatus]:
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
        :rtype: ~azure.core.async_paging.AsyncItemPaged[DocumentStatus]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_check_document_statuses_async.py
                :start-after: [START list_document_statuses_async]
                :end-before: [END list_document_statuses_async]
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
            AsyncItemPaged[DocumentStatus],
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

    @distributed_trace_async
    async def get_supported_glossary_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]:
        """Get the list of the glossary formats supported by the Document Translation service.

        :return: A list of supported glossary formats.
        :rtype: List[DocumentTranslationFileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return (await super()._get_supported_formats(type="glossary", **kwargs)).value

    @distributed_trace_async
    async def get_supported_document_formats(self, **kwargs: Any) -> List[DocumentTranslationFileFormat]:
        """Get the list of the document formats supported by the Document Translation service.

        :return: A list of supported document formats for translation.
        :rtype: List[DocumentTranslationFileFormat]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        return (await super()._get_supported_formats(type="document", **kwargs)).value


__all__: List[str] = [
    "DocumentTranslationClient",
    "AsyncDocumentTranslationLROPoller",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
