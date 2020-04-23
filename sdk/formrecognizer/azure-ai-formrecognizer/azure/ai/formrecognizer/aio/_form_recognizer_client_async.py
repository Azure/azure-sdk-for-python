# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from typing import (
    Any,
    List,
    IO,
    Union,
    TYPE_CHECKING,
)
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from ._form_training_client_async import FormTrainingClient
from .._generated.aio._form_recognizer_client_async import FormRecognizerClient as FormRecognizer
from .._response_handlers import (
    prepare_us_receipt,
    prepare_content_result,
    prepare_form_result
)
from .._generated.models import AnalyzeOperationResult
from .._helpers import get_content_type, error_map, POLLING_INTERVAL, COGNITIVE_KEY_HEADER
from .._user_agent import USER_AGENT
from .._polling import AnalyzePolling
if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential
    from .._models import (
        USReceipt,
        FormPage,
        RecognizedForm
    )


class FormRecognizerClient(object):
    """FormRecognizerClient extracts information from forms and images into structured data.
    It is the interface to use for analyzing receipts, recognizing content/layout from
    forms, and analyzing custom forms from trained models. It provides different methods
    based on inputs from a URL and inputs from a stream.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This is an instance of AzureKeyCredential if using an API key.
    :type credential: ~azure.core.credentials.AzureKeyCredential

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_get_bounding_boxes_async.py
            :start-after: [START create_form_recognizer_client_async]
            :end-before: [END create_form_recognizer_client_async]
            :language: python
            :dedent: 8
            :caption: Creating the FormRecognizerClient with an endpoint and API key.
    """

    def __init__(
            self,
            endpoint: str,
            credential: "AzureKeyCredential",
            **kwargs: Any
    ) -> None:
        self._endpoint = endpoint
        self._credential = credential
        self._client = FormRecognizer(
            endpoint=self._endpoint,
            credential=self._credential,
            sdk_moniker=USER_AGENT,
            authentication_policy=AzureKeyCredentialPolicy(credential, COGNITIVE_KEY_HEADER),
            **kwargs
        )

    def _receipt_callback(self, raw_response, _, headers):  # pylint: disable=unused-argument
        analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
        return prepare_us_receipt(analyze_result)

    @distributed_trace_async
    async def recognize_receipts(
            self,
            stream: Union[bytes, IO[bytes]],
            **kwargs: Any
    ) -> List["USReceipt"]:
        """Extract field text and semantic values from a given US sales receipt.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png' or 'image/tiff'.

        :param stream: .pdf, .jpg, .png or .tiff type file stream.
            Currently only supports US sales receipts.
        :type stream: stream
        :keyword bool include_text_content:
            Whether or not to include text elements such as lines and words in addition to form fields.
        :keyword str content_type: Media type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :return: A list of USReceipt.
        :rtype: list[~azure.ai.formrecognizer.USReceipt]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_recognize_receipts_async.py
                :start-after: [START recognize_receipts_async]
                :end-before: [END recognize_receipts_async]
                :language: python
                :dedent: 8
                :caption: Recognize US sales receipt fields.
        """

        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError("Call begin_recognize_receipts_from_url() to analyze a receipt from a url.")

        include_text_content = kwargs.pop("include_text_content", False)

        if content_type is None:
            content_type = get_content_type(stream)

        return await self._client.analyze_receipt_async(  # type: ignore
            file_stream=stream,
            content_type=content_type,
            include_text_details=include_text_content,
            cls=kwargs.pop("cls", self._receipt_callback),
            polling=AsyncLROBasePolling(timeout=polling_interval, **kwargs),
            error_map=error_map,
            **kwargs
        )

    @distributed_trace_async
    async def recognize_receipts_from_url(
            self,
            url: str,
            **kwargs: Any
    ) -> List["USReceipt"]:
        """Extract field text and semantic values from a given US sales receipt.
        The input document must be the location (Url) of the receipt to be analyzed.

        :param url: The url of the receipt. Currently only supports US sales receipts.
        :type url: str
        :keyword bool include_text_content:
            Whether or not to include text elements such as lines and words in addition to form fields.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :return: A list of USReceipt.
        :rtype: list[~azure.ai.formrecognizer.USReceipt]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_recognize_receipts_from_url_async.py
                :start-after: [START recognize_receipts_from_url_async]
                :end-before: [END recognize_receipts_from_url_async]
                :language: python
                :dedent: 8
                :caption: Recognize US sales receipt fields from a URL.
        """

        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        include_text_content = kwargs.pop("include_text_content", False)

        return await self._client.analyze_receipt_async(  # type: ignore
            file_stream={"source": url},
            include_text_details=include_text_content,
            cls=kwargs.pop("cls", self._receipt_callback),
            polling=AsyncLROBasePolling(timeout=polling_interval, **kwargs),
            error_map=error_map,
            **kwargs
        )

    def _content_callback(self, raw_response, _, headers):  # pylint: disable=unused-argument
        analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
        return prepare_content_result(analyze_result)

    @distributed_trace_async
    async def recognize_content(self, stream: Union[bytes, IO[bytes]], **kwargs: Any) -> List["FormPage"]:
        """Extract text and content/layout information from a given document.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png' or 'image/tiff'.

        :param stream: .pdf, .jpg, .png or .tiff type file stream.
        :type stream: stream
        :keyword str content_type: Media type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :return: A list of FormPage.
        :rtype: list[~azure.ai.formrecognizer.FormPage]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_recognize_content_async.py
                :start-after: [START recognize_content_async]
                :end-before: [END recognize_content_async]
                :language: python
                :dedent: 8
                :caption: Recognize text and content/layout information from a form.
        """

        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError("Call begin_recognize_content_from_url() to analyze a document from a url.")

        if content_type is None:
            content_type = get_content_type(stream)

        return await self._client.analyze_layout_async(  # type: ignore
            file_stream=stream,
            content_type=content_type,
            cls=kwargs.pop("cls", self._content_callback),
            polling=AsyncLROBasePolling(timeout=polling_interval, **kwargs),
            error_map=error_map,
            **kwargs
        )

    @distributed_trace_async
    async def recognize_content_from_url(self, url: str, **kwargs: Any) -> List["FormPage"]:
        """Extract text and layout information from a given document.
        The input document must be the location (Url) of the document to be analyzed.

        :param url: The url of the document.
        :type url: str
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :return: A list of FormPage.
        :rtype: list[~azure.ai.formrecognizer.FormPage]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        return await self._client.analyze_layout_async(  # type: ignore
            file_stream={"source": url},
            cls=kwargs.pop("cls", self._content_callback),
            polling=AsyncLROBasePolling(timeout=polling_interval, **kwargs),
            error_map=error_map,
            **kwargs
        )

    @distributed_trace_async
    async def recognize_custom_forms(
            self,
            model_id: str,
            stream: Union[bytes, IO[bytes]],
            **kwargs: Any
    ) -> List["RecognizedForm"]:
        """Analyze a custom form with a model trained with or without labels. The form
        to analyze should be of the same type as the forms that were used to train the model.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png' or 'image/tiff'.

        :param str model_id: Custom model identifier.
        :param stream: .pdf, .jpg, .png or .tiff type file stream.
        :type stream: stream
        :keyword bool include_text_content:
            Whether or not to include text elements such as lines and words in addition to form fields.
        :keyword str content_type: Media type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :return: A list of RecognizedForm.
        :rtype: list[~azure.ai.formrecognizer.RecognizedForm]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_recognize_custom_forms_async.py
                :start-after: [START recognize_custom_forms_async]
                :end-before: [END recognize_custom_forms_async]
                :language: python
                :dedent: 8
                :caption: Recognize fields and values from a custom form.
        """

        cls = kwargs.pop("cls", None)
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError("Call begin_recognize_custom_forms_from_url() to analyze a document from a url.")

        include_text_content = kwargs.pop("include_text_content", False)

        if content_type is None:
            content_type = get_content_type(stream)

        def analyze_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
            return prepare_form_result(analyze_result, model_id)

        deserialization_callback = cls if cls else analyze_callback
        return await self._client.analyze_with_custom_model(  # type: ignore
            file_stream=stream,
            model_id=model_id,
            include_text_details=include_text_content,
            content_type=content_type,
            cls=deserialization_callback,
            polling=AsyncLROBasePolling(timeout=polling_interval, lro_algorithms=[AnalyzePolling()], **kwargs),
            error_map=error_map,
            **kwargs
        )

    @distributed_trace_async
    async def recognize_custom_forms_from_url(
            self,
            model_id: str,
            url: str,
            **kwargs: Any
    ) -> List["RecognizedForm"]:
        """Analyze a custom form with a model trained with or without labels. The form
        to analyze should be of the same type as the forms that were used to train the model.
        The input document must be the location (Url) of the document to be analyzed.

        :param str model_id: Custom model identifier.
        :param url: The url of the document.
        :type url: str
        :keyword bool include_text_content:
            Whether or not to include text elements such as lines and words in addition to form fields.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :return: A list of RecognizedForm.
        :rtype: list[~azure.ai.formrecognizer.RecognizedForm]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        cls = kwargs.pop("cls", None)
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        include_text_content = kwargs.pop("include_text_content", False)

        def analyze_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
            return prepare_form_result(analyze_result, model_id)

        deserialization_callback = cls if cls else analyze_callback
        return await self._client.analyze_with_custom_model(  # type: ignore
            file_stream={"source": url},
            model_id=model_id,
            include_text_details=include_text_content,
            cls=deserialization_callback,
            polling=AsyncLROBasePolling(timeout=polling_interval, lro_algorithms=[AnalyzePolling()], **kwargs),
            error_map=error_map,
            **kwargs
        )

    def get_form_training_client(self, **kwargs: Any) -> FormTrainingClient:
        """Get an instance of a FormTrainingClient from FormRecognizerClient.

        :rtype: ~azure.ai.formrecognizer.aio.FormTrainingClient
        :return: A FormTrainingClient
        """
        return FormTrainingClient(
            endpoint=self._endpoint,
            credential=self._credential,
            **kwargs
        )

    async def __aenter__(self) -> "FormRecognizerClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close the :class:`~azure.ai.formrecognizer.aio.FormRecognizerClient` session.
        """
        await self._client.__aexit__()
