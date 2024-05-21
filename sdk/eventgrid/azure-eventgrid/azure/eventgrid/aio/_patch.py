# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List, Union, Any, TYPE_CHECKING, Optional
from azure.core.credentials import AzureKeyCredential, AzureSasCredential

from .._legacy.aio import EventGridPublisherClient as GAEventGridPublisherClient
from ._client import EventGridPublisherClient as InternalEventGridPublisherClient, EventGridConsumerClient as InternalEventGridConsumerClient
from .._serialization import Deserializer, Serializer
from .._patch import (
    ClientLevel,
    DEFAULT_BASIC_API_VERSION,
    DEFAULT_STANDARD_API_VERSION,
)

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials_async import AsyncTokenCredential


class EventGridPublisherClient(InternalEventGridPublisherClient):
    """Azure Messaging EventGrid Publisher Client.

    :param endpoint: The endpoint to the Event Grid resource.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.AzureSasCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: The API version to use for this operation. Default value for namespaces is
     "2023-10-01-preview". Default value for basic is "2018-01-01".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str or None
    :keyword namespace_topic: The topic of the Event Grid Namespace. Required for working with a namespace topic.
    :paramtype level: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, AzureSasCredential, "AsyncTokenCredential"],
        *,
        namespace_topic: Optional[str] = None,
        api_version: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        _endpoint = "{endpoint}"
        self._namespace = namespace_topic
        self._credential = credential

        if not self._namespace:
            self._client = GAEventGridPublisherClient(  # type: ignore[assignment]
                endpoint, credential, api_version=api_version or DEFAULT_BASIC_API_VERSION, **kwargs
            )
            self._send = self._client.send  # type: ignore[attr-defined]
        else:
            if isinstance(credential, AzureSasCredential):
                raise TypeError("SAS token authentication is not supported for the standard client.")

            super().__init__(
                endpoint=endpoint,
                credential=credential,
                api_version=api_version or DEFAULT_STANDARD_API_VERSION,
                **kwargs
            )
            self._send = self._publish_cloud_events
        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False

    def __repr__(self) -> str:
        return "<EventGridPublisherClient [namespace_topic={}] and credential type [{}]>".format(self._namespace, type(self.credential))

class EventGridConsumerClient(InternalEventGridConsumerClient):

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, "AsyncTokenCredential"], **kwargs: Any) -> None:
        return super().__init__(endpoint=endpoint, credential=credential, **kwargs)
    

    def __repr__(self) -> str:
        return "<EventGridConsumerClient>"

def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__: List[str] = [
    "EventGridPublisherClient",
    "EventGridConsumerClient",
]  # Add all objects you want publicly available to users at this package level
