# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import Any, Optional, get_args

from azure.core import MatchConditions
from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    map_error,
)

from .._utils.model_base import _is_model

__all__: list[str] = []  # Add all objects you want publicly available to users at this package level


def _contains_model(deserializer: Any) -> bool:
    if _is_model(deserializer):
        return True
    return any(_contains_model(argument) for argument in get_args(deserializer))


def _conditional_kwargs(if_none_match: Optional[str], kwargs: dict[str, Any]) -> dict[str, Any]:
    if if_none_match is not None:
        kwargs["etag"] = if_none_match
        kwargs["match_condition"] = MatchConditions.IfModified
    return kwargs


def _rename_orderby(orderby: Optional[str], kwargs: dict[str, Any]) -> dict[str, Any]:
    kwargs["order_by"] = orderby
    return kwargs


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    from . import _operations

    update_operations = _operations.DeviceUpdateOperations
    management_operations = _operations.DeviceManagementOperations

    generated_deserialize = getattr(_operations, "_deserialize")

    def raw_model_deserialize(deserializer, value, *args, **kwargs):
        if _contains_model(deserializer):
            return value
        return generated_deserialize(deserializer, value, *args, **kwargs)

    setattr(_operations, "_deserialize", raw_model_deserialize)

    get_update = update_operations.get_update
    get_file = update_operations.get_file
    get_update_operation = update_operations.get_operation_status
    list_update_operations = update_operations.list_operation_statuses

    def legacy_get_update(self, provider, name, version, *, if_none_match=None, **kwargs):
        return get_update(self, provider, name, version, **_conditional_kwargs(if_none_match, kwargs))

    def legacy_get_file(self, provider, name, version, file_id, *, if_none_match=None, **kwargs):
        return get_file(self, provider, name, version, file_id, **_conditional_kwargs(if_none_match, kwargs))

    def legacy_get_update_operation(self, operation_id, *, if_none_match=None, **kwargs):
        return get_update_operation(self, operation_id, **_conditional_kwargs(if_none_match, kwargs))

    update_operations.get_update = legacy_get_update
    update_operations.get_file = legacy_get_file
    setattr(update_operations, "get_operation", legacy_get_update_operation)
    setattr(update_operations, "list_operations", list_update_operations)

    mappings = {
        "get_operation": "get_operation_status",
        "list_operations": "list_operation_statuses",
        "get_group_update_compliance": "get_update_compliance_for_group",
        "get_device_class_subgroup_details": "get_device_class_subgroup",
        "list_best_updates_for_device_class_subgroup": "get_best_updates_for_device_class_subgroup",
        "delete_device_class_subgroup_deployment": "delete_deployment_for_device_class_subgroup",
        "list_devices_for_device_class_subgroup_deployment": "list_device_states_for_device_class_subgroup_deployment",
        "collect_logs": "start_log_collection",
        "get_log_collection_operation": "get_log_collection",
        "list_log_collection_operations": "list_log_collections",
        "get_log_collection_operation_detailed_status": "get_log_collection_detailed_status",
        "list_device_health": "list_health_of_devices",
    }
    saved = {old: getattr(management_operations, new) for old, new in mappings.items()}
    for old, method in saved.items():
        setattr(management_operations, old, method)

    get_management_operation = saved["get_operation"]
    collect_logs = saved["collect_logs"]
    get_log_collection = saved["get_log_collection_operation"]
    get_log_collection_status = saved["get_log_collection_operation_detailed_status"]

    def legacy_get_management_operation(self, operation_id, *, if_none_match=None, **kwargs):
        return get_management_operation(self, operation_id, **_conditional_kwargs(if_none_match, kwargs))

    setattr(management_operations, "get_operation", legacy_get_management_operation)

    def legacy_collect_logs(self, operation_id, log_collection_request, **kwargs):
        return collect_logs(self, operation_id, log_collection_request, **kwargs)

    def legacy_get_log_collection(self, operation_id, **kwargs):
        return get_log_collection(self, operation_id, **kwargs)

    def legacy_get_log_collection_status(self, operation_id, **kwargs):
        return get_log_collection_status(self, operation_id, **kwargs)

    setattr(management_operations, "collect_logs", legacy_collect_logs)
    setattr(management_operations, "get_log_collection_operation", legacy_get_log_collection)
    setattr(
        management_operations,
        "get_log_collection_operation_detailed_status",
        legacy_get_log_collection_status,
    )

    list_device_classes = management_operations.list_device_classes
    list_groups = management_operations.list_groups

    list_group_deployments = management_operations.list_deployments_for_group
    list_subgroup_deployments = management_operations.list_deployments_for_device_class_subgroup
    list_best_updates = management_operations.list_best_updates_for_group

    def legacy_list_device_classes(self, **kwargs):
        return list_device_classes(self, **kwargs)

    def legacy_list_groups(self, *, orderby=None, **kwargs):
        return list_groups(self, **_rename_orderby(orderby, kwargs))

    def legacy_list_group_deployments(self, group_id, *, orderby=None, **kwargs):
        return list_group_deployments(self, group_id, **_rename_orderby(orderby, kwargs))

    def legacy_list_subgroup_deployments(self, group_id, device_class_id, *, orderby=None, **kwargs):
        return list_subgroup_deployments(self, group_id, device_class_id, **_rename_orderby(orderby, kwargs))

    def legacy_list_best_updates(self, group_id, *, filter=None, **kwargs):
        if filter is not None:
            params = dict(kwargs.pop("params", {}) or {})
            params["$filter"] = filter
            kwargs["params"] = params
        return list_best_updates(self, group_id, **kwargs)

    management_operations.list_device_classes = legacy_list_device_classes
    management_operations.list_groups = legacy_list_groups
    management_operations.list_deployments_for_group = legacy_list_group_deployments
    management_operations.list_deployments_for_device_class_subgroup = legacy_list_subgroup_deployments
    management_operations.list_best_updates_for_group = legacy_list_best_updates

    def legacy_list_device_health(self, *, filter, **kwargs):
        headers = kwargs.pop("headers", {}) or {}
        params = kwargs.pop("params", {}) or {}
        cls = kwargs.pop("cls", None)
        error_map = {
            401: ClientAuthenticationError,
            404: ResourceNotFoundError,
            409: ResourceExistsError,
            304: ResourceNotModifiedError,
        }
        error_map.update(kwargs.pop("error_map", {}) or {})
        request = _operations.build_device_management_list_health_of_devices_request(
            instance_id=self._config.instance_id,
            filter=filter,
            api_version=self._config.api_version,
            headers=headers,
            params=params,
        )
        request.url = self._client.format_url(
            request.url,
            endpoint=self._serialize.url("self._config.endpoint", self._config.endpoint, "str"),
        )
        pipeline_response = self._client._pipeline.run(request, stream=False, **kwargs)
        response = pipeline_response.http_response
        if response.status_code != 200:
            map_error(status_code=response.status_code, response=response, error_map=error_map)
            raise HttpResponseError(response=response)
        deserialized = response.json() if response.content else None
        if cls:
            return cls(pipeline_response, deserialized, {})
        return deserialized

    setattr(management_operations, "list_device_health", legacy_list_device_health)

    for operation_name in {
        "get_operation_status",
        "list_operation_statuses",
        "get_update_compliance_for_group",
        "get_device_class_subgroup",
        "get_best_updates_for_device_class_subgroup",
        "delete_deployment_for_device_class_subgroup",
        "list_device_states_for_device_class_subgroup_deployment",
        "start_log_collection",
        "get_log_collection",
        "list_log_collections",
        "get_log_collection_detailed_status",
        "list_health_of_devices",
    }:
        delattr(management_operations, operation_name)

    delattr(update_operations, "get_operation_status")
    delattr(update_operations, "list_operation_statuses")
