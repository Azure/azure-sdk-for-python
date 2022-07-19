# coding=utf-8
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------

# This file is used for handwritten extensions to the generated code. Example:
# https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/customize_code/how-to-patch-sdk-code.md

import importlib
from typing import Union, Any
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, BearerTokenCredentialPolicy
from ._question_answering_projects_client import QuestionAnsweringProjectsClient \
    as QuestionAnsweringProjectsClientGenerated


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


class QuestionAnsweringProjectsClient(QuestionAnsweringProjectsClientGenerated):
    """The language service API is a suite of natural language processing (NLP) skills built with
    best-in-class Microsoft machine learning algorithms.  The API can be used to analyze
    unstructured text for tasks such as sentiment analysis, key phrase extraction, language
    detection and question answering. Further documentation can be found in :code:`<a
    href="https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/overview">https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/overview</a>`.

    :param endpoint: Supported Cognitive Services endpoint (e.g.,
     https://:code:`<resource-name>`.api.cognitiveservices.azure.com).
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
        This can be the an instance of AzureKeyCredential if using a Language API key
        or a token credential from :mod:`azure.identity`.
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.TokenCredential
    :keyword api_version: Api Version. The default value is "2021-10-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        super().__init__(
            endpoint=endpoint,
            credential=credential,  # type: ignore
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential, **kwargs)),
            **kwargs
        )


def patch_sdk():
    curr_package = importlib.import_module("azure.ai.language.questionanswering.projects")
    curr_package.QuestionAnsweringProjectsClient = QuestionAnsweringProjectsClient
