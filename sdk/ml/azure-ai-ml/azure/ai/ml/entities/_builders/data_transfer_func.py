# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

from typing import Optional, Dict, Union, Callable, Tuple

from azure.ai.ml.entities._component.datatransfer_component import (
    DataTransferCopyComponent,
)
from azure.ai.ml.constants._common import AssetTypes, LegacyAssetTypes
from azure.ai.ml.constants._component import (
    ComponentSource,
    ExternalDataType,
    DataTransferBuiltinComponentUri,
)
from azure.ai.ml.entities._inputs_outputs.external_data import Database, FileSystem
from azure.ai.ml.entities._inputs_outputs import Output, Input
from azure.ai.ml.entities._job.pipeline._io import PipelineInput, NodeOutput
from azure.ai.ml.entities._builders.base_node import pipeline_node_decorator
from azure.ai.ml.entities._job.pipeline._component_translatable import (
    ComponentTranslatableMixin,
)
from azure.ai.ml.exceptions import ErrorTarget, ValidationErrorType, ValidationException
from .data_transfer import (
    DataTransferCopy,
    DataTransferImport,
    DataTransferExport,
    _build_source_sink,
)


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
    elif isinstance(input_value, str):
        # Input bindings
        component_input = ComponentTranslatableMixin._to_input_builder_function(
            input_value
        )
        job_input = input_value
    elif isinstance(input_value, (PipelineInput, NodeOutput)):
        # datatransfer node can accept PipelineInput/NodeOutput for export task.
        if input_value._data is None or isinstance(input_value._data, Output):
            data = Input(type=input_value.type, mode=input_value.mode)
        else:
            data = input_value._data
        component_input, _ = _parse_input(data)
        job_input = input_value
    else:
        msg = (
            f"Unsupported input type: {type(input_value)}, only Input, dict, str, PipelineInput and NodeOutput are "
            f"supported."
        )
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.JOB,
            error_type=ValidationErrorType.INVALID_VALUE,
        )
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
    elif isinstance(
        output_value, str
    ):  # When output is passed in from pipeline job yaml
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


def copy_data(
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[Dict] = None,
    display_name: Optional[str] = None,
    experiment_name: Optional[str] = None,
    compute: Optional[str] = None,
    inputs: Optional[Dict] = None,
    outputs: Optional[Dict] = None,
    is_deterministic: bool = True,
    data_copy_mode: Optional[str] = None,
    **kwargs,
) -> DataTransferCopy:
    """Create a DataTransferCopy object which can be used inside dsl.pipeline as a function.

    :param name: The name of the job.
    :type name: str
    :param description: Description of the job.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param display_name: Display name of the job.
    :type display_name: str
    :param experiment_name:  Name of the experiment the job will be created under.
    :type experiment_name: str
    :param compute: The compute resource the job runs on.
    :type compute: str
    :param inputs: Mapping of inputs data bindings used in the job.
    :type inputs: dict
    :param outputs: Mapping of outputs data bindings used in the job.
    :type outputs: dict
    :param is_deterministic: Specify whether the command will return same output given same input.
        If a command (component) is deterministic, when use it as a node/step in a pipeline,
        it will reuse results from a previous submitted job in current workspace which has same inputs and settings.
        In this case, this step will not use any compute resource.
        Default to be True, specify is_deterministic=False if you would like to avoid such reuse behavior.
    :type is_deterministic: bool
    :param data_copy_mode: data copy mode in copy task, possible value is "merge_with_overwrite", "fail_if_conflict".
    :type data_copy_mode: str
    """
    inputs = inputs or {}
    outputs = outputs or {}
    component_inputs, job_inputs = _parse_inputs_outputs(
        inputs, parse_func=_parse_input
    )
    # job inputs can not be None
    job_inputs = {k: v for k, v in job_inputs.items() if v is not None}
    component_outputs, job_outputs = _parse_inputs_outputs(
        outputs, parse_func=_parse_output
    )
    component = kwargs.pop("component", None)
    if component is None:
        component = DataTransferCopyComponent(
            name=name,
            tags=tags,
            display_name=display_name,
            description=description,
            inputs=component_inputs,
            outputs=component_outputs,
            data_copy_mode=data_copy_mode,
            _source=ComponentSource.BUILDER,
            is_deterministic=is_deterministic,
            **kwargs,
        )
    data_transfer_copy_obj = DataTransferCopy(
        component=component,
        name=name,
        description=description,
        tags=tags,
        display_name=display_name,
        experiment_name=experiment_name,
        compute=compute,
        inputs=job_inputs,
        outputs=job_outputs,
        data_copy_mode=data_copy_mode,
        **kwargs,
    )
    return data_transfer_copy_obj


