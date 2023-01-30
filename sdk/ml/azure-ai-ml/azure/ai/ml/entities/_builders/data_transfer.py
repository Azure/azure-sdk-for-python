# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import copy
import logging
import os
from enum import Enum
from os import PathLike
from typing import Dict, List, Optional, Union

from marshmallow import INCLUDE, Schema

from azure.ai.ml._restclient.v2022_10_01_preview.models import JobBase
from azure.ai.ml._schema.job.data_transfer_job import DataTransferJobSchema
from azure.ai.ml.constants._component import ComponentSource, NodeType
from azure.ai.ml.entities._component.datatransfer_component import DataTransferComponent, DataTransferCopyComponent
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, from_rest_inputs_to_dataset_literal
from azure.ai.ml.entities._job.data_transfer.data_transfer_job import DataTransferCopyJob
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.entities._system_data import SystemData
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException

from ..._schema import PathAwareSchema
from .._util import (
    convert_ordered_dict_to_dict,
    from_rest_dict_to_dummy_rest_object,
    get_rest_dict_for_node_attrs,
    load_from_dict,
    validate_attribute_type,
)
from .base_node import BaseNode

module_logger = logging.getLogger(__name__)


class DataTransfer(BaseNode):
    """Base class for data transfer node, used for data transfer component version
    consumption.

    You should not instantiate this class directly.
    """
    def __init__(
        self,
        *,
        component: Union[str, DataTransferComponent],
        compute: Optional[str] = None,
        inputs: Optional[Dict[str, Union[Input, str]]] = None,
        outputs: Optional[Dict[str, Union[str, Output]]] = None,
        **kwargs,
    ):
        # resolve normal dict to dict[str, JobService]
        kwargs.pop("type", None)
        self._parameters = kwargs.pop("parameters", {})
        super().__init__(
            type=NodeType.DATATRANSFER,
            inputs=inputs,
            outputs=outputs,
            component=component,
            compute=compute,
            **kwargs,
        )

    @property
    def parameters(self) -> Dict[str, str]:
        """MLFlow parameters.

        :return: MLFlow parameters logged in job.
        :rtype: Dict[str, str]
        """
        return self._parameters

    @classmethod
    def _create_schema_for_validation(cls, context) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline import DataTransferSchema

        return DataTransferSchema(context=context)


