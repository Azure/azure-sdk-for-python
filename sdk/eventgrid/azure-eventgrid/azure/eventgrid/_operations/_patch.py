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
    IO,
    List,
    Optional,
    TypeVar,
    Union,
    overload,
    TYPE_CHECKING,
)

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.messaging import CloudEvent
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.utils import case_insensitive_dict

from ._operations import EventGridClientOperationsMixin as OperationsMixin
from .._model_base import _deserialize
from ..models._patch import (
    ReceiveResult,
    ReceiveDetails,
)
from .. import models as _models
from ..models._models import AcknowledgeOptions, ReleaseOptions, RejectOptions, RenewLockOptions
from .._validation import api_version_validation


from .._legacy import EventGridEvent
from .._legacy._helpers import _from_cncf_events, _is_eventgrid_event
from .._serialization import Serializer

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object
T = TypeVar("T")
ClsType = Optional[
    Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]
]
_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False

if TYPE_CHECKING:
    from cloudevents.http.event import CloudEvent as CNCFCloudEvent

EVENT_TYPES_BASIC = Union[
    CloudEvent,
    List[CloudEvent],
    Dict[str, Any],
    List[Dict[str, Any]],
    EventGridEvent,
    List[EventGridEvent],
    "CNCFCloudEvent",
    List["CNCFCloudEvent"],
]
EVENT_TYPES_STD = Union[
    CloudEvent,
    List[CloudEvent],
    Dict[str, Any],
    List[Dict[str, Any]],
]


