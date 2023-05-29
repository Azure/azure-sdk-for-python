# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access

import logging
import uuid
from abc import abstractmethod
from enum import Enum
from functools import wraps
from typing import Dict, List, Optional, Union

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
from azure.ai.ml.entities._job.pipeline._io import NodeOutput, PipelineInput, PipelineNodeIOMixin
from azure.ai.ml.entities._job.pipeline._pipeline_expression import PipelineExpression
from azure.ai.ml.entities._job.sweep.search_space import SweepDistribution
from azure.ai.ml.entities._mixins import YamlTranslatableMixin
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict, resolve_pipeline_parameters
from azure.ai.ml.entities._validation import MutableValidationResult, SchemaValidatableMixin
from azure.ai.ml.exceptions import ErrorTarget, ValidationErrorType, ValidationException

module_logger = logging.getLogger(__name__)


def parse_inputs_outputs(data):
    if "inputs" in data:
        data["inputs"] = {key: build_input_output(val) for key, val in data["inputs"].items()}
    if "outputs" in data:
        data["outputs"] = {key: build_input_output(val, inputs=False) for key, val in data["outputs"].items()}
    return data


def pipeline_node_decorator(func):
    """Wrap func and add it return value to current DSL pipeline."""

    @wraps(func)
    def wrapper(*args, **kwargs):
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
class BaseNode(Job, PipelineNodeIOMixin, YamlTranslatableMixin, _AttrDict, SchemaValidatableMixin):
    """Base class for node in pipeline, used for component version consumption. Can't be instantiated directly.

    You should not instantiate this class directly. Instead, you should
    create from a builder function.

    :param type: Type of pipeline node
    :type type: str
    :param component: Id or instance of the component version to be run for the step
    :type component: Union[Component, str]
    :param inputs: Inputs to the node.
    :type inputs: Dict[str, Union[Input, SweepDistribution, str, bool, int, float, Enum, dict]]
    :param outputs: Mapping of output data bindings used in the job.
    :type outputs: Dict[str, Union[str, Output, dict]]
    :param name: Name of the node.
    :type name: str
    :param description: Description of the node.
    :type description: str
    :param tags: Tag dictionary. Tags can be added, removed, and updated.
    :type tags: dict[str, str]
    :param properties: The job property dictionary.
    :type properties: dict[str, str]
    :param comment: Comment of the pipeline node, which will be shown in designer canvas.
    :type comment: str
    :param display_name: Display name of the job.
    :type display_name: str
    :param compute: Compute definition containing the compute information for the step
    :type compute: str
    :param experiment_name:  Name of the experiment the job will be created under,
        if None is provided, default will be set to current directory name. Will be ignored as a pipeline step.
    :type experiment_name: str
    """

    def __init__(
        self,
        *,
        type: str = JobType.COMPONENT,  # pylint: disable=redefined-builtin
        component: Component,
        inputs: Optional[
            Dict[
                str,
                Union[
                    PipelineInput,
                    NodeOutput,
                    Input,
                    str,
                    bool,
                    int,
                    float,
                    Enum,
                    "Input",
                ],
            ]
        ] = None,
        outputs: Optional[Dict[str, Union[str, Output, "Output"]]] = None,
        name: Optional[str] = None,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict] = None,
        properties: Optional[Dict] = None,
        comment: Optional[str] = None,
        compute: Optional[str] = None,
        experiment_name: Optional[str] = None,
        **kwargs,
    ):
        self._init = True
        # property _source can't be set
        kwargs.pop("_source", None)
        _from_component_func = kwargs.pop("_from_component_func", False)
        self._name = None
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
        self._parse_io(inputs, Input)
        self._validate_io(inputs, self._get_supported_inputs_types())
        self._parse_io(outputs, Output)
        self._validate_io(outputs, self._get_supported_outputs_types())
        # parse empty dict to None so we won't pass default mode, type to backend
        # add `isinstance` to avoid converting to expression
        for k, v in inputs.items():
            if isinstance(v, dict) and v == {}:
                inputs[k] = None

        # TODO: get rid of self._job_inputs, self._job_outputs once we have unified Input
        self._job_inputs, self._job_outputs = inputs, outputs
        if isinstance(component, Component):
            # Build the inputs from component input definition and given inputs, unfilled inputs will be None
            self._inputs = self._build_inputs_dict(component.inputs, inputs or {})
            # Build the outputs from component output definition and given outputs, unfilled outputs will be None
            self._outputs = self._build_outputs_dict(component.outputs, outputs or {})
        else:
            # Build inputs/outputs dict without meta when definition not available
            self._inputs = self._build_inputs_dict_without_meta(inputs or {})
            self._outputs = self._build_outputs_dict_without_meta(outputs or {})

        self._component = component
        self._referenced_control_flow_node_instance_id = None
        self.kwargs = kwargs

        # Generate an id for every instance
        self._instance_id = str(uuid.uuid4())
        if _from_component_func:
            # add current component in pipeline stack for dsl scenario
            self._register_in_current_pipeline_component_builder()

        self._source = (
            self._component._source
            if isinstance(self._component, Component)
            else Component._resolve_component_source_from_id(id=self._component)
        )
        self._validate_required_input_not_provided = True
        self._init = False

    @property
    def name(self) -> str:
        """Name of the node."""
        return self._name

    @name.setter
    def name(self, value):
        """Set name of the node."""
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
    def _get_supported_inputs_types(cls):
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

    @classmethod
    def _get_supported_outputs_types(cls):
        # supported output types for node input
        return None

    @property
    def _skip_required_compute_missing_validation(self):
        return False

    @classmethod
    def _validate_io(cls, io_dict: dict, allowed_types: Optional[tuple]):
        if allowed_types is None:
            return
        for key, value in io_dict.items():
            if value is None or isinstance(value, allowed_types):
                pass
            else:
                msg = "Expecting {} for input/output {}, got {} instead."
                raise ValidationException(
                    message=msg.format(allowed_types, key, type(value)),
                    no_personal_data_message=msg.format(allowed_types, "[key]", type(value)),
                    target=ErrorTarget.PIPELINE,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )

    @classmethod
    def _parse_io(cls, io_dict: dict, parse_cls):
        for key, value in io_dict.items():
            # output mode of last node should not affect input mode of next node
            if isinstance(value, NodeOutput):
                # value = copy.deepcopy(value)
                value = value._deepcopy()  # Decoupled input and output
                io_dict[key] = value
                value.mode = None
            elif type(value) == dict:  # pylint: disable=unidiomatic-typecheck
                # Use type comparison instead of is_instance to skip _GroupAttrDict
                # when loading from yaml io will be a dict,
                # like {'job_data_path': '${{parent.inputs.pipeline_job_data_path}}'}
                # parse dict to allowed type
                io_dict[key] = parse_cls(**value)

    def _initializing(self) -> bool:
        # use this to indicate ongoing init process so all attributes set during init process won't be set as
        # arbitrary attribute in _AttrDict
        # TODO: replace this hack
        return self._init

    def _set_base_path(self, base_path):
        """Set the base path for the node.

        Will be used for schema validation. If not set, will use Path.cwd() as the base path (default logic defined in
        SchemaValidatableMixin._base_path_for_validation).
        """
        self._base_path = base_path

    def _set_referenced_control_flow_node_instance_id(self, instance_id):
        """Set the referenced control flow node instance id.

        If this node is referenced to a control flow node, the instance_id will not be modified.
        """
        if not self._referenced_control_flow_node_instance_id:
            self._referenced_control_flow_node_instance_id = instance_id

    def _get_component_id(self) -> Union[str, Component]:
        """Return component id if possible."""
        if isinstance(self._component, Component) and self._component.id:
            # If component is remote, return it's asset id
            return self._component.id
        # Otherwise, return the component version or arm id.
        return self._component

    def _get_component_name(self):
        # first use component version/job's display name or name as component name
        # make it unique when pipeline build finished.
        if self._component is None:
            return None
        if isinstance(self._component, str):
            return self._component
        return self._component.name

    def _to_dict(self) -> Dict:
        return self._dump_for_validation()

    @classmethod
    def _get_validation_error_target(cls) -> ErrorTarget:
        """Return the error target of this resource.

        Should be overridden by subclass. Value should be in ErrorTarget enum.
        """
        return ErrorTarget.PIPELINE

    def _validate_inputs(self, raise_error=True):
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
        return validation_result.try_raise(self._get_validation_error_target(), raise_error=raise_error)

    def _customized_validate(self) -> MutableValidationResult:
        """Validate the resource with customized logic.

        Override this method to add customized validation logic.
        """
        validate_result = self._validate_inputs(raise_error=False)
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
        """This private function is used by the CLI to get a plain job object so that the CLI can properly serialize the
        object.

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
        instance.__init__(**init_kwargs)
        return instance

    @classmethod
    def _from_rest_object_to_init_params(cls, obj: dict) -> Dict:
        """Transfer the rest object to a dict containing items to init the node.

        Will be used in _from_rest_object. Please override this method instead of _from_rest_object to make the logic
        reusable.
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
        """Override this method to add custom fields to be picked from self._to_dict() in self._to_rest_object().

        Pick nothing by default.
        """
        return []

    def _to_rest_object(self, **kwargs) -> dict:  # pylint: disable=unused-argument
        """Convert self to a rest object for remote call."""
        base_dict, rest_obj = self._to_dict(), {}
        for key in self._picked_fields_from_dict_to_rest_object():
            if key in base_dict:
                rest_obj[key] = base_dict.get(key)

        rest_obj.update(
            dict(
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
            rest_obj.update(dict(comment=self.comment))

        return convert_ordered_dict_to_dict(rest_obj)

    @property
    def inputs(self) -> Dict[str, Union[Input, str, bool, int, float]]:
        return self._inputs

    @property
    def outputs(self) -> Dict[str, Union[str, Output]]:
        return self._outputs

    def __str__(self):
        try:
            return str(self._to_yaml())
        except BaseException:  # pylint: disable=broad-except
            # add try catch in case component job failed in schema parse
            return _AttrDict.__str__()

    def __hash__(self):
        return hash(self.__str__())

    def __help__(self):
        # only show help when component has definition
        if isinstance(self._component, Component):
            return self._component.__help__()

    def __bool__(self):
        # _attr_dict will return False if no extra attributes are set
        return True

    def _get_origin_job_outputs(self):
        """Restore outputs to JobOutput/BindingString and return them."""
        outputs: Dict[str, Union[str, Output]] = {}
        if self.outputs is not None:
            for output_name, output_obj in self.outputs.items():
                if isinstance(output_obj, NodeOutput):
                    outputs[output_name] = output_obj._data
                else:
                    raise TypeError("unsupported built output type: {}: {}".format(output_name, type(output_obj)))
        return outputs

    def _get_telemetry_values(self):
        telemetry_values = {"type": self.type, "source": self._source}
        return telemetry_values

    def _register_in_current_pipeline_component_builder(self):
        """Register this node in current pipeline component builder by adding self to a global stack."""
        from azure.ai.ml.dsl._pipeline_component_builder import _add_component_to_current_definition_builder

        # TODO: would it be better if we make _add_component_to_current_definition_builder a public function of
        #  _PipelineComponentBuilderStack and make _PipelineComponentBuilderStack a singleton?
        _add_component_to_current_definition_builder(self)

    def _is_input_set(self, input_name: str) -> bool:
        built_inputs = self._build_inputs()
        return input_name in built_inputs and built_inputs[input_name] is not None

    @classmethod
    def _refine_optional_inputs_with_no_value(cls, node, kwargs):
        """Refine optional inputs that have no default value and no value is provided when calling command/parallel
        function This is to align with behavior of calling component to generate a pipeline node."""
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
