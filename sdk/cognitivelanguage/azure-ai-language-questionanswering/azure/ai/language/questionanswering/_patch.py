# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
from typing import Any

from azure.core.credentials import AzureKeyCredential

from ._question_answering_client import QuestionAnsweringClient as QuestionAnsweringClientGenerated


class QuestionAnsweringClient(QuestionAnsweringClientGenerated):
    __doc__ = QuestionAnsweringClientGenerated.__doc__

    def __init__(self, endpoint: str, credential: AzureKeyCredential, **kwargs: Any) -> None:
        super().__init__(endpoint, credential, **kwargs)
        self._default_language = kwargs.pop("default_language", None)


def patch_sdk():
    pass


__all__ = ["QuestionAnsweringClient"]