@pipeline_node_decorator
def import_data(
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[Dict] = None,
    display_name: Optional[str] = None,
    experiment_name: Optional[str] = None,
    compute: Optional[str] = None,
    source: Optional[Union[Dict, Database, FileSystem]] = None,
    outputs: Optional[Dict] = None,
    **kwargs,
) -> DataTransferImport:
    """Create a DataTransferImport object which can be used inside dsl.pipeline.

    :param name: The name of the job.
    :type name: str
    :param description: Description of the job.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param display_name: Display name of the job.
    :type display_name: str
    :param experiment_name:  Name of the experiment the job will be created under.
    :type experiment_name: str
    :param compute: The compute resource the job runs on.
    :type compute: str
    :param source: The data source of file system or database
    :type source: Union[Dict, Database, FileSystem]
    :param outputs: Mapping of outputs data bindings used in the job, default will be an output port with key "sink"
    and type "mltable".
    :type outputs: dict
    """
    source = _build_source_sink(source)
    outputs = outputs or {"sink": Output(type=AssetTypes.MLTABLE)}
    # # job inputs can not be None
    # job_inputs = {k: v for k, v in job_inputs.items() if v is not None}
    _, job_outputs = _parse_inputs_outputs(outputs, parse_func=_parse_output)
    component = kwargs.pop("component", None)
    update_source = False
    if component is None:
        if source and source.type == ExternalDataType.DATABASE:
            component = DataTransferBuiltinComponentUri.IMPORT_DATABASE
        else:
            component = DataTransferBuiltinComponentUri.IMPORT_FILE_SYSTEM
        update_source = True

    data_transfer_import_obj = DataTransferImport(
        component=component,
        name=name,
        description=description,
        tags=tags,
        display_name=display_name,
        experiment_name=experiment_name,
        compute=compute,
        source=source,
        outputs=job_outputs,
        **kwargs,
    )
    if update_source:
        data_transfer_import_obj._source = ComponentSource.BUILTIN

    return data_transfer_import_obj


@pipeline_node_decorator
def export_data(
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[Dict] = None,
    display_name: Optional[str] = None,
    experiment_name: Optional[str] = None,
    compute: Optional[str] = None,
    sink: Optional[Union[Dict, Database, FileSystem]] = None,
    inputs: Optional[Dict] = None,
    **kwargs,
) -> DataTransferExport:
    """Create a DataTransferExport object which can be used inside dsl.pipeline.

    :param name: The name of the job.
    :type name: str
    :param description: Description of the job.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param display_name: Display name of the job.
    :type display_name: str
    :param experiment_name:  Name of the experiment the job will be created under.
    :type experiment_name: str
    :param compute: The compute resource the job runs on.
    :type compute: str
    :param sink: The sink of external data and databases.
    :type sink: Union[Dict, Database, FileSystem]
    :param inputs: Mapping of inputs data bindings used in the job.
    :type inputs: dict
    """
    sink = _build_source_sink(sink)
    _, job_inputs = _parse_inputs_outputs(inputs, parse_func=_parse_input)
    # job inputs can not be None
    job_inputs = {k: v for k, v in job_inputs.items() if v is not None}
    component = kwargs.pop("component", None)
    update_source = False
    if component is None:
        if sink and sink.type == ExternalDataType.DATABASE:
            component = DataTransferBuiltinComponentUri.EXPORT_DATABASE
        else:
            msg = "Sink is a required field for export data task and we don't support exporting file system for now."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.JOB,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        update_source = True

    data_transfer_export_obj = DataTransferExport(
        component=component,
        name=name,
        description=description,
        tags=tags,
        display_name=display_name,
        experiment_name=experiment_name,
        compute=compute,
        sink=sink,
        inputs=job_inputs,
        **kwargs,
    )
    if update_source:
        data_transfer_export_obj._source = ComponentSource.BUILTIN

    return data_transfer_export_obj
