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

from ._generated._form_recognizer_client import FormRecognizerClient as FormRecognizer
from ._generated.models import TrainRequest, TrainSourceFilter
from ._base_client import FormRecognizerClientBase
from ._response_handlers import (
    prepare_receipt_result,
    prepare_layout_result,
    prepare_unlabeled_result,
    prepare_labeled_result,
    get_content_type
)
from azure.core.polling import LROPoller
from azure.core.exceptions import HttpResponseError
from ._generated.models import AnalyzeOperationResult, Model
from azure.core.polling.base_polling import LROBasePolling
from ._models import (
    ModelInfo,
    ModelsSummary,
    CustomModel,
    CustomLabeledModel,
    get_pipeline_response
)
if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class FormRecognizerClient(FormRecognizerClientBase):


    def __init__(self, endpoint, credential, **kwargs):
        super(FormRecognizerClient, self).__init__(credential=credential, **kwargs)
        self._client = FormRecognizer(
            endpoint=endpoint, credential=credential, pipeline=self._pipeline
        )

    def begin_extract_receipts(self, form, **kwargs):
        include_text_details = kwargs.pop("include_text_details", False)
        content_type = kwargs.pop("content_type", None)

        if isinstance(form, six.string_types):
            form = {"source": form}
            content_type = content_type or "application/json"
        elif content_type is None:
            content_type = get_content_type(form)
        response = self._client.analyze_receipt_async(
            file_stream=form,
            content_type=content_type,
            include_text_details=include_text_details,
            cls=get_pipeline_response,
            **kwargs
        )

        def callback(raw_response):
            analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_receipt = prepare_receipt_result(analyze_result, include_text_details)
            return extracted_receipt

        return LROPoller(self._client._client, response, callback, LROBasePolling(timeout=3, **kwargs))

    def begin_extract_layouts(self, form, **kwargs):
        content_type = kwargs.pop("content_type", None)

        if isinstance(form, six.string_types):
            form = {"source": form}
            content_type = content_type or "application/json"
        elif content_type is None:
            content_type = get_content_type(form)

        response = self._client.analyze_layout_async(
            file_stream=form,
            content_type=content_type,
            cls=get_pipeline_response,
            **kwargs
        )

        def callback(raw_response):
            analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_layout_result(analyze_result, include_elements=True)
            return extracted_layout

        return LROPoller(self._client._client, response, callback, LROBasePolling(timeout=3, **kwargs))
