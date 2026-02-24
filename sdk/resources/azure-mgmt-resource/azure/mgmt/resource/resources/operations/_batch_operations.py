# pylint: disable=too-many-lines
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from typing import Any, Callable, Dict, IO, Optional, TypeVar, Union, cast

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import HttpResponse
from azure.core.polling import LROPoller, NoPolling, PollingMethod
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict
from azure.mgmt.core.exceptions import ARMErrorFormat
from azure.mgmt.core.polling.arm_polling import ARMPolling
from msrest import Serializer

from .. import models as _models

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, HttpResponse], T, Dict[str, Any]], Any]]

_SERIALIZER = Serializer()
_SERIALIZER.client_side_validation = False


class BatchOperations:
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.mgmt.resource.ResourceManagementClient`'s
        :attr:`batch_operations` attribute.
    """

    models = _models

    def __init__(self, *args, **kwargs):
        input_args = list(args)
        self._client = input_args.pop(0) if input_args else kwargs.pop("client")
        self._config = input_args.pop(0) if input_args else kwargs.pop("config")
        self._serialize = input_args.pop(0) if input_args else kwargs.pop("serializer")
        self._deserialize = input_args.pop(0) if input_args else kwargs.pop("deserializer")

    @distributed_trace
    def begin_invoke_at_subscription_scope(
        self,
        subscription_id: str,
        batch_requests: "_models.BatchRequests",
        **kwargs: Any
    ) -> LROPoller["_models.BatchResponseStatus"]:
        """Invokes a batch of individual Azure Resource Manager requests at a subscription scope.

        The batch API can be used to invoke multiple Azure Resource Manager requests at once. Batches
        are processed asynchronously and allow for more efficient handling of many concurrent requests.

        :param subscription_id: The ID of the target subscription. Required.
        :type subscription_id: str
        :param batch_requests: Specifications for all of the requests that will be invoked as part of
         the batch. Required.
        :type batch_requests: ~azure.mgmt.resource.models.BatchRequests
        :keyword callable cls: A custom type or function that will be passed the direct response
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be ARMPolling. Pass in False for this
         operation to not poll, or pass in your own initialized polling object for a personal polling
         strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
         Retry-After header is present.
        :return: An instance of LROPoller that returns either BatchResponseStatus or the result of
         cls(response)
        :rtype: ~azure.core.polling.LROPoller[~azure.mgmt.resource.models.BatchResponseStatus]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        api_version = kwargs.pop("api_version", "2025-08-01-preview")
        content_type = kwargs.pop("content_type", "application/json")
        cls = kwargs.pop("cls", None)
        polling = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token = kwargs.pop("continuation_token", None)

        if cont_token is None:
            raw_result = self._invoke_at_subscription_scope_initial(
                subscription_id=subscription_id,
                batch_requests=batch_requests,
                api_version=api_version,
                content_type=content_type,
                cls=lambda x, y, z: x,
                **kwargs
            )
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response = pipeline_response.http_response
            deserialized = self._deserialize("BatchResponseStatus", pipeline_response)
            if cls:
                return cls(pipeline_response, deserialized, {})
            return deserialized

        if polling is True:
            polling_method = cast(PollingMethod, ARMPolling(lro_delay, **kwargs))
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if cont_token:
            return LROPoller.from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return LROPoller(self._client, raw_result, get_long_running_output, polling_method)

    def _invoke_at_subscription_scope_initial(
        self,
        subscription_id: str,
        batch_requests: "_models.BatchRequests",
        **kwargs: Any
    ) -> Optional["_models.BatchResponseStatus"]:
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        api_version = kwargs.pop("api_version", "2025-08-01-preview")
        content_type = kwargs.pop("content_type", "application/json")
        cls = kwargs.pop("cls", None)

        _json = self._serialize.body(batch_requests, "BatchRequests")

        request = build_invoke_at_subscription_scope_request(
            subscription_id=subscription_id,
            api_version=api_version,
            content_type=content_type,
            json=_json,
            **kwargs
        )
        request.url = self._client.format_url(request.url)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200, 202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.CloudError, pipeline_response)
            raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

        deserialized = None
        response_headers = {}
        if response.status_code == 200:
            deserialized = self._deserialize("BatchResponseStatus", pipeline_response)

        if response.status_code == 202:
            deserialized = self._deserialize("BatchResponseStatus", pipeline_response)
            response_headers["Location"] = self._deserialize("str", response.headers.get("Location"))

        if cls:
            return cls(pipeline_response, deserialized, response_headers)

        return deserialized

    _invoke_at_subscription_scope_initial.metadata = {"url": "/subscriptions/{subscriptionId}/providers/Microsoft.Resources/invokeAtSubscriptionScope"}

    @distributed_trace
    def begin_invoke_at_resource_group_scope(
        self,
        subscription_id: str,
        resource_group_name: str,
        batch_requests: "_models.BatchRequests",
        **kwargs: Any
    ) -> LROPoller["_models.BatchResponseStatus"]:
        """Invokes a batch of individual Azure Resource Manager requests at a resource group scope.

        The batch API can be used to invoke multiple Azure Resource Manager requests at once. Batches
        are processed asynchronously and allow for more efficient handling of many concurrent requests.

        :param subscription_id: The ID of the target subscription. Required.
        :type subscription_id: str
        :param resource_group_name: The name of the resource group. Required.
        :type resource_group_name: str
        :param batch_requests: Specifications for all of the requests that will be invoked as part of
         the batch. Required.
        :type batch_requests: ~azure.mgmt.resource.models.BatchRequests
        :keyword callable cls: A custom type or function that will be passed the direct response
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be ARMPolling. Pass in False for this
         operation to not poll, or pass in your own initialized polling object for a personal polling
         strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
         Retry-After header is present.
        :return: An instance of LROPoller that returns either BatchResponseStatus or the result of
         cls(response)
        :rtype: ~azure.core.polling.LROPoller[~azure.mgmt.resource.models.BatchResponseStatus]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        api_version = kwargs.pop("api_version", "2025-08-01-preview")
        content_type = kwargs.pop("content_type", "application/json")
        cls = kwargs.pop("cls", None)
        polling = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token = kwargs.pop("continuation_token", None)

        if cont_token is None:
            raw_result = self._invoke_at_resource_group_scope_initial(
                subscription_id=subscription_id,
                resource_group_name=resource_group_name,
                batch_requests=batch_requests,
                api_version=api_version,
                content_type=content_type,
                cls=lambda x, y, z: x,
                **kwargs
            )
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            response = pipeline_response.http_response
            deserialized = self._deserialize("BatchResponseStatus", pipeline_response)
            if cls:
                return cls(pipeline_response, deserialized, {})
            return deserialized

        if polling is True:
            polling_method = cast(PollingMethod, ARMPolling(lro_delay, **kwargs))
        elif polling is False:
            polling_method = cast(PollingMethod, NoPolling())
        else:
            polling_method = polling
        if cont_token:
            return LROPoller.from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return LROPoller(self._client, raw_result, get_long_running_output, polling_method)

    def _invoke_at_resource_group_scope_initial(
        self,
        subscription_id: str,
        resource_group_name: str,
        batch_requests: "_models.BatchRequests",
        **kwargs: Any
    ) -> Optional["_models.BatchResponseStatus"]:
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        api_version = kwargs.pop("api_version", "2025-08-01-preview")
        content_type = kwargs.pop("content_type", "application/json")
        cls = kwargs.pop("cls", None)

        _json = self._serialize.body(batch_requests, "BatchRequests")

        request = build_invoke_at_resource_group_scope_request(
            subscription_id=subscription_id,
            resource_group_name=resource_group_name,
            api_version=api_version,
            content_type=content_type,
            json=_json,
            **kwargs
        )
        request.url = self._client.format_url(request.url)

        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response

        if response.status_code not in [200, 202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = self._deserialize.failsafe_deserialize(_models.CloudError, pipeline_response)
            raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)

        deserialized = None
        response_headers = {}
        if response.status_code == 200:
            deserialized = self._deserialize("BatchResponseStatus", pipeline_response)

        if response.status_code == 202:
            deserialized = self._deserialize("BatchResponseStatus", pipeline_response)
            response_headers["Location"] = self._deserialize("str", response.headers.get("Location"))

        if cls:
            return cls(pipeline_response, deserialized, response_headers)

        return deserialized

    _invoke_at_resource_group_scope_initial.metadata = {"url": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Resources/invokeAtResourceGroupScope"}


def build_invoke_at_subscription_scope_request(
    subscription_id: str, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    api_version = kwargs.pop("api_version", "2025-08-01-preview")
    content_type = kwargs.pop("content_type", _headers.pop("Content-Type", "application/json"))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/subscriptions/{subscriptionId}/providers/Microsoft.Resources/invokeAtSubscriptionScope"
    path_format_arguments = {
        "subscriptionId": _SERIALIZER.url("subscription_id", subscription_id, "str"),
    }

    _url = _url.format(**path_format_arguments)

    # Construct parameters
    _params["api-version"] = _SERIALIZER.query("api_version", api_version, "str")

    # Construct headers
    _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, params=_params, headers=_headers, **kwargs)


def build_invoke_at_resource_group_scope_request(
    subscription_id: str, resource_group_name: str, **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    api_version = kwargs.pop("api_version", "2025-08-01-preview")
    content_type = kwargs.pop("content_type", _headers.pop("Content-Type", "application/json"))
    accept = _headers.pop("Accept", "application/json")

    # Construct URL
    _url = "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Resources/invokeAtResourceGroupScope"
    path_format_arguments = {
        "subscriptionId": _SERIALIZER.url("subscription_id", subscription_id, "str"),
        "resourceGroupName": _SERIALIZER.url("resource_group_name", resource_group_name, "str"),
    }

    _url = _url.format(**path_format_arguments)

    # Construct parameters
    _params["api-version"] = _SERIALIZER.query("api_version", api_version, "str")

    # Construct headers
    _headers["Content-Type"] = _SERIALIZER.header("content_type", content_type, "str")
    _headers["Accept"] = _SERIALIZER.header("accept", accept, "str")

    return HttpRequest(method="POST", url=_url, params=_params, headers=_headers, **kwargs)