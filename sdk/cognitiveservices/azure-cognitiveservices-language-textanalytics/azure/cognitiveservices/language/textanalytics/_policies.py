# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.policies import SansIOHTTPPolicy, HTTPPolicy
from ._models import RequestStatistics


class CognitiveServicesCredentialPolicy(SansIOHTTPPolicy):
    def __init__(self, cognitiveservices_key):
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
        self._response_callback = kwargs.get("response_hook")
        super(TextAnalyticsResponseHook, self).__init__()

    def send(self, request):
        if request.context.options.get("response_hook", self._response_callback):
            response_callback = request.context.options.pop("response_hook", self._response_callback)

            response = self.next.send(request)
            data = ContentDecodePolicy.deserialize_from_http_generics(response.http_response)
            statistics = data.get("statistics", None)
            model_version = data.get("modelVersion", None)

            batch_statistics = RequestStatistics._from_generated(statistics)  # pylint: disable=protected-access
            response.statistics = batch_statistics
            response.model_version = model_version
            response.raw_response = data
            if response_callback:
                response_callback(response)
            return response
        return self.next.send(request)
