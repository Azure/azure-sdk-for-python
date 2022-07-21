# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Union, Any
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, AsyncBearerTokenCredentialPolicy
from ._client import QuestionAnsweringClient as QuestionAnsweringClientGenerated


def _authentication_policy(credential, **kwargs):
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(
            name="Ocp-Apim-Subscription-Key", credential=credential, **kwargs
        )
    elif hasattr(credential, "get_token"):
        authentication_policy = AsyncBearerTokenCredentialPolicy(
            credential, *kwargs.pop("credential_scopes", ["https://cognitiveservices.azure.com/.default"]), **kwargs
        )
    else:
        raise TypeError(
            "Unsupported credential: {}. Use an instance of AzureKeyCredential "
            "or a token credential from azure.identity".format(type(credential))
        )
    return authentication_policy


class QuestionAnsweringClient(QuestionAnsweringClientGenerated):
    """The language service API is a suite of natural language processing (NLP) skills built with best-in-class Microsoft machine learning algorithms.

    The API can be used to analyze unstructured text for tasks such as sentiment
    analysis, key phrase extraction, language detection and question answering.
    Further documentation can be found in https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview

    :param endpoint: Supported Cognitive Services endpoint (e.g.,
     https://<resource-name>.api.cognitiveservices.azure.com).
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
        This can be the an instance of AzureKeyCredential if using a Language API key
        or a token credential from :mod:`azure.identity`.
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials_async.AsyncTokenCredential
    :keyword str default_language: Sets the default language to use for all operations.
    """

    def __init__(
        self, endpoint: str, credential: Union[AzureKeyCredential, AsyncTokenCredential], **kwargs: Any
    ) -> None:
        super().__init__(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            **kwargs
        )
        self._default_language = kwargs.pop("default_language", None)


__all__: List[str] = [
    "QuestionAnsweringClient"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
