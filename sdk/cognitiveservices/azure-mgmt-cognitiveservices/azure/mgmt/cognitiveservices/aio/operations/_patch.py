# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import json
import time
from collections.abc import MutableMapping
from io import IOBase
from typing import IO, Any, Optional, Union, cast

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.polling.base_polling import _raise_if_bad_http_status_and_method
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict
from azure.mgmt.core.exceptions import ARMErrorFormat
from azure.mgmt.core.polling.arm_polling import BodyContentPolling, StatusCheckPolling
from azure.mgmt.core.polling.async_arm_polling import AsyncARMPolling

from ... import models as _models
from ..._utils.model_base import SdkJSONEncoder, _deserialize, _failsafe_deserialize
from ...operations._operations import build_computes_create_or_update_request
from ...operations._patch import _TERMINAL_FAILED_STATES, _compute_provisioning_error
from ._operations import ComputesOperations as _ComputesOperationsGenerated

JSON = MutableMapping[str, Any]


class _AsyncComputeResourcePolling(AsyncARMPolling):
    """``AsyncARMPolling`` that tolerates the compute-create read-after-write window.

    Right after the service accepts the create (HTTP 202), the new compute is briefly not queryable: a
    ``GET`` on the resource returns ``404 "Cluster not found"`` for ~15-20s. Plain resource polling
    (:class:`BodyContentPolling`) would treat that 404 as a failure and wrongly fail a create that
    actually succeeded. This subclass treats a 404 as "still in progress" and keeps polling until the
    resource is queryable and reaches a terminal ``provisioningState``. A generous grace period bounds
    the tolerance so a genuinely missing resource still surfaces instead of hanging forever. When the
    compute provisions to a failed state it raises the resource's own error detail rather than the
    generic ``Operation returned an invalid status 'OK'``.
    """

    _NOT_FOUND_GRACE_SECONDS = 300

    async def update_status(self) -> None:
        self._pipeline_response = await self.request_status(self._operation.get_polling_url())
        response = self._pipeline_response.http_response
        if response.status_code == 404:
            first_seen = getattr(self, "_not_found_since", None)
            if first_seen is None:
                self._not_found_since = time.monotonic()
            elif time.monotonic() - first_seen > self._NOT_FOUND_GRACE_SECONDS:
                _raise_if_bad_http_status_and_method(response)  # grace exhausted: surface the 404
            self._status = "InProgress"
            return
        self._not_found_since = None
        _raise_if_bad_http_status_and_method(response)
        self._status = self._operation.get_status(self._pipeline_response)
        if str(self._status).lower() in _TERMINAL_FAILED_STATES:
            raise _compute_provisioning_error(response)


