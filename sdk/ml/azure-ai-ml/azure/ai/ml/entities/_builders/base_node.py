# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

import logging
import os
import uuid
from abc import abstractmethod
from enum import Enum
from functools import wraps
from typing import Any, Dict, List, Optional, Union

from azure.ai.ml._utils._arm_id_utils import get_resource_name_from_arm_id_safe
from azure.ai.ml.constants import JobType
from azure.ai.ml.constants._common import CommonYamlFields
from azure.ai.ml.constants._component import NodeType
from azure.ai.ml.entities import Data, Model
from azure.ai.ml.entities._component.component import Component
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job._input_output_helpers import build_input_output
from azure.ai.ml.entities._job.job import Job
from azure.ai.ml.entities._job.pipeline._attr_dict import _AttrDict
from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput
from azure.ai.ml.entities._job.pipeline._io.mixin import NodeWithGroupInputMixin
from azure.ai.ml.entities._job.pipeline._pipeline_expression import PipelineExpression
from azure.ai.ml.entities._job.sweep.search_space import SweepDistribution
from azure.ai.ml.entities._mixins import YamlTranslatableMixin
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict, resolve_pipeline_parameters
from azure.ai.ml.entities._validation import MutableValidationResult, PathAwareSchemaValidatableMixin
from azure.ai.ml.exceptions import ErrorTarget, ValidationException

module_logger = logging.getLogger(__name__)


def parse_inputs_outputs(data: dict) -> dict:
    """Parse inputs and outputs from data. If data is a list, parse each item in the list.

    :param data: A dict that may contain "inputs" or "outputs" keys
    :type data: dict
    :return: Dict with parsed "inputs" and "outputs" keys
    :rtype: Dict
    """

    if "inputs" in data:
        data["inputs"] = {key: build_input_output(val) for key, val in data["inputs"].items()}
    if "outputs" in data:
        data["outputs"] = {key: build_input_output(val, inputs=False) for key, val in data["outputs"].items()}
    return data


