# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any

from azure.core.exceptions import (
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceNotFoundError,
)
from azure.core.polling import LROPoller, NoPolling
from azure.core.rest import HttpRequest
from azure.mgmt.core.polling.arm_polling import ARMPolling


def _build_create_or_update_model_with_system_metadata_request(
    subscription_id: str,
    resource_group_name: str,
    registry_name: str,
    name: str,
    version: str,
    **kwargs: Any,
) -> HttpRequest:
    api_version = kwargs.pop("api_version", "2021-10-01-dataplanepreview")
    url = (
        "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}"
        "/providers/Microsoft.MachineLearningServices/registries/{registryName}"
        "/models/{name}/versions/{version}"
    )
    path_format_arguments = {
        "subscriptionId": subscription_id,
        "resourceGroupName": resource_group_name,
        "registryName": registry_name,
        "name": name,
        "version": version,
    }
    url = url.format(**path_format_arguments)
    return HttpRequest(
        method="PUT",
        url=url,
        params={"api-version": api_version},
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json=kwargs.get("json"),
    )


def _begin_create_or_update_model_with_system_metadata(
    self,
    subscription_id: str,
    name: str,
    version: str,
    resource_group_name: str,
    registry_name: str,
    body: Any,
    **kwargs: Any,
) -> LROPoller:
    """Create or update a model version with system metadata in a registry.

    This is a custom operation not present in the TypeSpec-generated code.
    It was originally part of the old autorest-generated client and is needed
    for registry model operations that include system_metadata.
    """
    error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
    error_map.update(kwargs.pop("error_map", {}))

    _json = self._serialize.body(body, "ModelVersionData")
    _json["properties"]["system_metadata"] = body.properties.system_metadata

    request = _build_create_or_update_model_with_system_metadata_request(
        subscription_id=subscription_id,
        resource_group_name=resource_group_name,
        registry_name=registry_name,
        name=name,
        version=version,
        json=_json,
    )
    request.url = self._client.format_url(request.url)

    pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
    response = pipeline_response.http_response

    cls = kwargs.pop("cls", None)

    def get_long_running_output(pipeline_response):
        if cls:
            return cls(pipeline_response, None, {})
        return None

    polling = kwargs.pop("polling", True)
    if polling is True:
        lro_delay = kwargs.pop("polling_interval", self._config.polling_interval)
        polling_method = ARMPolling(lro_delay, **kwargs)
    elif polling is False:
        polling_method = NoPolling()
    else:
        polling_method = polling

    return LROPoller(self._client, pipeline_response, get_long_running_output, polling_method)


__all__: list[str] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    from ._operations import ModelsOperations

    ModelsOperations.begin_create_or_update_model_with_system_metadata = (
        _begin_create_or_update_model_with_system_metadata
    )
