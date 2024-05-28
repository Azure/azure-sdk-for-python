# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# mypy: disable-error-code="attr-defined"
# pylint: disable=too-many-lines

from typing import Any, List, Union, overload, Optional, cast
from enum import Enum
import json

from azure.core import CaseInsensitiveEnumMeta
from azure.core.tracing.decorator import distributed_trace
from azure.core.paging import ItemPaged
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline.policies import HttpLoggingPolicy

from ._operations._patch import DocumentTranslationLROPoller, DocumentTranslationLROPollingMethod, TranslationPolling
from ._client import DocumentTranslationClient as GeneratedDocumentTranslationClient
from .models import (
    BatchRequest,
    SourceInput,
    TargetInput,
    DocumentFilter,
    Glossary,
    DocumentStatus,
    StartTranslationDetails,
    StorageInputType,
)

POLLING_INTERVAL = 1


class DocumentTranslationApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Document Translation API versions supported by this package"""

    #: This is the default version
    V2024_05_01 = "2024-05-01"


def get_translation_input(args, kwargs, continuation_token):

    inputs = kwargs.pop("inputs", None)
    if not inputs:
        inputs = args[0]
    if isinstance(inputs, StartTranslationDetails):
        request = inputs if not continuation_token else None
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

            request = StartTranslationDetails(inputs=[
                BatchRequest(
                    source=SourceInput(
                        source_url=source_url,
                        filter=DocumentFilter(prefix=prefix, suffix=suffix),
                        language=source_language,
                    ),
                    targets=[
                        TargetInput(
                            target_url=target_url,
                            language=target_language,
                            glossaries=glossaries,
                            category=category_id,
                        )
                    ],
                    storage_type=storage_type,
                )
            ])
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
        glossaries: Optional[List[Glossary]] = None,
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
        self, inputs: StartTranslationDetails, **kwargs: Any
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
        self, *args: Union[str, StartTranslationDetails], **kwargs: Any
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
            return self.get_documents_status(translation_status["id"])

        polling_interval = kwargs.pop(
            "polling_interval",
            self._config.polling_interval,  # pylint: disable=protected-access
        )

        pipeline_response = None
        if continuation_token:
            pipeline_response = super().get_translation_status(
                continuation_token,
                cls=lambda pipeline_response, _, response_headers: pipeline_response,
            )

        callback = kwargs.pop("cls", deserialization_callback)
        return cast(
            DocumentTranslationLROPoller[ItemPaged[DocumentStatus]],
            super().begin_start_translation(
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


__all__: List[str] = [
    "DocumentTranslationClient",
    "DocumentTranslationLROPoller",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
