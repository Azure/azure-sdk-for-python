# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# mypy: disable-error-code="attr-defined"

import json
import datetime
from typing import Any, List, Union, overload, Optional, cast, Tuple, TypeVar
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
    StartTranslationDetails,
    StorageInputType,
    TranslationGlossary,
)
from ...document._patch import (
    get_http_logging_policy,
    get_translation_input,
)

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
        credential: Union[AzureKeyCredential, AsyncTokenCredential],  # pylint: disable=used-before-assignment
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
        :return: An instance of a AsyncDocumentTranslationLROPoller. Call `result()` on the poller
            object to return a pageable of DocumentStatus. A DocumentStatus will be
            returned for each translation on a document.
        :rtype: AsyncDocumentTranslationLROPoller[~azure.core.async_paging.AsyncItemPaged[DocumentStatus]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def begin_translation(  # pylint: disable=docstring-missing-param
        self, *args: Union[str, StartTranslationDetails], **kwargs: Any
    ) -> AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]]:
        """Begin translating the document(s) in your source container to your target container
        in the given language. There are two ways to call this method:

        1) To perform translation on documents from a single source container to a single target container, pass the
        `source_url`, `target_url`, and `target_language` parameters including any optional keyword arguments.

        2) To pass multiple inputs for translation (multiple sources or targets), pass the `inputs` parameter
        as a list of :class:`~azure.ai.translation.document.DocumentTranslationInput`.

        For supported languages and document formats, see the service documentation:
        https://docs.microsoft.com/azure/cognitive-services/translator/document-translation/overview

        :return: An instance of an AsyncDocumentTranslationLROPoller. Call `result()` on the poller
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
            return super().list_document_statuses(translation_status["id"])

        polling_interval = kwargs.pop(
            "polling_interval",
            super()._config.polling_interval,  # pylint: disable=protected-access
        )

        pipeline_response = None
        if continuation_token:
            pipeline_response = await super().get_translation_status(
                continuation_token,
                cls=lambda pipeline_response, _, response_headers: pipeline_response,
            )

        callback = kwargs.pop("cls", deserialization_callback)
        return cast(
            AsyncDocumentTranslationLROPoller[AsyncItemPaged[DocumentStatus]],
            await super().begin_start_translation(
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
