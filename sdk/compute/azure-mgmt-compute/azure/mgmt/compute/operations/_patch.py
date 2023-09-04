# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Union, Any, IO
from azure.core.polling import LROPoller
from azure.mgmt.core.polling.arm_polling import ARMPolling
from .. import models as _models
from ._operations import VirtualMachinesOperations as VirtualMachinesOperationsGen


def get_long_running_output(pipeline_response):
    body_as_json = pipeline_response.context["deserialized_data"]
    if isinstance(body_as_json, list):
        body_as_json = {"value": body_as_json}
    return _models.RunCommandResult.deserialize(body_as_json)


class RunCommandPolling(ARMPolling):
    def initialize(
        self,
        client,
        initial_response,
        _,
    ):
        super().initialize(client, initial_response, get_long_running_output)


class VirtualMachinesOperations(VirtualMachinesOperationsGen):
    def begin_run_command(
        self,
        resource_group_name: str,
        vm_name: str,
        parameters: Union[_models.RunCommandInput, IO],
        **kwargs: Any
    ) -> LROPoller[_models.RunCommandResult]:
        return super().begin_run_command(
            resource_group_name,
            vm_name,
            parameters,
            polling=RunCommandPolling(lro_options={"final-state-via": "location"}),
            **kwargs
        )


__all__: List[str] = [
    "VirtualMachinesOperations"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
