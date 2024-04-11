# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, overload, Union, Any, Optional, Callable, Dict, TypeVar, IO
import sys
from azure.core.messaging import CloudEvent
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, AsyncHttpResponse
from azure.core.utils import case_insensitive_dict
from ...models._patch import ReceiveResult, ReceiveDetails
from ..._operations._patch import _to_http_request, use_standard_only
from ._operations import EventGridClientOperationsMixin as OperationsMixin
from ... import models as _models
from ...models._models import AcknowledgeOptions, ReleaseOptions, RejectOptions, RenewLockOptions
from ..._model_base import _deserialize
from ..._validation import api_version_validation

from ..._operations._patch import (
    _serialize_events,
    EVENT_TYPES_BASIC,
    EVENT_TYPES_STD,
    validate_args,
)

from ..._legacy import EventGridEvent
from ..._legacy._helpers import _is_eventgrid_event

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[
    Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]
]


class EventGridClientOperationsMixin(OperationsMixin):

    @overload
    async def send(
        self,
        events: EVENT_TYPES_BASIC,
        *,
        channel_name: Optional[str] = None,
        content_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Send events to the Event Grid Basic Service.

        :param event: The event to send.
        :type event: CloudEvent or List[CloudEvent] or EventGridEvent or List[EventGridEvent]
         or Dict[str, Any] or List[Dict[str, Any]] or CNCFCloudEvent or List[CNCFCloudEvent]
        :keyword channel_name: The name of the channel to send the event to.
        :paramtype channel_name: str or None
        :keyword content_type: The content type of the event. If not specified, the default value is
         "application/cloudevents+json; charset=utf-8".
        :paramtype content_type: str or None

        :return: None
        :rtype: None
        """
        ...

    @overload
    async def send(
        self,
        topic_name: str,
        events: EVENT_TYPES_STD,
        *,
        binary_mode: bool = False,
        content_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Send events to the Event Grid Namespace Service.

        :param topic_name: The name of the topic to send the event to.
        :type topic_name: str
        :param event: The event to send.
        :type event: CloudEvent or List[CloudEvent] or Dict[str, Any] or List[Dict[str, Any]]
        :keyword binary_mode: Whether to send the event in binary mode. If not specified, the default
         value is False.
        :paramtype binary_mode: bool
        :keyword content_type: The content type of the event. If not specified, the default value is
         "application/cloudevents+json; charset=utf-8".
        :paramtype content_type: str or None

        :return: None
        :rtype: None
        """
        ...

    @validate_args(
        kwargs_mapping={
            "Basic": ["channel_name"],
            "Standard": ["binary_mode"],
        }
    )
    @distributed_trace_async
    async def send(self, *args, **kwargs) -> None:
        """Send events to the Event Grid Namespace Service.

        :param topic_name: The name of the topic to send the event to.
        :type topic_name: str
        :param event: The event to send.
        :type event: CloudEvent or List[CloudEvent] or Dict[str, Any] or List[Dict[str, Any]]
        :keyword binary_mode: Whether to send the event in binary mode. If not specified, the default
         value is False.
        :paramtype binary_mode: bool
        :keyword channel_name: The name of the channel to send the event to.
        :paramtype channel_name: str or None
        :keyword content_type: The content type of the event. If not specified, the default value is
         "application/cloudevents+json; charset=utf-8".
        :paramtype content_type: str

        :return: None
        :rtype: None

        A single instance or a list of dictionaries, CloudEvents are accepted. In the case of an Azure Event Grid
        Basic Resource, EventGridEvent(s) and CNCFCloudEvents are also accepted.

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/eventgrid_client_samples/sample_publish_operation_async.py
                :start-after: [START publish_cloud_event_async]
                :end-before: [END publish_cloud_event_async]
                :language: python
                :dedent: 0
                :caption: Publishing a Cloud Event to a Namespace Topic.

            .. literalinclude:: ../samples/async_samples/sample_publish_events_using_cloud_events_1.0_schema_async.py
                :start-after: [START publish_cloud_event_to_topic_async]
                :end-before: [END publish_cloud_event_to_topic_async]
                :language: python
                :dedent: 0
                :caption: Publishing a CloudEvent to a Basic Topic.
        """
        # Check kwargs
        channel_name = kwargs.pop("channel_name", None)
        binary_mode = kwargs.pop("binary_mode", False)
        topic_name = kwargs.pop("topic_name", None)
        events = kwargs.pop("events", None)

        # both there
        if len(args) > 1:
            if events is not None:
                raise ValueError("events is already passed as a keyword argument.")
            if topic_name is not None:
                raise ValueError("topic_name is already passed as a keyword argument.")
            events = args[1]
            topic_name = args[0]

        elif len(args) == 1:
            if events is not None:
                if topic_name is not None:
                    raise ValueError(
                        "topic_name is already passed as a keyword argument."
                    )
                topic_name = args[0]
            else:
                events = args[0]

        if self._level == "Standard" and topic_name is None:
            raise ValueError("Topic name is required for standard level client.")

        # check binary mode
        if binary_mode:
            await self._send_binary(topic_name, events, **kwargs)
        else:
            # If no binary_mode is set, send whatever event is passed

            # If a cloud event dict, convert to CloudEvent for serializing
            try:
                if isinstance(events, dict):
                    events = CloudEvent.from_dict(events)
                if isinstance(events, list) and isinstance(events[0], dict):
                    events = [CloudEvent.from_dict(e) for e in events]
            except Exception: # pylint: disable=broad-except
                pass

            if self._level == "Standard":
                kwargs["content_type"] = kwargs.get(
                    "content_type", "application/cloudevents-batch+json; charset=utf-8"
                )
                if not isinstance(events, list):
                    events = [events]

                if isinstance(events[0], EventGridEvent) or _is_eventgrid_event(events[0]):
                    raise TypeError("EventGridEvent is not supported for standard level client.")
                try:
                    # Try to send via namespace
                    await self._send(topic_name, _serialize_events(events), **kwargs)
                except Exception as exception:  # pylint: disable=broad-except
                    self._http_response_error_handler(exception, "Standard")
                    raise exception
            else:
                try:
                    await self._send(events, channel_name=channel_name, **kwargs)
                except Exception as exception:
                    self._http_response_error_handler(exception, "Basic")
                    raise exception

    async def _send_binary(self, topic_name: str, events: Any, **kwargs: Any) -> None:
        # If data is passed as a dictionary, make sure it is a CloudEvent
        try:
            if isinstance(events, dict):
                events = CloudEvent.from_dict(events)
        except AttributeError:
            raise TypeError("Binary mode is only supported for type CloudEvent.") # pylint: disable=raise-missing-from

        # If data is a cloud event, convert to an HTTP Request in binary mode
        if isinstance(events, CloudEvent):
            await self._publish(
                topic_name, events, self._config.api_version, **kwargs
            )
        else:
            raise TypeError("Binary mode is only supported for type CloudEvent.")

    def _http_response_error_handler(self, exception, level):
        if isinstance(exception, HttpResponseError):
            if exception.status_code == 400:
                raise HttpResponseError(
                    "Invalid event data. Please check the data and try again."
                ) from exception
            if exception.status_code == 404:
                raise ResourceNotFoundError(
                    "Resource not found. "
                    f"Please check that the level set on the client, {level}, corresponds to the correct "
                    "endpoint and/or topic name."
                ) from exception
            raise exception

    @use_standard_only
    @distributed_trace_async
    async def receive_cloud_events(
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
        receive_result = await self._receive_cloud_events(
            topic_name,
            subscription_name,
            max_events=max_events,
            max_wait_time=max_wait_time,
            **kwargs,
        )
        for detail_item in receive_result.value:
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

    @use_standard_only
    @distributed_trace_async
    async def acknowledge_cloud_events(
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
        return await super()._acknowledge_cloud_events(
            topic_name, subscription_name, options, **kwargs
        )

    @use_standard_only
    @distributed_trace_async
    @api_version_validation(
        params_added_on={"2023-10-01-preview": ["release_delay"]},
    )
    async def release_cloud_events(
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
        :paramtype release_delay: int or ~azure.eventgrid.models.ReleaseDelay
        :return: ReleaseResult. The ReleaseResult is compatible with MutableMapping
        :rtype: ~azure.eventgrid.models.ReleaseResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        options = ReleaseOptions(lock_tokens=lock_tokens)
        return await super()._release_cloud_events(
            topic_name,
            subscription_name,
            options,
            release_delay_in_seconds=release_delay,
            **kwargs,
        )

    @use_standard_only
    @distributed_trace_async
    async def reject_cloud_events(
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
        return await super()._reject_cloud_events(
            topic_name, subscription_name, options, **kwargs
        )

    @use_standard_only
    @distributed_trace_async
    @api_version_validation(
        method_added_on="2023-10-01-preview",
    )
    async def renew_cloud_event_locks(
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
        return await super()._renew_cloud_event_locks(
            topic_name, subscription_name, options, **kwargs
        )

    async def _publish(
        self, topic_name: str, event: Any, api_version, **kwargs: Any
    ) -> None:

        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[_models._models.PublishResult] = kwargs.pop(
            "cls", None
        )  # pylint: disable=protected-access

        content_type = kwargs.pop("content_type", None) # pylint: disable=unused-variable
        # Given that we know the cloud event is binary mode, we can convert it to a HTTP request
        http_request = _to_http_request(
            topic_name=topic_name,
            api_version=api_version,
            headers=_headers,
            params=_params,
            event=event,
            **kwargs,
        )

        _stream = kwargs.pop("stream", False)

        path_format_arguments = {
            "endpoint": self._serialize.url(
                "self._config.endpoint", self._config.endpoint, "str", skip_quote=True
            ),
        }
        http_request.url = self._client.format_url(
            http_request.url, **path_format_arguments
        )

        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            http_request, stream=_stream, **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                await response.read()  # Load the body in memory and close the socket
            map_error(
                status_code=response.status_code, response=response, error_map=error_map
            )
            raise HttpResponseError(response=response)

        if _stream:
            deserialized = response.iter_bytes()
        else:
            deserialized = _deserialize(
                _models._models.PublishResult,  # pylint: disable=protected-access
                response.json(),
            )

        if cls:
            return cls(pipeline_response, deserialized, {})  # type: ignore

        return deserialized  # type: ignore


__all__: List[str] = [
    "EventGridClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
