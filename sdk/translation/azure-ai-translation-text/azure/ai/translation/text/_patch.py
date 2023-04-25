# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import ( Union, Optional )
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import ( SansIOHTTPPolicy, BearerTokenCredentialPolicy, AzureKeyCredentialPolicy )
from azure.core.credentials import ( TokenCredential, AzureKeyCredential )

from ._client import TextTranslationClient as ServiceClientGenerated

DEFAULT_TOKEN_SCOPE = "https://api.microsofttranslator.com/"

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

class TranslatorCredential:
    """ Credential for Translator Service. It is using combination of Resource key and region.
    """
    def __init__(self, key: str, region: str) -> None:
        self.key = key
        self.region = region

    def update(self, key: str) -> None:
        """Update the key.
        This can be used when you've regenerated your service key and want
        to update long-lived clients.
        :param str key: The key used to authenticate to an Azure service
        :raises: ValueError or TypeError
        """
        if not key:
            raise ValueError("The key used for updating can not be None or empty")
        if not isinstance(key, str):
            raise TypeError("The key used for updating must be a string.")
        self.key = key

class TranslatorAuthenticationPolicy(SansIOHTTPPolicy):
    """ Translator Authentication Policy. Adds both authentication headers that are required.
    Ocp-Apim-Subscription-Region header contains region of the Translator resource.
    Ocp-Apim-Subscription-Key header contains API key of the Translator resource.
    """
    def __init__(self, credential: TranslatorCredential):
        self.credential = credential

    def on_request(self, request: PipelineRequest) -> None:
        request.http_request.headers["Ocp-Apim-Subscription-Key"] = self.credential.key
        request.http_request.headers["Ocp-Apim-Subscription-Region"] = self.credential.region

def get_translation_endpoint(endpoint, api_version):
    if not endpoint:
        endpoint = "https://api.cognitive.microsofttranslator.com"

    translator_endpoint: str = ""
    if "cognitiveservices" in endpoint:
        translator_endpoint = endpoint + "/translator/text/v" + api_version
    else:
        translator_endpoint = endpoint

    return translator_endpoint

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
            kwargs["authentication_policy"] = BearerTokenCredentialPolicy(credential, *kwargs.pop("credential_scopes", [DEFAULT_TOKEN_SCOPE]), kwargs)

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
    :type credential: Union[AzureKeyCredential , TokenCredential , TranslatorCredential]
    :keyword api_version: Default value is "3.0". Note that overriding this default value may
     result in unsupported behavior.
    :paramtype api_version: str
    """
    def __init__(
            self,
            credential: Union[AzureKeyCredential , TokenCredential , TranslatorCredential],
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

__all__ = ["TextTranslationClient", "TranslatorCredential"]
