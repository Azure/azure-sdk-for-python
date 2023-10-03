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
from azure.core.tracing.decorator import distributed_trace
from ._operations import EventGridClientOperationsMixin as OperationsMixin
from ..models._models import CloudEvent as InternalCloudEvent
from ..models._patch import ReceiveResult, ReceiveDetails


def _cloud_event_to_generated(cloud_event, **kwargs):
    data_kwargs = {}

    if isinstance(cloud_event.data, bytes):
        data_kwargs["data_base64"] = base64.b64encode(
            cloud_event.data
        )
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


class EventGridClientOperationsMixin(OperationsMixin):
    @overload
    def publish_cloud_events(
        self,
        topic_name: str,
        body: List[CloudEvent],
        *,
        content_type: str = "application/cloudevents-batch+json; charset=utf-8",
        **kwargs: Any
    ) -> None:
        """Publish Batch Cloud Event to namespace topic. In case of success, the server responds with an
        HTTP 200 status code with an empty JSON object in response. Otherwise, the server can return
        various error codes. For example, 401: which indicates authorization failure, 403: which
        indicates quota exceeded or message is too large, 410: which indicates that specific topic is
        not found, 400: for bad request, and 500: for internal server error.

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
    def publish_cloud_events(
        self,
        topic_name: str,
        body: CloudEvent,
        *,
        content_type: str = "application/cloudevents+json; charset=utf-8",
        **kwargs: Any
    ) -> None:
        """Publish Single Cloud Event to namespace topic. In case of success, the server responds with an
        HTTP 200 status code with an empty JSON object in response. Otherwise, the server can return
        various error codes. For example, 401: which indicates authorization failure, 403: which
        indicates quota exceeded or message is too large, 410: which indicates that specific topic is
        not found, 400: for bad request, and 500: for internal server error.

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

    @distributed_trace
    def publish_cloud_events(
        self, topic_name: str, body: Union[List[CloudEvent], CloudEvent], **kwargs
    ) -> None:
        """Publish Batch Cloud Event or Events to namespace topic. In case of success, the server responds with an
        HTTP 200 status code with an empty JSON object in response. Otherwise, the server can return
        various error codes. For example, 401: which indicates authorization failure, 403: which
        indicates quota exceeded or message is too large, 410: which indicates that specific topic is
        not found, 400: for bad request, and 500: for internal server error.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param body: Cloud Event or array of Cloud Events being published. Required.
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
            self._publish_cloud_event(topic_name, internal_body, **kwargs)
        else:
            kwargs["content_type"] = "application/cloudevents-batch+json; charset=utf-8"
            internal_body_list = []
            for item in body:
                internal_body_list.append(_cloud_event_to_generated(item))
            self._publish_cloud_events(topic_name, internal_body_list, **kwargs)

    @distributed_trace
    def receive_cloud_events(
        self,
        topic_name: str,
        event_subscription_name: str,
        *,
        max_events: Optional[int] = None,
        max_wait_time: Optional[int] = None,
        **kwargs: Any
    ) -> ReceiveResult:
        """Receive Batch of Cloud Events from the Event Subscription.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param event_subscription_name: Event Subscription Name. Required.
        :type event_subscription_name: str
        :keyword max_events: Max Events count to be received. Minimum value is 1, while maximum value
         is 100 events. If not specified, the default value is 1. Default value is None.
        :paramtype max_events: int
        :keyword max_wait_time: Max wait time value for receive operation in Seconds. It is the time in
         seconds that the server approximately waits for the availability of an event and responds to
         the request. If an event is available, the broker responds immediately to the client. Minimum
         value is 10 seconds, while maximum value is 120 seconds. If not specified, the default value is
         60 seconds. Default value is None.
        :paramtype max_wait_time: int
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: ReceiveResult. The ReceiveResult is compatible with MutableMapping
        :rtype: ~azure.eventgrid.models.ReceiveResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        detail_items = []
        received_result = self._receive_cloud_events(
            topic_name,
            event_subscription_name,
            max_events=max_events,
            max_wait_time=max_wait_time,
            **kwargs
        )
        for detail_item in received_result.value:
            deserialized_cloud_event = CloudEvent.from_dict(detail_item.event)
            detail_item.event = deserialized_cloud_event
            detail_items.append(
                ReceiveDetails(
                    broker_properties=detail_item.broker_properties,
                    event=detail_item.event,
                )
            )
        receive_result_deserialized = ReceiveResult(value=detail_items)
        return receive_result_deserialized


__all__: List[str] = [
    "EventGridClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
