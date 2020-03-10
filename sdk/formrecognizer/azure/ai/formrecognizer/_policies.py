# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.pipeline.policies import SansIOHTTPPolicy, ContentDecodePolicy


class CognitiveServicesCredentialPolicy(SansIOHTTPPolicy):
    def __init__(self, api_key_credential):
        self.credential = api_key_credential
        super(CognitiveServicesCredentialPolicy, self).__init__()

    def on_request(self, request):
        request.http_request.headers[
            "Ocp-Apim-Subscription-Key"
        ] = self.credential.api_key


class FormRecognizerResponseHookPolicy(SansIOHTTPPolicy):
    def __init__(self, **kwargs):
        self._response_callback = kwargs.get("raw_response_hook")
        super(FormRecognizerResponseHookPolicy, self).__init__()

    def on_request(self, request):
        self._response_callback = request.context.options.pop("raw_response_hook", self._response_callback)

    def on_response(self, request, response):
        if self._response_callback:
            data = ContentDecodePolicy.deserialize_from_http_generics(response.http_response)
            response.raw_response = data
            self._response_callback(response)