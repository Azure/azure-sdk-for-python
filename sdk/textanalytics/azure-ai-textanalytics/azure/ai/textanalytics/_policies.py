# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.policies import SansIOHTTPPolicy
from ._models import TextDocumentBatchStatistics


class TextAnalyticsResponseHookPolicy(SansIOHTTPPolicy):
    def __init__(self, **kwargs):
        self._response_callback = kwargs.get("raw_response_hook")
        super(TextAnalyticsResponseHookPolicy, self).__init__()

    def on_request(self, request):
        self._response_callback = request.context.options.pop("raw_response_hook", self._response_callback)

    def on_response(self, request, response):

        if self._response_callback:
            data = ContentDecodePolicy.deserialize_from_http_generics(response.http_response)
            if data:
                statistics = data.get("statistics", None)
                model_version = data.get("modelVersion", None)

                if statistics or model_version:
                    batch_statistics = TextDocumentBatchStatistics._from_generated(statistics)  # pylint: disable=protected-access
                    response.statistics = batch_statistics
                    response.model_version = model_version
            response.raw_response = data
            self._response_callback(response)
