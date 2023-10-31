# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, overload, Union, Any, Optional, Callable, Dict, TypeVar
import sys
from azure.core.messaging import CloudEvent
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, ResourceNotModifiedError, map_error
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.pipeline import PipelineResponse
from azure.core.rest import HttpRequest, AsyncHttpResponse
from azure.core.utils import case_insensitive_dict
from ...models._patch import ReceiveResult, ReceiveDetails
from ..._operations._patch import _cloud_event_to_generated, _to_http_request
from ._operations import EventGridClientOperationsMixin as OperationsMixin
from ... import models as _models
from ..._model_base import _deserialize
if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any] # pylint: disable=unsubscriptable-object
T = TypeVar('T')
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]

class EventGridClientOperationsMixin(OperationsMixin):
    @overload
    async def publish_cloud_events(
        self,
        topic_name: str,
        body: List[CloudEvent],
        *,
        binary_mode: Optional[bool] = False,
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
        :keyword bool binary_mode: Whether to use binary mode for sending events. Defaults to False.
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
    async def publish_cloud_events(
        self,
        topic_name: str,
        body: CloudEvent,
        *,
        binary_mode: Optional[bool] = False,
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
        :keyword bool binary_mode: Whether to use binary mode for sending events. Defaults to False.
        :keyword content_type: content type. Default value is "application/cloudevents+json;
         charset=utf-8".
        :paramtype content_type: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @overload
    async def publish_cloud_events(
        self,
        topic_name: str,
        body: Dict[str, Any],
        *,
        binary_mode: Optional[bool] = False,
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
        :type body: dict
        :keyword bool binary_mode: Whether to use binary mode for sending events. Defaults to False.
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
    async def publish_cloud_events(
        self, topic_name: str, body: Union[List[CloudEvent], CloudEvent, Dict[str, Any]], *, binary_mode: Optional[bool] = False, **kwargs
    ) -> None:
        """Publish Batch Cloud Event or Events to namespace topic. In case of success, the server responds with an
        HTTP 200 status code with an empty JSON object in response. Otherwise, the server can return
        various error codes. For example, 401: which indicates authorization failure, 403: which
        indicates quota exceeded or message is too large, 410: which indicates that specific topic is
        not found, 400: for bad request, and 500: for internal server error.

        :param topic_name: Topic Name. Required.
        :type topic_name: str
        :param body: Cloud Event or Array of Cloud Events being published. Required.
        :type body: ~azure.core.messaging.CloudEvent or list[~azure.core.messaging.CloudEvent] or dict[str, Any]
        :keyword bool binary_mode: Whether to use binary mode for sending events. Defaults to False.
        :keyword content_type: content type. Default value is "application/cloudevents+json;
         charset=utf-8".
        :paramtype content_type: str
        :keyword bool stream: Whether to stream the response of this operation. Defaults to False. You
         will have to context manage the returned stream.
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        # Check that the body is a CloudEvent or list of CloudEvents even if dict
        if isinstance(body, dict):
            try:
                body = CloudEvent.from_dict(body)
            except:
                raise TypeError("Incorrect type for body. Expected CloudEvent or list of CloudEvents.")
        if isinstance(body, CloudEvent):
            kwargs["content_type"] = "application/cloudevents+json; charset=utf-8"
            if self._binary_mode:
                self._publish_binary_mode(topic_name, body, self._config.api_version, **kwargs)
            internal_body = _cloud_event_to_generated(body)
            await self._publish_cloud_event(topic_name, internal_body, **kwargs)
        else:
            kwargs["content_type"] = "application/cloudevents-batch+json; charset=utf-8"
            internal_body_list = []
            for item in body:
                internal_body_list.append(_cloud_event_to_generated(item))
            if self._binary_mode:
                raise ValueError("Binary mode is not supported for batch events.")
            await self._publish_cloud_events(topic_name, internal_body_list, **kwargs)

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


__all__: List[str] = [
    "EventGridClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
