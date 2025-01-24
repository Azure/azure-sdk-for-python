# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Union, Any, Optional, Callable, Dict, TypeVar, TYPE_CHECKING
import sys
from azure.core.messaging import CloudEvent
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
)
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, AsyncHttpResponse
from ...models._patch import ReceiveDetails
from ._operations import (
    EventGridPublisherClientOperationsMixin as PublisherOperationsMixin,
    EventGridConsumerClientOperationsMixin as ConsumerOperationsMixin,
)
from ... import models as _models
from ..._validation import api_version_validation

from ..._operations._patch import (
    _serialize_events,
)

from ..._legacy import EventGridEvent
from ..._legacy._helpers import _is_eventgrid_event_format

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]

if TYPE_CHECKING:
    from cloudevents.http.event import CloudEvent as CNCFCloudEvent


class EventGridPublisherClientOperationsMixin(PublisherOperationsMixin):

    @distributed_trace_async
    async def send(
        self,
        events: Union[
            CloudEvent,
            List[CloudEvent],
            Dict[str, Any],
            List[Dict[str, Any]],
            "CNCFCloudEvent",
            List["CNCFCloudEvent"],
            EventGridEvent,
            List[EventGridEvent],
        ],
        *,
        channel_name: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Send events to the Event Grid Service.

        :param events: The event(s) to send. If sending to an Event Grid Namespace, the dict, list of dicts,
         or event(s) should be in the format of a CloudEvent.
        :type events: CloudEvent or List[CloudEvent] or Dict[str, Any] or List[Dict[str, Any]]
         or CNCFCloudEvent or List[CNCFCloudEvent] or EventGridEvent or List[EventGridEvent]
        :keyword channel_name: The name of the channel to send the event to. Event Grid Basic Resource only.
        :paramtype channel_name: str or None
        :keyword content_type: The content type of the event. If not specified, the default value is
         "application/cloudevents+json; charset=utf-8".
        :paramtype content_type: str

        :return: None
        :rtype: None
        """
        if self._namespace and channel_name:
            raise ValueError("Channel name is not supported for Event Grid Namespaces.")

        # If a cloud event dict, convert to CloudEvent for serializing
        try:
            if isinstance(events, dict):
                events = CloudEvent.from_dict(events)
            if isinstance(events, list) and isinstance(events[0], dict):
                events = [CloudEvent.from_dict(e) for e in events]
        except Exception:  # pylint: disable=broad-except
            pass

        if self._namespace:
            kwargs["content_type"] = (
                content_type if content_type else "application/cloudevents-batch+json; charset=utf-8"
            )
            if not isinstance(events, list):
                events = [events]

            if isinstance(events[0], EventGridEvent) or _is_eventgrid_event_format(events[0]):
                raise TypeError("EventGridEvent is not supported for Event Grid Namespaces.")
            try:
                # Try to send via namespace
                await self._publish(self._namespace, _serialize_events(events), **kwargs)
            except Exception as exception:
                self._http_response_error_handler(exception)
                raise exception
        else:
            kwargs["content_type"] = content_type if content_type else "application/json; charset=utf-8"
            try:
                await self._publish(events, channel_name=channel_name, **kwargs)
            except Exception as exception:
                self._http_response_error_handler(exception)
                raise exception

    def _http_response_error_handler(self, exception):
        if isinstance(exception, HttpResponseError):
            if exception.status_code == 404:
                raise ResourceNotFoundError(
                    "Resource not found. "
                    "For Event Grid Namespaces, please specify the namespace_topic name on the client. "
                    "For Event Grid Basic, do not specify the namespace_topic name."
                ) from exception
            raise exception


class EventGridConsumerClientOperationsMixin(ConsumerOperationsMixin):

    @distributed_trace_async
    async def receive(
        self,
        *,
        max_events: Optional[int] = None,
        max_wait_time: Optional[int] = None,
        **kwargs: Any,
    ) -> List[ReceiveDetails]:
        """Receive Batch of Cloud Events from the Event Subscription.

        :keyword max_events: Max Events count to be received. Minimum value is 1, while maximum value
         is 100 events. The default is None, meaning it will receive one event if available.
        :paramtype max_events: int
        :keyword max_wait_time: Max wait time value for receive operation in Seconds. It is the time in
         seconds that the server approximately waits for the availability of an event and responds to
         the request. If an event is available, the broker responds immediately to the client. Minimum
         value is 10 seconds, while maximum value is 120 seconds. The default value is None, meaning it
         will wait for 60 seconds.
        :paramtype max_wait_time: int
        :return: ReceiveDetails list of received events and their broker properties.
        :rtype: list[~azure.eventgrid.models.ReceiveDetails]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        detail_items = []
        receive_result = await self._receive(
            self._namespace,
            self._subscription,
            max_events=max_events,
            max_wait_time=max_wait_time,
            **kwargs,
        )
        for detail_item in receive_result.details:
            deserialized_cloud_event = CloudEvent.from_dict(detail_item.event)
            detail_item.event = deserialized_cloud_event
            detail_items.append(
                ReceiveDetails(
                    broker_properties=detail_item.broker_properties,
                    event=detail_item.event,
                )
            )
        return detail_items

    @distributed_trace_async
    async def acknowledge(
        self,
        *,
        lock_tokens: List[str],
        **kwargs: Any,
    ) -> _models.AcknowledgeResult:
        """Acknowledge a batch of Cloud Events. The response will include the set of successfully
        acknowledged lock tokens, along with other failed lock tokens with their corresponding error
        information. Successfully acknowledged events will no longer be available to be received by any
        consumer.

        :keyword lock_tokens: Array of lock tokens of Cloud Events. Required.
        :paramtype lock_tokens: List[str]
        :return: AcknowledgeResult. The AcknowledgeResult is compatible with MutableMapping
        :rtype: ~azure.eventgrid.models.AcknowledgeResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._acknowledge(self._namespace, self._subscription, lock_tokens=lock_tokens, **kwargs)

    @distributed_trace_async
    @api_version_validation(
        params_added_on={"2023-10-01-preview": ["release_delay"]},
    )
    async def release(
        self,
        *,
        lock_tokens: List[str],
        release_delay: Optional[Union[int, _models.ReleaseDelay]] = None,
        **kwargs: Any,
    ) -> _models.ReleaseResult:
        """Release a batch of Cloud Events. The response will include the set of successfully released
        lock tokens, along with other failed lock tokens with their corresponding error information.
        Successfully released events can be received by consumers.

        :keyword lock_tokens: Array of lock tokens of Cloud Events. Required.
        :paramtype lock_tokens: List[str]
        :keyword release_delay: Release cloud events with the specified delay in seconds.
         Known values are: 0, 10, 60, 600, and 3600. Default value is None, indicating no delay.
        :paramtype release_delay: int or ~azure.eventgrid.models.ReleaseDelay
        :return: ReleaseResult. The ReleaseResult is compatible with MutableMapping
        :rtype: ~azure.eventgrid.models.ReleaseResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._release(
            self._namespace,
            self._subscription,
            lock_tokens=lock_tokens,
            release_delay_in_seconds=release_delay,
            **kwargs,
        )

    @distributed_trace_async
    async def reject(
        self,
        *,
        lock_tokens: List[str],
        **kwargs: Any,
    ) -> _models.RejectResult:
        """Reject a batch of Cloud Events. The response will include the set of successfully rejected lock
        tokens, along with other failed lock tokens with their corresponding error information.
        Successfully rejected events will be dead-lettered and can no longer be received by a consumer.

        :keyword lock_tokens: Array of lock tokens of Cloud Events. Required.
        :paramtype lock_tokens: List[str]
        :return: RejectResult. The RejectResult is compatible with MutableMapping
        :rtype: ~azure.eventgrid.models.RejectResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._reject(self._namespace, self._subscription, lock_tokens=lock_tokens, **kwargs)

    @distributed_trace_async
    @api_version_validation(
        method_added_on="2023-10-01-preview",
        params_added_on={"2023-10-01-preview": ["api_version", "content_type", "accept"]},
    )
    async def renew_locks(
        self,
        *,
        lock_tokens: List[str],
        **kwargs: Any,
    ) -> _models.RenewLocksResult:
        """Renew lock for batch of Cloud Events. The server responds with an HTTP 200 status code if the
        request is successfully accepted. The response body will include the set of successfully
        renewed lockTokens, along with other failed lockTokens with their corresponding error
        information.

        :keyword lock_tokens: Array of lock tokens of Cloud Events. Required.
        :paramtype lock_tokens: List[str]
        :return: RenewLocksResult. The RenewLocksResult is compatible with
         MutableMapping
        :rtype: ~azure.eventgrid.models.RenewLocksResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await super()._renew_locks(self._namespace, self._subscription, lock_tokens=lock_tokens, **kwargs)


__all__: List[str] = [
    "EventGridPublisherClientOperationsMixin",
    "EventGridConsumerClientOperationsMixin",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
