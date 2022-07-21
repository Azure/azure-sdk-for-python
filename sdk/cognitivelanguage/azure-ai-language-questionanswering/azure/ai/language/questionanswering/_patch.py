# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from typing import Union, Any
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, BearerTokenCredentialPolicy
from ._client import QuestionAnsweringClient as QuestionAnsweringClientGenerated


def _authentication_policy(credential, **kwargs):
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(
            name="Ocp-Apim-Subscription-Key", credential=credential, **kwargs
        )
    elif hasattr(credential, "get_token"):
        authentication_policy = BearerTokenCredentialPolicy(
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
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential
    :keyword str default_language: Sets the default language to use for all operations.
    """

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        super().__init__(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential, **kwargs)),
            **kwargs
        )
        self._default_language = kwargs.pop("default_language", None)


def patch_sdk():
    pass


__all__ = ["QuestionAnsweringClient"]
