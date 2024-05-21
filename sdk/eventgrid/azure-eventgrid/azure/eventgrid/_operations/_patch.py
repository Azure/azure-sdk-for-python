# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import json
import sys
from functools import wraps
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    TypeVar,
    Union,
    overload,
    TYPE_CHECKING,
)

from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
)
from azure.core.messaging import CloudEvent
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.utils import case_insensitive_dict

from ._operations import (
    EventGridPublisherClientOperationsMixin as OperationsPubMixin,
    EventGridConsumerClientOperationsMixin as OperationsConsumerMixin,
)
from ..models._patch import (
    ReceiveResult,
    ReceiveDetails,
)
from .. import models as _models
from ..models._models import (
    AcknowledgeOptions,
    ReleaseOptions,
    RejectOptions,
    RenewLockOptions,
    CloudEvent as InternalCloudEvent,
)
from .._validation import api_version_validation


from .._legacy import EventGridEvent
from .._legacy._helpers import _from_cncf_events, _is_eventgrid_event, _is_cloud_event
from .._serialization import Serializer

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]
_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False

if TYPE_CHECKING:
    from cloudevents.http.event import CloudEvent as CNCFCloudEvent


def validate_args(**kwargs: Any):
    kwargs_mapping = kwargs.pop("kwargs_mapping", None)

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> T:
            selected_client_level = self._level  # pylint: disable=protected-access

            if kwargs_mapping:
                unsupported_kwargs = {
                    arg: level
                    for level, arguments in kwargs_mapping.items()
                    for arg in arguments
                    if arg in kwargs.keys()  # pylint: disable=consider-iterating-dictionary
                    and selected_client_level != level
                }

                error_strings = []
                if unsupported_kwargs:
                    error_strings += [
                        f"'{param}' is not available for the {selected_client_level} client. "
                        f"Use the {level} client.\n"
                        for param, level in unsupported_kwargs.items()
                    ]
                if len(error_strings) > 0:
                    raise ValueError("".join(error_strings))

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


