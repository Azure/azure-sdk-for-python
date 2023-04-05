# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Union
from azure.core.pipeline.policies import ( BearerTokenCredentialPolicy, AzureKeyCredentialPolicy )
from azure.core.credentials import ( TokenCredential, AzureKeyCredential )

from .._patch import (
    TranslatorCredential,
    TranslatorAuthenticationPolicy,
)

from ._client import TextTranslationClient as ServiceClientGenerated

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

class TextTranslationClient(ServiceClientGenerated):
    def __init__(
            self,
            endpoint: Union[str , None],
            credential: Union[AzureKeyCredential , TokenCredential , TranslatorCredential],
            **kwargs):
        if isinstance(credential, TranslatorCredential):
            if not kwargs.get("authentication_policy"):
                kwargs["authentication_policy"] = TranslatorAuthenticationPolicy(credential)

        if isinstance(credential, TokenCredential):
            if not kwargs.get("authentication_policy"):
                kwargs["authentication_policy"] = BearerTokenCredentialPolicy(credential)

        if isinstance(credential, AzureKeyCredential):
            if not kwargs.get("authentication_policy"):
                kwargs["authentication_policy"] = AzureKeyCredentialPolicy(
                    name="Ocp-Apim-Subscription-Key", credential=credential)

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
