# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import os
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from azure.ai.ml.constants._common import AssetTypes, LegacyAssetTypes
from azure.ai.ml.constants._component import ComponentSource
from azure.ai.ml.entities._assets.environment import Environment
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._credentials import (
    AmlTokenConfiguration,
    ManagedIdentityConfiguration,
    UserIdentityConfiguration,
)
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.distribution import (
    DistributionConfiguration,
    MpiDistribution,
    PyTorchDistribution,
    RayDistribution,
    TensorFlowDistribution,
)
from azure.ai.ml.entities._job.job_service import (
    JobService,
    JupyterLabJobService,
    SshJobService,
    TensorBoardJobService,
    VsCodeJobService,
)
from azure.ai.ml.entities._job.pipeline._component_translatable import ComponentTranslatableMixin
from azure.ai.ml.entities._job.sweep.search_space import SweepDistribution
from azure.ai.ml.exceptions import ErrorTarget, ValidationErrorType, ValidationException

from .command import Command

SUPPORTED_INPUTS = [
    LegacyAssetTypes.PATH,
    AssetTypes.URI_FILE,
    AssetTypes.URI_FOLDER,
    AssetTypes.CUSTOM_MODEL,
    AssetTypes.MLFLOW_MODEL,
    AssetTypes.MLTABLE,
    AssetTypes.TRITON_MODEL,
]


def _parse_input(input_value: Union[Input, Dict, SweepDistribution, str, bool, int, float]) -> Tuple:
    component_input = None
    job_input: Optional[Union[Input, Dict, SweepDistribution, str, bool, int, float]] = None

    if isinstance(input_value, Input):
        component_input = Input(**input_value._to_dict())
        input_type = input_value.type
        if input_type in SUPPORTED_INPUTS:
            job_input = Input(**input_value._to_dict())
    elif isinstance(input_value, dict):
        # if user provided dict, we try to parse it to Input.
        # for job input, only parse for path type
        input_type = input_value.get("type", None)
        if input_type in SUPPORTED_INPUTS:
            job_input = Input(**input_value)
        component_input = Input(**input_value)
    elif isinstance(input_value, (SweepDistribution, str, bool, int, float)):
        # Input bindings are not supported
        component_input = ComponentTranslatableMixin._to_input_builder_function(input_value)
        job_input = input_value
    else:
        msg = f"Unsupported input type: {type(input_value)}"
        msg += ", only Input, dict, str, bool, int and float are supported."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.JOB,
            error_type=ValidationErrorType.INVALID_VALUE,
        )
    return component_input, job_input


def _parse_output(output_value: Optional[Union[Output, Dict, str]]) -> Tuple:
    component_output = None
    job_output: Optional[Union[Output, Dict, str]] = None

    if isinstance(output_value, Output):
        component_output = Output(**output_value._to_dict())
        job_output = Output(**output_value._to_dict())
    elif not output_value:
        # output value can be None or empty dictionary
        # None output value will be packed into a JobOutput object with mode = ReadWriteMount & type = UriFolder
        component_output = ComponentTranslatableMixin._to_output(output_value)
        job_output = output_value
    elif isinstance(output_value, dict):  # When output value is a non-empty dictionary
        job_output = Output(**output_value)
        component_output = Output(**output_value)
    elif isinstance(output_value, str):  # When output is passed in from pipeline job yaml
        job_output = output_value
    else:
        msg = f"Unsupported output type: {type(output_value)}, only Output and dict are supported."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.JOB,
            error_type=ValidationErrorType.INVALID_VALUE,
        )
    return component_output, job_output


def _parse_inputs_outputs(io_dict: Dict, parse_func: Callable) -> Tuple[Dict, Dict]:
    component_io_dict, job_io_dict = {}, {}
    if io_dict:
        for key, val in io_dict.items():
            component_io, job_io = parse_func(val)
            component_io_dict[key] = component_io
            job_io_dict[key] = job_io
    return component_io_dict, job_io_dict


