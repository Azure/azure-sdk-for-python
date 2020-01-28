# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.pipeline.policies import ContentDecodePolicy
from azure.core.pipeline.policies import SansIOHTTPPolicy, HTTPPolicy
from ._models import TextDocumentBatchStatistics


class CognitiveServicesCredentialPolicy(SansIOHTTPPolicy):
    def __init__(self, api_key_credential):
        self.credential = api_key_credential
        super(CognitiveServicesCredentialPolicy, self).__init__()

    def on_request(self, request):
        request.http_request.headers[
            "Ocp-Apim-Subscription-Key"
        ] = self.credential.api_key
        request.http_request.headers["X-BingApis-SDK-Client"] = "Python-SDK"


class TextAnalyticsResponseHook(HTTPPolicy):
    def __init__(self, **kwargs):
        self._response_callback = kwargs.get("response_hook")
        super(TextAnalyticsResponseHook, self).__init__()

    def send(self, request):
        response_callback = request.context.options.pop("response_hook", self._response_callback)
        if response_callback:
            response = self.next.send(request)
            data = ContentDecodePolicy.deserialize_from_http_generics(response.http_response)
            statistics = data.get("statistics", None)
            model_version = data.get("modelVersion", None)

            batch_statistics = TextDocumentBatchStatistics._from_generated(statistics)  # pylint: disable=protected-access
            response.statistics = batch_statistics
            response.model_version = model_version
            response.raw_response = data
            response_callback(response)
            return response
        return self.next.send(request)
