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
from ._helpers import get_pipeline_response
from ._response_handlers import (
    prepare_receipt_result,
    prepare_layout_result,
    prepare_training_result,
    prepare_labeled_training_result,
    prepare_analyze_result,
)
from azure.core.exceptions import HttpResponseError
from azure.core.polling import LROPoller
from ._generated.models import AnalyzeOperationResult, Model
from azure.core.polling.base_polling import LROBasePolling
from ._models import ModelInfo, ModelsSummary

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class FormRecognizerClient(FormRecognizerClientBase):


    def __init__(self, endpoint, credential, **kwargs):
        super(FormRecognizerClient, self).__init__(credential=credential, **kwargs)
        self._client = FormRecognizer(
            endpoint=endpoint, credential=credential, pipeline=self._pipeline
        )

    def begin_extract_receipt(self, form, content_type, **kwargs):
        # raw_response_hook = kwargs.pop("raw_response_hook")
        include_text_details = kwargs.pop("include_text_details", False)
        if isinstance(form, six.string_types):
            form = {"source": form}

        try:
            response = self._client.analyze_receipt_async(
                file_stream=form,
                content_type=content_type,
                include_text_details=include_text_details,
                cls=get_pipeline_response,
                **kwargs
            )
        except ErrorResponseException as err:
            raise HttpResponseError(err)

        def callback(raw_response):
            analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_receipt = prepare_receipt_result(analyze_result, include_text_details)
            return extracted_receipt

        # poll_method = LROBasePolling(raw_response_hook=raw_response_hook)
        poll_method = LROBasePolling()
        poller = LROPoller(self._client._client, response, callback, poll_method)
        return poller

    def begin_extract_layout(self, form, content_type, **kwargs):
        # import json
        #
        # json_file_path = "../result_layout.json"
        #
        # with open(json_file_path, 'r') as j:
        #     result = json.loads(j.read())
        # analyze_result = self._client._deserialize(AnalyzeOperationResult, result)
        # extracted_layout = prepare_layout_result(analyze_result, include_raw=True)
        # return extracted_layout

        include_text_details = kwargs.pop("include_text_details", False)
        if isinstance(form, six.string_types):
            form = {"source": form}

        try:
            response = self._client.analyze_layout_async(
                file_stream=form,
                content_type=content_type,
                cls=get_pipeline_response,
                **kwargs
            )
        except ErrorResponseException as err:
            raise HttpResponseError(err)

        def callback(raw_response):
            analyze_result = self._client._deserialize(AnalyzeOperationResult, raw_response)
            extracted_layout = prepare_layout_result(analyze_result, include_text_details)
            return extracted_layout

        poll_method = LROBasePolling()
        poller = LROPoller(self._client._client, response, callback, poll_method)
        return poller

    def begin_training(self, source, content_type, source_prefix_filter=None, include_sub_folders=False, include_keys=False, **kwargs):
        # import json
        #
        # json_file_path = "../result_training_unlabeled_with_keys.json"
        #
        # with open(json_file_path, 'r') as j:
        #     result = json.loads(j.read())
        #
        # model = self._client._deserialize(Model, result)
        # custom_model = prepare_training_result(model)
        # return custom_model

        try:
            response = self._client.train_custom_model_async(
                train_request={
                    "source": source,
                    "source_filter": source_prefix_filter,
                    "include_sub_folders": include_sub_folders
                },
                content_type=content_type,
                cls=get_pipeline_response,
                **kwargs
            )
        except ErrorResponseException as err:
            raise HttpResponseError(err)

        def callback(raw_response):
            model = self._client._deserialize(Model, raw_response)
            custom_model = prepare_training_result(model)
            return custom_model

        # FIXME: Don't do this but figure out how to let user specify include_keys
        if include_keys:
            response.http_response.headers["Location"] = response.http_response.headers["Location"] + "?includeKeys=true"

        poll_method = LROBasePolling()
        poller = LROPoller(self._client._client, response, callback, poll_method)
        return poller

    def begin_labeled_training(self, source, content_type, source_prefix_filter=None, include_sub_folders=False, **kwargs):
        # import json
        #
        # json_file_path = "../result_training_labeled.json"
        #
        # with open(json_file_path, 'r') as j:
        #     result = json.loads(j.read())
        #
        # model = self._client._deserialize(Model, result)
        # custom_model = prepare_labeled_training_result(model)
        # return custom_model

        try:
            response = self._client.train_custom_model_async(
                train_request={"source": source, "source_filter": source_prefix_filter, "use_label_file": True},
                content_type=content_type,
                cls=get_pipeline_response,
                **kwargs
            )
        except ErrorResponseException as err:
            raise HttpResponseError(err)

        def callback(raw_response):
            model = self._client._deserialize(Model, raw_response)
            custom_model = prepare_labeled_training_result(model)
            return custom_model

        poll_method = LROBasePolling()
        poller = LROPoller(self._client._client, response, callback, poll_method)
        return poller

    def begin_extract_form(self, form, model_id, content_type, **kwargs):
        include_text_details = kwargs.pop("include_text_details", False)
        # import json
        #
        # json_file_path = "../result_unlabeled.json"
        #
        # with open(json_file_path, 'r') as j:
        #     result = json.loads(j.read())
        #
        # extracted_form = self._client._deserialize(AnalyzeOperationResult, result)
        # form_result = prepare_analyze_result(extracted_form, include_text_details)
        # return form_result

        if isinstance(form, six.string_types):
            form = {"source": form}

        try:
            response = self._client.analyze_with_custom_model(
                file_stream=form,
                model_id=model_id,
                include_text_details=include_text_details,
                content_type=content_type,
                cls=get_pipeline_response,
                **kwargs
            )
        except ErrorResponseException as err:
            raise HttpResponseError(err)

        def callback(raw_response):
            extracted_form = self._client._deserialize(AnalyzeOperationResult, raw_response)
            form_result = prepare_analyze_result(extracted_form, include_text_details)
            return form_result

        poll_method = LROBasePolling()
        poller = LROPoller(self._client._client, response, callback, poll_method)
        return poller

    def delete_custom_model(self, model_id, **kwargs):
        try:
            self._client.delete_custom_model(
                model_id=model_id,
                **kwargs
            )
        except ErrorResponseException as err:
            raise HttpResponseError(err)

    def list_custom_models(self, **kwargs):
        try:
            return self._client.list_custom_models(
                cls=lambda objs: [ModelInfo._from_generated(x) for x in objs],
                **kwargs
        )
        except ErrorResponseException as err:
            raise HttpResponseError(err)

    def get_models_summary(self, **kwargs):
        try:
            response = self._client.get_custom_models(**kwargs)
            return ModelsSummary._from_generated(response.summary)
        except ErrorResponseException as err:
            raise HttpResponseError(err)
