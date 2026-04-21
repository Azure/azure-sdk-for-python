# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=C4717, C4722, C4748
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Optional, Any, Union, List
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential

from .._patch import get_translation_endpoint, TranslatorHeaderPolicy
from ._client import TextTranslationClient as ServiceClientGenerated


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class TextTranslationClient(ServiceClientGenerated):
    """Azure Translator is a cloud-based, multilingual, neural machine translation service. The Text
    Translation API enables robust and scalable translation capabilities suitable for diverse
    applications.

    Combinations of endpoint and credential values:

    - endpoint + AzureKeyCredential - custom domain translator endpoint
    - endpoint + AzureKeyCredential + region - global translator endpoint with regional resource
    - endpoint + AsyncTokenCredential - regional endpoint with token authentication
    - endpoint + None - on-prem container (no authentication)
    - AzureKeyCredential only - global translator endpoint with global Translator resource (uses default endpoint)
    - AsyncTokenCredential only - global translator endpoint with token authentication (uses default endpoint)
    - AsyncTokenCredential + region + resource_id - global translator endpoint with regional Translator resource

    :param endpoint: Supported Text Translation endpoints (protocol and hostname, for example:
     https://api.cognitive.microsofttranslator.com). Defaults to the global translator endpoint.
    :type endpoint: str
    :param credential: Credential used to authenticate with the Translator service. Optional for
     unauthenticated operations like get_languages.
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials_async.AsyncTokenCredential or None
    :param region: Azure region of the Translator resource, required when using global endpoint with regional resource.
    :type region: str or None
    :param resource_id: Azure resource ID, required with TokenCredential when using global endpoint with regional resource.
    :type resource_id: str or None
    :param audience: Scopes of the credentials.
    :type audience: str or None
    :param api_version: Default value is "2026-06-06". Note that overriding this default value may
     result in unsupported behavior.
    :type api_version: str
    """

    def __init__(
        self,
        endpoint: str = "https://api.cognitive.microsofttranslator.com",
        credential: Optional[Union[AzureKeyCredential, AsyncTokenCredential]] = None,
        *,
        region: Optional[str] = None,
        resource_id: Optional[str] = None,
        audience: Optional[str] = None,
        api_version: str = "2026-06-06",
        **kwargs: Any,
    ) -> None:
        if resource_id and not region:
            raise ValueError("'region' must be provided when 'resource_id' is specified.")

        translation_endpoint = get_translation_endpoint(endpoint, api_version)

        # Add translator-specific header policy for regional resources
        if region or resource_id:
            per_call_policies: List[SansIOHTTPPolicy] = list(kwargs.pop("per_call_policies", []) or [])
            per_call_policies.insert(0, TranslatorHeaderPolicy(region=region, resource_id=resource_id))
            kwargs["per_call_policies"] = per_call_policies

        if audience:
            kwargs["credential_scopes"] = [audience]

        super().__init__(
            endpoint=translation_endpoint,
            credential=credential,
            api_version=api_version,
            **kwargs,
        )


__all__ = ["TextTranslationClient"]
