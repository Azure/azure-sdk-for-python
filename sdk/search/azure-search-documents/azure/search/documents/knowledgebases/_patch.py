# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Union

from azure.core.credentials import AzureKeyCredential, TokenCredential

from ._client import KnowledgeBaseRetrievalClient as _KnowledgeBaseRetrievalClient


class KnowledgeBaseRetrievalClient(_KnowledgeBaseRetrievalClient):
    """KnowledgeBaseRetrievalClient.

    :param endpoint: The endpoint URL of the search service. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a key
     credential type or a token credential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
    :param knowledge_base_name: The name of the knowledge base. Required.
    :type knowledge_base_name: str
    :keyword api_version: The API version to use for this operation. Known values are "2026-04-01"
     and None. Default value is "2026-04-01". Note that overriding this default value may result in
     unsupported behavior.
    :paramtype api_version: str
    :keyword str audience: Sets the Audience to use for authentication with Microsoft Entra ID. The
     audience is not considered when using a shared key. If audience is not provided, the public cloud
     audience will be assumed.
    """

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:
        audience = kwargs.pop("audience", None)
        if audience:
            kwargs.setdefault("credential_scopes", [audience.rstrip("/") + "/.default"])
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)


__all__: list[str] = [
    "KnowledgeBaseRetrievalClient",
]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
