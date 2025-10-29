# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Union
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from ._client import SearchClient as _SearchClient
from ._operations._patch import AsyncSearchItemPaged


class SearchClient(_SearchClient):
    """SearchClient."""

    def __init__(
        self, endpoint: str, index_name: str, credential: Union[AzureKeyCredential, AsyncTokenCredential], **kwargs: Any
    ):
        """Initialize SearchClient.
        :param endpoint: Service host. Required.
        :type endpoint: str
        :param credential: Credential used to authenticate requests to the service. Is either a key
         credential type or a token credential type. Required.
        :type credential: ~azure.core.credentials.AzureKeyCredential or
         ~azure.core.credentials_async.AsyncTokenCredential
        :param index_name: The name of the index. Required.
        :type index_name: str
        :keyword api_version: The API version to use for this operation. Default value is
         "2025-11-01-preview". Note that overriding this default value may result in unsupported
         behavior.
        :paramtype api_version: str
        """
        super().__init__(endpoint=endpoint, credential=credential, index_name=index_name, **kwargs)


__all__: list[str] = [
    "SearchClient",
    "AsyncSearchItemPaged",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
