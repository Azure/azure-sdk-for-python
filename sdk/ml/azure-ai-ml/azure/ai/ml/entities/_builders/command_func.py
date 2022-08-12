# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import os
from typing import Callable, Dict, Tuple, Union

from azure.ai.ml._ml_exceptions import ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2022_02_01_preview.models import AmlToken, ManagedIdentity, UserIdentity
from azure.ai.ml.constants import AssetTypes, ComponentSource, LegacyAssetTypes
from azure.ai.ml.entities._component.command_component import CommandComponent
from azure.ai.ml.entities._assets.environment import Environment
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.distribution import MpiDistribution, PyTorchDistribution, TensorFlowDistribution
from azure.ai.ml.entities._job.pipeline._component_translatable import ComponentTranslatableMixin
from azure.ai.ml.entities._job.sweep.search_space import SweepDistribution

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


def _parse_input(input_value):
    component_input, job_input = None, None
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
        msg = f"Unsupported input type: {type(input_value)}, only Input, dict, str, bool, int and float are supported."
        raise ValidationException(message=msg, no_personal_data_message=msg, target=ErrorTarget.JOB)
    return component_input, job_input


def _parse_output(output_value):
    component_output, job_output = None, None
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
        raise ValidationException(message=msg, no_personal_data_message=msg, target=ErrorTarget.JOB)
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
    name: str = None,
    description: str = None,
    tags: Dict = None,
    properties: Dict = None,
    display_name: str = None,
    command: str = None,
    experiment_name: str = None,
    environment: Union[str, Environment] = None,
    environment_variables: Dict = None,
    distribution: Union[Dict, MpiDistribution, TensorFlowDistribution, PyTorchDistribution] = None,
    compute: str = None,
    inputs: Dict = None,
    outputs: Dict = None,
    instance_count: int = None,
    instance_type: str = None,
    timeout: int = None,
    code: Union[str, os.PathLike] = None,
    identity: Union[ManagedIdentity, AmlToken, UserIdentity] = None,
    is_deterministic: bool = True,
    **kwargs,
) -> Command:
    """Create a Command object which can be used inside dsl.pipeline as a
    function and can also be created as a standalone command job.

    :param name: Name of the command job or component created
    :type name: str
    :param description: a friendly description of the command
    :type description: str
    :param tags: Tags to be attached to this command
    :type tags: Dict
    :param properties: The asset property dictionary.
    :type properties: dict[str, str]
    :param display_name: a friendly name
    :type display_name: str
    :param experiment_name:  Name of the experiment the job will be created under, if None is provided, default will be set to current directory name. Will be ignored as a pipeline step.
    :type experiment_name: str
    :param command: the command string that will be run
    :type command: str
    :param environment: the environment to use for this command
    :type environment: Union[str, azure.ai.ml.entities.Environment]
    :param environment_variables: environment variables to set on the compute before this command is executed
    :type environment_variables: dict
    :param distribution: the distribution mode to use for this command
    :type distribution: Union[Dict, azure.ai.ml.MpiDistribution, azure.ai.ml.TensorFlowDistribution, azure.ai.ml.PyTorchDistribution]
    :param compute: the name of the compute where the command job is executed(
        will not be used if the command is used as a component/function)
    :type compute: str
    :param inputs: a dict of inputs used by this command.
    :type inputs: Dict
    :param outputs: the outputs of this command
    :type outputs: Dict
    :param instance_count: Optional number of instances or nodes used by the compute target. Defaults to 1.
    :vartype instance_count: int
    :param instance_type: Optional type of VM used as supported by the compute target.
    :vartype instance_type: str
    :param timeout: The number in seconds, after which the job will be cancelled.
    :vartype timeout: int
    :param code: the code folder to run -- typically a local folder that will be uploaded as the job is submitted
    :type code: Union[str, os.PathLike]
    :param identity: Identity that training job will use while running on compute.
    :type identity: Union[azure.ai.ml.ManagedIdentity, azure.ai.ml.AmlToken]
    :param is_deterministic: Specify whether the command will return same output given same input. If a command (component) is deterministic, when use it as a node/step in a pipeline, it will reuse results from a previous submitted job in current workspace which has same inputs and settings. In this case, this step will not use any compute resource. Default to be True, specify is_deterministic=False if you would like to avoid such reuse behavior.
    :type is_deterministic: bool
    """
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
        **kwargs,
    )

    if instance_count is not None or instance_type is not None:
        command_obj.set_resources(instance_count=instance_count, instance_type=instance_type)

    if timeout is not None:
        command_obj.set_limits(timeout=timeout)

    return command_obj