class DataTransferCopy(DataTransfer):
    """Base class for data transfer copy node.

    You should not instantiate this class directly. Instead, you should
    create from builder function: copy_data.

    :param component: Id or instance of the data transfer component/job to be run for the step
    :type component: DataTransferComponent
    :param inputs: Inputs to the data transfer.
    :type inputs: Dict[str, Union[Input, str, bool, int, float, Enum, dict]]
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: Dict[str, Union[str, Output, dict]]
    :param name: Name of the data transfer.
    :type name: str
    :param description: Description of the data transfer.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param display_name: Display name of the job.
    :type display_name: str
    :param experiment_name:  Name of the experiment the job will be created under,
        if None is provided, default will be set to current directory name.
    :type experiment_name: str
    :param compute: The compute target the job runs on.
    :type compute: str
    :param task: task type in data transfer component, possible value is "copy_data".
    :type task: str
    :param data_copy_mode: data copy mode in copy task, possible value is "merge_with_overwrite", "fail_if_conflict".
    :type data_copy_mode: str
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if DataTransferCopy cannot be successfully validated.
        Details will be provided in the error message.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        *,
        component: Union[str, DataTransferCopyComponent],
        compute: Optional[str] = None,
        inputs: Optional[Dict[str, Union[Input, str]]] = None,
        outputs: Optional[Dict[str, Union[str, Output]]] = None,
        task: Optional[str] = None,
        data_copy_mode: Optional[str] = None,
        **kwargs,
    ):
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())
        super().__init__(
            inputs=inputs,
            outputs=outputs,
            component=component,
            compute=compute,
            **kwargs,
        )
        # init mark for _AttrDict
        self._init = True
        self.task = task
        self.data_copy_mode = data_copy_mode
        is_component = isinstance(component, DataTransferCopyComponent)
        if is_component:
            self.task = component.task or self.task
            self.driver_cores = component.data_copy_mode or self.data_copy_mode
        self._init = False

    @classmethod
    def _get_supported_inputs_types(cls):
        # Todo: update input types for data transfer
        supported_types = super()._get_supported_inputs_types() or ()
        return (
            *supported_types,
        )

    @classmethod
    def _get_supported_outputs_types(cls):
        return str, Output

    @property
    def component(self) -> Union[str, DataTransferCopyComponent]:
        return self._component

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "component": (str, DataTransferCopyComponent),
        }

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return ["type"]

    def _to_rest_object(self, **kwargs) -> dict:
        rest_obj = super()._to_rest_object(**kwargs)
        for key, value in {
            "componentId": self._get_component_id(),
        }.items():
            if value is not None:
                rest_obj[key] = value
        return convert_ordered_dict_to_dict(rest_obj)

    @classmethod
    def _load_from_rest_job(cls, obj: JobBase) -> "DataTransferCopy":
        from .data_transfer_func import copy_data

        rest_data_transfer_job = obj.properties

        data_transfer_job = copy_data(
            name=obj.name,
            display_name=rest_data_transfer_job.display_name,
            description=rest_data_transfer_job.description,
            tags=rest_data_transfer_job.tags,
            properties=rest_data_transfer_job.properties,
            experiment_name=rest_data_transfer_job.experiment_name,
            status=rest_data_transfer_job.status,
            creation_context=SystemData._from_rest_object(obj.system_data) if obj.system_data else None,
            compute=rest_data_transfer_job.compute_id,
            parameters=rest_data_transfer_job.parameters,
            inputs=from_rest_inputs_to_dataset_literal(rest_data_transfer_job.inputs),
            outputs=from_rest_data_outputs(rest_data_transfer_job.outputs),
            task=rest_data_transfer_job.task,
            data_copy_mode=rest_data_transfer_job.rest_data_transfer_job
        )
        data_transfer_job._id = obj.id
        data_transfer_job.component._source = (
            ComponentSource.REMOTE_WORKSPACE_JOB
        )  # This is used by pipeline job telemetries.

        return data_transfer_job

    def _build_inputs(self):
        inputs = super(DataTransferCopy, self)._build_inputs()
        built_inputs = {}
        # Validate and remove non-specified inputs
        for key, value in inputs.items():
            if value is not None:
                built_inputs[key] = value

        return built_inputs

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs) -> "Spark":
        from .data_transfer_func import copy_data

        loaded_data = load_from_dict(DataTransferJobSchema, data, context, additional_message, **kwargs)
        data_transfer_job = copy_data(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

        return data_transfer_job

    def _to_job(self) -> DataTransferCopyJob:

        return DataTransferCopyJob(
            experiment_name=self.experiment_name,
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            tags=self.tags,
            status=self.status,
            inputs=self._job_inputs,
            outputs=self._job_outputs,
            services=self.services,
            compute=self.compute,
            task=self.task,
            data_copy_mode=self.data_copy_mode
        )

    def __call__(self, *args, **kwargs) -> "DataTransferCopy":
        """Call Command as a function will return a new instance each time."""
        if isinstance(self._component, Component):
            # call this to validate inputs
            node = self._component(*args, **kwargs)
            # merge inputs
            for name, original_input in self.inputs.items():
                if name not in kwargs.keys():
                    # use setattr here to make sure owner of input won't change
                    setattr(node.inputs, name, original_input._data)
                    node._job_inputs[name] = original_input._data
                # get outputs
            for name, original_output in self.outputs.items():
                # use setattr here to make sure owner of input won't change
                setattr(node.outputs, name, original_output._data)
            self._refine_optional_inputs_with_no_value(node, kwargs)
            # set default values: compute, environment_variables, outputs
            node._name = self.name
            node.compute = self.compute
            node.tags = self.tags
            # Pass through the display name only if the display name is not system generated.
            node.display_name = self.display_name if self.display_name != self.name else None
            return node
        msg = "Command can be called as a function only when referenced component is {}, currently got {}."
        raise ValidationException(
            message=msg.format(type(Component), self._component),
            no_personal_data_message=msg.format(type(Component), "self._component"),
            target=ErrorTarget.DATA_TRANSFER_JOB,
            error_type=ValidationErrorType.INVALID_VALUE,
        )
