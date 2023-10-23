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
from azure.core.exceptions import HttpResponseError
from azure.core.messaging import CloudEvent
from azure.core.tracing.decorator import distributed_trace
from ._operations import EventGridClientOperationsMixin as OperationsMixin
from .._model_base import AzureJSONEncoder
from ..models._models import CloudEvent as InternalCloudEvent
from ..models._patch import ReceiveResult, ReceiveDetails
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, HttpResponse
from azure.core.utils import case_insensitive_dict
from .. import models as _models
from .._model_base import _deserialize
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
            if self._binary_mode:
                self._publish_binary_mode(topic_name, body, self._config.api_version, **kwargs)
            else:
                internal_body = _cloud_event_to_generated(body)
                self._publish_cloud_event(topic_name, internal_body, **kwargs)
        else:
            kwargs["content_type"] = "application/cloudevents-batch+json; charset=utf-8"
            internal_body_list = []
            for item in body:
                internal_body_list.append(_cloud_event_to_generated(item))
            if self._binary_mode:
                raise HttpResponseError("Binary mode is not supported for batch events.")
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

    def _publish_binary_mode(self, topic_name: str, event: Any, api_version, **kwargs: Any) -> None:

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
    binary_mode = kwargs.pop("binary_mode", True)

    # Content of the request is the data, if already in binary - no work needed
    _content = _check_content_type(event.data)
 
    # content_type must be CloudEvent DataContentType when in binary mode
    default_content_type = kwargs.pop('content_type', _headers.pop('content-type', "application/cloudevents+json; charset=utf-8"))
    content_type: str = event.datacontenttype or default_content_type

    api_version: str = kwargs.pop('api_version', _params.pop('api-version', "2023-06-01-preview"))
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
        _headers['ce-extensions'] = _SERIALIZER.header('ce-extensions', event.extensions, 'dict')

    return HttpRequest(
        method="POST",
        url=_url,
        params=_params,
        headers=_headers,
        content=_content, # pass through content
        **kwargs
    )

def _check_content_type(data: Any) -> None:
    # Check the content type of the data and convert to bytes if needed
    if isinstance(data, bytes):
        return data
    elif isinstance(data, str):
        return data.encode("utf-8")
    else:
        try:
            return json.dumps(event, cls=AzureJSONEncoder, exclude_readonly=True)  # type: ignore
        except:
            raise TypeError("Incorrect type for data. Expected bytes, str, or JSON serializable object to encode.")


__all__: List[str] = [
    "EventGridClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
