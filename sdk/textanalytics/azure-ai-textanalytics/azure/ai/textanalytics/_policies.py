# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from copy import deepcopy
from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.policies import SansIOHTTPPolicy
from ._models import TextDocumentBatchStatistics, AnalyzeActionsType
from ._lro import _FINISHED, _FAILED

def _finished_polling(data):
    return bool(data) and data['status'] in _FINISHED.union(_FAILED)

def _get_task_name_from_task_type(task_type):
    if task_type == AnalyzeActionsType.RECOGNIZE_ENTITIES:
        return "entityRecognitionTasks"
    if task_type == AnalyzeActionsType.RECOGNIZE_PII_ENTITIES:
        return "entityRecognitionPiiTasks"
    if task_type == AnalyzeActionsType.RECOGNIZE_LINKED_ENTITIES:
        return "entityLinkingTasks"
    if task_type == AnalyzeActionsType.ANALYZE_SENTIMENT:
        return "sentimentAnalysisTasks"
    return "keyPhraseExtractionTasks"

class TextAnalyticsResponseHookPolicy(SansIOHTTPPolicy):
    def __init__(self, **kwargs):
        self._response_callback = kwargs.get("raw_response_hook")
        self._is_lro = False
        self._task_order = None
        super(TextAnalyticsResponseHookPolicy, self).__init__()

    def on_request(self, request):
        self._response_callback = request.context.options.pop("raw_response_hook", self._response_callback)
        if not self._task_order:
            self._task_order = request.context.options.pop("_task_order", None)

    def on_response(self, request, response):
        if response.http_response.status_code == 202:
            self._is_lro = True  # lro calls start with 202
        if self._response_callback:
            data = ContentDecodePolicy.deserialize_from_http_generics(response.http_response)
            if self._is_lro and not _finished_polling(data):
                return
            statistics = None
            model_version = None
            action_statistics = None
            action_model_versions = None
            if self._task_order:
                data_copy = deepcopy(data)
                action_statistics = []
                action_model_versions = []
                for task in self._task_order:
                    property_name = _get_task_name_from_task_type(task)
                    results = data_copy['tasks'][property_name].pop(0)['results']
                    if results.get("statistics"):
                        action_statistics.append(results.pop("statistics"))
                    if results.get("modelVersion"):
                        action_model_versions.append(results.pop("modelVersion"))
            else:
                statistics = data.get("statistics", None)
                model_version = data.get("modelVersion", None)

            if any([statistics, model_version, action_statistics, action_model_versions]):
                if statistics:
                    batch_statistics = TextDocumentBatchStatistics._from_generated(statistics)  # pylint: disable=protected-access
                    response.statistics = batch_statistics
                if action_statistics:
                    response.action_statistics = [
                        TextDocumentBatchStatistics._from_generated(stat)  # pylint: disable=protected-access
                        for stat in action_statistics
                    ]
                if model_version:
                    response.model_version = model_version
                if action_model_versions:
                    response.action_model_versions = action_model_versions
                response.raw_response = data
                self._response_callback(response)
