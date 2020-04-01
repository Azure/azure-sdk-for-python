# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from typing import (  # pylint: disable=unused-import
    Any,
    IO,
    TYPE_CHECKING,
)
import six
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import LROBasePolling
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from ._generated._form_recognizer_client import FormRecognizerClient as FormRecognizer
from ._response_handlers import (
    prepare_receipt_result,
    prepare_layout_result,
)
from ._generated.models import AnalyzeOperationResult
from ._helpers import get_content_type, POLLING_INTERVAL, COGNITIVE_KEY_HEADER
from ._user_agent import USER_AGENT
if TYPE_CHECKING:
    from azure.core.credentials import AzureKeyCredential


class FormRecognizerClient(object):
    """FormRecognizerClient.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This is an instance of AzureKeyCredential if using an API key.
    :type credential: ~azure.core.credentials.AzureKeyCredential
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, AzureKeyCredential, Any) -> None
        self._client = FormRecognizer(
            endpoint=endpoint,
            credential=credential,
            sdk_moniker=USER_AGENT,
            authentication_policy=AzureKeyCredentialPolicy(credential, COGNITIVE_KEY_HEADER),
            **kwargs
        )

    def _receipt_callback(self, raw_response, _, headers):  # pylint: disable=unused-argument
        analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
        return prepare_receipt_result(analyze_result)

    @distributed_trace
    def begin_extract_receipts(self, stream, **kwargs):
        # type: (IO[bytes], Any) -> LROPoller
        """Extract field text and semantic values from a given receipt document.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png' or 'image/tiff'.

        :param stream: .pdf, .jpg, .png or .tiff type file stream.
        :type stream: stream
        :keyword bool include_text_details: Include text lines and element references in the result.
        :keyword str content_type: Media type of the body sent to the API.
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.ExtractedReceipt]]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if isinstance(stream, six.string_types):
            raise TypeError("Call begin_extract_receipts_from_url() to analyze a receipt from a url.")

        include_text_details = kwargs.pop("include_text_details", False)
        content_type = kwargs.pop("content_type", None)
        if content_type is None:
            content_type = get_content_type(stream)

        return self._client.begin_analyze_receipt_async(
            file_stream=stream,
            content_type=content_type,
            include_text_details=include_text_details,
            cls=kwargs.pop("cls", self._receipt_callback),
            polling=LROBasePolling(timeout=POLLING_INTERVAL, **kwargs),
            **kwargs
        )

    @distributed_trace
    def begin_extract_receipts_from_url(self, url, **kwargs):
        # type: (str, Any) -> LROPoller
        """Extract field text and semantic values from a given receipt document.
        The input document must be the location (Url) of the document to be analyzed.

        :param url: The url of the receipt.
        :type url: str
        :keyword bool include_text_details: Include text lines and element references in the result.
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.ExtractedReceipt]]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if not isinstance(url, six.string_types):
            raise TypeError("Call begin_extract_receipts() to analyze a receipt from a stream.")

        include_text_details = kwargs.pop("include_text_details", False)

        return self._client.begin_analyze_receipt_async(
            file_stream={"source": url},
            include_text_details=include_text_details,
            cls=kwargs.pop("cls", self._receipt_callback),
            polling=LROBasePolling(timeout=POLLING_INTERVAL, **kwargs),
            **kwargs
        )

    def _layout_callback(self, raw_response, _, headers):  # pylint: disable=unused-argument
        analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
        return prepare_layout_result(analyze_result)

    @distributed_trace
    def begin_extract_layouts(self, stream, **kwargs):
        # type: (IO[bytes], Any) -> LROPoller
        """Extract text and layout information from a given document.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png' or 'image/tiff'.

        :param stream: .pdf, .jpg, .png or .tiff type file stream.
        :type stream: stream
        :keyword str content_type: Media type of the body sent to the API.
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.ExtractedLayoutPage]]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if isinstance(stream, six.string_types):
            raise TypeError("Call begin_extract_layouts_from_url() to analyze a document from a url.")

        content_type = kwargs.pop("content_type", None)
        if content_type is None:
            content_type = get_content_type(stream)

        return self._client.begin_analyze_layout_async(
            file_stream=stream,
            content_type=content_type,
            cls=kwargs.pop("cls", self._layout_callback),
            polling=LROBasePolling(timeout=POLLING_INTERVAL, **kwargs),
            **kwargs
        )

    @distributed_trace
    def begin_extract_layouts_from_url(self, url, **kwargs):
        # type: (str, Any) -> LROPoller
        """Extract text and layout information from a given document.
        The input document must be the location (Url) of the document to be analyzed.

        :param url: The url of the document.
        :type url: str
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller[list[~azure.ai.formrecognizer.ExtractedLayoutPage]]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        if not isinstance(url, six.string_types):
            raise TypeError("Call begin_extract_layouts() to analyze a document from a stream.")

        return self._client.begin_analyze_layout_async(
            file_stream={"source": url},
            cls=kwargs.pop("cls", self._layout_callback),
            polling=LROBasePolling(timeout=POLLING_INTERVAL, **kwargs),
            **kwargs
        )

    def close(self):
        # type: () -> None
        """Close the :class:`~azure.ai.formrecognizer.FormRecognizer` session.
        """
        return self._client.close()

    def __enter__(self):
        # type: () -> FormRecognizerClient
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)  # pylint:disable=no-member