def pipeline_node_decorator(func: Any) -> Any:
    """Wrap a function and add its return value to the current DSL pipeline.

    :param func: The function to be wrapped.
    :type func: callable
    :return: The wrapped function.
    :rtype: callable
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        automl_job = func(*args, **kwargs)
        from azure.ai.ml.dsl._pipeline_component_builder import (
            _add_component_to_current_definition_builder,
            _is_inside_dsl_pipeline_func,
        )

        if _is_inside_dsl_pipeline_func():
            # Build automl job to automl node if it's defined inside DSL pipeline func.
            automl_job._instance_id = str(uuid.uuid4())
            _add_component_to_current_definition_builder(automl_job)
        return automl_job

    return wrapper


# pylint: disable=too-many-instance-attributes
class BaseNode(Job, YamlTranslatableMixin, _AttrDict, PathAwareSchemaValidatableMixin, NodeWithGroupInputMixin):
    """Base class for node in pipeline, used for component version consumption. Can't be instantiated directly.

    You should not instantiate this class directly. Instead, you should
    create from a builder function.

    :param type: Type of pipeline node. Defaults to JobType.COMPONENT.
    :type type: str
    :param component: Id or instance of the component version to be run for the step
    :type component: Component
    :param inputs: The inputs for the node.
    :type inputs: Optional[Dict[str, Union[
        ~azure.ai.ml.entities._job.pipeline._io.PipelineInput,
        ~azure.ai.ml.entities._job.pipeline._io.NodeOutput,
        ~azure.ai.ml.entities.Input,
        str,
        bool,
        int,
        float,
        Enum,
        'Input']]]
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: Optional[Dict[str, Union[str, ~azure.ai.ml.entities.Output, 'Output']]]
    :param name: The name of the node.
    :type name: Optional[str]
    :param display_name: The display name of the node.
    :type display_name: Optional[str]
    :param description: The description of the node.
    :type description: Optional[str]
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: Optional[Dict]
    :param properties: The properties of the job.
    :type properties: Optional[Dict]
    :param comment: Comment of the pipeline node, which will be shown in designer canvas.
    :type comment: Optional[str]
    :param compute: Compute definition containing the compute information for the step.
    :type compute: Optional[str]
    :param experiment_name: Name of the experiment the job will be created under,
        if None is provided, default will be set to current directory name.
        Will be ignored as a pipeline step.
    :type experiment_name: Optional[str]
    :param kwargs: Additional keyword arguments for future compatibility.
    """

    def __init__(
        self,
        *,
        type: str = JobType.COMPONENT,  # pylint: disable=redefined-builtin
        component: Any,
        inputs: Optional[Dict] = None,
        outputs: Optional[Dict] = None,
        name: Optional[str] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        comment: Optional[str] = None,
        compute: Optional[str] = None,
        experiment_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self._init = True
        # property _source can't be set
        source = kwargs.pop("_source", None)
        _from_component_func = kwargs.pop("_from_component_func", False)
        self._name: Optional[str] = None
        super(BaseNode, self).__init__(
            type=type,
            name=name,
            display_name=display_name,
            description=description,
            tags=tags,
            properties=properties,
            compute=compute,
            experiment_name=experiment_name,
            **kwargs,
        )
        self.comment = comment

        # initialize io
        inputs = resolve_pipeline_parameters(inputs)
        inputs, outputs = inputs or {}, outputs or {}
        # parse empty dict to None so we won't pass default mode, type to backend
        # add `isinstance` to avoid converting to expression
        for k, v in inputs.items():
            if isinstance(v, dict) and v == {}:
                inputs[k] = None

        # TODO: get rid of self._job_inputs, self._job_outputs once we have unified Input
        self._job_inputs, self._job_outputs = inputs, outputs
        if isinstance(component, Component):
            # Build the inputs from component input definition and given inputs, unfilled inputs will be None
            self._inputs = self._build_inputs_dict(inputs or {}, input_definition_dict=component.inputs)
            # Build the outputs from component output definition and given outputs, unfilled outputs will be None
            self._outputs = self._build_outputs_dict(outputs or {}, output_definition_dict=component.outputs)
        else:
            # Build inputs/outputs dict without meta when definition not available
            self._inputs = self._build_inputs_dict(inputs or {})
            self._outputs = self._build_outputs_dict(outputs or {})

        self._component = component
        self._referenced_control_flow_node_instance_id: Optional[str] = None
        self.kwargs = kwargs

        # Generate an id for every instance
        self._instance_id = str(uuid.uuid4())
        if _from_component_func:
            # add current component in pipeline stack for dsl scenario
            self._register_in_current_pipeline_component_builder()

        if source is None:
            if isinstance(component, Component):
                source = self._component._source
            else:
                source = Component._resolve_component_source_from_id(id=self._component)
        self._source = source
        self._validate_required_input_not_provided = True
        self._init = False

    @property
    def name(self) -> Optional[str]:
        """Get the name of the node.

        :return: The name of the node.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the name of the node.

        :param value: The name to set for the node.
        :type value: str
        :return: None
        """
        # when name is not lower case, lower it to make sure it's a valid node name
        if value and value != value.lower():
            module_logger.warning(
                "Changing node name %s to lower case: %s since upper case is not allowed node name.",
                value,
                value.lower(),
            )
            value = value.lower()
        self._name = value

    @classmethod
    def _get_supported_inputs_types(cls) -> Any:
        """Get the supported input types for node input.

        :param cls: The class (or instance) to retrieve supported input types for.
        :type cls: object

        :return: A tuple of supported input types.
        :rtype: tuple
        """
        # supported input types for node input
        return (
            PipelineInput,
            NodeOutput,
            Input,
            Data,
            Model,
            str,
            bool,
            int,
            float,
            Enum,
            PipelineExpression,
        )

    @property
    def _skip_required_compute_missing_validation(self) -> bool:
        return False

    def _initializing(self) -> bool:
        # use this to indicate ongoing init process so all attributes set during init process won't be set as
        # arbitrary attribute in _AttrDict
        # TODO: replace this hack
        return self._init

    def _set_base_path(self, base_path: Optional[Union[str, os.PathLike]]) -> None:
        """Set the base path for the node.

        Will be used for schema validation. If not set, will use Path.cwd() as the base path
        (default logic defined in SchemaValidatableMixin._base_path_for_validation).

        :param base_path: The new base path
        :type base_path: Union[str, os.PathLike]
        """
        self._base_path = base_path

    def _set_referenced_control_flow_node_instance_id(self, instance_id: str) -> None:
        """Set the referenced control flow node instance id.

        If this node is referenced to a control flow node, the instance_id will not be modified.

        :param instance_id: The new instance id
        :type instance_id: str
        """
        if not self._referenced_control_flow_node_instance_id:
            self._referenced_control_flow_node_instance_id = instance_id

    def _get_component_id(self) -> Union[str, Component]:
        """Return component id if possible.

        :return: The component id
        :rtype: Union[str, Component]
        """
        if isinstance(self._component, Component) and self._component.id:
            # If component is remote, return it's asset id
            return self._component.id
        # Otherwise, return the component version or arm id.
        res: Union[str, Component] = self._component
        return res

    def _get_component_name(self) -> Optional[str]:
        # first use component version/job's display name or name as component name
        # make it unique when pipeline build finished.
        if self._component is None:
            return None
        if isinstance(self._component, str):
            return self._component
        return str(self._component.name)

    def _to_dict(self) -> Dict:
        return dict(convert_ordered_dict_to_dict(self._dump_for_validation()))

    @classmethod
    def _create_validation_error(cls, message: str, no_personal_data_message: str) -> ValidationException:
        return ValidationException(
            message=message,
            no_personal_data_message=no_personal_data_message,
            target=ErrorTarget.PIPELINE,
        )

    def _validate_inputs(self) -> MutableValidationResult:
        validation_result = self._create_empty_validation_result()
        if self._validate_required_input_not_provided:
            # validate required inputs not provided
            if isinstance(self._component, Component):
                for key, meta in self._component.inputs.items():
                    # raise error when required input with no default value not set
                    if (
                        not self._is_input_set(input_name=key)  # input not provided
                        and meta.optional is not True  # and it's required
                        and meta.default is None  # and it does not have default
                    ):
                        validation_result.append_error(
                            yaml_path=f"inputs.{key}",
                            message=f"Required input {key!r} for component {self.name!r} not provided.",
                        )

        inputs = self._build_inputs()
        for input_name, input_obj in inputs.items():
            if isinstance(input_obj, SweepDistribution):
                validation_result.append_error(
                    yaml_path=f"inputs.{input_name}",
                    message=f"Input of command {self.name} is a SweepDistribution, "
                    f"please use command.sweep to transform the command into a sweep node.",
                )
        return validation_result

    def _customized_validate(self) -> MutableValidationResult:
        """Validate the resource with customized logic.

        Override this method to add customized validation logic.

        :return: The validation result
        :rtype: MutableValidationResult
        """
        validate_result = self._validate_inputs()
        return validate_result

    @classmethod
    def _get_skip_fields_in_schema_validation(cls) -> List[str]:
        return [
            "inputs",  # processed separately
            "outputs",  # processed separately
            "name",
            "display_name",
            "experiment_name",  # name is not part of schema but may be set in dsl/yml file
            "kwargs",
        ]

    @classmethod
    def _get_component_attr_name(cls) -> str:
        return "component"

    @abstractmethod
    def _to_job(self) -> Job:
        """This private function is used by the CLI to get a plain job object
        so that the CLI can properly serialize the object.

        It is needed as BaseNode._to_dict() dumps objects using pipeline child job schema instead of standalone job
        schema, for example Command objects dump have a nested component property, which doesn't apply to stand alone
        command jobs. BaseNode._to_dict() needs to be able to dump to both pipeline child job dict as well as stand
        alone job dict base on context.
        """

    @classmethod
    def _from_rest_object(cls, obj: dict) -> "BaseNode":
        if CommonYamlFields.TYPE not in obj:
            obj[CommonYamlFields.TYPE] = NodeType.COMMAND

        from azure.ai.ml.entities._job.pipeline._load_component import pipeline_node_factory

        # todo: refine Hard code for now to support different task type for DataTransfer node
        _type = obj[CommonYamlFields.TYPE]
        if _type == NodeType.DATA_TRANSFER:
            _type = "_".join([NodeType.DATA_TRANSFER, obj.get("task", "")])
        instance: BaseNode = pipeline_node_factory.get_create_instance_func(_type)()
        init_kwargs = instance._from_rest_object_to_init_params(obj)
        # TODO: Bug Item number: 2883415
        instance.__init__(**init_kwargs)  # type: ignore
        return instance

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: dict) -> Dict:
        """Convert the rest object to a dict containing items to init the node.

        Will be used in _from_rest_object. Please override this method instead of _from_rest_object to make the logic
        reusable.

        :param obj: The REST object
        :type obj: dict
        :return: The init params
        :rtype: Dict
        """
        inputs = obj.get("inputs", {})
        outputs = obj.get("outputs", {})

        obj["inputs"] = BaseNode._from_rest_inputs(inputs)
        obj["outputs"] = BaseNode._from_rest_outputs(outputs)

        # Change computeId -> compute
        compute_id = obj.pop("computeId", None)
        obj["compute"] = get_resource_name_from_arm_id_safe(compute_id)

        # Change componentId -> component. Note that sweep node has no componentId.
        if "componentId" in obj:
            obj["component"] = obj.pop("componentId")

        # distribution, sweep won't have distribution
        if "distribution" in obj and obj["distribution"]:
            from azure.ai.ml.entities._job.distribution import DistributionConfiguration

            obj["distribution"] = DistributionConfiguration._from_rest_object(obj["distribution"])

        return obj

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        """List of fields to be picked from self._to_dict() in self._to_rest_object().

        By default, returns an empty list.

        Override this method to add custom fields.

        :return: List of fields to pick
        :rtype: List[str]
        """

        return []

    def _to_rest_object(self, **kwargs: Any) -> dict:  # pylint: disable=unused-argument
        """Convert self to a rest object for remote call.

        :return: The rest object
        :rtype: dict
        """
        base_dict, rest_obj = self._to_dict(), {}
        for key in self._picked_fields_from_dict_to_rest_object():
            if key in base_dict:
                rest_obj[key] = base_dict.get(key)

        rest_obj.update(
            dict(  # pylint: disable=use-dict-literal
                name=self.name,
                type=self.type,
                display_name=self.display_name,
                tags=self.tags,
                computeId=self.compute,
                inputs=self._to_rest_inputs(),
                outputs=self._to_rest_outputs(),
                properties=self.properties,
                _source=self._source,
                # add all arbitrary attributes to support setting unknown attributes
                **self._get_attrs(),
            )
        )
        # only add comment in REST object when it is set
        if self.comment is not None:
            rest_obj.update({"comment": self.comment})

        return dict(convert_ordered_dict_to_dict(rest_obj))

    @property
    def inputs(self) -> Dict:
        """Get the inputs for the object.

        :return: A dictionary containing the inputs for the object.
        :rtype: Dict[str, Union[Input, str, bool, int, float]]
        """
        return self._inputs  # type: ignore

    @property
    def outputs(self) -> Dict:
        """Get the outputs of the object.

        :return: A dictionary containing the outputs for the object.
        :rtype: Dict[str, Union[str, Output]]
        """
        return self._outputs  # type: ignore

    def __str__(self) -> str:
        try:
            return str(self._to_yaml())
        except BaseException:  # pylint: disable=W0718
            # add try catch in case component job failed in schema parse
            _obj: _AttrDict = _AttrDict()
            return _obj.__str__()

    def __hash__(self) -> int:  # type: ignore
        return hash(self.__str__())

    def __help__(self) -> Any:
        # only show help when component has definition
        if isinstance(self._component, Component):
            # TODO: Bug Item number: 2883422
            return self._component.__help__()  # type: ignore
        return None

    def __bool__(self) -> bool:
        # _attr_dict will return False if no extra attributes are set
        return True

    def _get_origin_job_outputs(self) -> Dict[str, Union[str, Output]]:
        """Restore outputs to JobOutput/BindingString and return them.

        :return: The origin job outputs
        :rtype: Dict[str, Union[str, Output]]
        """
        outputs: Dict = {}
        if self.outputs is not None:
            for output_name, output_obj in self.outputs.items():
                if isinstance(output_obj, NodeOutput):
                    outputs[output_name] = output_obj._data
                else:
                    raise TypeError("unsupported built output type: {}: {}".format(output_name, type(output_obj)))
        return outputs

    def _get_telemetry_values(self) -> Dict:
        telemetry_values = {"type": self.type, "source": self._source}
        return telemetry_values

    def _register_in_current_pipeline_component_builder(self) -> None:
        """Register this node in current pipeline component builder by adding self to a global stack."""
        from azure.ai.ml.dsl._pipeline_component_builder import _add_component_to_current_definition_builder

        # TODO: would it be better if we make _add_component_to_current_definition_builder a public function of
        #  _PipelineComponentBuilderStack and make _PipelineComponentBuilderStack a singleton?
        _add_component_to_current_definition_builder(self)

    def _is_input_set(self, input_name: str) -> bool:
        built_inputs = self._build_inputs()
        return input_name in built_inputs and built_inputs[input_name] is not None

    @classmethod
    def _refine_optional_inputs_with_no_value(cls, node: "BaseNode", kwargs: Any) -> None:
        """Refine optional inputs that have no default value and no value is provided when calling command/parallel
        function.

        This is to align with behavior of calling component to generate a pipeline node.

        :param node: The node
        :type node: BaseNode
        :param kwargs: The kwargs
        :type kwargs: dict
        """
        for key, value in node.inputs.items():
            meta = value._data
            if (
                isinstance(meta, Input)
                and meta._is_primitive_type is False
                and meta.optional is True
                and not meta.path
                and key not in kwargs
            ):
                value._data = None
