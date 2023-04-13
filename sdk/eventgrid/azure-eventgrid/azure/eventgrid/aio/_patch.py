# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List
from .._patch import EventGridSharedAccessKeyPolicy
from azure.core.credentials import AzureKeyCredential
from ._client import EventGridNamespaceClient as ServiceClientGenerated
from .._legacy.aio import EventGridPublisherClient

class EventGridNamespaceClient(ServiceClientGenerated):
    """Azure Messaging EventGrid Namespace Client.

    :param endpoint: The host name of the namespace, e.g.
     namespaceName1.westus-1.eventgrid.azure.net. Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "2023-06-01-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    """

    def __init__(self, endpoint: str, credential: AzureKeyCredential, **kwargs) -> None:
        if isinstance(credential, AzureKeyCredential):
            # if it's our credential, we default to our authentication policy.
            # Otherwise, we use the default
            if not kwargs.get("authentication_policy"):
                kwargs["authentication_policy"] = EventGridSharedAccessKeyPolicy(credential)
        super().__init__(
            endpoint=endpoint,
            credential=credential,
            **kwargs
        )

def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__: List[str] = ["EventGridNamespaceClient",  "EventGridPublisherClient"]  # Add all objects you want publicly available to users at this package level
