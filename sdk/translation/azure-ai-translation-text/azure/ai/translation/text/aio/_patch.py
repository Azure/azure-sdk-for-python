# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=C4717, C4722, C4748
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Optional, Any, overload
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import AsyncBearerTokenCredentialPolicy, AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential

from .._patch import (
    DEFAULT_TOKEN_SCOPE,
    DEFAULT_ENTRA_ID_SCOPE,
    DEFAULT_SCOPE,
    get_translation_endpoint,
    TranslatorAuthenticationPolicy,
)

from ._client import TextTranslationClient as ServiceClientGenerated


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class AsyncTranslatorEntraIdAuthenticationPolicy(AsyncBearerTokenCredentialPolicy):  # pylint: disable=name-too-long
    """Translator Entra Id Authentication Policy. Adds headers that are required by Translator Service
    when global endpoint is used with Entra Id policy.
    Ocp-Apim-Subscription-Region header contains region of the Translator resource.
    Ocp-Apim-ResourceId header contains Azure resource Id - Translator resource.

    :param credential: Translator Entra Id Credentials used to access Translator Resource for global endpoint.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential
    :keyword str region: Used for National Clouds.
    :keyword str resource_id: Used with both a TokenCredential combined with a region.
    :keyword str audience: Scopes of the credentials.
    """

    def __init__(
        self, credential: AsyncTokenCredential, resource_id: str, region: str, audience: str, **kwargs: Any
    ) -> None:
        super(AsyncTranslatorEntraIdAuthenticationPolicy, self).__init__(credential, audience, **kwargs)
        self.resource_id = resource_id
        self.region = region
        self.translator_credential = credential

    async def on_request(self, request: PipelineRequest) -> None:
        request.http_request.headers["Ocp-Apim-ResourceId"] = self.resource_id
        request.http_request.headers["Ocp-Apim-Subscription-Region"] = self.region
        await super().on_request(request)


def set_authentication_policy(credential, kwargs):
    if isinstance(credential, AzureKeyCredential):
        if not kwargs.get("authentication_policy"):
            if kwargs.get("region"):
                kwargs["authentication_policy"] = TranslatorAuthenticationPolicy(credential, kwargs["region"])
            else:
                kwargs["authentication_policy"] = AzureKeyCredentialPolicy(
                    name="Ocp-Apim-Subscription-Key", credential=credential
                )
    elif hasattr(credential, "get_token"):
        if not kwargs.get("authentication_policy"):
            if kwargs.get("region") and kwargs.get("resource_id"):
                scope = kwargs.pop("audience", DEFAULT_ENTRA_ID_SCOPE).rstrip("/") + DEFAULT_SCOPE
                kwargs["authentication_policy"] = AsyncTranslatorEntraIdAuthenticationPolicy(
                    credential,
                    kwargs["resource_id"],
                    kwargs["region"],
                    scope,
                )
            else:
                if kwargs.get("resource_id") or kwargs.get("region"):
                    raise ValueError(
                        """Both 'resource_id' and 'region' must be provided with a TokenCredential
                         for regional resource authentication."""
                    )
                kwargs["authentication_policy"] = AsyncBearerTokenCredentialPolicy(
                    credential, *[kwargs.pop("audience", DEFAULT_TOKEN_SCOPE)], kwargs
                )


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
    str + AzureKeyCredential + Region - used for global translator endpoint
    str + AsyncTokenCredential - used for regional endpoint with token authentication
    str + None - used with text translation on-prem container
    None + AzureKeyCredential - used for global translator endpoint with global Translator resource
    None + AsyncTokenCredential - general translator endpoint with token authentication
    None + AsyncTokenCredential + Region - general translator endpoint with regional Translator resource

    :keyword str endpoint: Supported Text Translation endpoints (protocol and hostname, for example:
     https://api.cognitive.microsofttranslator.com). If not provided, global translator endpoint will be used.
    :keyword credential: Credential used to authenticate with the Translator service
    :paramtype credential: Union[AzureKeyCredential, AsyncTokenCredential]
    :keyword str region: Used for National Clouds.
    :keyword str resource_id: Used with both a TokenCredential combined with a region.
    :keyword str audience: Scopes of the credentials.
    :keyword  str api_version: Default value is "3.0". Note that overriding this default value may
     result in unsupported behavior.
    """

    @overload
    def __init__(
        self,
        *,
        credential: AsyncTokenCredential,
        region: Optional[str] = None,
        endpoint: Optional[str] = None,
        resource_id: Optional[str] = None,
        audience: Optional[str] = None,
        api_version: str = "3.0",
        **kwargs
    ): ...

    @overload
    def __init__(
        self,
        *,
        credential: AzureKeyCredential,
        region: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_version: str = "3.0",
        **kwargs
    ): ...

    @overload
    def __init__(self, *, endpoint: str, api_version: str = "3.0", **kwargs): ...

    def __init__(self, **kwargs):
        api_version = kwargs.get("api_version", "3.0")
        set_authentication_policy(kwargs.get("credential"), kwargs)
        translation_endpoint = get_translation_endpoint(
            kwargs.pop("endpoint", "https://api.cognitive.microsofttranslator.com"), api_version
        )
        super().__init__(endpoint=translation_endpoint, api_version=api_version, **kwargs)


__all__ = ["TextTranslationClient"]