def use_standard_only(func):
    """Use the standard client only.

    This decorator raises an AttributeError if the client is not a standard client.

    :param func: The function to decorate.
    :type func: Callable
    :return: The decorated function.
    :rtype: Callable
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._level == "Basic":  # pylint: disable=protected-access
            raise ValueError(
                "The basic client is not supported for this operation."
            )
        return func(self, *args, **kwargs)

    return wrapper


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
                    if arg
                    in kwargs.keys()  # pylint: disable=consider-iterating-dictionary
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


class EventGridClientOperationsMixin(OperationsMixin):

    @overload
    def send(
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
    def send(
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
    @distributed_trace
    def send(self, *args, **kwargs) -> None:
        """Send events to the Event Grid Service.

        :param topic_name: The name of the topic to send the event to.
        :type topic_name: str
        :param event: The event to send.
        :type event: CloudEvent or List[CloudEvent] or Dict[str, Any] or List[Dict[str, Any]]
         or CNCFCloudEvent or List[CNCFCloudEvent] or EventGridEvent or List[EventGridEvent]
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

            .. literalinclude:: ../samples/sync_samples/eventgrid_client_samples/sample_publish_operation.py
                :start-after: [START publish_cloud_event]
                :end-before: [END publish_cloud_event]
                :language: python
                :dedent: 0
                :caption: Publishing a Cloud Event to a Namespace Topic.

            .. literalinclude:: ../samples/sync_samples/sample_publish_events_using_cloud_events_1.0_schema.py
                :start-after: [START publish_cloud_event_to_topic]
                :end-before: [END publish_cloud_event_to_topic]
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
            self._send_binary(topic_name, events, **kwargs)
        else:
            # If not binary_mode send whatever event is passed

            # If a cloud event dict, convert to CloudEvent for serializing
            try:
                if isinstance(events, dict):
                    events = CloudEvent.from_dict(events)
                if isinstance(events, list) and isinstance(events[0], dict):
                    events = [CloudEvent.from_dict(e) for e in events]
            except Exception:  # pylint: disable=broad-except
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
                    self._send(topic_name, _serialize_events(events), **kwargs)
                except Exception as exception:  # pylint: disable=broad-except
                    self._http_response_error_handler(exception, "Standard")
                    raise exception
            else:
                try:
                    self._send(events, channel_name=channel_name, **kwargs)
                except Exception as exception:
                    self._http_response_error_handler(exception, "Basic")
                    raise exception

    def _send_binary(self, topic_name, events, **kwargs):
        # If data is passed as a dictionary, make sure it is a CloudEvent
        try:
            if isinstance(events, dict):
                events = CloudEvent.from_dict(events)
        except AttributeError:
            raise TypeError(  # pylint: disable=raise-missing-from
                "Binary mode is only supported for type CloudEvent."
            )

        # If data is a cloud event, convert to an HTTP Request in binary mode
        # Content type becomes the data content type
        if isinstance(events, CloudEvent):
            self._publish(topic_name, events, self._config.api_version, **kwargs)
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

    def _publish(
        self,
        topic_name: str,
        event: Any,
        api_version: str,
        **kwargs: Any,
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

        content_type = kwargs.pop( # pylint: disable=unused-variable
            "content_type", None
        )
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

        pipeline_response: PipelineResponse = (
            self._client._pipeline.run(  # pylint: disable=protected-access
                http_request, stream=_stream, **kwargs
            )
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                response.read()  # Load the body in memory and close the socket
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

    @use_standard_only
    @distributed_trace
    def receive_cloud_events(
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
        received_result = self._receive_cloud_events(
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

    @use_standard_only
    @distributed_trace
    def acknowledge_cloud_events(
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
        return super()._acknowledge_cloud_events(
            topic_name=topic_name,
            event_subscription_name=subscription_name,
            acknowledge_options=options,
            **kwargs,
        )

    @use_standard_only
    @distributed_trace
    @api_version_validation(
        params_added_on={"2023-10-01-preview": ["release_delay"]},
    )
    def release_cloud_events(
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
        return super()._release_cloud_events(
            topic_name=topic_name,
            event_subscription_name=subscription_name,
            release_options=options,
            release_delay_in_seconds=release_delay,
            **kwargs,
        )

    @use_standard_only
    @distributed_trace
    def reject_cloud_events(
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
        return super()._reject_cloud_events(
            topic_name=topic_name,
            event_subscription_name=subscription_name,
            reject_options=options,
            **kwargs,
        )

    @use_standard_only
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
        return super()._renew_cloud_event_locks(
            topic_name=topic_name,
            event_subscription_name=subscription_name,
            renew_lock_options=options,
            **kwargs,
        )


def _to_http_request(topic_name: str, **kwargs: Any) -> HttpRequest:
    # Create a HTTP request for a binary mode CloudEvent

    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    event = kwargs.pop("event")

    # Content of the request is the data, if already in binary - no work needed
    try:
        if isinstance(event.data, bytes):
            _content = event.data
        else:
            raise TypeError(
                "CloudEvent data must be bytes when in binary mode."
                "Did you forget to call `json.dumps()` and/or `encode()` on CloudEvent data?"
            )
    except AttributeError as exc:
        raise TypeError(
            "Binary mode is not supported for batch CloudEvents."
            " Set `binary_mode` to False when passing in a batch of CloudEvents."
        ) from exc

    # content_type must be CloudEvent DataContentType when in binary mode
    if not event.datacontenttype:
        raise ValueError("CloudEvent datacontenttype must be set when in binary mode.")
    content_type: str = event.datacontenttype

    api_version: str = kwargs.pop(
        "api_version", _params.pop("api-version", "2023-10-01-preview")
    )
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/topics/{topicName}:publish"
    path_format_arguments = {
        "topicName": _SERIALIZER.url("topic_name", topic_name, "str"),
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    _params["api-version"] = _SERIALIZER.query("api_version", api_version, "str")

    # Construct headers
    _headers["content-type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    # Cloud Headers
    _headers["ce-source"] = _SERIALIZER.header("ce-source", event.source, "str")
    _headers["ce-type"] = _SERIALIZER.header("ce-type", event.type, "str")
    if event.specversion:
        _headers["ce-specversion"] = _SERIALIZER.header(
            "ce-specversion", event.specversion, "str"
        )
    if event.id:
        _headers["ce-id"] = _SERIALIZER.header("ce-id", event.id, "str")
    if event.time:
        _headers["ce-time"] = _SERIALIZER.header("ce-time", event.time, "str")
    if event.dataschema:
        _headers["ce-dataschema"] = _SERIALIZER.header(
            "ce-dataschema", event.dataschema, "str"
        )
    if event.subject:
        _headers["ce-subject"] = _SERIALIZER.header("ce-subject", event.subject, "str")
    if event.extensions:
        for extension, value in event.extensions.items():
            _headers[f"ce-{extension}"] = _SERIALIZER.header(
                "ce-extensions", value, "str"
            )

    return HttpRequest(
        method="POST",
        url=_url,
        params=_params,
        headers=_headers,
        content=_content,  # pass through content
        **kwargs,
    )


def _serialize_events(events):
    if isinstance(events[0], CloudEvent):
        internal_body_list = []
        for item in events:
            internal_body_list.append(_serialize_cloud_event(item))
        return json.dumps(internal_body_list)
    try:
        serialize = Serializer()
        body = serialize.body(events, "[object]")
        if body is None:
            data = None
        else:
            data = json.dumps(body)

        return data
    except AttributeError:
        return events


def _serialize_cloud_event(event):
    try:
        data = {}
        # CloudEvent required fields but validate they are not set to None
        if event.type:
            data["type"] = _SERIALIZER.body(event.type, "str")
        if event.specversion:
            data["specversion"] = _SERIALIZER.body(event.specversion, "str")
        if event.source:
            data["source"] = _SERIALIZER.body(event.source, "str")
        if event.id:
            data["id"] = _SERIALIZER.body(event.id, "str")

        # Check if data is bytes and serialize to base64
        if isinstance(event.data, bytes):
            data["data_base64"] = _SERIALIZER.serialize_bytearray(event.data)
        elif event.data:
            data["data"] = _SERIALIZER.body(event.data, "str")

        if event.subject:
            data["subject"] = _SERIALIZER.body(event.subject, "str")
        if event.time:
            data["time"] = _SERIALIZER.body(event.time, "str")
        if event.datacontenttype:
            data["datacontenttype"] = _SERIALIZER.body(event.datacontenttype, "str")
        if event.extensions:
            for extension, value in event.extensions.items():
                data[extension] = _SERIALIZER.body(value, "str")

        return data
    except AttributeError:
        return [_from_cncf_events(e) for e in event]


__all__: List[str] = [
    "EventGridClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
