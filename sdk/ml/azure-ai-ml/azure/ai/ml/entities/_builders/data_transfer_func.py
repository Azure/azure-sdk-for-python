# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Dict, Union

from azure.ai.ml.entities._component.datatransfer_component import DataTransferCopyComponent, \
    DataTransferImportComponent, DataTransferExportComponent
from azure.ai.ml.constants._common import AssetTypes
from azure.ai.ml.constants._component import ComponentSource, ExternalDataType, DataTransferBuiltinComponentUri, \
    DataTransferTaskType
from azure.ai.ml.entities._inputs_outputs.external_data import Database, FileSystem
from azure.ai.ml.entities._inputs_outputs.output import Output
from .data_transfer import DataTransferCopy, DataTransferImport, DataTransferExport, _build_source_sink
from .command_func import _parse_inputs_outputs, _parse_input, _parse_output


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
        task: Optional[str] = DataTransferTaskType.COPY_DATA,
        data_copy_mode: Optional[str] = None,
        **kwargs,
) -> DataTransferCopy:
    """Create a Spark object which can be used inside dsl.pipeline as a function and
    can also be created as a standalone spark job.

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
    :param task: task type in data transfer component, possible value is "copy_data".
    :type task: str
    :param data_copy_mode: data copy mode in copy task, possible value is "merge_with_overwrite", "fail_if_conflict".
    :type data_copy_mode: str
    """
    inputs = inputs or {}
    outputs = outputs or {}
    component_inputs, job_inputs = _parse_inputs_outputs(inputs, parse_func=_parse_input)
    # job inputs can not be None
    job_inputs = {k: v for k, v in job_inputs.items() if v is not None}
    component_outputs, job_outputs = _parse_inputs_outputs(outputs, parse_func=_parse_output)
    component = kwargs.pop("component", None)
    if component is None:
        component = DataTransferCopyComponent(
            name=name,
            tags=tags,
            display_name=display_name,
            description=description,
            inputs=component_inputs,
            outputs=component_outputs,
            task=task,
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
        task=task,
        **kwargs,
    )
    return data_transfer_copy_obj


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
        is_deterministic: bool = True,
        task: Optional[str] = DataTransferTaskType.IMPORT_DATA,
        **kwargs,
) -> DataTransferImport:
    """Create a Spark object which can be used inside dsl.pipeline as a function and
    can also be created as a standalone spark job.

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
    :param is_deterministic: Specify whether the command will return same output given same input.
        If a command (component) is deterministic, when use it as a node/step in a pipeline,
        it will reuse results from a previous submitted job in current workspace which has same inputs and settings.
        In this case, this step will not use any compute resource.
        Default to be True, specify is_deterministic=False if you would like to avoid such reuse behavior.
    :type is_deterministic: bool
    :param task: task type in data transfer component, possible value is "copy_data".
    :type task: str
    """
    source = _build_source_sink(source)
    outputs = outputs or {'sink': Output(type=AssetTypes.MLTABLE)}
    # # job inputs can not be None
    # job_inputs = {k: v for k, v in job_inputs.items() if v is not None}
    component_outputs, job_outputs = _parse_inputs_outputs(outputs, parse_func=_parse_output)
    component = kwargs.pop("component", None)
    if component is None:
        if source.type == ExternalDataType.DATABASE:
            component_id = DataTransferBuiltinComponentUri.IMPORT_DATABASE
        else:
            component_id = DataTransferBuiltinComponentUri.IMPORT_FILE_SYSTEM
        component = DataTransferImportComponent(
            name=name,
            tags=tags,
            display_name=display_name,
            description=description,
            source=source,
            outputs=component_outputs,
            task=task,
            _source=ComponentSource.BUILDER,
            is_deterministic=is_deterministic,
            id=component_id,
            **kwargs,
        )
        component._source = ComponentSource.BUIlTIN
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
        task=task,
        **kwargs,
    )
    return data_transfer_import_obj


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
        is_deterministic: bool = True,
        task: Optional[str] = DataTransferTaskType.EXPORT_DATA,
        **kwargs,
) -> DataTransferExport:
    """Create a Spark object which can be used inside dsl.pipeline as a function and
    can also be created as a standalone spark job.

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
    :param is_deterministic: Specify whether the command will return same output given same input.
        If a command (component) is deterministic, when use it as a node/step in a pipeline,
        it will reuse results from a previous submitted job in current workspace which has same inputs and settings.
        In this case, this step will not use any compute resource.
        Default to be True, specify is_deterministic=False if you would like to avoid such reuse behavior.
    :type is_deterministic: bool
    :param task: task type in data transfer component, possible value is "copy_data".
    :type task: str
    """
    sink = _build_source_sink(sink)
    component_inputs, job_inputs = _parse_inputs_outputs(inputs, parse_func=_parse_input)
    # job inputs can not be None
    job_inputs = {k: v for k, v in job_inputs.items() if v is not None}
    component = kwargs.pop("component", None)

    if component is None:
        if sink.type == ExternalDataType.DATABASE:
            id = DataTransferBuiltinComponentUri.EXPORT_DATABASE
        else:
            id = DataTransferBuiltinComponentUri.EXPORT_FILE_SYSTEM
        component = DataTransferExportComponent(
            name=name,
            tags=tags,
            display_name=display_name,
            description=description,
            sink=sink,
            inputs=component_inputs,
            task=task,
            _source=ComponentSource.BUILDER,
            is_deterministic=is_deterministic,
            id=id,
            **kwargs,
        )
        component._source = ComponentSource.BUIlTIN
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
        task=task,
        **kwargs,
    )
    return data_transfer_export_obj
