# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Union, Any, IO
from azure.core.tracing.decorator import distributed_trace
from azure.core.polling import LROPoller
from .. import models as _models
from ._operations import VirtualMachinesOperations as VirtualMachinesOperationsGen
from .._validation import api_version_validation

def deserialization_hook(pipeline_response)：
    body_as_json = pipeline_response.context["deserialized_data"]
    if isinstance(body_as_json, list):
        body_as_json = {"value": body_as_json}

class VirtualMachinesOperations(VirtualMachinesOperationsGen):

    @api_version_validation(
       method_valid_on=['2017-03-30', '2017-12-01', '2018-04-01', '2018-06-01', '2018-10-01', '2019-03-01', '2019-07-01', '2019-12-01', '2020-06-01', '2020-12-01', '2021-03-01', '2021-04-01', '2021-07-01', '2021-11-01', '2022-03-01', '2022-08-01', '2022-11-01', '2023-03-01'],
    )
    @distributed_trace
    def begin_run_command(
        self, resource_group_name: str, vm_name: str, parameters: Union[_models.RunCommandInput, IO], **kwargs: Any
    ) -> LROPoller[_models.RunCommandResult]:
        super().begin_run_command(resource_group_name, vm_name, parameters, deserialization_hook=deserialization_hook, **kwargs)
        

__all__: List[str] = [
    "VirtualMachinesOperations",
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
