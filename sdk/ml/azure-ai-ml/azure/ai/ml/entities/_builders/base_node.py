# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import uuid
from enum import Enum
from functools import wraps
from abc import abstractmethod
from typing import Dict, Union, List, Optional
from azure.ai.ml._utils._arm_id_utils import get_resource_name_from_arm_id_safe
from azure.ai.ml.constants import JobType, ComponentSource
from azure.ai.ml.entities._job.pipeline._attr_dict import _AttrDict
from azure.ai.ml.entities._job.pipeline._io import (
    InputsAttrDict,
    OutputsAttrDict,
    PipelineOutputBase,
    NodeIOMixin,
    PipelineInput,
)
from azure.ai.ml.entities._job.sweep.search_space import SweepDistribution
from azure.ai.ml.entities._mixins import RestTranslatableMixin, YamlTranslatableMixin, TelemetryMixin
from azure.ai.ml.entities._job._input_output_helpers import (
    build_input_output,
)
from azure.ai.ml.entities import Component, Job, ResourceConfiguration
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml._ml_exceptions import ValidationException, ErrorTarget
from azure.ai.ml.entities._util import convert_ordered_dict_to_dict
from azure.ai.ml.entities._validation import SchemaValidatableMixin, ValidationResult

module_logger = logging.getLogger(__name__)


def parse_inputs_outputs(data):
    data["inputs"] = {key: build_input_output(val) for key, val in data.get("inputs", {}).items()}
    data["outputs"] = {key: build_input_output(val, inputs=False) for key, val in data.get("outputs", {}).items()}
    return data


