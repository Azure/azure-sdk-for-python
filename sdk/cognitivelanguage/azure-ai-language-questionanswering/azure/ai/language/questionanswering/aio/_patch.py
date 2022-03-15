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
    __doc__ = QuestionAnsweringClientGenerated.__doc__

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
