# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Union
from azure.core.credentials import ( TokenCredential, AzureKeyCredential )

from .._patch import (
    get_translation_endpoint,
    set_authentication_policy,
    TranslatorCredential
)

from ._client import TextTranslationClient as ServiceClientGenerated

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """

class TextTranslationClient(ServiceClientGenerated):
    def __init__(
            self,
            endpoint: Union[str , None],
            credential: Union[AzureKeyCredential , TokenCredential , TranslatorCredential],
            **kwargs):

        set_authentication_policy(credential, kwargs)

        translation_endpoint = get_translation_endpoint(endpoint)

        super().__init__(
            endpoint=translation_endpoint,
            **kwargs
        )


__all__ = ["TextTranslationClient"]
