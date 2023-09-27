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
    """DocumentAnalysisClient analyzes information from documents and images, and classifies documents.
    It is the interface to use for analyzing with prebuilt models (receipts, business cards,
    invoices, identity documents, among others), analyzing layout from documents, analyzing general
    document types, and analyzing custom documents with built models (to see a full list of models
    supported by the service, see: https://aka.ms/azsdk/formrecognizer/models). It provides different
    methods based on inputs from a URL and inputs from a stream.

    .. note:: DocumentAnalysisClient should be used with API versions
        2022-08-31 and up. To use API versions <=v2.1, instantiate a FormRecognizerClient.

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

    .. versionadded:: 2022-08-31
        The *DocumentAnalysisClient* and its client methods.

    .. admonition:: Example:

        .. literalinclude:: ../samples/v3.2_and_later/async_samples/sample_authentication_async.py
            :start-after: [START create_da_client_with_key_async]
            :end-before: [END create_da_client_with_key_async]
            :language: python
            :dedent: 4
            :caption: Creating the DocumentAnalysisClient with an endpoint and API key.

        .. literalinclude:: ../samples/v3.2_and_later/async_samples/sample_authentication_async.py
            :start-after: [START create_da_client_with_aad_async]
            :end-before: [END create_da_client_with_aad_async]
            :language: python
            :dedent: 4
            :caption: Creating the DocumentAnalysisClient with a token credential.
    """

    def __init__(
        self, endpoint: str, credential: Union[AzureKeyCredential, AsyncTokenCredential], **kwargs: Any
    ) -> None:
        api_version = kwargs.pop("api_version", DocumentAnalysisApiVersion.V2023_07_31)
        super().__init__(
            endpoint=endpoint, credential=credential, api_version=api_version, client_kind="document", **kwargs
        )

    def _analyze_document_callback(self, raw_response, _, headers):  # pylint: disable=unused-argument
        analyze_operation_result = self._deserialize(self._generated_models.AnalyzeResultOperation, raw_response)
        return AnalyzeResult._from_generated(analyze_operation_result.analyze_result)

    @distributed_trace_async
    async def begin_analyze_document(
        self, model_id: str, document: Union[bytes, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[AnalyzeResult]:
        """Analyze field text and semantic values from a given document.

        :param str model_id: A unique model identifier can be passed in as a string.
            Use this to specify the custom model ID or prebuilt model ID. Prebuilt model IDs supported
            can be found here: https://aka.ms/azsdk/formrecognizer/models
        :param document: File stream or bytes. For service supported file types,
            see: https://aka.ms/azsdk/formrecognizer/supportedfiles.
        :type document: bytes or IO[bytes]
        :keyword str pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages="1-3, 5-6"`. Separate each page number or range with a comma.
        :keyword str locale: Locale hint of the input document.
            See supported locales here: https://aka.ms/azsdk/formrecognizer/supportedlocales.
        :keyword features: Document analysis features to enable.
        :paramtype features: list[str]
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.AnalyzeResult`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.formrecognizer.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: 2023-07-31
            The *features* keyword argument.

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2_and_later/async_samples/sample_analyze_invoices_async.py
                :start-after: [START analyze_invoices_async]
                :end-before: [END analyze_invoices_async]
                :language: python
                :dedent: 4
                :caption: Analyze an invoice. For more samples see the `samples` folder.

            .. literalinclude:: ../samples/v3.2_and_later/async_samples/sample_analyze_custom_documents_async.py
                :start-after: [START analyze_custom_documents_async]
                :end-before: [END analyze_custom_documents_async]
                :language: python
                :dedent: 4
                :caption: Analyze a custom document. For more samples see the `samples` folder.
        """

        cls = kwargs.pop("cls", self._analyze_document_callback)
        continuation_token = kwargs.pop("continuation_token", None)

        if continuation_token is None and not model_id:
            raise ValueError("model_id cannot be None or empty.")

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            _client_op_path = self._client
            if kwargs.pop("features", None):
                raise ValueError(
                    "Keyword argument 'features' is only available for API version V2023_07_31 and later."
                )
        else:
            _client_op_path = self._client.document_models
        return await _client_op_path.begin_analyze_document(  # type: ignore
            model_id=model_id,
            analyze_request=document,  # type: ignore
            content_type="application/octet-stream",
            string_index_type="unicodeCodePoint",
            continuation_token=continuation_token,
            cls=cls,
            **kwargs
        )

    @distributed_trace_async
    async def begin_analyze_document_from_url(
        self, model_id: str, document_url: str, **kwargs: Any
    ) -> AsyncLROPoller[AnalyzeResult]:
        """Analyze field text and semantic values from a given document.
        The input must be the location (URL) of the document to be analyzed.

        :param str model_id: A unique model identifier can be passed in as a string.
            Use this to specify the custom model ID or prebuilt model ID. Prebuilt model IDs supported
            can be found here: https://aka.ms/azsdk/formrecognizer/models
        :param str document_url: The URL of the document to analyze. The input must be a valid, properly
            encoded  (i.e. encode special characters, such as empty spaces), and publicly accessible URL.
            For service supported file types, see: https://aka.ms/azsdk/formrecognizer/supportedfiles.
        :keyword str pages: Custom page numbers for multi-page documents(PDF/TIFF). Input the page numbers
            and/or ranges of pages you want to get in the result. For a range of pages, use a hyphen, like
            `pages="1-3, 5-6"`. Separate each page number or range with a comma.
        :keyword str locale: Locale hint of the input document.
            See supported locales here: https://aka.ms/azsdk/formrecognizer/supportedlocales.
        :keyword features: Document analysis features to enable.
        :paramtype features: list[str]
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.AnalyzeResult`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.formrecognizer.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: 2023-07-31
            The *features* keyword argument.

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2_and_later/async_samples/sample_analyze_receipts_from_url_async.py
                :start-after: [START analyze_receipts_from_url_async]
                :end-before: [END analyze_receipts_from_url_async]
                :language: python
                :dedent: 4
                :caption: Analyze a receipt. For more samples see the `samples` folder.
        """

        cls = kwargs.pop("cls", self._analyze_document_callback)
        continuation_token = kwargs.pop("continuation_token", None)

        if continuation_token is None:
            if not model_id:
                raise ValueError("model_id cannot be None or empty.")

            if not isinstance(document_url, str):
                raise ValueError(
                    "'document_url' needs to be of type 'str'. "
                    "Please see `begin_analyze_document()` to pass a byte stream."
                )

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            _client_op_path = self._client
            if kwargs.pop("features", None):
                raise ValueError(
                    "Keyword argument 'features' is only available for API version V2023_07_31 and later."
                )
        else:
            _client_op_path = self._client.document_models
        return await _client_op_path.begin_analyze_document(  # type: ignore
            model_id=model_id,
            analyze_request={"urlSource": document_url},  # type: ignore
            string_index_type="unicodeCodePoint",
            continuation_token=continuation_token,
            cls=cls,
            **kwargs
        )

    @distributed_trace_async
    async def begin_classify_document(
        self, classifier_id: str, document: Union[bytes, IO[bytes]], **kwargs: Any
    ) -> AsyncLROPoller[AnalyzeResult]:
        """Classify a document using a document classifier. For more information on how to build
        a custom classifier model, see https://aka.ms/azsdk/formrecognizer/buildclassifiermodel.

        :param str classifier_id: A unique document classifier identifier can be passed in as a string.
        :param document: File stream or bytes. For service supported file types, see:
            https://aka.ms/azsdk/formrecognizer/supportedfiles.
        :type document: bytes or IO[bytes]
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.AnalyzeResult`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.formrecognizer.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: 2023-07-31
            The *begin_classify_document* client method.

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2_and_later/async_samples/sample_classify_document_async.py
                :start-after: [START classify_document_async]
                :end-before: [END classify_document_async]
                :language: python
                :dedent: 4
                :caption: Classify a document. For more samples see the `samples` folder.
        """

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            raise ValueError("Method 'begin_classify_document()' is only available for API version "
                             "V2023_07_31 and later")

        cls = kwargs.pop("cls", self._analyze_document_callback)
        continuation_token = kwargs.pop("continuation_token", None)

        if continuation_token is None and not classifier_id:
            raise ValueError("classifier_id cannot be None or empty.")

        return await self._client.document_classifiers.begin_classify_document(  # type: ignore
            classifier_id=classifier_id,
            content_type="application/octet-stream",
            string_index_type="unicodeCodePoint",
            classify_request=document,  # type: ignore
            continuation_token=continuation_token,
            cls=cls,
            **kwargs
        )

    @distributed_trace_async
    async def begin_classify_document_from_url(
        self, classifier_id: str, document_url: str, **kwargs: Any
    ) -> AsyncLROPoller[AnalyzeResult]:
        """Classify a given document with a document classifier. For more information on how to build
        a custom classifier model, see https://aka.ms/azsdk/formrecognizer/buildclassifiermodel.
        The input must be the location (URL) of the document to be classified.

        :param str classifier_id: A unique document classifier identifier can be passed in as a string.
        :param str document_url: The URL of the document to classify. The input must be a valid, properly
            encoded  (i.e. encode special characters, such as empty spaces), and publicly accessible URL
            of one of the supported formats: https://aka.ms/azsdk/formrecognizer/supportedfiles.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a :class:`~azure.ai.formrecognizer.AnalyzeResult`.
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.ai.formrecognizer.AnalyzeResult]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. versionadded:: 2023-07-31
            The *begin_classify_document_from_url* client method.

        .. admonition:: Example:

            .. literalinclude:: ../samples/v3.2_and_later/async_samples/sample_classify_document_from_url_async.py
                :start-after: [START classify_document_from_url_async]
                :end-before: [END classify_document_from_url_async]
                :language: python
                :dedent: 4
                :caption: Classify a document. For more samples see the `samples` folder.
        """

        if self._api_version == DocumentAnalysisApiVersion.V2022_08_31:
            raise ValueError("Method 'begin_classify_document_from_url()' is only available for API version "
                             "V2023_07_31 and later")
        cls = kwargs.pop("cls", self._analyze_document_callback)
        continuation_token = kwargs.pop("continuation_token", None)

        if continuation_token is None:
            if not classifier_id:
                raise ValueError("classifier_id cannot be None or empty.")

            if not isinstance(document_url, str):
                raise ValueError(
                    "'document_url' needs to be of type 'str'. "
                    "Please see `begin_classify_document()` to pass a byte stream."
                )

        return await self._client.document_classifiers.begin_classify_document(  # type: ignore
            classifier_id=classifier_id,
            string_index_type="unicodeCodePoint",
            classify_request={"urlSource": document_url},  # type: ignore
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
