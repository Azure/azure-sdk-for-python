# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.policies import SansIOHTTPPolicy, HTTPPolicy
from ._models import RequestStatistics


class CognitiveServicesCredentialPolicy(SansIOHTTPPolicy):
    def __init__(self, cognitiveservices_key, **kwargs):
        if cognitiveservices_key is None:
            raise ValueError("Parameter 'credential' must not be None.")
        self.cognitiveservices_key = cognitiveservices_key
        super(CognitiveServicesCredentialPolicy, self).__init__()

    def on_request(self, request):
        request.http_request.headers[
            "Ocp-Apim-Subscription-Key"
        ] = self.cognitiveservices_key
        request.http_request.headers["X-BingApis-SDK-Client"] = "Python-SDK"


class TextAnalyticsResponseHook(HTTPPolicy):
    def __init__(self, **kwargs):
        self._response_callback = kwargs.get("raw_response_hook")
        super(TextAnalyticsResponseHook, self).__init__()

    def send(self, request, **kwargs):
        if request.context.options.get("response_hook", self._response_callback):
            statistics = request.context.get("statistics") or request.context.options.pop("statistics", None)
            model_version = request.context.get("model_version") or request.context.options.pop("model_version", None)
            response_callback = request.context.get("response_callback") or \
                request.context.options.pop("response_hook", self._response_callback)

            response = self.next.send(request)
            if statistics is None and model_version is None:
                data = ContentDecodePolicy.deserialize_from_http_generics(
                    response.http_response
                )
                statistics = data.get("statistics", None)
                model_version = data.get("modelVersion", None)
            for pipeline_obj in [request, response]:
                if statistics is not None and not isinstance(statistics, RequestStatistics):
                    statistics = RequestStatistics._from_generated(statistics)
                pipeline_obj.statistics = statistics
                pipeline_obj.model_version = model_version
            if response_callback:
                response_callback(response)
                request.context.response_callback = response_callback
            return response
        return self.next.send(request)
