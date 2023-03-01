# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import ( SansIOHTTPPolicy, BearerTokenCredentialPolicy, AzureKeyCredentialPolicy )
from azure.core.credentials import ( TokenCredential, AzureKeyCredential )

from ._client import TranslatorClient as ServiceClientGenerated

from typing import List

__all__: List[str] = ["TranslatorClient", "TranslatorCredential", "TranslatorCustomEndpoint"]

class TranslatorCredential:
    def __init__(self, key: str, region: str) -> None:
        self.key = key
        self.region = region

class TranslatorCustomEndpoint:
    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint

class TranslatorAuthenticationPolicy(SansIOHTTPPolicy):
    def __init__(self, credential: TranslatorCredential):
        self.credential = credential

    def on_request(self, request: PipelineRequest) -> None:
        request.http_request.headers["Ocp-Apim-Subscription-Key"] = self.credential.key
        request.http_request.headers["Ocp-Apim-Subscription-Region"] = self.credential.region

class TranslatorClient(ServiceClientGenerated):
    def __init__(self, endpoint: str | TranslatorCustomEndpoint, credential: AzureKeyCredential | TokenCredential | TranslatorCredential | None, **kwargs):

        if isinstance(credential, TranslatorCredential):
            if not kwargs.get("authentication_policy"):
                kwargs["authentication_policy"] = TranslatorAuthenticationPolicy(credential)

        if isinstance(credential, TokenCredential):
            if not kwargs.get("authentication_policy"):
                kwargs["authentication_policy"] = BearerTokenCredentialPolicy(credential)

        if isinstance(credential, AzureKeyCredential):
            if not kwargs.get("authentication_policy"):
                kwargs["authentication_policy"] = AzureKeyCredentialPolicy(name="Ocp-Apim-Subscription-Key", credential=credential)

        translator_endpoint: str = ""
        if isinstance(endpoint, str):
            translator_endpoint = endpoint
        if isinstance(endpoint, TranslatorCustomEndpoint):
            translator_endpoint = endpoint.endpoint + "/translator/text/v3.0"

        super().__init__(
            endpoint=translator_endpoint,
            **kwargs
        )

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
