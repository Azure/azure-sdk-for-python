# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import six
from typing import (  # pylint: disable=unused-import
    Union,
    Optional,
    Any,
    List,
    Dict,
    IO,
    TYPE_CHECKING,
)
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller
from azure.core.polling.base_polling import LROBasePolling
from ._generated._form_recognizer_client import FormRecognizerClient as FormRecognizer
from ._base_client import FormRecognizerClientBase
from ._response_handlers import (
    prepare_receipt_result,
    prepare_layout_result,

)
from ._generated.models import AnalyzeOperationResult
from ._helpers import get_pipeline_response, get_content_type, POLLING_INTERVAL
if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from ._credential import FormRecognizerApiKeyCredential


class FormRecognizerClient(FormRecognizerClientBase):
    """FormRecognizerClient.

    :param str endpoint: Supported Cognitive Services endpoints (protocol and hostname,
        for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the an instance of FormRecognizerApiKeyCredential if using an API key
        or a token credential from azure.identity.
    :type credential: ~azure.ai.formrecognizer.FormRecognizerApiKeyCredential
        or ~azure.core.credentials.TokenCredential
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Union[FormRecognizerApiKeyCredential, TokenCredential], Any) -> None
        super(FormRecognizerClient, self).__init__(credential=credential, **kwargs)
        self._client = FormRecognizer(
            endpoint=endpoint, credential=credential, pipeline=self._pipeline
        )

    @distributed_trace
    def begin_extract_receipts(self, form, **kwargs):
        # type: (Union[str, IO[bytes]], Any) -> LROPoller
        """Extract field text and semantic values from a given receipt document.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png' or 'image/tiff'. Alternatively, use 'application/json'
        type to specify the location (Uri) of the document to be analyzed.

        :param form: .json, .pdf, .jpg, .png or .tiff type file stream.
        :type form: str or file stream
        :keyword bool include_text_details: Include text lines and element references in the result.
        :keyword str content_type: Media type of the body sent to the API.
        :return: LROPoller
        :rtype: ~azure.core.polling.LROPoller
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        include_text_details = kwargs.pop("include_text_details", False)
        content_type = kwargs.pop("content_type", None)

        if isinstance(form, six.string_types):
            form = {"source": form}
            content_type = content_type or "application/json"
        elif content_type is None:
            content_type = get_content_type(form)

        def callback(raw_response, _, headers):
            analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_receipt = prepare_receipt_result(analyze_result, include_text_details)
            return extracted_receipt

        return self._client.begin_analyze_receipt_async(
            file_stream=form,
            content_type=content_type,
            include_text_details=include_text_details,
            cls=callback,
            polling=LROBasePolling(timeout=POLLING_INTERVAL, **kwargs),
            **kwargs
        )

    @distributed_trace
    def begin_extract_layouts(self, form, **kwargs):
        # type: (Union[str, IO[bytes]], Any) -> LROPoller
        """Extract text and layout information from a given document.
        The input document must be of one of the supported content types - 'application/pdf',
        'image/jpeg', 'image/png' or 'image/tiff'. Alternatively, use 'application/json'
        type to specify the location (Uri) of the document to be analyzed.

        :param form: .json, .pdf, .jpg, .png or .tiff type file stream.
        :type form: str or file stream
        :keyword str content_type: Media type of the body sent to the API.
        :return: No
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        content_type = kwargs.pop("content_type", None)

        if isinstance(form, six.string_types):
            form = {"source": form}
            content_type = content_type or "application/json"
        elif content_type is None:
            content_type = get_content_type(form)

        def callback(raw_response, _, headers):
            analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_layout_result(analyze_result, include_elements=True)
            return extracted_layout

        return self._client.begin_analyze_layout_async(
            file_stream=form,
            content_type=content_type,
            cls=callback,
            polling=LROBasePolling(timeout=POLLING_INTERVAL, **kwargs),
            **kwargs
        )
