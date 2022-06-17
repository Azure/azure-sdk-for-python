# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from typing import Any, IO, Union
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.polling import AsyncLROPoller
from .._api_versions import DocumentAnalysisApiVersion
from ._form_base_client_async import FormRecognizerClientBaseAsync
from .._models import AnalyzeResult


class DocumentAnalysisClient(FormRecognizerClientBaseAsync):
    """DocumentAnalysisClient analyzes information from documents and images.
    It is the interface to use for analyzing with prebuilt models (receipts, business cards,
    invoices, identity documents), analyzing layout from documents, analyzing general
    document types, and analyzing custom documents with built models. It provides different
    methods based on inputs from a URL and inputs from a stream.

    .. note:: DocumentAnalysisClient should be used with API versions
        2021-09-30-preview and up. To use API versions <=v2.1, instantiate a FormRecognizerClient.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This is an instance of AzureKeyCredential if using an API key or a token
        credential from :mod:`azure.identity`.
    :type credential: :class:`~azure.core.credentials.AzureKeyCredential` or
        :class:`~azure.core.credentials.TokenCredential`
    :keyword api_version:
        The API version of the service to use for requests. It defaults to the latest service version.
        Setting to an older version may result in reduced feature compatibility. To use API versions
        <=v2.1, instantiate a FormRecognizerClient.
    :paramtype api_version: str or ~azure.ai.formrecognizer.DocumentAnalysisApiVersion

    .. versionadded:: 2021-09-30-preview
        The *DocumentAnalysisClient* and its client methods.

    .. admonition:: Example:

        .. literalinclude:: ../samples/v3.2-beta/async_samples/sample_authentication_async.py
            :start-after: [START create_da_client_with_key_async]
            :end-before: [END create_da_client_with_key_async]
            :language: python
            :dedent: 4
            :caption: Creating the DocumentAnalysisClient with an endpoint and API key.

        .. literalinclude:: ../samples/v3.2-beta/async_samples/sample_authentication_async.py
            :start-after: [START create_da_client_with_aad_async]
            :end-before: [END create_da_client_with_aad_async]
            :language: python
            :dedent: 4
            :caption: Creating the DocumentAnalysisClient with a token credential.
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
        **kwargs: Any
    ) -> None:
        api_version = kwargs.pop(
            "api_version", DocumentAnalysisApiVersion.V2022_06_30_PREVIEW
        )
        super().__init__(
            endpoint=endpoint,
            credential=credential,
            api_version=api_version,
            client_kind="document",
            **kwargs
        )

    def _analyze_document_callback(
        self, raw_response, _, headers
    ):  # pylint: disable=unused-argument
        analyze_operation_result = self._deserialize(
            self._generated_models.AnalyzeResultOperation, raw_response
        )
        return AnalyzeResult._from_generated(analyze_operation_result.analyze_result)

    @distributed_trace_async
    async def begin_analyze_document(
        self, model: str, document: Union[bytes, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[AnalyzeResult]:
        """Analyze field text and semantic values from a given document.

        :param str model: A unique model identifier can be passed in as a string.
            Use this to specify the custom model ID or prebuilt model ID. Prebuilt model IDs supported
            can be found here: https://aka.ms/azsdk/formrecognizer/models
        :param document: JPEG, PNG, PDF, TIFF, or BMP type file stream or bytes.
        :type document: bytes or IO[bytes]
        :keyword str pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages="1-3, 5-6"`. Separate each page number or range with a comma.
        :keyword str locale: Locale hint of the input document.
            See supported locales here: https://aka.ms/azsdk/formrecognizer/supportedlocales.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.AnalyzeResult`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.formrecognizer.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2-beta/async_samples/sample_analyze_invoices_async.py
                :start-after: [START analyze_invoices_async]
                :end-before: [END analyze_invoices_async]
                :language: python
                :dedent: 4
                :caption: Analyze an invoice. For more samples see the `samples` folder.

            .. literalinclude:: ../samples/v3.2-beta/async_samples/sample_analyze_custom_documents_async.py
                :start-after: [START analyze_custom_documents_async]
                :end-before: [END analyze_custom_documents_async]
                :language: python
                :dedent: 4
                :caption: Analyze a custom document. For more samples see the `samples` folder.
        """

        if not model:
            raise ValueError("model cannot be None or empty.")

        cls = kwargs.pop("cls", self._analyze_document_callback)
        continuation_token = kwargs.pop("continuation_token", None)

        return await self._client.begin_analyze_document(  # type: ignore
            model_id=model,
            analyze_request=document,  # type: ignore
            content_type="application/octet-stream",
            string_index_type="unicodeCodePoint",
            continuation_token=continuation_token,
            cls=cls,
            **kwargs
        )

    @distributed_trace_async
    async def begin_analyze_document_from_url(
        self, model: str, document_url: str, **kwargs: Any
    ) -> AsyncLROPoller[AnalyzeResult]:
        """Analyze field text and semantic values from a given document.
        The input must be the location (URL) of the document to be analyzed.

        :param str model: A unique model identifier can be passed in as a string.
            Use this to specify the custom model ID or prebuilt model ID. Prebuilt model IDs supported
            can be found here: https://aka.ms/azsdk/formrecognizer/models
        :param str document_url: The URL of the document to analyze. The input must be a valid, properly
            encoded  (i.e. encode special characters, such as empty spaces), and publicly accessible URL
            of one of the supported formats: JPEG, PNG, PDF, TIFF, or BMP.
        :keyword str pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages="1-3, 5-6"`. Separate each page number or range with a comma.
        :keyword str locale: Locale hint of the input document.
            See supported locales here: https://aka.ms/azsdk/formrecognizer/supportedlocales.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.AnalyzeResult`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.formrecognizer.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2-beta/async_samples/sample_analyze_receipts_from_url_async.py
                :start-after: [START analyze_receipts_from_url_async]
                :end-before: [END analyze_receipts_from_url_async]
                :language: python
                :dedent: 4
                :caption: Analyze a receipt. For more samples see the `samples` folder.
        """

        if not model:
            raise ValueError("model cannot be None or empty.")

        cls = kwargs.pop("cls", self._analyze_document_callback)
        continuation_token = kwargs.pop("continuation_token", None)

        return await self._client.begin_analyze_document(  # type: ignore
            model_id=model,
            analyze_request={"urlSource": document_url},  # type: ignore
            string_index_type="unicodeCodePoint",
            continuation_token=continuation_token,
            cls=cls,
            **kwargs
        )

    async def __aenter__(self) -> "DocumentAnalysisClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.ai.formrecognizer.aio.DocumentAnalysisClient` session."""
        await self._client.__aexit__()
