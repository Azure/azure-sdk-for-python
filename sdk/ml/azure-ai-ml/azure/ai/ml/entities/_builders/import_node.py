# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

import logging
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from marshmallow import Schema

from azure.ai.ml._restclient.v2022_02_01_preview.models import CommandJob as RestCommandJob
from azure.ai.ml._restclient.v2022_02_01_preview.models import JobBaseData
from azure.ai.ml._schema.job.import_job import ImportJobSchema
from azure.ai.ml.constants._common import BASE_PATH_CONTEXT_KEY
from azure.ai.ml.constants._component import ComponentSource, NodeType
from azure.ai.ml.constants._compute import ComputeType
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._component.import_component import ImportComponent
from azure.ai.ml.entities._inputs_outputs import Output
from azure.ai.ml.entities._job._input_output_helpers import from_rest_data_outputs, from_rest_inputs_to_dataset_literal
from azure.ai.ml.entities._job.import_job import ImportJob, ImportSource
from azure.ai.ml.exceptions import ErrorTarget, ValidationErrorType, ValidationException

from ..._schema import PathAwareSchema
from .._inputs_outputs import Output
from .._util import convert_ordered_dict_to_dict, load_from_dict, validate_attribute_type
from .base_node import BaseNode

module_logger = logging.getLogger(__name__)


class Import(BaseNode):
    """Base class for import node, used for import component version consumption.

    You should not instantiate this class directly. Instead, you should
    create from a builder function.

    :param component: Id or instance of the import component/job to be run for the step.
    :type component: ~azure.ai.ml.entities._component.import_component.ImportComponent
    :param inputs: Input parameters to the import.
    :type inputs: Dict[str, str]
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: Dict[str, Union[str, ~azure.ai.ml.entities.Output]]
    :param name: Name of the import.
    :type name: str
    :param description: Description of the import.
    :type description: str
    :param display_name: Display name of the job.
    :type display_name: str
    :param experiment_name: Name of the experiment the job will be created under,
        if None is provided, the default will be set to the current directory name.
    :type experiment_name: str
    """

    def __init__(
        self,
        *,
        component: Union[str, ImportComponent],
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        **kwargs: Any,
    ) -> None:
        # validate init params are valid type
        validate_attribute_type(attrs_to_check=locals(), attr_type_map=self._attr_type_map())

        kwargs.pop("type", None)
        kwargs.pop("compute", None)

        self._parameters = kwargs.pop("parameters", {})
        BaseNode.__init__(
            self,
            type=NodeType.IMPORT,
            inputs=inputs,
            outputs=outputs,
            component=component,
            compute=ComputeType.ADF,
            **kwargs,
        )

    @classmethod
    def _get_supported_inputs_types(cls) -> Type[str]:
        # import source parameters type, connection, query, path are always str
        return str

    @classmethod
    def _get_supported_outputs_types(cls) -> Tuple:
        return str, Output

    @property
    def component(self) -> Union[str, ImportComponent]:
        res: Union[str, ImportComponent] = self._component
        return res

    @classmethod
    def _attr_type_map(cls) -> dict:
        return {
            "component": (str, ImportComponent),
        }

    def _to_job(self) -> ImportJob:
        return ImportJob(
            id=self.id,
            name=self.name,
            display_name=self.display_name,
            description=self.description,
            experiment_name=self.experiment_name,
            status=self.status,
            source=ImportSource._from_job_inputs(self._job_inputs),
            output=self._job_outputs.get("output"),
            creation_context=self.creation_context,
        )

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        return []

    def _to_rest_object(self, **kwargs: Any) -> dict:
        rest_obj: dict = super()._to_rest_object(**kwargs)
        rest_obj.update(
            convert_ordered_dict_to_dict(
                {
                    "componentId": self._get_component_id(),
                }
            )
        )
        return rest_obj

    @classmethod
    def _load_from_dict(cls, data: Dict, context: Dict, additional_message: str, **kwargs: Any) -> "Import":
        from .import_func import import_job

        loaded_data = load_from_dict(ImportJobSchema, data, context, additional_message, **kwargs)

        _import_job: Import = import_job(base_path=context[BASE_PATH_CONTEXT_KEY], **loaded_data)

        return _import_job

    @classmethod
    def _load_from_rest_job(cls, obj: JobBaseData) -> "Import":
        from .import_func import import_job

        rest_command_job: RestCommandJob = obj.properties
        inputs = from_rest_inputs_to_dataset_literal(rest_command_job.inputs)
        outputs = from_rest_data_outputs(rest_command_job.outputs)

        _import_job: Import = import_job(
            name=obj.name,
            display_name=rest_command_job.display_name,
            description=rest_command_job.description,
            experiment_name=rest_command_job.experiment_name,
            status=rest_command_job.status,
            creation_context=obj.system_data,
            inputs=inputs,
            output=outputs["output"] if "output" in outputs else None,
        )
        _import_job._id = obj.id
        if isinstance(_import_job.component, ImportComponent):
            _import_job.component._source = (
                ComponentSource.REMOTE_WORKSPACE_JOB
            )  # This is used by pipeline job telemetries.

        return _import_job

    @classmethod
    def _create_schema_for_validation(cls, context: Any) -> Union[PathAwareSchema, Schema]:
        from azure.ai.ml._schema.pipeline import ImportSchema

        return ImportSchema(context=context)

    # pylint: disable-next=docstring-missing-param
    def __call__(self, *args: Any, **kwargs: Any) -> "Import":
        """Call Import as a function will return a new instance each time.

        :return: An Import node.
        :rtype: Import
        """
        if isinstance(self._component, Component):
            # call this to validate inputs
            node: Import = self._component(*args, **kwargs)
            # merge inputs
            for name, original_input in self.inputs.items():
                if name not in kwargs:
                    # use setattr here to make sure owner of input won't change
                    setattr(node.inputs, name, original_input._data)
                    node._job_inputs[name] = original_input._data
                # get outputs
            for name, original_output in self.outputs.items():
                # use setattr here to make sure owner of input won't change
                if not isinstance(original_output, str):
                    setattr(node.outputs, name, original_output._data)
            self._refine_optional_inputs_with_no_value(node, kwargs)
            # set default values: compute, environment_variables, outputs
            node._name = self.name
            node.compute = self.compute
            node.tags = self.tags
            # Pass through the display name only if the display name is not system generated.
            node.display_name = self.display_name if self.display_name != self.name else None
            return node
        msg = "Import can be called as a function only when referenced component is {}, currently got {}."
        raise ValidationException(
            message=msg.format(type(Component), self._component),
            no_personal_data_message=msg.format(type(Component), "self._component"),
            target=ErrorTarget.COMMAND_JOB,
            error_type=ValidationErrorType.INVALID_VALUE,
        )
