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
    TYPE_CHECKING
)
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import LROBasePolling
from ._generated._form_recognizer_client import FormRecognizerClient as FormRecognizer
from ._response_handlers import (
    prepare_receipt,
    prepare_content_result,
    prepare_form_result
)
from ._generated.models import AnalyzeOperationResult
from ._helpers import get_content_type, get_authentication_policy, error_map, POLLING_INTERVAL
from ._user_agent import USER_AGENT
from ._polling import AnalyzePolling
if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential, TokenCredential
    from ._models import RecognizedReceipt, FormPage, RecognizedForm


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
    :type credential: :class:`~azure.core.credentials.AzureKeyCredential` or
        :class:`~azure.core.credentials.TokenCredential`

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_fr_client_with_key]
            :end-before: [END create_fr_client_with_key]
            :language: python
            :dedent: 8
            :caption: Creating the FormRecognizerClient with an endpoint and API key.

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_fr_client_with_aad]
            :end-before: [END create_fr_client_with_aad]
            :language: python
            :dedent: 8
            :caption: Creating the FormRecognizerClient with a token credential.
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Union[AzureKeyCredential, TokenCredential], Any) -> None

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

    @distributed_trace
    def begin_recognize_receipts(self, receipt, **kwargs):
        # type: (Union[bytes, IO[bytes]], Any) -> LROPoller[List[RecognizedReceipt]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedReceipt`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedReceipt]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_receipts.py
                :start-after: [START recognize_receipts]
                :end-before: [END recognize_receipts]
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

        return self._client.begin_analyze_receipt_async(
            file_stream=receipt,
            content_type=content_type,
            include_text_details=include_text_content,
            cls=kwargs.pop("cls", self._receipt_callback),
            polling=LROBasePolling(timeout=polling_interval, **kwargs),
            error_map=error_map,
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace
    def begin_recognize_receipts_from_url(self, receipt_url, **kwargs):
        # type: (str, Any) -> LROPoller[List[RecognizedReceipt]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedReceipt`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedReceipt]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_receipts_from_url.py
                :start-after: [START recognize_receipts_from_url]
                :end-before: [END recognize_receipts_from_url]
                :language: python
                :dedent: 8
                :caption: Recognize US sales receipt fields from a URL.
        """

        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        continuation_token = kwargs.pop("continuation_token", None)
        include_text_content = kwargs.pop("include_text_content", False)

        return self._client.begin_analyze_receipt_async(
            file_stream={"source": receipt_url},
            include_text_details=include_text_content,
            cls=kwargs.pop("cls", self._receipt_callback),
            polling=LROBasePolling(timeout=polling_interval, **kwargs),
            error_map=error_map,
            continuation_token=continuation_token,
            **kwargs
        )

    def _content_callback(self, raw_response, _, headers):  # pylint: disable=unused-argument
        analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
        return prepare_content_result(analyze_result)

    @distributed_trace
    def begin_recognize_content(self, form, **kwargs):
        # type: (Union[bytes, IO[bytes]], Any) -> LROPoller[List[FormPage]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.FormPage`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.FormPage]]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_content.py
                :start-after: [START recognize_content]
                :end-before: [END recognize_content]
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

        return self._client.begin_analyze_layout_async(
            file_stream=form,
            content_type=content_type,
            cls=kwargs.pop("cls", self._content_callback),
            polling=LROBasePolling(timeout=polling_interval, **kwargs),
            error_map=error_map,
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace
    def begin_recognize_content_from_url(self, form_url, **kwargs):
        # type: (str, Any) -> LROPoller[List[FormPage]]
        """Extract text and layout information from a given document.
        The input document must be the location (Url) of the document to be analyzed.

        :param str form_url: The url of the form to analyze. The input must be a valid, encoded url
            of one of the supported formats: JPEG, PNG, PDF and TIFF.
        :keyword int polling_interval: Waiting time between two polls for LRO operations
            if no Retry-After header is present. Defaults to 5 seconds.
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.FormPage`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.FormPage]]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        polling_interval = kwargs.pop("polling_interval", POLLING_INTERVAL)
        continuation_token = kwargs.pop("continuation_token", None)

        return self._client.begin_analyze_layout_async(
            file_stream={"source": form_url},
            cls=kwargs.pop("cls", self._content_callback),
            polling=LROBasePolling(timeout=polling_interval, **kwargs),
            error_map=error_map,
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace
    def begin_recognize_custom_forms(self, model_id, form, **kwargs):
        # type: (str, Union[bytes, IO[bytes]], Any) -> LROPoller[List[RecognizedForm]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedForm]
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_recognize_custom_forms.py
                :start-after: [START recognize_custom_forms]
                :end-before: [END recognize_custom_forms]
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
        return self._client.begin_analyze_with_custom_model(
            file_stream=form,
            model_id=model_id,
            include_text_details=include_text_content,
            content_type=content_type,
            cls=deserialization_callback,
            polling=LROBasePolling(timeout=polling_interval, lro_algorithms=[AnalyzePolling()], **kwargs),
            error_map=error_map,
            continuation_token=continuation_token,
            **kwargs
        )

    @distributed_trace
    def begin_recognize_custom_forms_from_url(self, model_id, form_url, **kwargs):
        # type: (str, str, Any) -> LROPoller[List[RecognizedForm]]
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
        :return: An instance of an LROPoller. Call `result()` on the poller
            object to return a list[:class:`~azure.ai.formrecognizer.RecognizedForm`].
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.RecognizedForm]
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
        return self._client.begin_analyze_with_custom_model(
            file_stream={"source": form_url},
            model_id=model_id,
            include_text_details=include_text_content,
            cls=deserialization_callback,
            polling=LROBasePolling(timeout=polling_interval, lro_algorithms=[AnalyzePolling()], **kwargs),
            error_map=error_map,
            continuation_token=continuation_token,
            **kwargs
        )

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.ai.formrecognizer.FormRecognizerClient` session.
        """
        return self._client.close()

    def __enter__(self):
        # type: () -> FormRecognizerClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
