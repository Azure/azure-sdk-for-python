# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access, too-many-locals

import os
from typing import Callable, Dict, List, Optional, Tuple, Union

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
    elif isinstance(input_value, (str, bool, int, float)):
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
    **kwargs,
) -> Spark:
    """Create a Spark object which can be used inside dsl.pipeline as a function and
    can also be created as a standalone spark job.

    :param experiment_name:  Name of the experiment the job will be created under.
    :type experiment_name: str
    :param name: The name of the job.
    :type name: str
    :param display_name: Display name of the job.
    :type display_name: str
    :param description: Description of the job.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param code: The source code to run the job.
    :type code: Union[str, os.PathLike]
    :param entry: File or class entry point.
    :type entry: dict[str, str]
    :param py_files: List of .zip, .egg or .py files to place on the PYTHONPATH for Python apps.
    :type py_files: Optional[typing.List[str]]
    :param jars: List of jars to include on the driver and executor classpaths.
    :type jars: Optional[typing.List[str]]
    :param files: List of files to be placed in the working directory of each executor.
    :type files: Optional[typing.List[str]]
    :param archives: List of archives to be extracted into the working directory of each executor.
    :type archives: Optional[typing.List[str]]
    :param identity: Identity that spark job will use while running on compute.
    :type identity: Union[Dict, ManagedIdentity, AmlToken, UserIdentity]
    :param driver_cores: Number of cores to use for the driver process, only in cluster mode.
    :type driver_cores: int
    :param driver_memory: Amount of memory to use for the driver process.
    :type driver_memory: str
    :param executor_cores: The number of cores to use on each executor.
    :type executor_cores: int
    :param executor_memory: Amount of memory to use per executor process, in the same format as JVM memory strings with
        a size unit suffix ("k", "m", "g" or "t") (e.g. 512m, 2g).
    :type executor_memory: str
    :param executor_instances: Initial number of executors.
    :type executor_instances: int
    :param dynamic_allocation_enabled: Whether to use dynamic resource allocation, which scales the number of executors
        registered with this application up and down based on the workload.
    :type dynamic_allocation_enabled: bool
    :param dynamic_allocation_min_executors: Lower bound for the number of executors if dynamic allocation is enabled.
    :type dynamic_allocation_min_executors: int
    :param dynamic_allocation_max_executors: Upper bound for the number of executors if dynamic allocation is enabled.
    :type dynamic_allocation_max_executors: int
    :param conf: A dict with pre-defined spark configurations key and values.
    :type conf: dict
    :param environment: Azure ML environment to run the job in.
    :type environment: Union[str, azure.ai.ml.entities.Environment]
    :param inputs: Mapping of inputs data bindings used in the job.
    :type inputs: dict
    :param outputs: Mapping of outputs data bindings used in the job.
    :type outputs: dict
    :param args: Arguments for the job.
    :type args: str
    :param compute: The compute resource the job runs on.
    :type compute: str
    :param resources: Compute Resource configuration for the job.
    :type resources: Union[Dict, SparkResourceConfiguration]
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