class EventGridPublisherClientOperationsMixin(OperationsPubMixin):

    @distributed_trace
    def send(
        self,
        events: Union[
            CloudEvent,
            List[CloudEvent],
            Dict[str, Any],
            List[Dict[str, Any]],
            EventGridEvent,
            List[EventGridEvent],
            "CNCFCloudEvent",
            List["CNCFCloudEvent"],
        ],
        *,
        channel_name: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None: # pylint: disable=docstring-should-be-keyword, docstring-missing-param
        """Send events to the Event Grid Service.

        :param topic_name: The name of the topic to send the event to.
        :type topic_name: str
        :param events: The event(s) to send.
        :type events: CloudEvent or List[CloudEvent] or Dict[str, Any] or List[Dict[str, Any]]
         or CNCFCloudEvent or List[CNCFCloudEvent] or EventGridEvent or List[EventGridEvent]
        :keyword channel_name: The name of the channel to send the event to.
        :paramtype channel_name: str or None
        :keyword content_type: The content type of the event. If not specified, the default value is
         "application/cloudevents+json; charset=utf-8".
        :paramtype content_type: str or None

        :return: None
        :rtype: None

        A single instance or a list of dictionaries, CloudEvents are accepted. In the case of an Azure Event Grid
        Basic Resource, EventGridEvent(s) and CNCFCloudEvents are also accepted.

        .. admonition:: Example:

            .. literalinclude:: ../samples/sync_samples/eventgrid_client_samples/sample_publish_operation.py
                :start-after: [START publish_cloud_event]
                :end-before: [END publish_cloud_event]
                :language: python
                :dedent: 0
                :caption: Publishing a Cloud Event to a Namespace Topic.

            .. literalinclude:: ../samples/sync_samples/sample_publish_events_using_1.0_schema.py
                :start-after: [START publish_cloud_event_to_topic]
                :end-before: [END publish_cloud_event_to_topic]
                :language: python
                :dedent: 0
                :caption: Publishing a CloudEvent to a Basic Topic.
        """
        # Check kwargs
        events = kwargs.pop("events", None) or events

        if events is None:
            raise ValueError("events is required for the `send` operation.")

        if self._namespace and channel_name:
            raise ValueError("Channel Name is not supported for Event Grid Namespaces.")

        # If a cloud event dict, convert to CloudEvent for serializing
        try:
            if isinstance(events, dict):
                events = CloudEvent.from_dict(events)
            if isinstance(events, list) and isinstance(events[0], dict):
                events = [CloudEvent.from_dict(e) for e in events]
        except Exception:  # pylint: disable=broad-except
            pass

        if self._namespace:
            kwargs["content_type"] = kwargs.get("content_type", "application/cloudevents-batch+json; charset=utf-8")
            if not isinstance(events, list):
                events = [events]

            if isinstance(events[0], EventGridEvent) or _is_eventgrid_event(events[0]):
                raise TypeError("EventGridEvent is not supported for Event Grid Namespaces.")
            try:
                # Try to send via namespace
                self._send(self._namespace, _serialize_events(events), **kwargs)
            except Exception as exception:  # pylint: disable=broad-except
                self._http_response_error_handler(exception, "Namespace")
                raise exception
        else:
            try:
                self._send(events, channel_name=channel_name, **kwargs)
            except Exception as exception:
                self._http_response_error_handler(exception, "Basic")
                raise exception

    def _http_response_error_handler(self, exception, level):
        if isinstance(exception, HttpResponseError):
            if exception.status_code == 400:
                raise HttpResponseError("Invalid event data. Please check the data and try again.") from exception
            if exception.status_code == 404:
                raise ResourceNotFoundError(
                    "Resource not found. "
                    f"Please check that the tier you are using, corresponds to the correct "
                    "endpoint and/or topic name."
                ) from exception
            raise exception


class EventGridConsumerClientOperationsMixin(OperationsConsumerMixin):

    @distributed_trace
    def receive(
        self,
        topic_name: str,
        subscription_name: str,
        *,
        max_events: Optional[int] = None,
        max_wait_time: Optional[int] = None,
        **kwargs: Any,
    ) -> ReceiveResult:
        """Receive Batch of Cloud Events from the Event Subscription.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param subscription_name: Event Subscription Name. Required.
        :type subscription_name: str
        :keyword max_events: Max Events count to be received. Minimum value is 1, while maximum value
         is 100 events. If not specified, the default value is 1. Default value is None.
        :paramtype max_events: int
        :keyword max_wait_time: Max wait time value for receive operation in Seconds. It is the time in
         seconds that the server approximately waits for the availability of an event and responds to
         the request. If an event is available, the broker responds immediately to the client. Minimum
         value is 10 seconds, while maximum value is 120 seconds. If not specified, the default value is
         60 seconds. Default value is None.
        :paramtype max_wait_time: int
        :return: ReceiveResult. The ReceiveResult is compatible with MutableMapping
        :rtype: ~azure.eventgrid.models.ReceiveResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        detail_items = []
        received_result = self._receive(
            topic_name,
            subscription_name,
            max_events=max_events,
            max_wait_time=max_wait_time,
            **kwargs,
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

    @distributed_trace
    def acknowledge(
        self,
        topic_name: str,
        subscription_name: str,
        *,
        lock_tokens: List[str],
        **kwargs: Any,
    ) -> _models.AcknowledgeResult:
        """Acknowledge batch of Cloud Events. The server responds with an HTTP 200 status code if the
        request is successfully accepted. The response body will include the set of successfully
        acknowledged lockTokens, along with other failed lockTokens with their corresponding error
        information. Successfully acknowledged events will no longer be available to any consumer.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param subscription_name: Event Subscription Name. Required.
        :type subscription_name: str
        :keyword lock_tokens: Array of lock tokens of Cloud Events. Required.
        :paramtype lock_tokens: List[str]
        :return: AcknowledgeResult. The AcknowledgeResult is compatible with MutableMapping
        :rtype: ~azure.eventgrid.models.AcknowledgeResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        options = AcknowledgeOptions(lock_tokens=lock_tokens)
        return super()._acknowledge(
            topic_name=topic_name,
            event_subscription_name=subscription_name,
            acknowledge_options=options,
            **kwargs,
        )

    @distributed_trace
    @api_version_validation(
        params_added_on={"2023-10-01-preview": ["release_delay"]},
    )
    def release(
        self,
        topic_name: str,
        subscription_name: str,
        *,
        lock_tokens: List[str],
        release_delay: Optional[Union[int, _models.ReleaseDelay]] = None,
        **kwargs: Any,
    ) -> _models.ReleaseResult:
        """Release batch of Cloud Events. The server responds with an HTTP 200 status code if the request
        is successfully accepted. The response body will include the set of successfully released
        lockTokens, along with other failed lockTokens with their corresponding error information.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param subscription_name: Event Subscription Name. Required.
        :type subscription_name: str
        :keyword lock_tokens: Array of lock tokens of Cloud Events. Required.
        :paramtype lock_tokens: List[str]
        :keyword release_delay: Release cloud events with the specified delay in seconds.
         Known values are: 0, 10, 60, 600, and 3600. Default value is None.
        :paramtype release_delay: int or ~azure.eventgrid.models.ReleaseDelay or None
        :return: ReleaseResult. The ReleaseResult is compatible with MutableMapping
        :rtype: ~azure.eventgrid.models.ReleaseResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        options = ReleaseOptions(lock_tokens=lock_tokens)
        return super()._release(
            topic_name=topic_name,
            event_subscription_name=subscription_name,
            release_options=options,
            release_delay_in_seconds=release_delay,
            **kwargs,
        )

    @distributed_trace
    def reject(
        self,
        topic_name: str,
        subscription_name: str,
        *,
        lock_tokens: List[str],
        **kwargs: Any,
    ) -> _models.RejectResult:
        """Reject batch of Cloud Events. The server responds with an HTTP 200 status code if the request
        is successfully accepted. The response body will include the set of successfully rejected
        lockTokens, along with other failed lockTokens with their corresponding error information.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param subscription_name: Event Subscription Name. Required.
        :type subscription_name: str
        :keyword lock_tokens: Array of lock tokens of Cloud Events. Required.
        :paramtype lock_tokens: List[str]
        :return: RejectResult. The RejectResult is compatible with MutableMapping
        :rtype: ~azure.eventgrid.models.RejectResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        options = RejectOptions(lock_tokens=lock_tokens)
        return super()._reject(
            topic_name=topic_name,
            event_subscription_name=subscription_name,
            reject_options=options,
            **kwargs,
        )

    @distributed_trace
    @api_version_validation(
        method_added_on="2023-10-01-preview",
    )
    def renew_cloud_event_locks(
        self,
        topic_name: str,
        subscription_name: str,
        *,
        lock_tokens: List[str],
        **kwargs: Any,
    ) -> _models.RenewCloudEventLocksResult:
        """Renew lock for batch of Cloud Events. The server responds with an HTTP 200 status code if the
        request is successfully accepted. The response body will include the set of successfully
        renewed lockTokens, along with other failed lockTokens with their corresponding error
        information.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param subscription_name: Event Subscription Name. Required.
        :type subscription_name: str
        :keyword lock_tokens: Array of lock tokens of Cloud Events. Required.
        :paramtype lock_tokens: List[str]
        :return: RenewCloudEventLocksResult. The RenewCloudEventLocksResult is compatible with
         MutableMapping
        :rtype: ~azure.eventgrid.models.RenewCloudEventLocksResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        options = RenewLockOptions(lock_tokens=lock_tokens)
        return super()._renew_lock(
            topic_name=topic_name,
            event_subscription_name=subscription_name,
            renew_lock_options=options,
            **kwargs,
        )


def _serialize_events(events):
    if isinstance(events[0], CloudEvent) or _is_cloud_event(events[0]):
        # Try to serialize cloud events
        try:
            internal_body_list = []
            for item in events:
                internal_body_list.append(_serialize_cloud_event(item))
            return internal_body_list
        except AttributeError:
            # Try to serialize CNCF Cloud Events
            return [_from_cncf_events(e) for e in events]
    else:
        # Does not conform to format, send as is
        return json.dumps(events)


def _serialize_cloud_event(cloud_event):
    data_kwargs = {}

    if isinstance(cloud_event.data, bytes):
        data_kwargs["data_base64"] = cloud_event.data
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
    )
    if cloud_event.extensions:
        internal_event.update(cloud_event.extensions)
    return internal_event


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
