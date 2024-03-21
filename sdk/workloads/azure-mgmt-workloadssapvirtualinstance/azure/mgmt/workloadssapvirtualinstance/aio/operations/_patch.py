# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List

from typing import Any, Callable, Dict, IO, Optional, TypeVar, Union, cast

from azure.core.pipeline import PipelineResponse
from azure.core.pipeline.transport import AsyncHttpResponse
from azure.core.polling import AsyncLROPoller, AsyncNoPolling, AsyncPollingMethod
from azure.core.rest import HttpRequest
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.utils import case_insensitive_dict
from azure.mgmt.core.polling.async_arm_polling import AsyncARMPolling

from ... import models as _models
from ._sap_virtual_instances_operations import SAPVirtualInstancesOperations as SAPVirtualInstancesOperationsGen
from ..operations._patch import is_rest, update_api_version_of_status_link

T = TypeVar("T")
ClsType = Optional[Callable[[PipelineResponse[HttpRequest, AsyncHttpResponse], T, Dict[str, Any]], Any]]

class AsyncPatchArmPolling(AsyncARMPolling):
    async def request_status(self, status_link: str):
        """Do a simple GET to this status link.

        This method re-inject 'x-ms-client-request-id'.

        :param str status_link: URL to poll.
        :rtype: azure.core.pipeline.PipelineResponse
        :return: The response of the status request.
        """
        if self._path_format_arguments:
            status_link = self._client.format_url(status_link, **self._path_format_arguments)
        status_link, request_params = update_api_version_of_status_link(
            status_link, (self._lro_options or {}).get("api_version")
        )
        # Re-inject 'x-ms-client-request-id' while polling
        if "request_id" not in self._operation_config:
            self._operation_config["request_id"] = self._get_request_id()

        if is_rest(self._initial_response.http_response):
            rest_request = HttpRequest("GET", status_link, params=request_params)
            # Need a cast, as "_return_pipeline_response" mutate the return type, and that return type is not
            # declared in the typing of "send_request"
            return await self._client.send_request(rest_request, _return_pipeline_response=True, **self._operation_config)

        # Legacy HttpRequest and AsyncHttpResponse from azure.core.pipeline.transport
        # casting things here, as we don't want the typing system to know
        # about the legacy APIs.
        request = self._client.get(status_link, params=request_params)
        return await self._client._pipeline.run(  # pylint: disable=protected-access
                request, stream=False, **self._operation_config
            )

class SAPVirtualInstancesOperations(SAPVirtualInstancesOperationsGen):
    """
    .. warning::
        **DO NOT** instantiate this class directly.

        Instead, you should access the following operations through
        :class:`~azure.mgmt.workloadssapvirtualinstance.aio.WorkloadsSapVirtualInstanceMgmtClient`'s
        :attr:`sap_virtual_instances` attribute.
    """

    @distributed_trace_async
    async def begin_create(
        self,
        resource_group_name: str,
        sap_virtual_instance_name: str,
        body: Optional[Union[_models.SAPVirtualInstance, IO]] = None,
        **kwargs: Any
    ) -> AsyncLROPoller[_models.SAPVirtualInstance]:
        """Creates a Virtual Instance for SAP solutions (VIS) resource.

        :param resource_group_name: The name of the resource group. The name is case insensitive.
         Required.
        :type resource_group_name: str
        :param sap_virtual_instance_name: The name of the Virtual Instances for SAP solutions resource.
         Required.
        :type sap_virtual_instance_name: str
        :param body: Virtual Instance for SAP solutions resource request body. Is either a
         SAPVirtualInstance type or a IO type. Default value is None.
        :type body: ~azure.mgmt.workloadssapvirtualinstance.models.SAPVirtualInstance or IO
        :keyword content_type: Body Parameter content-type. Known values are: 'application/json'.
         Default value is None.
        :paramtype content_type: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be AsyncARMPolling. Pass in False for
         this operation to not poll, or pass in your own initialized polling object for a personal
         polling strategy.
        :paramtype polling: bool or ~azure.core.polling.AsyncPollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
         Retry-After header is present.
        :return: An instance of AsyncLROPoller that returns either SAPVirtualInstance or the result of
         cls(response)
        :rtype:
         ~azure.core.polling.AsyncLROPoller[~azure.mgmt.workloadssapvirtualinstance.models.SAPVirtualInstance]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
        _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

        api_version: str = kwargs.pop("api_version", _params.pop("api-version", self._config.api_version))
        content_type: Optional[str] = kwargs.pop("content_type", _headers.pop("Content-Type", None))
        cls: ClsType[_models.SAPVirtualInstance] = kwargs.pop("cls", None)
        polling: Union[bool, AsyncPollingMethod] = kwargs.pop("polling", True)
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        cont_token: Optional[str] = kwargs.pop("continuation_token", None)
        if cont_token is None:
            raw_result = await self._create_initial(
                resource_group_name=resource_group_name,
                sap_virtual_instance_name=sap_virtual_instance_name,
                body=body,
                api_version=api_version,
                content_type=content_type,
                cls=lambda x, y, z: x,
                headers=_headers,
                params=_params,
                **kwargs
            )
        kwargs.pop("error_map", None)

        def get_long_running_output(pipeline_response):
            deserialized = self._deserialize("SAPVirtualInstance", pipeline_response)
            if cls:
                return cls(pipeline_response, deserialized, {})
            return deserialized

        if polling is True:
            polling_method: AsyncPollingMethod = cast(
                AsyncPollingMethod, AsyncPatchArmPolling(lro_delay, lro_options={"final-state-via": "location", "api_version": api_version}, **kwargs)
            )
        elif polling is False:
            polling_method = cast(AsyncPollingMethod, AsyncNoPolling())
        else:
            polling_method = polling
        if cont_token:
            return AsyncLROPoller.from_continuation_token(
                polling_method=polling_method,
                continuation_token=cont_token,
                client=self._client,
                deserialization_callback=get_long_running_output,
            )
        return AsyncLROPoller(self._client, raw_result, get_long_running_output, polling_method)  # type: ignore

    begin_create.metadata = {
        "url": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Workloads/sapVirtualInstances/{sapVirtualInstanceName}"
    }

__all__: List[str] = [
    "SAPVirtualInstancesOperations"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
