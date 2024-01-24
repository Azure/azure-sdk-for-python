# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access, too-many-locals

import os
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import AmlToken, ManagedIdentity, UserIdentity
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._component import ComponentSource
from azure.ai.ml.entities import Environment
from azure.ai.ml.entities._component.spark_component import SparkComponent
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.pipeline._component_translatable import ComponentTranslatableMixin
from azure.ai.ml.entities._job.spark_job_entry import SparkJobEntry
from azure.ai.ml.entities._job.spark_resource_configuration import SparkResourceConfiguration
from azure.ai.ml.exceptions import ErrorTarget, ValidationException

from .spark import Spark

SUPPORTED_INPUTS = [AssetTypes.URI_FILE, AssetTypes.URI_FOLDER, AssetTypes.MLTABLE]


def _parse_input(input_value: Union[Input, dict, str, bool, int, float]) -> Tuple:
    component_input = None
    job_input: Union[Input, dict, str, bool, int, float] = ""

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
    elif isinstance(input_value, (str, bool, int, float)):
        # Input bindings are not supported
        component_input = ComponentTranslatableMixin._to_input_builder_function(input_value)
        job_input = input_value
    else:
        msg = f"Unsupported input type: {type(input_value)}, only Input, dict, str, bool, int and float are supported."
        raise ValidationException(message=msg, no_personal_data_message=msg, target=ErrorTarget.JOB)
    return component_input, job_input


def _parse_output(output_value: Union[Output, dict]) -> Tuple:
    component_output = None
    job_output: Union[Output, dict] = {}

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


