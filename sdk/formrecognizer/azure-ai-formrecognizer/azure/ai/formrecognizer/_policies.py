# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.pipeline.policies import SansIOHTTPPolicy


class CognitiveServicesCredentialPolicy(SansIOHTTPPolicy):
    def __init__(self, api_key_credential):
        self.credential = api_key_credential
        super(CognitiveServicesCredentialPolicy, self).__init__()

    def on_request(self, request):
        request.http_request.headers[
            "Ocp-Apim-Subscription-Key"
        ] = self.credential.api_key
