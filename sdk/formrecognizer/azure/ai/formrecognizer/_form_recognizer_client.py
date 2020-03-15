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
from ._helpers import TrainingPolling
from ._response_handlers import (
    prepare_receipt_result,
    prepare_layout_result,
    prepare_unlabeled_result,
    prepare_labeled_result
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

    def begin_extract_receipt(self, form, content_type, **kwargs):
        include_text_details = kwargs.pop("include_text_details", False)
        if isinstance(form, six.string_types):
            form = {"source": form}

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

    def begin_extract_layout(self, form, content_type, **kwargs):
        if isinstance(form, six.string_types):
            form = {"source": form}

        response = self._client.analyze_layout_async(
            file_stream=form,
            content_type=content_type,
            cls=get_pipeline_response,
            **kwargs
        )

        def callback(raw_response):
            analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_layout_result(analyze_result, include_ocr=True)
            return extracted_layout

        return LROPoller(self._client._client, response, callback, LROBasePolling(timeout=3, **kwargs))

    def begin_training(self, source, content_type, source_prefix_filter=None, include_sub_folders=False, **kwargs):

        response = self._client.train_custom_model_async(
            train_request=TrainRequest(
                source=source,
                source_filter=TrainSourceFilter(
                    prefix=source_prefix_filter,
                    include_sub_folders=include_sub_folders
                )
            ),
            content_type=content_type,
            cls=get_pipeline_response,
            **kwargs
        )

        def callback(raw_response):
            model = self._client._deserialize(Model, raw_response)
            return CustomModel._from_generated(model)

        # FIXME: Don't do this, figure out a way to default to True.
        response.http_response.headers["Location"] = response.http_response.headers["Location"] + "?includeKeys=true"
        # return LROPoller(self._client._client, response, callback, LROBasePolling(timeout=3, **kwargs))
        return LROPoller(self._client._client, response, callback, LROBasePolling(timeout=3, lro_algorithms=[TrainingPolling()], **kwargs))

    def begin_labeled_training(self, source, content_type, source_prefix_filter=None, include_sub_folders=False, **kwargs):

        response = self._client.train_custom_model_async(
            train_request=TrainRequest(
                source=source,
                source_filter=TrainSourceFilter(
                    prefix=source_prefix_filter,
                    include_sub_folders=include_sub_folders
                ),
                use_label_file=True
            ),
            content_type=content_type,
            cls=get_pipeline_response,
            **kwargs
        )

        def callback(raw_response):
            model = self._client._deserialize(Model, raw_response)
            return CustomLabeledModel._from_generated(model)

        # return LROPoller(self._client._client, response, callback, LROBasePolling(timeout=3, **kwargs))
        return LROPoller(self._client._client, response, callback, LROBasePolling(timeout=3, lro_algorithms=[TrainingPolling()], **kwargs))

    def begin_extract_forms(self, form, model_id, content_type, **kwargs):
        include_text_details = kwargs.pop("include_text_details", False)

        if isinstance(form, six.string_types):
            form = {"source": form}

        response = self._client.analyze_with_custom_model(
            file_stream=form,
            model_id=model_id,
            include_text_details=include_text_details,
            content_type=content_type,
            cls=get_pipeline_response,
            **kwargs
        )

        def callback(raw_response):
            extracted_form = self._client._deserialize(AnalyzeOperationResult, raw_response)
            form_result = prepare_unlabeled_result(extracted_form, include_text_details)
            return form_result

        return LROPoller(self._client._client, response, callback, LROBasePolling(timeout=3, **kwargs))

    def begin_extract_labeled_forms(self, form, model_id, content_type, **kwargs):
        include_text_details = kwargs.pop("include_text_details", False)

        if isinstance(form, six.string_types):
            form = {"source": form}

        response = self._client.analyze_with_custom_model(
            file_stream=form,
            model_id=model_id,
            include_text_details=include_text_details,
            content_type=content_type,
            cls=get_pipeline_response,
            **kwargs
        )

        def callback(raw_response):
            extracted_form = self._client._deserialize(AnalyzeOperationResult, raw_response)
            form_result = prepare_labeled_result(extracted_form, include_text_details)
            return form_result

        return LROPoller(self._client._client, response, callback, LROBasePolling(timeout=3, **kwargs))

    def delete_custom_model(self, model_id, **kwargs):
        self._client.delete_custom_model(
            model_id=model_id,
            **kwargs
        )

    def list_custom_models(self, **kwargs):
        return self._client.list_custom_models(
            op="full",
            cls=lambda objs: [ModelInfo._from_generated(x) for x in objs],
            **kwargs
        )

    def get_models_summary(self, **kwargs):
        response = self._client.get_custom_models(op="summary", **kwargs)
        return ModelsSummary._from_generated(response.summary)

    def get_custom_model(self, model_id, **kwargs):
        response = self._client.get_custom_model(model_id=model_id, include_keys=True, **kwargs)
        if response.keys:
            return CustomModel._from_generated(response)
        raise HttpResponseError(message="Model id '{}' is a labeled model. Call get_custom_labeled_model() "
                                        "with the model id.".format(model_id))

    def get_custom_labeled_model(self, model_id, **kwargs):
        response = self._client.get_custom_model(model_id=model_id, **kwargs)
        if response.keys is None:
            return CustomLabeledModel._from_generated(response)
        raise HttpResponseError(message="Model id '{}' is not a labeled model. Call get_custom_model() "
                                        "with the model id.".format(model_id))