def spark(
    *,
    experiment_name: Optional[str] = None,
    name: Optional[str] = None,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[Dict] = None,
    code: Optional[Union[str, os.PathLike]] = None,
    entry: Union[Dict[str, str], SparkJobEntry, None] = None,
    py_files: Optional[List[str]] = None,
    jars: Optional[List[str]] = None,
    files: Optional[List[str]] = None,
    archives: Optional[List[str]] = None,
    identity: Optional[Union[Dict[str, str], ManagedIdentity, AmlToken, UserIdentity]] = None,
    driver_cores: Optional[int] = None,
    driver_memory: Optional[str] = None,
    executor_cores: Optional[int] = None,
    executor_memory: Optional[str] = None,
    executor_instances: Optional[int] = None,
    dynamic_allocation_enabled: Optional[bool] = None,
    dynamic_allocation_min_executors: Optional[int] = None,
    dynamic_allocation_max_executors: Optional[int] = None,
    conf: Optional[Dict[str, str]] = None,
    environment: Optional[Union[str, Environment]] = None,
    inputs: Optional[Dict] = None,
    outputs: Optional[Dict] = None,
    args: Optional[str] = None,
    compute: Optional[str] = None,
    resources: Optional[Union[Dict, SparkResourceConfiguration]] = None,
    **kwargs: Any,
) -> Spark:
    """Creates a Spark object which can be used inside a dsl.pipeline function or used as a standalone Spark job.

    :keyword experiment_name:  The name of the experiment the job will be created under.
    :paramtype experiment_name: Optional[str]
    :keyword name: The name of the job.
    :paramtype name: Optional[str]
    :keyword display_name: The job display name.
    :paramtype display_name: Optional[str]
    :keyword description: The description of the job. Defaults to None.
    :paramtype description: Optional[str]
    :keyword tags: The dictionary of tags for the job. Tags can be added, removed, and updated. Defaults to None.
    :paramtype tags: Optional[dict[str, str]]
    :keyword code: The source code to run the job. Can be a local path or "http:", "https:", or "azureml:" url
        pointing to a remote location.
    :type code: Optional[Union[str, os.PathLike]]
    :keyword entry: The file or class entry point.
    :paramtype entry: Optional[Union[dict[str, str], ~azure.ai.ml.entities.SparkJobEntry]]
    :keyword py_files: The list of .zip, .egg or .py files to place on the PYTHONPATH for Python apps.
        Defaults to None.
    :paramtype py_files: Optional[List[str]]
    :keyword jars: The list of .JAR files to include on the driver and executor classpaths. Defaults to None.
    :paramtype jars: Optional[List[str]]
    :keyword files: The list of files to be placed in the working directory of each executor. Defaults to None.
    :paramtype files: Optional[List[str]]
    :keyword archives: The list of archives to be extracted into the working directory of each executor.
        Defaults to None.
    :paramtype archives: Optional[List[str]]
    :keyword identity: The identity that the Spark job will use while running on compute.
    :paramtype identity: Optional[Union[
        dict[str, str],
        ~azure.ai.ml.entities.ManagedIdentityConfiguration,
        ~azure.ai.ml.entities.AmlTokenConfiguration,
        ~azure.ai.ml.entities.UserIdentityConfiguration]]
    :keyword driver_cores: The number of cores to use for the driver process, only in cluster mode.
    :paramtype driver_cores: Optional[int]
    :keyword driver_memory: The amount of memory to use for the driver process, formatted as strings with a size unit
        suffix ("k", "m", "g" or "t") (e.g. "512m", "2g").
    :paramtype driver_memory: Optional[str]
    :keyword executor_cores: The number of cores to use on each executor.
    :paramtype executor_cores: Optional[int]
    :keyword executor_memory: The amount of memory to use per executor process, formatted as strings with a size unit
        suffix ("k", "m", "g" or "t") (e.g. "512m", "2g").
    :paramtype executor_memory: Optional[str]
    :keyword executor_instances: The initial number of executors.
    :paramtype executor_instances: Optional[int]
    :keyword dynamic_allocation_enabled: Whether to use dynamic resource allocation, which scales the number of
        executors registered with this application up and down based on the workload.
    :paramtype dynamic_allocation_enabled: Optional[bool]
    :keyword dynamic_allocation_min_executors: The lower bound for the number of executors if dynamic allocation is
        enabled.
    :paramtype dynamic_allocation_min_executors: Optional[int]
    :keyword dynamic_allocation_max_executors: The upper bound for the number of executors if dynamic allocation is
        enabled.
    :paramtype dynamic_allocation_max_executors: Optional[int]
    :keyword conf: A dictionary with pre-defined Spark configurations key and values. Defaults to None.
    :paramtype conf: Optional[dict[str, str]]
    :keyword environment: The Azure ML environment to run the job in.
    :paramtype environment: Optional[Union[str, ~azure.ai.ml.entities.Environment]]
    :keyword inputs: A mapping of input names to input data used in the job. Defaults to None.
    :paramtype inputs: Optional[dict[str, ~azure.ai.ml.Input]]
    :keyword outputs: A mapping of output names to output data used in the job. Defaults to None.
    :paramtype outputs: Optional[dict[str, ~azure.ai.ml.Output]]
    :keyword args: The arguments for the job.
    :paramtype args: Optional[str]
    :keyword compute: The compute resource the job runs on.
    :paramtype compute: Optional[str]
    :keyword resources: The compute resource configuration for the job.
    :paramtype resources: Optional[Union[dict, ~azure.ai.ml.entities.SparkResourceConfiguration]]
    :return: A Spark object.
    :rtype: ~azure.ai.ml.entities.Spark

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_spark_configurations.py
            :start-after: [START spark_function_configuration_1]
            :end-before: [END spark_function_configuration_1]
            :language: python
            :dedent: 8
            :caption: Configuring a SparkJob.

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_spark_configurations.py
            :start-after: [START spark_function_configuration_2]
            :end-before: [END spark_function_configuration_2]
            :language: python
            :dedent: 8
            :caption: Configuring a SparkJob.

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_spark_configurations.py
            :start-after: [START spark_dsl_pipeline]
            :end-before: [END spark_dsl_pipeline]
            :language: python
            :dedent: 8
            :caption: Building a Spark pipeline using the DSL pipeline decorator
    """

    inputs = inputs or {}
    outputs = outputs or {}
    component_inputs, job_inputs = _parse_inputs_outputs(inputs, parse_func=_parse_input)
    # job inputs can not be None
    job_inputs = {k: v for k, v in job_inputs.items() if v is not None}
    component_outputs, job_outputs = _parse_inputs_outputs(outputs, parse_func=_parse_output)
    component = kwargs.pop("component", None)

    if component is None:
        component = SparkComponent(
            name=name,
            display_name=display_name,
            tags=tags,
            description=description,
            code=code,
            entry=entry,
            py_files=py_files,
            jars=jars,
            files=files,
            archives=archives,
            driver_cores=driver_cores,
            driver_memory=driver_memory,
            executor_cores=executor_cores,
            executor_memory=executor_memory,
            executor_instances=executor_instances,
            dynamic_allocation_enabled=dynamic_allocation_enabled,
            dynamic_allocation_min_executors=dynamic_allocation_min_executors,
            dynamic_allocation_max_executors=dynamic_allocation_max_executors,
            conf=conf,
            environment=environment,
            inputs=component_inputs,
            outputs=component_outputs,
            args=args,
            _source=ComponentSource.BUILDER,
            **kwargs,
        )
    if isinstance(component, SparkComponent):
        spark_obj = Spark(
            experiment_name=experiment_name,
            name=name,
            display_name=display_name,
            tags=tags,
            description=description,
            component=component,
            identity=identity,
            driver_cores=driver_cores,
            driver_memory=driver_memory,
            executor_cores=executor_cores,
            executor_memory=executor_memory,
            executor_instances=executor_instances,
            dynamic_allocation_enabled=dynamic_allocation_enabled,
            dynamic_allocation_min_executors=dynamic_allocation_min_executors,
            dynamic_allocation_max_executors=dynamic_allocation_max_executors,
            conf=conf,
            inputs=job_inputs,
            outputs=job_outputs,
            compute=compute,
            resources=resources,
            **kwargs,
        )
    else:
        # when we load a remote job, component now is an arm_id, we need get entry from node level returned from
        # service
        spark_obj = Spark(
            experiment_name=experiment_name,
            name=name,
            display_name=display_name,
            tags=tags,
            description=description,
            component=component,
            identity=identity,
            driver_cores=driver_cores,
            driver_memory=driver_memory,
            executor_cores=executor_cores,
            executor_memory=executor_memory,
            executor_instances=executor_instances,
            dynamic_allocation_enabled=dynamic_allocation_enabled,
            dynamic_allocation_min_executors=dynamic_allocation_min_executors,
            dynamic_allocation_max_executors=dynamic_allocation_max_executors,
            conf=conf,
            inputs=job_inputs,
            outputs=job_outputs,
            compute=compute,
            resources=resources,
            entry=entry,
            py_files=py_files,
            jars=jars,
            files=files,
            archives=archives,
            args=args,
            **kwargs,
        )
    return spark_obj
