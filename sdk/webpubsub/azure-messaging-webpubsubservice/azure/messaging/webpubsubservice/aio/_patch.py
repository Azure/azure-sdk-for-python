# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from typing import Any, TYPE_CHECKING, Union

from azure.core.credentials import AzureKeyCredential


from .._patch import _parse_connection_string, WebPubSubServiceClientBase
from ._client import WebPubSubServiceClient as WebPubSubServiceClientGenerated

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class WebPubSubServiceClient(WebPubSubServiceClientBase, WebPubSubServiceClientGenerated):
    """WebPubSubServiceClient.

    :param endpoint: HTTP or HTTPS endpoint for the Web PubSub service instance.
    :type endpoint: str
    :param hub: Target hub name, which should start with alphabetic characters and only contain
     alpha-numeric characters or underscore.
    :type hub: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials_async.AsyncTokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword api_version: Api Version. The default value is "2021-10-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self, endpoint: str, hub: str, credential: Union["AsyncTokenCredential", AzureKeyCredential], **kwargs: Any
    ) -> None:
        super().__init__(endpoint=endpoint, hub=hub, credential=credential, **kwargs)

    @classmethod
    def from_connection_string(cls, connection_string: str, hub: str, **kwargs: Any) -> "WebPubSubServiceClient":
        """Create a new WebPubSubServiceClient from a connection string.

        :param connection_string: Connection string
        :type connection_string: ~str
        :param hub: Target hub name, which should start with alphabetic characters and only contain
         alpha-numeric characters or underscore.
        :type hub: str
        :rtype: WebPubSubServiceClient
        """
        kwargs = _parse_connection_string(connection_string, **kwargs)

        credential = AzureKeyCredential(kwargs.pop("accesskey"))
        return cls(hub=hub, credential=credential, **kwargs)


__all__: List[str] = [
    "WebPubSubServiceClient"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