class ComputesOperations(_ComputesOperationsGenerated):
    """Customized ``ComputesOperations`` that polls the compute resource instead of its
    operation-status endpoint.

    The generated :meth:`begin_create_or_update` has two problems against the current service:

    * it rejects the ``202 Accepted`` the service returns for the async create with
      "Operation returned an invalid status 'Accepted'"; and
    * its poller follows the ``Azure-AsyncOperation`` header to
      ``.../locations/{location}/computeOperations/{operationId}``, which requires the
      ``Microsoft.CognitiveServices/locations/computeOperations/read`` permission. Many callers who
      are allowed to create a compute lack that permission, so the poll fails with
      ``AuthorizationFailed`` even though the create itself succeeded.

    This override accepts the ``202`` and polls the compute resource itself (a ``GET`` on the resource
    URL, watching ``provisioningState``) via :class:`BodyContentPolling`, deliberately excluding the
    algorithms that would follow the ``Azure-AsyncOperation``/``Location`` headers. As a result the
    poller only needs ``computes/read`` (which callers already have), still blocks until the operation
    reaches a terminal state, and surfaces a genuine provisioning failure instead of masking it.
    """

    @distributed_trace_async
    async def begin_create_or_update(
        self,
        resource_group_name: str,
        account_name: str,
        compute_name: str,
        resource: Union[_models.Compute, JSON, IO[bytes]],
        **kwargs: Any,
    ) -> AsyncLROPoller[_models.Compute]:
        """Creates or updates a compute associated with the Cognitive Services account.

        This override accepts the service's ``202 Accepted`` and polls the compute resource itself
        (a ``GET`` on the resource URL, watching ``provisioningState``) instead of the operation-status
        endpoint that requires ``computeOperations/read``. It still blocks until the operation reaches
        a terminal state and raises on a genuine provisioning failure, so callers get correct results
        without needing the operation-status read permission.

        :param resource_group_name: The name of the resource group. The name is case insensitive.
         Required.
        :type resource_group_name: str
        :param account_name: The name of Cognitive Services account. Required.
        :type account_name: str
        :param compute_name: The name of the compute associated with the Cognitive Services Account.
         Required.
        :type compute_name: str
        :param resource: The compute properties. Is one of the following types: Compute, JSON,
         IO[bytes] Required.
        :type resource: ~azure.mgmt.cognitiveservices.models.Compute or JSON or IO[bytes]
        :return: An instance of AsyncLROPoller that returns Compute. The Compute is compatible with
         MutableMapping
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.mgmt.cognitiveservices.models.Compute]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = kwargs.pop("params", {}) or {}

        content_type: Optional[str] = (
            kwargs.pop("content_type", _headers.pop("Content-Type", None)) or "application/json"
        )
        cls = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        kwargs.pop("continuation_token", None)

        error_map: dict = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})

        if isinstance(resource, (IOBase, bytes)):
            _content = resource
        else:
            _content = json.dumps(resource, cls=SdkJSONEncoder, exclude_readonly=True)  # type: ignore

        _request = build_computes_create_or_update_request(
            resource_group_name=resource_group_name,
            account_name=account_name,
            compute_name=compute_name,
            subscription_id=self._config.subscription_id,
            content_type=content_type,
            api_version=self._config.api_version,
            content=_content,
            headers=_headers,
            params=_params,
        )
        _request.url = self._client.format_url(
            _request.url,
            endpoint=self._serialize.url("self._config.base_url", self._config.base_url, "str", skip_quote=True),
        )

        pipeline_response = await self._client._pipeline.run(  # pylint: disable=protected-access
            _request, stream=False, **kwargs
        )
        response = pipeline_response.http_response
        # Accept 202 (async "Accepted") in addition to 200/201. The generated create rejects 202 with
        # "Operation returned an invalid status 'Accepted'", failing a create the service accepted.
        if response.status_code not in [200, 201, 202]:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            error = _failsafe_deserialize(_models.ErrorResponse, response)
            raise HttpResponseError(response=response, model=error, error_format=ARMErrorFormat)
        await response.read()  # load the body so the poller/deserializer can read it

        def get_long_running_output(pipeline_response):
            response = pipeline_response.http_response
            deserialized = _deserialize(_models.Compute, response.json())
            if cls:
                return cls(pipeline_response, deserialized, {})
            return deserialized

        path_format_arguments = {
            "endpoint": self._serialize.url("self._config.base_url", self._config.base_url, "str", skip_quote=True),
        }

        # Poll the compute resource itself (a GET on the resource URL, watching ``provisioningState``)
        # instead of the operation-status endpoint. ``BodyContentPolling`` polls the resource URL, so
        # the poller never calls ``.../computeOperations/{id}`` (which requires ``computeOperations/read``
        # that many callers lack). Excluding ``AzureAsyncOperationPolling`` and ``LocationPolling``
        # guarantees the ``Azure-AsyncOperation``/``Location`` headers the service returns are ignored,
        # while the poller still blocks until terminal and raises on a failed provisioning.
        # ``_AsyncComputeResourcePolling`` additionally tolerates the ~20s read-after-write window where
        # the resource GET returns 404 "Cluster not found" right after the create is accepted.
        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod,
                _AsyncComputeResourcePolling(
                    lro_delay,
                    lro_algorithms=[BodyContentPolling(), StatusCheckPolling()],
                    path_format_arguments=path_format_arguments,
                    **kwargs,
                ),
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling
        return AsyncLROPoller[_models.Compute](
            self._client, pipeline_response, get_long_running_output, polling_method  # type: ignore
        )


__all__: list[str] = [
    "ComputesOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
