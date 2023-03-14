# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import ( SansIOHTTPPolicy, BearerTokenCredentialPolicy, AzureKeyCredentialPolicy )
from azure.core.credentials import ( TokenCredential, AzureKeyCredential )

from ._client import TextTranslationClient as ServiceClientGenerated

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

class TranslatorCredential:
    def __init__(self, key: str, region: str) -> None:
        self.key = key
        self.region = region

class TranslatorAuthenticationPolicy(SansIOHTTPPolicy):
    def __init__(self, credential: TranslatorCredential):
        self.credential = credential

    def on_request(self, request: PipelineRequest) -> None:
        request.http_request.headers["Ocp-Apim-Subscription-Key"] = self.credential.key
        request.http_request.headers["Ocp-Apim-Subscription-Region"] = self.credential.region

class TextTranslationClient(ServiceClientGenerated):
    def __init__(self, endpoint: str | None, credential: AzureKeyCredential | TokenCredential | TranslatorCredential, **kwargs):
        if isinstance(credential, TranslatorCredential):
            if not kwargs.get("authentication_policy"):
                kwargs["authentication_policy"] = TranslatorAuthenticationPolicy(credential)

        if isinstance(credential, TokenCredential):
            if not kwargs.get("authentication_policy"):
                kwargs["authentication_policy"] = BearerTokenCredentialPolicy(credential)

        if isinstance(credential, AzureKeyCredential):
            if not kwargs.get("authentication_policy"):
                kwargs["authentication_policy"] = AzureKeyCredentialPolicy(name="Ocp-Apim-Subscription-Key", credential=credential)

        if not endpoint:
            endpoint = "https://api.cognitive.microsofttranslator.com"

        translator_endpoint: str = ""
        if "cognitiveservices" in endpoint:
            translator_endpoint = endpoint + "/translator/text/v3.0"
        else:
            translator_endpoint = endpoint

        super().__init__(
            endpoint=translator_endpoint,
            **kwargs
        )

__all__ = ["TextTranslationClient", "TranslatorCredential"]
