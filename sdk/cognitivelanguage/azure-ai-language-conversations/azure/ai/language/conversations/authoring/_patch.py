# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Union, Any
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from ._client import ConversationAuthoringClient as GeneratedConversationAuthoringClient

POLLING_INTERVAL_DEFAULT = 5


def _authentication_policy(credential):
    authentication_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(name="Ocp-Apim-Subscription-Key", credential=credential)
    elif credential is not None and not hasattr(credential, "get_token"):
        raise TypeError(
            f"Unsupported credential: {type(credential)}. Use an instance of AzureKeyCredential "
            "or a token credential from azure.identity"
        )
    return authentication_policy


class ConversationAuthoringClient(GeneratedConversationAuthoringClient):
    """The language service conversations API is a suite of natural language processing (NLP) skills
    that can be used to analyze structured conversations (textual or spoken). Further documentation
    can be found in https://docs.microsoft.com/azure/cognitive-services/language-service/overview.

    :param endpoint: Supported Cognitive Services endpoint (e.g.,
     https://:code:`<resource-name>`.cognitiveservices.azure.com). Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
        This can be the an instance of AzureKeyCredential if using a Language API key
        or a token credential from :mod:`azure.identity`.
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential
    :keyword api_version: Api Version. Available values are "2023-04-01" and "2022-05-01". Default value is
        "2023-04-01". Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
        Retry-After header is present.
    """

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        try:
            endpoint = endpoint.rstrip("/")
        except AttributeError:
            raise ValueError("Parameter 'endpoint' must be a string.")
        super().__init__(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            polling_interval=kwargs.pop("polling_interval", POLLING_INTERVAL_DEFAULT),
            **kwargs,
        )


__all__: List[str] = ["ConversationAuthoringClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
