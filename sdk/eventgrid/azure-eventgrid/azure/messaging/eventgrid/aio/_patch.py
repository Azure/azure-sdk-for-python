# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List, overload, Union, Any, Optional
from azure.core.messaging import CloudEvent
from ..models import ReceiveResponse
from .._patch import _cloud_event_to_generated, EventGridSharedAccessKeyPolicy
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator_async import distributed_trace_async
from ._client import EventGridClient as ServiceClientGenerated
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


    @overload
    async def publish(self, topic_name: str, body: List[CloudEvent], *, content_type: str = "application/cloudevents-batch+json; charset=utf-8", **kwargs: Any) -> None:
        """Publish Batch of Cloud Events to namespace topic.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param body: Array of Cloud Events being published. Required.
        :type body: list[~azure.core.messaging.CloudEvent]
        :keyword content_type: content type. Default value is "application/cloudevents-batch+json;
         charset=utf-8".
        :paramtype content_type: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def publish(self, topic_name: str, body: CloudEvent, *, content_type: str = "application/cloudevents+json; charset=utf-8", **kwargs: Any) -> None:
        """Publish Single Cloud Event to namespace topic.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param body: Single Cloud Event being published. Required.
        :type body: ~azure.core.messaging.CloudEvent
        :keyword content_type: content type. Default value is "application/cloudevents+json;
         charset=utf-8".
        :paramtype content_type: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def publish(self, topic_name: str, body: Union[List[CloudEvent], CloudEvent], **kwargs) -> None:
        """Publish Cloud Events to namespace topic.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param body: Single Cloud Event or list of Cloud Events being published. Required.
        :type body: ~azure.core.messaging.CloudEvent or list[~azure.core.messaging.CloudEvent]
        :keyword content_type: content type. Default value is "application/cloudevents+json;
         charset=utf-8".
        :paramtype content_type: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        if isinstance(body, CloudEvent):
            kwargs["content_type"] = "application/cloudevents+json; charset=utf-8"
            internal_body = _cloud_event_to_generated(body)
            await self._publish_cloud_event(topic_name, internal_body, **kwargs)
        else:
            kwargs["content_type"] = "application/cloudevents-batch+json; charset=utf-8"
            internal_body_list = []
            for item in body:
                internal_body_list.append(_cloud_event_to_generated(item))
            await self._publish_batch_of_cloud_events(topic_name, internal_body_list, **kwargs)
    
    @distributed_trace_async
    async def receive(
        self,
        topic_name: str,
        event_subscription_name: str,
        *,
        max_events: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs:Any
        ) -> List[ReceiveResponse]:
        """Receive Batch of Cloud Events from the Event Subscription.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param event_subscription_name: Event Subscription Name. Required.
        :type event_subscription_name: str
        :keyword max_events: Max Events count to be received. Default value is None.
        :paramtype max_events: int
        :keyword timeout: Timeout value for receive operation in Seconds. Default is 60 seconds.
         Default value is None.
        :paramtype timeout: int
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: ReceiveResponse. The ReceiveResponse is compatible with MutableMapping
        :rtype: ~azure.messaging.eventgrid.models.ReceiveResponse
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        deserialized_response = []
        received_response = await self._receive_batch_of_cloud_events(topic_name, event_subscription_name, max_events=max_events, timeout=timeout, **kwargs)
        for detail_item in received_response.get("value"):
            deserialized_cloud_event = CloudEvent.from_dict(detail_item.get("event"))
            detail_item["event"] = deserialized_cloud_event
            deserialized_response.append(detail_item)
        return deserialized_response


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__: List[str] = ["EventGridNamespaceClient",  "EventGridPublisherClient"]  # Add all objects you want publicly available to users at this package level
