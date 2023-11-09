# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import base64
import json
import sys
from typing import Any, Callable, Dict, IO, List, Optional, TypeVar, Union, overload

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, ResourceNotModifiedError, map_error
from azure.core.messaging import CloudEvent
from azure.core.tracing.decorator import distributed_trace
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.utils import case_insensitive_dict

from ._operations import EventGridClientOperationsMixin as OperationsMixin
from .._model_base import _deserialize 
from ..models._patch import ReceiveResult, ReceiveDetails
from .. import models as _models

from .._serialization import Serializer
if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports

JSON = MutableMapping[str, Any] # pylint: disable=unsubscriptable-object
T = TypeVar('T')
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]
_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


class EventGridClientOperationsMixin(OperationsMixin):
    @overload
    def publish_cloud_events(
        self,
        topic_name: str,
        body: List[CloudEvent],
        *,
        binary_mode: bool = False,
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
        :keyword bool binary_mode: Whether to publish a CloudEvent in binary mode. Defaults to False.
         When True and `datacontenttype` is specified in CloudEvent, content type is set to `datacontenttype`. If 'datacontenttype` is not specified,
         the default content type is `application/cloudevents-batch+json; charset=utf-8`.
         Requires CloudEvent data to be passed in as bytes.
        :keyword content_type: content type. Default value is "application/cloudevents-batch+json;
         charset=utf-8".
        :paramtype content_type: str
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
        binary_mode: bool = False,
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
        :keyword bool binary_mode: Whether to publish a CloudEvent in binary mode. Defaults to False.
         When True and `datacontenttype` is specified in CloudEvent, content type is set to `datacontenttype`.
         If `datacontenttype` is not specified, the default content type is `application/cloudevents+json; charset=utf-8`.
         Requires CloudEvent data to be passed in as bytes.
        :keyword content_type: content type. Default value is "application/cloudevents+json;
         charset=utf-8".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    def publish_cloud_events(
        self,
        topic_name: str,
        body: Dict[str, Any],
        *,
        binary_mode: bool = False,
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
        :type body: dict[str, Any]
        :keyword bool binary_mode: Whether to publish a CloudEvent in binary mode. Defaults to False.
         When True and `datacontenttype` is specified in CloudEvent, content type is set to `datacontenttype`.
         If `datacontenttype` is not specified, the default content type is `application/cloudevents+json; charset=utf-8`.
         Requires CloudEvent data to be passed in as bytes.
        :keyword content_type: content type. Default value is "application/cloudevents+json;
         charset=utf-8".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
    
    @overload
    def publish_cloud_events(
        self,
        topic_name: str,
        body: List[Dict[str, Any]],
        *,
        binary_mode: bool = False,
        content_type: str = "application/cloudevents-batch+json; charset=utf-8",
        **kwargs: Any
    ) -> None:
        """Publish Single Cloud Event to namespace topic. In case of success, the server responds with an
        HTTP 200 status code with an empty JSON object in response. Otherwise, the server can return
        various error codes. For example, 401: which indicates authorization failure, 403: which
        indicates quota exceeded or message is too large, 410: which indicates that specific topic is
        not found, 400: for bad request, and 500: for internal server error.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param body: Batch of Cloud Events being published. Required.
        :type body: list[dict[str, Any]]
        :keyword bool binary_mode: Whether to publish a CloudEvent in binary mode. Defaults to False.
         When True and `datacontenttype` is specified in CloudEvent, content type is set to `datacontenttype`.
         If 'datacontenttype` is not specified, the default content type is `application/cloudevents-batch+json; charset=utf-8`.
         Requires CloudEvent data to be passed in as bytes.
        :keyword content_type: content type. Default value is "application/cloudevents-batch+json; charset=utf-8".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
    
    @distributed_trace
    def publish_cloud_events(
        self,
        topic_name: str,
        body: Union[List[CloudEvent], CloudEvent, List[Dict[str, Any]], Dict[str, Any]],
        *,
        binary_mode: bool = False,
        **kwargs
    ) -> None:
        """Publish Batch Cloud Event or Events to namespace topic. In case of success, the server responds with an
        HTTP 200 status code with an empty JSON object in response. Otherwise, the server can return
        various error codes. For example, 401: which indicates authorization failure, 403: which
        indicates quota exceeded or message is too large, 410: which indicates that specific topic is
        not found, 400: for bad request, and 500: for internal server error.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param body: Cloud Event or array of Cloud Events being published. Required.
        :type body: ~azure.core.messaging.CloudEvent or list[~azure.core.messaging.CloudEvent] or dict[str, any] or list[dict[str, any]]
        :keyword bool binary_mode: Whether to publish the events in binary mode. Defaults to False.
         When True and `datacontenttype` is specified in CloudEvent, content type is set to `datacontenttype`.
         If not specified, the default content type is "application/cloudevents+json; charset=utf-8".
         Requires CloudEvent data to be passed in as bytes.
        :keyword content_type: content type. Default value is "application/cloudevents+json;
         charset=utf-8".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        
        # Check that the body is a CloudEvent or list of CloudEvents even if dict
        if isinstance(body, dict) or (isinstance(body, list) and isinstance(body[0], dict)):
            try:
                if isinstance(body, list):
                    body = [CloudEvent.from_dict(event) for event in body]
                else:
                    body = CloudEvent.from_dict(body)
            except AttributeError:
                raise TypeError("Incorrect type for body. Expected CloudEvent,"
                                " list of CloudEvents, dict, or list of dicts."
                                " If dict passed, must follow the CloudEvent format.")


        if isinstance(body, CloudEvent):
            kwargs["content_type"] = "application/cloudevents+json; charset=utf-8"
            self._publish(topic_name, body, self._config.api_version, binary_mode, **kwargs)
        elif isinstance(body, list):
            kwargs["content_type"] = "application/cloudevents-batch+json; charset=utf-8"
            self._publish(topic_name, body, self._config.api_version, binary_mode, **kwargs)
        else:
            raise TypeError("Incorrect type for body. Expected CloudEvent,"
                            " list of CloudEvents, dict, or list of dicts."
                            " If dict passed, must follow the CloudEvent format.")

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

    def _publish(self, topic_name: str, event: Any, api_version: str, binary_mode: Optional[bool] = False, **kwargs: Any) -> None:

        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError, 304: ResourceNotModifiedError
        }
        error_map.update(kwargs.pop('error_map', {}) or {})

        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        cls: ClsType[_models._models.PublishResult] = kwargs.pop(  # pylint: disable=protected-access
            'cls', None
        )

        content_type: str = kwargs.pop('content_type', _headers.pop('content-type', "application/cloudevents+json; charset=utf-8"))

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
            "endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
        }
        http_request.url = self._client.format_url(http_request.url, **path_format_arguments)

        # pipeline_response: PipelineResponse = self.send_request(http_request, **kwargs)
        pipeline_response: PipelineResponse = self._client._pipeline.run(   # pylint: disable=protected-access
            http_request,
            stream=_stream,
            **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                    response.read()  # Load the body in memory and close the socket
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)

        if _stream:
            deserialized = response.iter_bytes()
        else:
            deserialized = _deserialize(
                _models._models.PublishResult,  # pylint: disable=protected-access
                response.json()
            )

        if cls:
            return cls(pipeline_response, deserialized, {}) # type: ignore

        return deserialized # type: ignore


