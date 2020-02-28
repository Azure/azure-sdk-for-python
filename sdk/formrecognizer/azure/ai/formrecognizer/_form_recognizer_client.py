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
    TYPE_CHECKING,
)

from ._generated.models import ErrorResponseException
from ._generated._form_recognizer_client import FormRecognizerClient as FormRecognizer
from ._base_client import FormRecognizerClientBase
from ._response_handlers import (
    get_pipeline_response,
    prepare_receipt_result,
    prepare_layout_result
)
from azure.core.exceptions import HttpResponseError
from azure.core.polling import LROPoller
from ._generated.models import AnalyzeOperationResult
from azure.mgmt.core.polling.arm_polling import ARMPolling

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class FormRecognizerClient(FormRecognizerClientBase):


    def __init__(self, endpoint, credential, **kwargs):
        super(FormRecognizerClient, self).__init__(credential=credential, **kwargs)
        self._client = FormRecognizer(
            endpoint=endpoint, credential=credential, pipeline=self._pipeline
        )

    def begin_extract_receipt(self, form, content_type, **kwargs):
        include_text_details = kwargs.pop("include_text_details", False)
        if isinstance(form, six.string_types):
            form = {"source": form}

        try:
            response = self._client.analyze_receipt_async(
                file_stream=form,
                content_type=content_type,
                include_text_details=include_text_details,
                cls=get_pipeline_response
            )
        except ErrorResponseException as err:
            raise HttpResponseError(err)

        def callback(raw_response):
            analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_receipt = prepare_receipt_result(analyze_result, include_text_details)
            return extracted_receipt

        poll_method = ARMPolling()
        poller = LROPoller(self._client._client, response, callback, poll_method)
        return poller

    def begin_extract_layout(self, form, content_type, **kwargs):
        include_text_details = kwargs.pop("include_text_details", False)
        # if isinstance(form, six.string_types):
        #     form = {"source": form}
        #
        # try:
        #     response = self._client.analyze_layout_async(
        #         file_stream=form,
        #         content_type=content_type,
        #         include_text_details=include_text_details,
        #         cls=get_pipeline_response
        #     )
        # except ErrorResponseException as err:
        #     raise HttpResponseError(err)

        import json

        json_file_path = "../result_layout.json"

        with open(json_file_path, 'r') as j:
            result = json.loads(j.read())
        analyze_result = self._client._deserialize(AnalyzeOperationResult, result)
        extracted_layout = prepare_layout_result(analyze_result, include_text_details)
        return extracted_layout
        # def callback(raw_response):
        #     analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
        #     extracted_layout = prepare_layout_result(analyze_result, include_text_details)
        #     return extracted_layout
        #
        # poll_method = ARMPolling()
        # poller = LROPoller(self._client._client, response, callback, poll_method)
        # return poller
