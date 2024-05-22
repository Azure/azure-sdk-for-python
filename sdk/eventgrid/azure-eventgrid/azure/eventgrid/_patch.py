# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List, Union, Optional, Any
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta
from azure.core.credentials import (
    AzureKeyCredential,
    TokenCredential,
    AzureSasCredential,
)

from ._legacy import (
    EventGridPublisherClient as GAEventGridPublisherClient,
    SystemEventNames,
    EventGridEvent,
    generate_sas,
)
from ._client import (
    EventGridPublisherClient as InternalEventGridPublisherClient,
    EventGridConsumerClient as InternalEventGridConsumerClient,
)
from ._serialization import Serializer, Deserializer


DEFAULT_STANDARD_API_VERSION = "2023-10-01-preview"
DEFAULT_BASIC_API_VERSION = "2018-01-01"


class EventGridPublisherClient(InternalEventGridPublisherClient):
    """
    Azure Messaging EventGrid Publisher Client.

    :param endpoint: The endpoint to the Event Grid resource.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.AzureSasCredential or
     ~azure.core.credentials.TokenCredential
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
        credential: Union[AzureKeyCredential, AzureSasCredential, "TokenCredential"],
        *,
        namespace_topic: Optional[str] = None,
        api_version: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        _endpoint = "{endpoint}"
        self._namespace = namespace_topic
        self.credential = credential

        if not self._namespace:
            self._client = GAEventGridPublisherClient(
                endpoint,
                credential,
                api_version=api_version or DEFAULT_BASIC_API_VERSION,
            )  # type:ignore[assignment]
            self._send = self._client.send  # type:ignore[attr-defined]
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
        return "<EventGridPublisherClient [namespace_topic={}] and credential type [{}]>".format(
            self._namespace, type(self.credential)
        )


class EventGridConsumerClient(InternalEventGridConsumerClient):

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, "TokenCredential"], **kwargs: Any) -> None:
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
    "SystemEventNames",
    "EventGridEvent",
    "generate_sas",
]  # Add all objects you want publicly available to users at this package level
