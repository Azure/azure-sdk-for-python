# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from typing import Any

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


def patch_sdk():
    pass


__all__ = ["QuestionAnsweringClient"]