def pipeline_node_decorator(func):
    """Warp func and add it return value to current DSL pipeline."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        automl_job = func(*args, **kwargs)
        from azure.ai.ml.dsl._pipeline_component_builder import (
            _is_inside_dsl_pipeline_func,
            _add_component_to_current_definition_builder,
        )

        if _is_inside_dsl_pipeline_func():
            # Build automl job to automl node if it's defined inside DSL pipeline func.
            automl_job._instance_id = str(uuid.uuid4())
            _add_component_to_current_definition_builder(automl_job)
        return automl_job

    return wrapper


class BaseNode(Job, NodeIOMixin, YamlTranslatableMixin, _AttrDict, SchemaValidatableMixin):
    """Base class for node in pipeline, used for component version consumption. Can't be instantiated directly.

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
    :param display_name: Display name of the job.
    :type display_name: str
    :param compute: Compute definition containing the compute information for the step
    :type compute: str
    :param experiment_name:  Name of the experiment the job will be created under, if None is provided, default will be set to current directory name. Will be ignored as a pipeline step.
    :type experiment_name: str
    """

    def __init__(
        self,
        *,
        type: str = JobType.COMPONENT,
        component: Component,
        inputs: Dict[str, Union[PipelineInput, PipelineOutputBase, Input, str, bool, int, float, Enum, "Input"]] = None,
        outputs: Dict[str, Union[str, Output, "Output"]] = None,
        name: str = None,
        display_name: str = None,
        description: str = None,
        tags: Dict = None,
        properties: Dict = None,
        compute: str = None,
        experiment_name: str = None,
        **kwargs,
    ):
        self._init = True

        _from_component_func = kwargs.pop("_from_component_func", False)
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

        # initialize io
        inputs, outputs = inputs or {}, outputs or {}
        self._validate_io(inputs, self._get_supported_inputs_types(), Input)
        self._validate_io(outputs, self._get_supported_outputs_types(), Output)
        # parse empty dict to None so we won't pass default mode, type to backend
        for k, v in inputs.items():
            if v == {}:
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
        self.kwargs = kwargs

        # Generate an id for every instance
        self._instance_id = str(uuid.uuid4())
        if _from_component_func:
            # add current component in pipeline stack for dsl scenario
            self._register_in_current_pipeline_component_builder()

        self._source_path = self._component._source_path if isinstance(self._component, Component) else None
        self._init = False

    @classmethod
    def _get_supported_inputs_types(cls):
        return None

    @classmethod
    def _get_supported_outputs_types(cls):
        return None

    @classmethod
    def _validate_io(cls, io_dict: dict, allowed_types: Optional[tuple], parse_cls):
        if allowed_types is None:
            return
        for key, value in io_dict.items():
            # output mode of last node should not affect input mode of next node
            if isinstance(value, PipelineOutputBase):
                # value = copy.deepcopy(value)
                value = value._deepcopy()  # Decoupled input and output
                io_dict[key] = value
                value.mode = None
            if value is None or isinstance(value, allowed_types):
                pass
            elif isinstance(value, dict):
                # parse dict to allowed type
                io_dict[key] = parse_cls(**value)
            else:
                msg = "Expecting {} for input/output {}, got {} instead."
                raise ValidationException(
                    message=msg.format(allowed_types, key, type(value)),
                    no_personal_data_message=msg.format(allowed_types, "[key]", type(value)),
                    target=ErrorTarget.PIPELINE,
                )

    def _initializing(self) -> bool:
        # use this to indicate ongoing init process so all attributes set during init process won't be set as
        # arbitrary attribute in _AttrDict
        # TODO: replace this hack
        return self._init

    def _set_base_path(self, base_path):
        """
        Set the base path for the node. Will be used for schema validation.
        If not set, will use Path.cwd() as the base path
        (default logic defined in SchemaValidatableMixin._base_path_for_validation).
        """
        self._base_path = base_path

    def _set_source_path(self, source_path):
        """
        Update the source path for the node.
        """
        self._source_path = source_path

    def _get_component_id(self) -> Union[str, Component]:
        """Return component id if possible."""
        if isinstance(self._component, Component) and self._component.id:
            # If component is remote, return it's asset id
            return self._component.id
        else:
            # Otherwise, return the component version or arm id.
            return self._component

    def _get_component_name(self):
        # first use component version/job's display name or name as component name
        # make it unique when pipeline build finished.
        if self._component is None:
            return None
        elif isinstance(self._component, str):
            return self._component
        else:
            return self._component.name

    def _to_dict(self) -> Dict:
        return self._dump_for_validation()

    @classmethod
    def _get_validation_error_target(cls) -> ErrorTarget:
        """Return the error target of this resource. Should be overridden by subclass.
        Value should be in ErrorTarget enum.
        """
        return ErrorTarget.PIPELINE

    def _validate_inputs(self, raise_error=True):
        validation_result = self._create_empty_validation_result()
        # validate inputs
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
                        message=f"Required input {key} for component {self.name} not provided.",
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

    def _customized_validate(self) -> ValidationResult:
        """Validate the resource with customized logic.
        Override this method to add customized validation logic.
        """
        return self._validate_inputs(raise_error=False)

    @classmethod
    def _get_skip_fields_in_schema_validation(cls) -> List[str]:
        return [
            "inputs",  # processed separately
            "outputs",  # processed separately
            "name",
            "display_name",
            "experiment_name",  # name is not part of schema but may be set in dsl/yml file
            cls._get_component_attr_name(),  # processed separately
            "kwargs",
        ]

    @classmethod
    def _get_component_attr_name(cls) -> str:
        return "component"

    @abstractmethod
    def _to_job(self) -> Job:
        """
        This private function is used by the CLI to get a plain job object so that the CLI can properly serialize the object.
        It is needed as BaseNode._to_dict() dumps objects using pipeline child job schema instead of standalone job schema,
        for example Command objects dump have a nested component property, which doesn't apply to stand alone command jobs.
        BaseNode._to_dict() needs to be able to dump to both pipeline child job dict as well as stand alone job dict base on context.
        """

        pass

    @classmethod
    def _from_rest_object(cls, obj: dict) -> "BaseNode":
        from azure.ai.ml.entities._job.pipeline._load_component import pipeline_node_factory

        return pipeline_node_factory.load_from_rest_object(obj=obj)

    @classmethod
    def _rest_object_to_init_params(cls, obj: dict):
        """
        Transfer the rest object to a dict containing items to init the node. Will be used in _from_rest_object in
        subclasses.
        """
        inputs = obj.get("inputs", {})
        outputs = obj.get("outputs", {})

        obj["inputs"] = BaseNode._from_rest_inputs(inputs)
        obj["outputs"] = BaseNode._from_rest_outputs(outputs)

        # Change computeId -> compute
        compute_id = obj.pop("computeId", None)
        obj["compute"] = get_resource_name_from_arm_id_safe(compute_id)

        return obj

    @classmethod
    def _picked_fields_from_dict_to_rest_object(cls) -> List[str]:
        """
        Override this method to add custom fields to be picked from self._to_dict() in self._to_rest_object().
        Pick nothing by default.
        """
        return []

    def _to_rest_object(self, **kwargs) -> dict:
        """
        Convert self to a rest object for remote call.
        """
        base_dict, rest_obj = self._to_dict(), {}
        for key in self._picked_fields_from_dict_to_rest_object():
            if key not in base_dict:
                rest_obj[key] = None
            else:
                rest_obj[key] = base_dict.get(key)

        rest_obj.update(
            dict(
                name=self.name,
                display_name=self.display_name,
                tags=self.tags,
                computeId=self.compute,
                inputs=self._to_rest_inputs(),
                outputs=self._to_rest_outputs(),
                # add all arbitrary attributes to support setting unknown attributes
                **self._get_attrs(),
            )
        )

        return convert_ordered_dict_to_dict(rest_obj)

    @property
    def inputs(self) -> InputsAttrDict:
        return self._inputs

    @property
    def outputs(self) -> OutputsAttrDict:
        return self._outputs

    @property
    def _source(self) -> ComponentSource:
        # if self._component is component id, node should be rest type.
        return self._component._source if isinstance(self._component, Component) else ComponentSource.REST

    def __str__(self):
        try:
            return str(self._ordered_yaml())
        except BaseException:
            # add try catch in case component job failed in schema parse
            return _AttrDict.__str__()

    def __help__(self):
        # only show help when component has definition
        if isinstance(self._component, Component):
            return self._component.__help__()

    def _get_origin_job_outputs(self):
        """Restore outputs to JobOutput/BindingString and return them."""
        outputs: Dict[str, Union[str, Output]] = {}
        if self.outputs is not None:
            for output_name, output_obj in self.outputs.items():
                if isinstance(output_obj, PipelineOutputBase):
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

    def _refine_optional_inputs_with_no_value(self, node, kwargs):
        """
        Refine optional inputs that have no default value and no value is provided when calling command/parallel function
        This is to align with behavior of calling component to generate a pipeline node.
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