def command(
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[Dict] = None,
    properties: Optional[Dict] = None,
    display_name: Optional[str] = None,
    command: Optional[str] = None,  # pylint: disable=redefined-outer-name
    experiment_name: Optional[str] = None,
    environment: Optional[Union[str, Environment]] = None,
    environment_variables: Optional[Dict] = None,
    distribution: Optional[
        Union[
            Dict,
            MpiDistribution,
            TensorFlowDistribution,
            PyTorchDistribution,
            RayDistribution,
            DistributionConfiguration,
        ]
    ] = None,
    compute: Optional[str] = None,
    inputs: Optional[Dict] = None,
    outputs: Optional[Dict] = None,
    instance_count: Optional[int] = None,
    instance_type: Optional[str] = None,
    locations: Optional[List[str]] = None,
    docker_args: Optional[str] = None,
    shm_size: Optional[str] = None,
    timeout: Optional[int] = None,
    code: Optional[Union[str, os.PathLike]] = None,
    identity: Optional[Union[ManagedIdentityConfiguration, AmlTokenConfiguration, UserIdentityConfiguration]] = None,
    is_deterministic: bool = True,
    services: Optional[
        Dict[str, Union[JobService, JupyterLabJobService, SshJobService, TensorBoardJobService, VsCodeJobService]]
    ] = None,
    job_tier: Optional[str] = None,
    priority: Optional[str] = None,
    **kwargs: Any,
) -> Command:
    """Creates a Command object which can be used inside a dsl.pipeline function or used as a standalone Command job.

    :keyword name: The name of the Command job or component.
    :paramtype name: Optional[str]
    :keyword description: The description of the Command. Defaults to None.
    :paramtype description: Optional[str]
    :keyword tags: Tag dictionary. Tags can be added, removed, and updated. Defaults to None.
    :paramtype tags: Optional[dict[str, str]]
    :keyword properties: The job property dictionary. Defaults to None.
    :paramtype properties: Optional[dict[str, str]]
    :keyword display_name: The display name of the job. Defaults to a randomly generated name.
    :paramtype display_name: Optional[str]
    :keyword command: The command to be executed. Defaults to None.
    :paramtype command: Optional[str]
    :keyword experiment_name: The name of the experiment that the job will be created under. Defaults to current
        directory name.
    :paramtype experiment_name: Optional[str]
    :keyword environment: The environment that the job will run in.
    :paramtype environment: Optional[Union[str, ~azure.ai.ml.entities.Environment]]
    :keyword environment_variables: A dictionary of environment variable names and values.
        These environment variables are set on the process where user script is being executed.
        Defaults to None.
    :paramtype environment_variables: Optional[dict[str, str]]
    :keyword distribution: The configuration for distributed jobs. Defaults to None.
    :paramtype distribution: Optional[Union[dict, ~azure.ai.ml.PyTorchDistribution, ~azure.ai.ml.MpiDistribution,
        ~azure.ai.ml.TensorFlowDistribution, ~azure.ai.ml.RayDistribution]]
    :keyword compute: The compute target the job will run on. Defaults to default compute.
    :paramtype compute: Optional[str]
    :keyword inputs: A mapping of input names to input data sources used in the job. Defaults to None.
    :paramtype inputs: Optional[dict[str, Union[~azure.ai.ml.Input, str, bool, int, float, Enum]]]
    :keyword outputs: A mapping of output names to output data sources used in the job. Defaults to None.
    :paramtype outputs: Optional[dict[str, Union[str, ~azure.ai.ml.Output]]]
    :keyword instance_count: The number of instances or nodes to be used by the compute target. Defaults to 1.
    :paramtype instance_count: Optional[int]
    :keyword instance_type: The type of VM to be used by the compute target.
    :paramtype instance_type: Optional[str]
    :keyword locations: The list of locations where the job will run.
    :paramtype locations: Optional[List[str]]
    :keyword docker_args: Extra arguments to pass to the Docker run command. This would override any
        parameters that have already been set by the system, or in this section. This parameter is only
        supported for Azure ML compute types. Defaults to None.
    :paramtype docker_args: Optional[str]
    :keyword shm_size: The size of the Docker container's shared memory block. This should be in the
        format of (number)(unit) where the number has to be greater than 0 and the unit can be one of
        b(bytes), k(kilobytes), m(megabytes), or g(gigabytes).
    :paramtype shm_size: Optional[str]
    :keyword timeout: The number, in seconds, after which the job will be cancelled.
    :paramtype timeout: Optional[int]
    :keyword code: The source code to run the job. Can be a local path or "http:", "https:", or "azureml:" url
        pointing to a remote location.
    :paramtype code: Optional[Union[str, os.PathLike]]
    :keyword identity: The identity that the command job will use while running on compute.
    :paramtype identity: Optional[Union[
        ~azure.ai.ml.entities.ManagedIdentityConfiguration,
        ~azure.ai.ml.entities.AmlTokenConfiguration,
        ~azure.ai.ml.entities.UserIdentityConfiguration]]
    :keyword is_deterministic: Specifies whether the Command will return the same output given the same input.
        Defaults to True. When True, if a Command Component is deterministic and has been run before in the
        current workspace with the same input and settings, it will reuse results from a previously submitted
        job when used as a node or step in a pipeline. In that scenario, no compute resources will be used.
    :paramtype is_deterministic: bool
    :keyword services: The interactive services for the node. Defaults to None. This is an experimental parameter,
        and may change at any time. Please see https://aka.ms/azuremlexperimental for more information.
    :paramtype services: Optional[dict[str, Union[~azure.ai.ml.entities.JobService,
        ~azure.ai.ml.entities.JupyterLabJobService, ~azure.ai.ml.entities.SshJobService,
        ~azure.ai.ml.entities.TensorBoardJobService, ~azure.ai.ml.entities.VsCodeJobService]]]
    :keyword job_tier: The job tier. Accepted values are "Spot", "Basic", "Standard", or "Premium".
    :paramtype job_tier: Optional[str]
    :keyword priority: The priority of the job on the compute. Accepted values are "low", "medium", and "high".
        Defaults to "medium".
    :paramtype priority: Optional[str]
    :return: A Command object.
    :rtype: ~azure.ai.ml.entities.Command

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_command_configurations.py
            :start-after: [START command_function]
            :end-before: [END command_function]
            :language: python
            :dedent: 8
            :caption: Creating a Command Job using the command() builder method.
    """
    # pylint: disable=too-many-locals
    inputs = inputs or {}
    outputs = outputs or {}
    component_inputs, job_inputs = _parse_inputs_outputs(inputs, parse_func=_parse_input)
    # job inputs can not be None
    job_inputs = {k: v for k, v in job_inputs.items() if v is not None}
    component_outputs, job_outputs = _parse_inputs_outputs(outputs, parse_func=_parse_output)

    component = kwargs.pop("component", None)
    if component is None:
        component = CommandComponent(
            name=name,
            tags=tags,
            code=code,
            command=command,
            environment=environment,
            display_name=display_name,
            description=description,
            inputs=component_inputs,
            outputs=component_outputs,
            distribution=distribution,
            environment_variables=environment_variables,
            _source=ComponentSource.BUILDER,
            is_deterministic=is_deterministic,
            **kwargs,
        )
    command_obj = Command(
        component=component,
        name=name,
        description=description,
        tags=tags,
        properties=properties,
        display_name=display_name,
        experiment_name=experiment_name,
        compute=compute,
        inputs=job_inputs,
        outputs=job_outputs,
        identity=identity,
        distribution=distribution,
        environment=environment,
        environment_variables=environment_variables,
        services=services,
        **kwargs,
    )

    if (
        locations is not None
        or instance_count is not None
        or instance_type is not None
        or docker_args is not None
        or shm_size is not None
    ):
        command_obj.set_resources(
            locations=locations,
            instance_count=instance_count,
            instance_type=instance_type,
            docker_args=docker_args,
            shm_size=shm_size,
        )

    if timeout is not None:
        command_obj.set_limits(timeout=timeout)

    if job_tier is not None or priority is not None:
        command_obj.set_queue_settings(job_tier=job_tier, priority=priority)

    return command_obj
