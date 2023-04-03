# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import base64
from typing import List, overload, Union, Any, Optional
from azure.core.messaging import CloudEvent
from .models._models import CloudEventEvent as InternalCloudEvent
from .models._patch import ReceiveResponse
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator import distributed_trace
from ._client import AzureMessagingEventGridClient as ServiceClientGenerated

def _cloud_event_to_generated(cloud_event, **kwargs):
    data_kwargs = {}

    if isinstance(cloud_event.data, bytes):
        data_kwargs["data_base64"] = base64.b64encode(cloud_event.data) # base64 encode double check 
    else:
        data_kwargs["data"] = cloud_event.data

    internal_event = InternalCloudEvent(
        id=cloud_event.id,
        source=cloud_event.source,
        type=cloud_event.type,
        specversion=cloud_event.specversion,
        time=cloud_event.time,
        dataschema=cloud_event.dataschema,
        datacontenttype=cloud_event.datacontenttype,
        subject=cloud_event.subject,
        **data_kwargs,
        **kwargs
    )
    if cloud_event.extensions:
        internal_event.update(cloud_event.extensions)
    return internal_event


class EventGridSharedAccessKeyPolicy(SansIOHTTPPolicy):
    def __init__(
        self,
        credential: "AzureKeyCredential",
        **kwargs # pylint: disable=unused-argument
    ) -> None:
        super(EventGridSharedAccessKeyPolicy, self).__init__()
        self._credential = credential

    def on_request(self, request):
        request.http_request.headers["Authorization"] = "SharedAccessKey " + self._credential.key

class AzureMessagingEventGridClient(ServiceClientGenerated):

    def __init__(self, endpoint: str, credential: AzureKeyCredential, **kwargs):
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
    def publish(self, topic_name: str, body: List[CloudEvent], *, content_type: str = "application/cloudevents-batch+json; charset=utf-8", **kwargs: Any) -> None:
        """Publish Batch of Cloud Events to namespace topic."""

    @overload
    def publish(self, topic_name: str, body: CloudEvent, *, content_type: str = "application/cloudevents+json; charset=utf-8", **kwargs: Any) -> None:
        """Publish Single Cloud Event to namespace topic."""

    @distributed_trace
    def publish(self, topic_name: str, body: Union[List[CloudEvent], CloudEvent], **kwargs) -> None:
        """Publish Cloud Events to namespace topic."""
        if isinstance(body, CloudEvent):
            kwargs["content_type"] = "application/cloudevents+json; charset=utf-8"
            internal_body = _cloud_event_to_generated(body)
            self._publish_cloud_event(topic_name, internal_body, **kwargs)
        else:
            kwargs["content_type"] = "application/cloudevents-batch+json; charset=utf-8"
            internal_body_list = []
            for item in body:
                internal_body_list.append(_cloud_event_to_generated(item))
            self._publish_batch_of_cloud_events(topic_name, internal_body_list, **kwargs)
    
    @distributed_trace
    def receive(
        self,
        topic_name: str,
        event_subscription_name: str,
        *,
        max_events: Optional[int] = None,
        timeout: Optional[int] = None,
        **kwargs:Any
        ) -> List[ReceiveResponse]:
        """Receive Cloud Events from namespace topic."""

        deserialized_response = []
        received_response = self._receive_batch_of_cloud_events(topic_name, event_subscription_name, max_events=max_events, timeout=timeout, **kwargs)
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


__all__: List[str] = ["AzureMessagingEventGridClient"]  # Add all objects you want publicly available to users at this package level