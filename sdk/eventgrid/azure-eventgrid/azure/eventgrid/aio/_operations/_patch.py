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
from ..._operations._patch import _to_http_request
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
         When True and `datacontenttype` is specified in CloudEvent, content type is set to `datacontenttype`.
         If 'datacontenttype` is not specified the default content type is `application/cloudevents-batch+json; charset=utf-8`.
         Requires CloudEvent data to be passed in as bytes.
        :keyword content_type: content type. Default value is "application/cloudevents-batch+json;
         charset=utf-8".
        :paramtype content_type: str
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
    async def publish_cloud_events(
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
    async def publish_cloud_events(
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
        :keyword content_type: content type. Default value is "application/cloudevents+json;
         charset=utf-8".
        :paramtype content_type: str
        :return: None
        :rtype: None
        :raises ~azure.core.exceptions.HttpResponseError:
        """

    @distributed_trace_async
    async def publish_cloud_events(
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
        :param body: Cloud Event or Array of Cloud Events being published. Required.
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
            await self._publish(topic_name, body, self._config.api_version, binary_mode, **kwargs)
        elif isinstance(body, list):
            kwargs["content_type"] = "application/cloudevents-batch+json; charset=utf-8"
            await self._publish(topic_name, body, self._config.api_version, binary_mode, **kwargs)
        else:
            raise TypeError("Incorrect type for body. Expected CloudEvent,"
                            " list of CloudEvents, dict, or list of dicts."
                            " If dict passed, must follow the CloudEvent format.")

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

    async def _publish(self, topic_name: str, event: Any, api_version, binary_mode, **kwargs: Any) -> None:

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

        _stream = kwargs.pop("stream", False)
        pipeline_response: PipelineResponse = await self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
            http_request,
            stream=_stream,
            **kwargs
        )

        response = pipeline_response.http_response

        if response.status_code not in [200]:
            if _stream:
                await  response.read()  # Load the body in memory and close the socket
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
