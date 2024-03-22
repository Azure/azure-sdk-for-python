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
from ..._legacy import EventGridEvent
from ... import models as _models
from ..._model_base import _deserialize

from ..._operations._patch import _serialize_events, EVENT_TYPES_BASIC, EVENT_TYPES_STD, validate_args

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
        """Send events to the Event Grid Service.

        :param event: The event to send.
        :type event: CloudEvent or List[CloudEvent] or EventGridEvent or List[EventGridEvent]
         or Dict[str, Any] or List[Dict[str, Any]] or CNCFCloudEvent or List[CNCFCloudEvent]
         or CloudEventDict or List[CloudEventDict] or EventGridEventDict or List[EventGridEventDict]
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
        """Send events to the Event Grid Service.

        :param event: The event to send.
        :type event: CloudEvent or List[CloudEvent] or CloudEventDict or List[CloudEventDict]
        :keyword topic_name: The name of the topic to send the event to.
        :paramtype topic_name: str
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
            "Basic": ["channel_name", "content_type"],
            "Standard": ["binary_mode", "content_type"],
        }
    )
    @distributed_trace_async
    async def send(self, /, event, topic_name = None, *, binary_mode = False, channel_name = None, **kwargs) -> None:
        """Send events to the Event Grid Service."""
        
        channel_name = kwargs.pop("channel_name", None)
        binary_mode = kwargs.pop("binary_mode", False)

        if self._level == "Standard" and topic_name is None:
            raise ValueError("Topic name is required for standard level client.")
        
        # check binary mode
        if binary_mode:

            # If data is passed as a dictionary, make sure it is a CloudEvent
            try:
                if isinstance(event, dict):
                    event = CloudEvent.from_dict(event)
            except AttributeError:
                raise TypeError("Binary mode is only supported for type CloudEvent.")
            
            # If data is a cloud event, convert to an HTTP Request in binary mode
            if isinstance(event, CloudEvent):
                kwargs["content_type"] = "application/cloudevents+json; charset=utf-8"
                self._publish(
                    topic_name, event, self._config.api_version, binary_mode, **kwargs
                )  
            else:
                raise TypeError("Binary mode is only supported for type CloudEvent.")   

        else:
            # If no binary_mode is set, send whatever event is passed
            if self._level == "Standard": 
                
                try:
                    if isinstance(event, dict):
                        event = CloudEvent.from_dict(event)
                    if isinstance(event, list) and isinstance(event[0], dict):
                        event = [CloudEvent.from_dict(e) for e in event]
                except Exception:
                    pass

                try:
                    kwargs["content_type"] = "application/cloudevents-batch+json; charset=utf-8"
                    if not isinstance(event, list):
                        event = [event]
                    await self._publish_cloud_events(topic_name, _serialize_events(event), **kwargs)
                except HttpResponseError as e:
                    if e.status_code == 400:
                        raise HttpResponseError("Invalid event data. Please check the data and try again.") from e
                    else:
                        raise e
            else:
                await self._client.send(event, channel_name=channel_name, **kwargs)


    @use_standard_only
    @distributed_trace_async
    async def receive_cloud_events(
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
        receive_result = await self._receive_cloud_events(
            topic_name,
            event_subscription_name,
            max_events=max_events,
            max_wait_time=max_wait_time,
            **kwargs
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
        event_subscription_name: str,
        acknowledge_options: Union[_models.AcknowledgeOptions, JSON, IO],
        **kwargs: Any
    ) -> _models.AcknowledgeResult:
        return await self._acknowledge_cloud_events(
            topic_name, event_subscription_name, acknowledge_options, **kwargs
        )

    @use_standard_only
    @distributed_trace_async
    async def release_cloud_events(
        self,
        topic_name: str,
        event_subscription_name: str,
        release_options: Union[_models.ReleaseOptions, JSON, IO],
        *,
        release_delay_in_seconds: Optional[Union[int, _models.ReleaseDelay]] = None,
        **kwargs: Any
    ) -> _models.ReleaseResult:
        return await self._release_cloud_events(
            topic_name,
            event_subscription_name,
            release_options,
            release_delay_in_seconds=release_delay_in_seconds,
            **kwargs
        )

    @use_standard_only
    @distributed_trace_async
    async def reject_cloud_events(
        self,
        topic_name: str,
        event_subscription_name: str,
        reject_options: Union[_models.RejectOptions, JSON, IO],
        **kwargs: Any
    ) -> _models.RejectResult:
        return await self._reject_cloud_events(
            topic_name, event_subscription_name, reject_options, **kwargs
        )

    @use_standard_only
    @distributed_trace_async
    async def renew_cloud_event_locks(
        self,
        topic_name: str,
        event_subscription_name: str,
        renew_lock_options: Union[_models.RenewLockOptions, JSON, IO],
        **kwargs: Any
    ) -> _models.RenewCloudEventLocksResult:
        return await self._renew_cloud_event_locks(
            topic_name, event_subscription_name, renew_lock_options, **kwargs
        )

    async def _publish(
        self, topic_name: str, event: Any, api_version, binary_mode, **kwargs: Any
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

        content_type: str = kwargs.pop(
            "content_type",
            _headers.pop("content-type", "application/cloudevents+json; charset=utf-8"),
        )

        # Given that we know the cloud event is binary mode, we can convert it to a HTTP request
        http_request = _to_http_request(
            topic_name=topic_name,
            api_version=api_version,
            headers=_headers,
            params=_params,
            content_type=content_type,
            event=event,
            binary_mode=binary_mode,
            **kwargs
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
