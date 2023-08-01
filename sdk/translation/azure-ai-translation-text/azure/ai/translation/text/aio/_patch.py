# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import ( Union, Optional )
from azure.core.pipeline.policies import ( AsyncBearerTokenCredentialPolicy, AzureKeyCredentialPolicy )
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential

from .._patch import (
    DEFAULT_TOKEN_SCOPE,
    get_translation_endpoint,
    TranslatorAuthenticationPolicy,
    TranslatorCredential
)

from ._client import TextTranslationClient as ServiceClientGenerated

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

def set_authentication_policy(credential, kwargs):
    if isinstance(credential, TranslatorCredential):
        if not kwargs.get("authentication_policy"):
            kwargs["authentication_policy"] = TranslatorAuthenticationPolicy(credential)
    elif isinstance(credential, AzureKeyCredential):
        if not kwargs.get("authentication_policy"):
            kwargs["authentication_policy"] = AzureKeyCredentialPolicy(
                name="Ocp-Apim-Subscription-Key", credential=credential)
    elif hasattr(credential, "get_token"):
        if not kwargs.get("authentication_policy"):
            kwargs["authentication_policy"] = AsyncBearerTokenCredentialPolicy(credential, *kwargs.pop("credential_scopes", [DEFAULT_TOKEN_SCOPE]), kwargs)

class TextTranslationClient(ServiceClientGenerated):
    """Text translation is a cloud-based REST API feature of the Translator service that uses neural
    machine translation technology to enable quick and accurate source-to-target text translation
    in real time across all supported languages.

    The following methods are supported by the Text Translation feature:

    Languages. Returns a list of languages supported by Translate, Transliterate, and Dictionary
    Lookup operations.

    Translate. Renders single source-language text to multiple target-language texts with a single
    request.

    Transliterate. Converts characters or letters of a source language to the corresponding
    characters or letters of a target language.

    Detect. Returns the source code language code and a boolean variable denoting whether the
    detected language is supported for text translation and transliteration.

    Dictionary lookup. Returns equivalent words for the source term in the target language.

    Dictionary example Returns grammatical structure and context examples for the source term and
    target term pair.

    Combinations of endpoint and credential values:
    str + AzureKeyCredential - used custom domain translator endpoint
    str + TokenCredential - used for regional endpoint with token authentication
    str + TranslatorCredential - used for National Clouds
    None + AzureKeyCredential - used for global translator endpoint with global Translator resource
    None + Token - general translator endpoint with token authentication
    None + TranslatorCredential - general translator endpoint with regional Translator resource

    :param endpoint: Supported Text Translation endpoints (protocol and hostname, for example:
         https://api.cognitive.microsofttranslator.com). Required.
    :type endpoint: str
    :param credential: Credential used to authenticate with the Translator service
    :type credential: Union[AzureKeyCredential , AsyncTokenCredential , TranslatorCredential]
    :keyword api_version: Default value is "3.0". Note that overriding this default value may
     result in unsupported behavior.
    :paramtype api_version: str
    """
    def __init__(
            self,
            credential: Union[AzureKeyCredential , AsyncTokenCredential , TranslatorCredential],
            *,
            endpoint: Optional[str] = None,
            api_version = "3.0",
            **kwargs):

        set_authentication_policy(credential, kwargs)

        translation_endpoint = get_translation_endpoint(endpoint, api_version)

        super().__init__(
            endpoint=translation_endpoint,
            api_version=api_version,
            **kwargs
        )


__all__ = ["TextTranslationClient"]
