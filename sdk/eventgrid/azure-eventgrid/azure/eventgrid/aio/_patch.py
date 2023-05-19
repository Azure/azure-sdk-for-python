# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List
from azure.core.credentials import AzureKeyCredential
from .._patch import EventGridSharedAccessKeyPolicy
from ._client import EventGridClient as ServiceClientGenerated
from .._legacy.aio import EventGridPublisherClient


class EventGridClient(ServiceClientGenerated):
    """Azure Messaging EventGrid Client.

    :param endpoint: The host name of the namespace, e.g.
     namespaceName1.westus-1.eventgrid.azure.net. Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "2023-06-01-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: AzureKeyCredential, **kwargs) -> None:
        if isinstance(credential, AzureKeyCredential):
            if not kwargs.get("authentication_policy"):
                kwargs["authentication_policy"] = EventGridSharedAccessKeyPolicy(
                    credential
                )
        super().__init__(endpoint=endpoint, credential=credential, **kwargs)


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__: List[str] = [
    "EventGridClient",
    "EventGridPublisherClient",
]  # Add all objects you want publicly available to users at this package level
