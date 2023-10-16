# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List,  Any, TYPE_CHECKING, Union
from azure.core.credentials import AzureKeyCredential
from .._legacy.aio import EventGridPublisherClient

from ._client import EventGridClient as InternalEventGridClient

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials_async import AsyncTokenCredential


class EventGridClient(InternalEventGridClient):
    """Azure Messaging EventGrid Client.

    :param endpoint: The host name of the namespace, e.g.
     namespaceName1.westus-1.eventgrid.azure.net. Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword binary_mode: Whether to use binary mode for CloudEvents. Default value is False.
    :paramtype binary_mode: bool
    :keyword api_version: The API version to use for this operation. Default value is
     "2023-06-01-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "AsyncTokenCredential"],
        **kwargs: Any
    ) -> None:
        
        self._binary_mode = kwargs.get("binary_mode", False)
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__: List[str] = [
    "EventGridPublisherClient",
    "EventGridClient",
]  # Add all objects you want publicly available to users at this package level
