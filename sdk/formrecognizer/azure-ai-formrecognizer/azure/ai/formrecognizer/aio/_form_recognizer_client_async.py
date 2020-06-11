# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from typing import (
    Any,
    IO,
    Union,
    List,
    TYPE_CHECKING,
)
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.polling import AsyncLROPoller
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from .._generated.aio._form_recognizer_client_async import FormRecognizerClient as FormRecognizer
from .._response_handlers import (
    prepare_receipt,
    prepare_content_result,
    prepare_form_result
)
from .._generated.models import AnalyzeOperationResult
from .._helpers import get_content_type, get_authentication_policy, error_map, POLLING_INTERVAL
from .._user_agent import USER_AGENT
from .._polling import AnalyzePolling
from .._models import RecognizedReceipt, FormPage, RecognizedForm
if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential
    from azure.core.credentials_async import AsyncTokenCredential


class FormRecognizerClient(object):
    """FormRecognizerClient extracts information from forms and images into structured data.
    It is the interface to use for analyzing receipts, recognizing content/layout from
    forms, and analyzing custom forms from trained models. It provides different methods
    based on inputs from a URL and inputs from a stream.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This is an instance of AzureKeyCredential if using an API key or a token
        credential from :mod:`azure.identity`.
    :type credential: :class:`~azure.core.credentials.AzureKeyCredential`
        or :class:`~azure.core.credentials_async.AsyncTokenCredential`

    .. admonition:: Example:

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START create_fr_client_with_key_async]
            :end-before: [END create_fr_client_with_key_async]
            :language: python
            :dedent: 8
            :caption: Creating the FormRecognizerClient with an endpoint and API key.

        .. literalinclude:: ../samples/async_samples/sample_authentication_async.py
            :start-after: [START create_fr_client_with_aad_async]
            :end-before: [END create_fr_client_with_aad_async]
            :language: python
            :dedent: 8
            :caption: Creating the FormRecognizerClient with a token credential.
    """

    def __init__(
            self,
            endpoint: str,
            credential: Union["AzureKeyCredential", "AsyncTokenCredential"],
            **kwargs: Any
    ) -> None:

        authentication_policy = get_authentication_policy(credential)
        self._client = FormRecognizer(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            sdk_moniker=USER_AGENT,
            authentication_policy=authentication_policy,
            **kwargs
        )

    def _receipt_callback(self, raw_response, _, headers):  # pylint: disable=unused-argument
        analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
        return prepare_receipt(analyze_result)

    @distributed_trace_async
    async def begin_recognize_receipts(
            self,
            receipt: Union[bytes, IO[bytes]],
            **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedReceipt]]:
        """Extract field text and semantic values from a given US sales receipt.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png' or 'image/tiff'.

        :param receipt: JPEG, PNG, PDF and TIFF type file stream or bytes.
            Currently only supports US sales receipts.
        :type receipt: bytes or IO[bytes]
        :keyword bool include_text_content:
            Whether or not to include text elements such as lines and words in addition to form fields.
        :keyword str content_type: Media type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedReceipt`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedReceipt]]
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
        continuation_token = kwargs.pop("continuation_token", None)
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError("Call begin_recognize_receipts_from_url() to analyze a receipt from a url.")

        include_text_content = kwargs.pop("include_text_content", False)

        if content_type is None:
            content_type = get_content_type(receipt)

        return await self._client.begin_analyze_receipt_async(  # type: ignore
            file_stream=receipt,
            content_type=content_type,
            include_text_details=include_text_content,
            cls=kwargs.pop("cls", self._receipt_callback),
            polling=AsyncLROBasePolling(
                timeout=polling_interval,
                **kwargs
            ),
            error_map=error_map,
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace_async
    async def begin_recognize_receipts_from_url(
            self,
            receipt_url: str,
            **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedReceipt]]:
        """Extract field text and semantic values from a given US sales receipt.
        The input document must be the location (Url) of the receipt to be analyzed.

        :param str receipt_url: The url of the receipt to analyze. The input must be a valid, encoded url
            of one of the supported formats: JPEG, PNG, PDF and TIFF. Currently only supports
            US sales receipts.
        :keyword bool include_text_content:
            Whether or not to include text elements such as lines and words in addition to form fields.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedReceipt`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedReceipt]]
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
        continuation_token = kwargs.pop("continuation_token", None)
        include_text_content = kwargs.pop("include_text_content", False)

        return await self._client.begin_analyze_receipt_async(  # type: ignore
            file_stream={"source": receipt_url},
            include_text_details=include_text_content,
            cls=kwargs.pop("cls", self._receipt_callback),
            polling=AsyncLROBasePolling(
                timeout=polling_interval,
                **kwargs
            ),
            error_map=error_map,
            continuation_token=continuation_token,
            **kwargs
        )

    def _content_callback(self, raw_response, _, headers):  # pylint: disable=unused-argument
        analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
        return prepare_content_result(analyze_result)

    @distributed_trace_async
    async def begin_recognize_content(
            self,
            form: Union[bytes, IO[bytes]],
            **kwargs: Any
    ) -> AsyncLROPoller[List[FormPage]]:
        """Extract text and content/layout information from a given document.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png' or 'image/tiff'.

        :param form: JPEG, PNG, PDF and TIFF type file stream or bytes.
        :type form: bytes or IO[bytes]
        :keyword str content_type: Media type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.FormPage`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.FormPage]]
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
        continuation_token = kwargs.pop("continuation_token", None)
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError("Call begin_recognize_content_from_url() to analyze a document from a url.")

        if content_type is None:
            content_type = get_content_type(form)

        return await self._client.begin_analyze_layout_async(  # type: ignore
            file_stream=form,
            content_type=content_type,
            cls=kwargs.pop("cls", self._content_callback),
            polling=AsyncLROBasePolling(
                timeout=polling_interval,
                **kwargs
            ),
            error_map=error_map,
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace_async
    async def begin_recognize_content_from_url(self, form_url: str, **kwargs: Any) -> AsyncLROPoller[List[FormPage]]:
        """Extract text and layout information from a given document.
        The input document must be the location (Url) of the document to be analyzed.

        :param str form_url: The url of the form to analyze. The input must be a valid, encoded url
            of one of the supported formats: JPEG, PNG, PDF and TIFF.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.FormPage`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.FormPage]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        continuation_token = kwargs.pop("continuation_token", None)
        return await self._client.begin_analyze_layout_async(  # type: ignore
            file_stream={"source": form_url},
            cls=kwargs.pop("cls", self._content_callback),
            polling=AsyncLROBasePolling(
                timeout=polling_interval,
                **kwargs
            ),
            error_map=error_map,
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace_async
    async def begin_recognize_custom_forms(
            self,
            model_id: str,
            form: Union[bytes, IO[bytes]],
            **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Analyze a custom form with a model trained with or without labels. The form
        to analyze should be of the same type as the forms that were used to train the model.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png' or 'image/tiff'.

        :param str model_id: Custom model identifier.
        :param form: JPEG, PNG, PDF and TIFF type file stream or bytes.
        :type form: bytes or IO[bytes]
        :keyword bool include_text_content:
            Whether or not to include text elements such as lines and words in addition to form fields.
        :keyword str content_type: Media type of the body sent to the API. Content-type is
            auto-detected, but can be overridden by passing this keyword argument. For options,
            see :class:`~azure.ai.formrecognizer.FormContentType`.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_recognize_custom_forms_async.py
                :start-after: [START recognize_custom_forms_async]
                :end-before: [END recognize_custom_forms_async]
                :language: python
                :dedent: 8
                :caption: Recognize fields and values from a custom form.
        """

        if not model_id:
            raise ValueError("model_id cannot be None or empty.")

        cls = kwargs.pop("cls", None)
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        continuation_token = kwargs.pop("continuation_token", None)
        content_type = kwargs.pop("content_type", None)
        if content_type == "application/json":
            raise TypeError("Call begin_recognize_custom_forms_from_url() to analyze a document from a url.")

        include_text_content = kwargs.pop("include_text_content", False)

        if content_type is None:
            content_type = get_content_type(form)

        def analyze_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
            return prepare_form_result(analyze_result, model_id)

        deserialization_callback = cls if cls else analyze_callback
        return await self._client.begin_analyze_with_custom_model(  # type: ignore
            file_stream=form,
            model_id=model_id,
            include_text_details=include_text_content,
            content_type=content_type,
            cls=deserialization_callback,
            polling=AsyncLROBasePolling(
                timeout=polling_interval,
                lro_algorithms=[AnalyzePolling()],
                **kwargs
            ),
            error_map=error_map,
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace_async
    async def begin_recognize_custom_forms_from_url(
            self,
            model_id: str,
            form_url: str,
            **kwargs: Any
    ) -> AsyncLROPoller[List[RecognizedForm]]:
        """Analyze a custom form with a model trained with or without labels. The form
        to analyze should be of the same type as the forms that were used to train the model.
        The input document must be the location (Url) of the document to be analyzed.

        :param str model_id: Custom model identifier.
        :param str form_url: The url of the form to analyze. The input must be a valid, encoded url
            of one of the supported formats: JPEG, PNG, PDF and TIFF.
        :keyword bool include_text_content:
            Whether or not to include text elements such as lines and words in addition to form fields.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an AsyncLROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.AsyncLROPoller[list[~azure.ai.formrecognizer.RecognizedForm]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        if not model_id:
            raise ValueError("model_id cannot be None or empty.")

        cls = kwargs.pop("cls", None)
        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        continuation_token = kwargs.pop("continuation_token", None)
        include_text_content = kwargs.pop("include_text_content", False)

        def analyze_callback(raw_response, _, headers):  # pylint: disable=unused-argument
            analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
            return prepare_form_result(analyze_result, model_id)

        deserialization_callback = cls if cls else analyze_callback
        return await self._client.begin_analyze_with_custom_model(  # type: ignore
            file_stream={"source": form_url},
            model_id=model_id,
            include_text_details=include_text_content,
            cls=deserialization_callback,
            polling=AsyncLROBasePolling(
                timeout=polling_interval,
                lro_algorithms=[AnalyzePolling()],
                **kwargs
            ),
            error_map=error_map,
            continuation_token=continuation_token,
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
