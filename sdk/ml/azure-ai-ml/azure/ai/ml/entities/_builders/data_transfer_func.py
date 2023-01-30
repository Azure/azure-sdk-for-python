# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, List, Dict

from azure.ai.ml.entities._component.datatransfer_component import DataTransferCopyComponent
from azure.ai.ml.constants._component import ComponentSource

from .data_transfer import DataTransferCopy
from .command_func import _parse_inputs_outputs, _parse_input, _parse_output


class FileSystem:
    """Base class for file system.

    :param path: The path to which the file system is pointing.
    :type path: str
    :param connection: Connection is workspace, we didn't support storage connection here, need leverage workspace
    connection to store these credential info.
    :type connection: str
    """
    def __init__(
            self,
            *,
            path: Optional[str] = None,
            connection: Optional[str] = None
    ):
        self.path = path
        self.connection = connection


class Database:
    """Base class for database.

    :param query: The sql query to get data from database.
    :type query: str
    :param connection: Connection is workspace, we didn't support storage connection here, need leverage workspace
    connection to store these credential info.
    :type connection: str
    :param table_name: The database table name
    :type table_name: str
    :param stored_procedure: stored_procedure
    :type stored_procedure: str
    :param stored_procedure_params: stored_procedure_params
    :type stored_procedure_params: List[dict]
    """
    def __init__(
            self,
            *,
            query: Optional[str] = None,
            connection: Optional[str] = None,
            table_name: Optional[str] = None,
            stored_procedure: Optional[str] = None,
            stored_procedure_params: Optional[List[Dict[str, str]]] = None
    ):
        self.query = query
        self.connection = connection
        self.table_name = table_name
        self.stored_procedure = stored_procedure
        self.stored_procedure_params = stored_procedure_params


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
        task: Optional[str] = None,
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


def import_data():
    pass


def export_data():
    pass


