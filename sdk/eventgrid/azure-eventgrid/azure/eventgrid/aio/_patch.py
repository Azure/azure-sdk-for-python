# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List, Union, Any, TYPE_CHECKING, Optional
from azure.core.credentials import AzureKeyCredential, AzureSasCredential


from .._legacy.aio import EventGridPublisherClient as LegacyEventGridPublisherClient
from ._client import (
    EventGridPublisherClient as InternalEventGridPublisherClient,
    EventGridConsumerClient as InternalEventGridConsumerClient,
)
from .._serialization import Deserializer, Serializer
from .._patch import (
    DEFAULT_BASIC_API_VERSION,
    DEFAULT_STANDARD_API_VERSION,
)

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class EventGridPublisherClient(InternalEventGridPublisherClient):
    """EventGridPublisherClient.

    Sends events to a basic topic, basic domain, or a namespace topic
    specified during the client initialization.

    A single instance or a list of dictionaries, CloudEvents or EventGridEvents are accepted.
    If a list is provided, the list must contain only one type of event.
    If dictionaries are provided and sending to a namespace topic,
    the dictionary must follow the CloudEvent schema.

    :param endpoint: The host name of the namespace, e.g.
     namespaceName1.westus-1.eventgrid.azure.net. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a AsyncTokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword namespace_topic: The name of the topic to publish events to. Required for Event Grid Namespaces.
     Default value is None, which is used for Event Grid Basic.
    :paramtype namespace_topic: str or None
    :keyword api_version: The API version to use for this operation. Default value for Event Grid Namespace
     is "2024-06-01", default value for Event Grid Basic is "2018-01-01".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, AzureSasCredential, "AsyncTokenCredential"],
        *,
        namespace_topic: Optional[str] = None,
        api_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._namespace = namespace_topic
        self._credential = credential

        if not self._namespace:
            self._client = LegacyEventGridPublisherClient(  # type: ignore[assignment]
                endpoint, credential, api_version=api_version or DEFAULT_BASIC_API_VERSION, **kwargs
            )
            self._publish = self._client.send  # type: ignore[attr-defined]
        else:
            if isinstance(credential, AzureSasCredential):
                raise TypeError("SAS token authentication is not supported for Event Grid Namespace.")

            super().__init__(
                endpoint=endpoint,
                credential=credential,
                api_version=api_version or DEFAULT_STANDARD_API_VERSION,
                **kwargs,
            )
            self._publish = self._send_events
        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False

    def __repr__(self) -> str:
        return (
            f"<EventGridPublisherClient: namespace_topic={self._namespace}, credential type={type(self._credential)}>"
        )


class EventGridConsumerClient(InternalEventGridConsumerClient):
    """EventGridConsumerClient.

    Consumes and manages events from a namespace topic
    and event subscription specified during the client initialization.

    :param endpoint: The endpoint of the Event Grid tier (basic or namespace), e.g.
     namespaceName1.westus-1.eventgrid.azure.net. Required.
    :type endpoint: str
    :param credential: Credential used to authenticate requests to the service. Is either a
     AzureKeyCredential type or a AsyncTokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword namespace_topic: The name of the topic to consume events from. Required.
    :paramtype namespace_topic: str
    :keyword subscription: The name of the subscription to consume events from. Required.
    :paramtype subscription: str
    :keyword api_version: The API version to use for this operation. Default value is "2024-06-01".
     Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "AsyncTokenCredential"],
        *,
        namespace_topic: str,
        subscription: str,
        api_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._namespace = namespace_topic
        self._subscription = subscription
        self._credential = credential
        super().__init__(
            endpoint=endpoint, credential=credential, api_version=api_version or DEFAULT_STANDARD_API_VERSION, **kwargs
        )

    def __repr__(self) -> str:
        return f"<EventGridConsumerClient: namespace_topic={self._namespace}, \
            subscription={self._subscription}, credential type={type(self._credential)}>"


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__: List[str] = [
    "EventGridConsumerClient",
    "EventGridPublisherClient",
]  # Add all objects you want publicly available to users at this package level
