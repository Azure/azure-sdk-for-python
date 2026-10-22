# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=C4717, C4722, C4748

from typing import Optional, Any, Union, List
from azure.core.pipeline import PipelineRequest
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.credentials import TokenCredential, AzureKeyCredential

from ._client import TextTranslationClient as ServiceClientGenerated


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class TranslatorHeaderPolicy(SansIOHTTPPolicy):
    """Adds Translator-specific headers for regional resources.

    :param region: Azure region of the Translator resource.
    :type region: str or None
    :param resource_id: Azure resource ID of the Translator resource.
    :type resource_id: str or None
    """

    def __init__(self, region: Optional[str] = None, resource_id: Optional[str] = None):
        self.region = region
        self.resource_id = resource_id

    def on_request(self, request: PipelineRequest) -> None:
        if self.region:
            request.http_request.headers["Ocp-Apim-Subscription-Region"] = self.region
        if self.resource_id:
            request.http_request.headers["Ocp-Apim-ResourceId"] = self.resource_id


def get_translation_endpoint(endpoint: str, api_version: str) -> str:
    """Transform cognitive services endpoint to translator-specific path if needed.

    :param endpoint: The base endpoint URL.
    :type endpoint: str
    :param api_version: The API version string.
    :type api_version: str
    :return: The transformed endpoint URL.
    :rtype: str
    """
    if "cognitiveservices" in endpoint:
        return endpoint + "/translator/text/v" + api_version
    return endpoint


class TextTranslationClient(ServiceClientGenerated):
    """Azure Translator is a cloud-based, multilingual, neural machine translation service. The Text
    Translation API enables robust and scalable translation capabilities suitable for diverse
    applications.

    Combinations of endpoint and credential values:

    - (no args) - global endpoint, no auth (get_languages only)
    - endpoint only - custom endpoint or container, no auth
    - AzureKeyCredential + region - global endpoint with subscription key
    - TokenCredential + audience - global endpoint with Cognitive Services token
    - TokenCredential + resource_id - global endpoint with Entra ID (global resource)
    - TokenCredential + region + resource_id - global endpoint with Entra ID (regional resource)
    - endpoint + AzureKeyCredential - custom endpoint with subscription key
    - endpoint + TokenCredential - custom endpoint with Entra ID

    :param endpoint: Supported Text Translation endpoints (protocol and hostname, for example:
     https://api.cognitive.microsofttranslator.com). Defaults to the global translator endpoint.
    :type endpoint: str
    :param credential: Credential used to authenticate with the Translator service. Optional for
     unauthenticated operations like get_languages.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential or None
    :param region: Azure region of the Translator resource. Required for AzureKeyCredential,
     optional for Entra ID regional resources.
    :type region: str or None
    :param resource_id: Azure resource ID for Entra ID authentication. Required when using
     TokenCredential with global endpoint.
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
        credential: Optional[Union[AzureKeyCredential, TokenCredential]] = None,
        *,
        region: Optional[str] = None,
        resource_id: Optional[str] = None,
        audience: Optional[str] = None,
        api_version: str = "2026-06-06",
        **kwargs: Any,
    ) -> None:
        # Validate credential + region/resource_id combinations
        if region and credential is not None and not isinstance(credential, AzureKeyCredential) and not resource_id:
            raise ValueError("'resource_id' must be provided when using TokenCredential with 'region'.")

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