def _to_http_request(topic_name: str, **kwargs: Any) -> HttpRequest:   
    # Create a HTTP request for a binary mode CloudEvent

    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    event = kwargs.pop("event")
    binary_mode = kwargs.pop("binary_mode", False)

    
    if binary_mode:
        # Content of the request is the data, if already in binary - no work needed
        try:
            if isinstance(event.data, bytes):
                _content = event.data
            else:
                raise TypeError("CloudEvent data must be bytes when in binary mode." 
                                "Did you forget to call `json.dumps()` and/or `encode()` on CloudEvent data?")
        except AttributeError:
            raise TypeError("Binary mode is not supported for batch CloudEvents. Set `binary_mode` to False when passing in a batch of CloudEvents.")
    else:
        # Content of the request is the serialized CloudEvent or serialized List[CloudEvent]
        _content = _serialize_cloud_events(event)
    
    # content_type must be CloudEvent DataContentType when in binary mode
    default_content_type = kwargs.pop('content_type', _headers.pop('content-type', "application/cloudevents+json; charset=utf-8"))
    content_type: str = event.datacontenttype if (binary_mode and event.datacontenttype) else default_content_type

    api_version: str = kwargs.pop('api_version', _params.pop('api-version', "2023-10-01-preview"))
    accept = _headers.pop('Accept', "application/json")

    # Construct URL
    _url = "/topics/{topicName}:publish"
    path_format_arguments = {
        "topicName": _SERIALIZER.url("topic_name", topic_name, 'str'),
    }

    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    _params['api-version'] = _SERIALIZER.query("api_version", api_version, 'str')

    # Construct headers
    _headers['content-type'] = _SERIALIZER.header("content_type", content_type, 'str')
    _headers['Accept'] = _SERIALIZER.header("accept", accept, 'str')

    if binary_mode:
        # Cloud Headers
        _headers['ce-source'] = _SERIALIZER.header('ce-source', event.source, 'str')
        _headers['ce-type'] = _SERIALIZER.header('ce-type', event.type, 'str')
        if event.specversion:
            _headers['ce-specversion'] = _SERIALIZER.header('ce-specversion', event.specversion, 'str')
        if event.id:
            _headers['ce-id'] = _SERIALIZER.header('ce-id', event.id, 'str')
        if event.time:
            _headers['ce-time'] = _SERIALIZER.header('ce-time', event.time, 'str')
        if event.dataschema:
            _headers['ce-dataschema'] = _SERIALIZER.header('ce-dataschema', event.dataschema, 'str')
        if event.subject:
            _headers['ce-subject'] = _SERIALIZER.header('ce-subject', event.subject, 'str')
        if event.extensions:
            for extension, value in event.extensions.items():
                _headers[f'ce-{extension}'] = _SERIALIZER.header('ce-extensions', value, 'str')

    return HttpRequest(
        method="POST",
        url=_url,
        params=_params,
        headers=_headers,
        content=_content, # pass through content
        **kwargs
    )

def _serialize_cloud_events(events: Union[CloudEvent, List[CloudEvent]]) -> None:
    # Serialize CloudEvent or List[CloudEvent] into a JSON string
    is_list = isinstance(events, list)
    data = {}
    list_data = []
    for event in events if isinstance(events, list) else [events]:
        # CloudEvent required fields but validate they are not set to None
        if event.type:
            data["type"] =  _SERIALIZER.body(event.type, "str")
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

        # If single cloud event return the data
        if not is_list:
            return json.dumps(data)
        else:
            list_data.append(data)
    # If list of cloud events return the list
    return json.dumps(list_data)


__all__: List[str] = [
    "EventGridClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
