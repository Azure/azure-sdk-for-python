# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, List
from azure.core.credentials import AzureKeyCredential
from ._question_answering_client import QuestionAnsweringClient as QuestionAnsweringClientGenerated


class QuestionAnsweringClient(QuestionAnsweringClientGenerated):
    """The language service API is a suite of natural language processing (NLP) skills built with best-in-class Microsoft machine learning algorithms.

    The API can be used to analyze unstructured text for tasks such as sentiment
    analysis, key phrase extraction, language detection and question answering.
    Further documentation can be found in https://docs.microsoft.com/azure/cognitive-services/text-analytics/overview

    :param endpoint: Supported Cognitive Services endpoint (e.g.,
     https://<resource-name>.api.cognitiveservices.azure.com).
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.AzureKeyCredential
    :keyword str default_language: Sets the default language to use for all operations.
    """

    def __init__(self, endpoint: str, credential: AzureKeyCredential, **kwargs: Any) -> None:
        super().__init__(endpoint, credential, **kwargs)
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
