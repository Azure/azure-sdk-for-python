# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import copy
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Union

from azure.ai.ml._restclient.v2022_10_01_preview.models import JobInput as RestJobInput
from azure.ai.ml._restclient.v2022_10_01_preview.models import JobOutput as RestJobOutput
from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.constants._component import ComponentJobConstants, IOConstants
from azure.ai.ml.entities._assets._artifacts.data import Data
from azure.ai.ml.entities._inputs_outputs import GroupInput, Input, Output
from azure.ai.ml.entities._job._input_output_helpers import (
    from_rest_data_outputs,
    from_rest_inputs_to_dataset_literal,
    to_rest_data_outputs,
    to_rest_dataset_literal_inputs,
)
from azure.ai.ml.entities._job.pipeline._attr_dict import K, V
from azure.ai.ml.entities._job.pipeline._pipeline_expression import PipelineExpressionMixin
from azure.ai.ml.entities._job.pipeline._pipeline_job_helpers import from_dict_to_rest_io, process_sdk_component_job_io
from azure.ai.ml.entities._util import resolve_pipeline_parameter
from azure.ai.ml.exceptions import (
    ErrorCategory,
    ErrorTarget,
    UnexpectedAttributeError,
    UnexpectedKeywordError,
    UserErrorException,
    ValidationException,
)

# pylint: disable=pointless-string-statement
"""Classes in this file converts input & output set by user to pipeline job input & output."""


def _build_data_binding(data: Union["PipelineInput", "Output"]) -> str:
    """Build input builders to data bindings."""
    if isinstance(data, (InputOutputBase)):
        # Build data binding when data is PipelineInput, Output
        result = data._data_binding()
    else:
        # Otherwise just return the data
        result = data
    return result


def _resolve_builders_2_data_bindings(data: Union[list, dict]) -> Union[list, dict, str]:
    """Traverse data and build input builders inside it to data bindings."""
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, (dict, list)):
                data[key] = _resolve_builders_2_data_bindings(val)
            else:
                data[key] = _build_data_binding(val)
        return data
    if isinstance(data, list):
        resolved_data = []
        for val in data:
            resolved_data.append(_resolve_builders_2_data_bindings(val))
        return resolved_data
    return _build_data_binding(data)


def _data_to_input(data):
    """Convert a Data object to an Input object."""
    if data.id:
        return Input(type=data.type, path=data.id)
    return Input(type=data.type, path=f"{data.name}:{data.version}")


class InputOutputBase(ABC):
    def __init__(self, meta: Union[Input, Output], data, **kwargs):
        """Base class of input & output.

        :param meta: Metadata of this input/output, eg: type, min, max, etc.
        :type meta: Union[Input, Output]
        :param data: Actual value of input/output, None means un-configured data.
        :type data: Union[None, int, bool, float, str
                          azure.ai.ml.Input,
                          azure.ai.ml.Output]
        """
        self._meta = meta
        self._data = self._build_data(data)
        self._type = meta.type if meta else kwargs.pop("type", None)
        self._mode = self._data.mode if self._data and hasattr(self._data, "mode") else kwargs.pop("mode", None)
        self._description = (
            self._data.description
            if self._data and hasattr(self._data, "description") and self._data.description
            else kwargs.pop("description", None)
        )
        # TODO: remove this
        self._attribute_map = {}
        super(InputOutputBase, self).__init__(**kwargs)

    @abstractmethod
    def _build_data(self, data, key=None):  # pylint: disable=unused-argument, no-self-use
        """Validate if data matches type and translate it to Input/Output
        acceptable type."""

    @abstractmethod
    def _build_default_data(self):
        """Build default data when data not configured."""

    @property
    def type(self) -> str:
        """Type of input/output."""
        return self._type

    @type.setter
    def type(self, type):  # pylint: disable=redefined-builtin
        # For un-configured input/output, we build a default data entry for them.
        self._build_default_data()
        self._type = type
        if isinstance(self._data, (Input, Output)):
            self._data.type = type
        else:  # when type of self._data is InputOutputBase or its child class
            self._data._type = type

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, mode):
        # For un-configured input/output, we build a default data entry for them.
        self._build_default_data()
        self._mode = mode
        if isinstance(self._data, (Input, Output)):
            self._data.mode = mode
        else:
            self._data._mode = mode

    @property
    def description(self) -> str:
        return self._description

    @property
    def path(self) -> str:
        # This property is introduced for static intellisense.
        if hasattr(self._data, "path"):
            return self._data.path
        msg = f"{type(self._data)} does not have path."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            target=ErrorTarget.PIPELINE,
            error_category=ErrorCategory.USER_ERROR,
        )

    @path.setter
    def path(self, path):
        if hasattr(self._data, "path"):
            self._data.path = path
        else:
            msg = f"{type(self._data)} does not support setting path."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )

    def _data_binding(self) -> str:
        """Return data binding string representation for this input/output."""
        raise NotImplementedError()

    def keys(self):
        # This property is introduced to raise catchable Exception in marshmallow mapping validation trial.
        raise TypeError(f"'{type(self).__name__}' object is not a mapping")

    def __str__(self):
        try:
            return self._data_binding()
        except AttributeError:
            return super(InputOutputBase, self).__str__()


class NodeInput(InputOutputBase):
    """Define one input of a Component."""

    def __init__(
        self,
        name: str,
        meta: Input,
        *,
        data: Union[int, bool, float, str, Output, "PipelineInput", Input] = None,
        owner: Union["BaseComponent", "PipelineJob"] = None,
        **kwargs,
    ):
        """Initialize an input of a component.

        :param name: The name of the input.
        :type name: str
        :param meta: Metadata of this input, eg: type, min, max, etc.
        :type meta: Input
        :param data: The input data. Valid types include int, bool, float, str,
            Output of another component or pipeline input and Input.
            Note that the output of another component or pipeline input associated should be reachable in the scope
            of current pipeline. Input is introduced to support case like
            TODO: new examples
            component.inputs.xxx = Input(path="arm_id")
        :type data: Union[int, bool, float, str
                          azure.ai.ml.Output,
                          azure.ai.ml.Input]
        :param owner: The owner component of the input, used to calculate binding.
        :type owner: Union[azure.ai.ml.entities.BaseNode, azure.ai.ml.entities.PipelineJob]
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        """
        # TODO: validate data matches type in meta
        # TODO: validate supported data
        self._name = name
        self._owner = owner
        super().__init__(meta=meta, data=data, **kwargs)

    def _build_default_data(self):
        """Build default data when input not configured."""
        if self._data is None:
            self._data = Input()

    def _build_data(self, data, key=None):  # pylint: disable=unused-argument
        """Build input data according to assigned input, eg: node.inputs.key = data"""
        data = resolve_pipeline_parameter(data)
        if data is None:
            return data
        if type(data) is NodeInput:  # pylint: disable=unidiomatic-typecheck
            msg = "Can not bind input to another component's input."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )
        if isinstance(data, (PipelineInput, NodeOutput)):
            # If value is input or output, it's a data binding, we require it have a owner so we can convert it to
            # a data binding, eg: ${{inputs.xxx}}
            if isinstance(data, NodeOutput) and data._owner is None:
                msg = "Setting input binding {} to output without owner is not allowed."
                raise ValidationException(
                    message=msg.format(data),
                    no_personal_data_message=msg.format("[data]"),
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
            return data
        # for data binding case, set is_singular=False for case like "${{parent.inputs.job_in_folder}}/sample1.csv"
        if isinstance(data, Input) or is_data_binding_expression(data, is_singular=False):
            return data
        if isinstance(data, Data):
            return _data_to_input(data)
        # self._meta.type could be None when sub pipeline has no annotation
        if isinstance(self._meta, Input) and self._meta.type and not self._meta._is_primitive_type:
            if isinstance(data, str):
                return Input(type=self._meta.type, path=data)
            msg = "only path input is supported now but get {}: {}."
            raise UserErrorException(
                message=msg.format(type(data), data),
                no_personal_data_message=msg.format(type(data), "[data]"),
            )
        return data

    def _to_job_input(self):
        """convert the input to Input, this logic will change if backend
        contract changes."""
        if self._data is None:
            # None data means this input is not configured.
            result = None
        elif isinstance(self._data, (PipelineInput, NodeOutput)):
            # Build data binding when data is PipelineInput, Output
            result = Input(path=self._data._data_binding(), mode=self.mode)
        elif is_data_binding_expression(self._data):
            result = Input(path=self._data, mode=self.mode)
        else:
            data_binding = _build_data_binding(self._data)
            if is_data_binding_expression(self._data):
                result = Input(path=data_binding, mode=self.mode)
            else:
                result = data_binding
            # TODO: validate is self._data is supported

        return result

    def _data_binding(self):
        msg = "Input binding {} can only come from a pipeline, currently got {}"
        # call type(self._owner) to avoid circular import
        raise ValidationException(
            message=msg.format(self._name, type(self._owner)),
            target=ErrorTarget.PIPELINE,
            no_personal_data_message=msg.format("[name]", "[owner]"),
            error_category=ErrorCategory.USER_ERROR,
        )

    def _copy(self, owner):
        return NodeInput(
            name=self._name,
            data=self._data,
            owner=owner,
            meta=self._meta,
        )

    def _deepcopy(self):
        return NodeInput(
            name=self._name,
            data=copy.copy(self._data),
            owner=self._owner,
            meta=self._meta,
        )


class NodeOutput(InputOutputBase, PipelineExpressionMixin):
    """Define one output of a Component."""

    def __init__(
        self,
        name: str,
        meta: Output,
        *,
        data: Union[Output, str] = None,
        owner: Union["BaseComponent", "PipelineJob"] = None,
        **kwargs,
    ):
        """Initialize an Output of a component.

        :param name: The name of the output.
        :type name: str
        :param data: The output data. Valid types include str, Output
        :type data: Union[str
                          azure.ai.ml.entities.Output]
        :param mode: The mode of the output.
        :type mode: str
        :param owner: The owner component of the output, used to calculate binding.
        :type owner: Union[azure.ai.ml.entities.BaseNode, azure.ai.ml.entities.PipelineJob]
        :param kwargs: A dictionary of additional configuration parameters.
        :type kwargs: dict
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if object cannot be successfully validated.
            Details will be provided in the error message.
        """
        # Allow inline output binding with string, eg: "component_out_path_1": "${{parents.outputs.job_out_data_1}}"
        if data and not isinstance(data, (Output, str)):
            msg = "Got unexpected type for output: {}."
            raise ValidationException(
                message=msg.format(data),
                target=ErrorTarget.PIPELINE,
                no_personal_data_message=msg.format("[data]"),
            )
        super().__init__(meta=meta, data=data, **kwargs)
        self._name = name
        self._owner = owner
        self._is_control = meta.is_control if meta else None

    @property
    def is_control(self) -> str:
        return self._is_control

    def _build_default_data(self):
        """Build default data when output not configured."""
        if self._data is None:
            self._data = Output()

    def _build_data(self, data, key=None):
        """Build output data according to assigned input, eg: node.outputs.key = data"""
        if data is None:
            return data
        if not isinstance(data, (Output, str)):
            msg = f"{self.__class__.__name__} only allow set {Output.__name__} object, {type(data)} is not supported."
            raise ValidationException(
                message=msg,
                target=ErrorTarget.PIPELINE,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
            )
        return data

    def _to_job_output(self):
        """Convert the output to Output, this logic will change if backend
        contract changes."""
        if self._data is None:
            # None data means this output is not configured.
            result = None
        elif isinstance(self._data, str):
            result = Output(path=self._data, mode=self.mode)
        elif isinstance(self._data, Output):
            result = self._data
        elif isinstance(self._data, PipelineOutput):
            is_control = self._meta.is_control if self._meta else None
            result = Output(path=self._data._data_binding(), mode=self.mode, is_control=is_control)
        else:
            msg = "Got unexpected type for output: {}."
            raise ValidationException(
                message=msg.format(self._data),
                target=ErrorTarget.PIPELINE,
                no_personal_data_message=msg.format("[data]"),
            )
        return result

    def _data_binding(self):
        return f"${{{{parent.jobs.{self._owner.name}.outputs.{self._name}}}}}"

    def _copy(self, owner):
        return NodeOutput(
            name=self._name,
            data=self._data,
            owner=owner,
            meta=self._meta,
        )

    def _deepcopy(self):
        return NodeOutput(
            name=self._name,
            data=copy.copy(self._data),
            owner=self._owner,
            meta=self._meta,
        )

    def __hash__(self):
        return id(self)


class PipelineInput(NodeInput, PipelineExpressionMixin):
    """Define one input of a Pipeline."""

    def __init__(self, name: str, meta: Input, group_names: List[str] = None, **kwargs):
        """
        Initialize a PipelineInput.

        :param name: The name of the input.
        :type name: str
        :param meta: Metadata of this input, eg: type, min, max, etc.
        :type meta: Input
        :param group_names: The input parameter's group names.
        :type group_names: List[str]
        """
        super(PipelineInput, self).__init__(name=name, meta=meta, **kwargs)
        self._group_names = group_names if group_names else []
        self._full_name = "%s.%s" % (".".join(self._group_names), self._name) if self._group_names else self._name

    def __str__(self) -> str:
        return self._data_binding()

    def _build_data(self, data, key=None):  # pylint: disable=unused-argument
        """Build data according to input type."""
        if data is None:
            return data
        if type(data) is NodeInput:  # pylint: disable=unidiomatic-typecheck
            msg = "Can not bind input to another component's input."
            raise ValidationException(message=msg, no_personal_data_message=msg, target=ErrorTarget.PIPELINE)
        if isinstance(data, (PipelineInput, NodeOutput)):
            # If value is input or output, it's a data binding, we require it have a owner so we can convert it to
            # a data binding, eg: ${{parent.inputs.xxx}}
            if isinstance(data, NodeOutput) and data._owner is None:
                msg = "Setting input binding {} to output without owner is not allowed."
                raise ValidationException(
                    message=msg.format(data),
                    no_personal_data_message=msg.format("[data]"),
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
            return data
        if isinstance(data, Data):
            # If value is Data, we convert it to an corresponding Input
            return _data_to_input(data)
        return data

    def _data_binding(self):
        return f"${{{{parent.inputs.{self._full_name}}}}}"

    def _to_input(self) -> Input:
        """Convert pipeline input to component input for pipeline component."""
        if self._data is None:
            # None data means this input is not configured.
            return self._meta
        data_type = self._data.type if isinstance(self._data, Input) else None
        # If type is asset type, return data type without default.
        # Else infer type from data and set it as default.
        if data_type and data_type.lower() in AssetTypes.__dict__.values():
            result = Input(type=data_type, mode=self._data.mode)
        elif type(self._data) in IOConstants.PRIMITIVE_TYPE_2_STR:
            result = Input(
                type=IOConstants.PRIMITIVE_TYPE_2_STR[type(self._data)],
                default=self._data,
            )
        else:
            msg = f"Unsupported Input type {type(self._data)} detected when translate job to component."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )
        return result


class PipelineOutput(NodeOutput):
    """Define one output of a Pipeline."""

    def _to_job_output(self):
        if isinstance(self._data, Output):
            # For pipeline output with type Output, always pass to backend.
            return self._data
        return super(PipelineOutput, self)._to_job_output()

    def _data_binding(self):
        return f"${{{{parent.outputs.{self._name}}}}}"

    def _to_output(self) -> Output:
        """Convert pipeline output to component output for pipeline
        component."""
        if self._data is None:
            # None data means this input is not configured.
            return None
        if isinstance(self._meta, Output):
            return self._meta
        # Assign type directly as we didn't have primitive output type for now.
        return Output(type=self._data.type, mode=self._data.mode)


class InputsAttrDict(dict):
    def __init__(self, inputs: dict, **kwargs):
        self._validate_inputs(inputs)
        super(InputsAttrDict, self).__init__(**inputs, **kwargs)

    @classmethod
    def _validate_inputs(cls, inputs):
        msg = "Pipeline/component input should be a \
        azure.ai.ml.entities._job.pipeline._io.NodeInput with owner, got {}."
        for val in inputs.values():
            if isinstance(val, NodeInput) and val._owner is not None:
                continue
            if isinstance(val, _GroupAttrDict):
                continue
            raise ValidationException(
                message=msg.format(val),
                no_personal_data_message=msg.format("[val]"),
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )

    def __setattr__(
        self,
        key: str,
        value: Union[int, bool, float, str, NodeOutput, PipelineInput, Input],
    ):
        # Extract enum value.
        value = value.value if isinstance(value, Enum) else value
        original_input = self.__getattr__(key)  # Note that an exception will be raised if the keyword is invalid.
        if isinstance(original_input, _GroupAttrDict) or isinstance(value, _GroupAttrDict):
            # Set the value directly if is parameter group.
            self._set_group_with_type_check(key, GroupInput.custom_class_value_to_attr_dict(value))
            return
        original_input._data = original_input._build_data(value)

    def _set_group_with_type_check(self, key, value):
        msg = "{!r} is expected to be a parameter group, but got {}."
        if not isinstance(value, _GroupAttrDict):
            raise ValidationException(
                message=msg.format(key, type(value)),
                no_personal_data_message=msg.format("[key]", "[value_type]"),
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )
        self.__setitem__(key, GroupInput.custom_class_value_to_attr_dict(value))

    def __getattr__(self, item) -> NodeInput:
        return self.__getitem__(item)


class _GroupAttrDict(InputsAttrDict):
    """This class is used for accessing values with instance.some_key."""

    @classmethod
    def _validate_inputs(cls, inputs):
        msg = "Pipeline/component input should be a azure.ai.ml.entities._job.pipeline._io.NodeInput, got {}."
        for val in inputs.values():
            if isinstance(val, NodeInput) and val._owner is not None:
                continue
            if isinstance(val, _GroupAttrDict):
                continue
            # Allow PipelineInput as Group may appear at top level pipeline input.
            if isinstance(val, PipelineInput):
                continue
            raise ValidationException(
                message=msg.format(val),
                no_personal_data_message=msg.format("[val]"),
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )

    def __getattr__(self, name: K) -> V:
        if name not in self:
            # pylint: disable=unnecessary-comprehension
            raise UnexpectedAttributeError(keyword=name, keywords=[key for key in self])
        return super().__getitem__(name)

    def __getitem__(self, item: K) -> V:
        # We raise this exception instead of KeyError
        if item not in self:
            # pylint: disable=unnecessary-comprehension
            raise UnexpectedKeywordError(func_name="ParameterGroup", keyword=item, keywords=[key for key in self])
        return super().__getitem__(item)

    # For Jupyter Notebook auto-completion
    def __dir__(self):
        return list(super().__dir__()) + list(self.keys())

    def flatten(self, group_parameter_name):
        # Return the flattened result of self

        group_parameter_name = group_parameter_name if group_parameter_name else ""
        flattened_parameters = {}
        msg = "'%s' in parameter group should be a azure.ai.ml.entities._job._io.NodeInput, got '%s'."
        for k, v in self.items():
            flattened_name = ".".join([group_parameter_name, k])
            if isinstance(v, _GroupAttrDict):
                flattened_parameters.update(v.flatten(flattened_name))
            elif isinstance(v, NodeInput):
                flattened_parameters[flattened_name] = v._to_job_input()
            else:
                raise ValidationException(
                    message=msg % (flattened_name, type(v)),
                    no_personal_data_message=msg % ("name", "type"),
                    target=ErrorTarget.PIPELINE,
                )
        return flattened_parameters


class OutputsAttrDict(dict):
    def __init__(self, outputs: dict, **kwargs):
        for val in outputs.values():
            if not isinstance(val, NodeOutput) or val._owner is None:
                msg = "Pipeline/component output should be a azure.ai.ml.dsl.Output with owner, got {}."
                raise ValidationException(
                    message=msg.format(val),
                    no_personal_data_message=msg.format("[val]"),
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
        super(OutputsAttrDict, self).__init__(**outputs, **kwargs)

    def __getattr__(self, item) -> NodeOutput:
        return self.__getitem__(item)

    def __setattr__(self, key: str, value: Union[Data, Output]):
        if isinstance(value, Output):
            mode = value.mode
            value = Output(type=value.type, path=value.path, mode=mode)
        original_output = self.__getattr__(key)  # Note that an exception will be raised if the keyword is invalid.
        original_output._data = original_output._build_data(value)

    def __setitem__(self, key: str, value: Output):
        return self.__setattr__(key, value)


class NodeIOMixin:
    """Provides ability to wrap node inputs/outputs and build data bindings
    dynamically."""

    def _build_input(self, name, meta: Input, data) -> NodeInput:
        return NodeInput(name=name, meta=meta, data=data, owner=self)

    def _build_output(self, name, meta: Output, data) -> NodeOutput:
        # For un-configured outputs, settings it to None so we won't passing extra fields(eg: default mode)
        return NodeOutput(name=name, meta=meta, data=data, owner=self)

    def _get_default_input_val(self, val):  # pylint: disable=unused-argument, no-self-use
        # use None value as data placeholder for unfilled inputs.
        # server side will fill the default value
        return None

    def _build_inputs_dict(
        self,
        input_definition_dict: dict,
        inputs: Dict[str, Union[Input, str, bool, int, float]],
    ) -> InputsAttrDict:
        """Build an input attribute dict so user can get/set inputs by
        accessing attribute, eg: node1.inputs.xxx.

        :param input_definition_dict: Input definition dict from component entity.
        :param inputs: Provided kwargs when parameterizing component func.
        :return: Built input attribute dict.
        """
        # TODO: validate inputs.keys() in input_definitions.keys()
        input_dict = {}
        for key, val in input_definition_dict.items():
            if key in inputs.keys():
                # If input is set through component functions' kwargs, create an input object with real value.
                data = inputs[key]
            else:
                data = self._get_default_input_val(val)  # pylint: disable=assignment-from-none

            val = self._build_input(name=key, meta=val, data=data)
            input_dict[key] = val
        return InputsAttrDict(input_dict)

    def _build_outputs_dict(self, output_definition_dict: dict, outputs: Dict[str, Output]) -> OutputsAttrDict:
        """Build a output attribute dict so user can get/set outputs by
        accessing attribute, eg: node1.outputs.xxx.

        :param output_definition_dict: Output definition dict from component entity.
        :return: Built output attribute dict.
        """
        # TODO: check if we need another way to mark a un-configured output instead of just set None.
        # Create None as data placeholder for all outputs.
        output_dict = {}
        for key, val in output_definition_dict.items():
            if key in outputs.keys():
                # If output has given value, create an output object with real value.
                val = self._build_output(name=key, meta=val, data=outputs[key])
            else:
                val = self._build_output(name=key, meta=val, data=None)
            output_dict[key] = val
        return OutputsAttrDict(output_dict)

    def _build_inputs_dict_without_meta(self, inputs: Dict[str, Union[Input, str, bool, int, float]]) -> InputsAttrDict:
        input_dict = {key: self._build_input(name=key, meta=None, data=val) for key, val in inputs.items()}
        return InputsAttrDict(input_dict)

    def _build_outputs_dict_without_meta(self, outputs: Dict[str, Output]) -> OutputsAttrDict:
        output_dict = {key: self._build_output(name=key, meta=None, data=val) for key, val in outputs.items()}
        return OutputsAttrDict(output_dict)

    def _build_inputs(self) -> Dict[str, Union[Input, str, bool, int, float]]:
        """Build inputs of this component to a dict dict which maps output to
        actual value.

        The built input dict will have same input format as other jobs, eg:
        {
           "input_data": Input(path="path/to/input/data", mode="Mount"),
           "input_value": 10,
           "learning_rate": "${{jobs.step1.inputs.learning_rate}}"
        }
        """
        inputs = {}
        for name, input in self.inputs.items():  # pylint: disable=redefined-builtin
            if isinstance(input, _GroupAttrDict):
                # Flatten group inputs into inputs dict
                inputs.update(input.flatten(group_parameter_name=name))
                continue
            inputs[name] = input._to_job_input()
        return inputs

    def _build_outputs(self) -> Dict[str, Output]:
        """Build outputs of this component to a dict which maps output to
        actual value.

        The built output dict will have same output format as other jobs, eg:
        {
            "eval_output": "${{jobs.eval.outputs.eval_output}}"
        }
        """
        outputs = {}
        for name, output in self.outputs.items():
            if isinstance(output, NodeOutput):
                output = output._to_job_output()
            outputs[name] = output
        # Remove non-configured output
        return {k: v for k, v in outputs.items() if v is not None}

    def _to_rest_inputs(self) -> Dict[str, Dict]:
        """Translate input builders to rest input dicts.

        The built dictionary's format aligns with component job's input yaml, eg:
        {
           "input_data": {"data": {"path": "path/to/input/data"},  "mode"="Mount"},
           "input_value": 10,
           "learning_rate": "${{jobs.step1.inputs.learning_rate}}"
        }
        """
        built_inputs = self._build_inputs()

        # Convert io entity to rest io objects
        input_bindings, dataset_literal_inputs = process_sdk_component_job_io(
            built_inputs, [ComponentJobConstants.INPUT_PATTERN]
        )

        # parse input_bindings to InputLiteral(value=str(binding))
        rest_inputs = {**input_bindings, **dataset_literal_inputs}
        # Note: The function will only be called from BaseNode,
        # and job_type is used to enable dot in pipeline job input keys,
        # so pass job_type as None directly here.
        rest_inputs = to_rest_dataset_literal_inputs(rest_inputs, job_type=None)

        # convert rest io to dict
        rest_dataset_literal_inputs = {}
        for name, val in rest_inputs.items():
            rest_dataset_literal_inputs[name] = val.as_dict()
            if hasattr(val, "mode") and val.mode:
                rest_dataset_literal_inputs[name].update({"mode": val.mode.value})
        return rest_dataset_literal_inputs

    def _to_rest_outputs(self) -> Dict[str, Dict]:
        """Translate output builders to rest output dicts.

        The built dictionary's format aligns with component job's output yaml, eg:
        {"eval_output": "${{jobs.eval.outputs.eval_output}}"}
        """
        built_outputs = self._build_outputs()

        # Convert io entity to rest io objects
        output_bindings, data_outputs = process_sdk_component_job_io(
            built_outputs, [ComponentJobConstants.OUTPUT_PATTERN]
        )
        rest_data_outputs = to_rest_data_outputs(data_outputs)

        # convert rest io to dict
        # parse output_bindings to {"value": binding, "type": "literal"} since there's no mode for it
        rest_output_bindings = {}
        for key, binding in output_bindings.items():
            rest_output_bindings[key] = {"value": binding["value"], "type": "literal"}
            if "mode" in binding:
                rest_output_bindings[key].update({"mode": binding["mode"].value})
        rest_data_outputs = {name: val.as_dict() for name, val in rest_data_outputs.items()}
        rest_data_outputs.update(rest_output_bindings)
        return rest_data_outputs

    @classmethod
    def _from_rest_inputs(cls, inputs) -> Dict[str, Union[Input, str, bool, int, float]]:
        """Load inputs from rest inputs."""

        # JObject -> RestJobInput/RestJobOutput
        input_bindings, rest_inputs = from_dict_to_rest_io(inputs, RestJobInput, [ComponentJobConstants.INPUT_PATTERN])

        # RestJobInput/RestJobOutput -> Input/Output
        dataset_literal_inputs = from_rest_inputs_to_dataset_literal(rest_inputs)

        return {**dataset_literal_inputs, **input_bindings}

    @classmethod
    def _from_rest_outputs(cls, outputs) -> Dict[str, Output]:
        """Load outputs from rest outputs."""

        # JObject -> RestJobInput/RestJobOutput
        output_bindings, rest_outputs = from_dict_to_rest_io(
            outputs, RestJobOutput, [ComponentJobConstants.OUTPUT_PATTERN]
        )

        # RestJobInput/RestJobOutput -> Input/Output
        data_outputs = from_rest_data_outputs(rest_outputs)

        return {**data_outputs, **output_bindings}


class PipelineNodeIOMixin(NodeIOMixin):
    """This class provide build_inputs_dict for Pipeline and PipelineJob to support ParameterGroup."""

    def _validate_group_input_type(  # pylint: disable=no-self-use
        self,
        input_definition_dict: dict,
        inputs: Dict[str, Union[Input, str, bool, int, float]],
    ):
        """Raise error when group input receive a value not group type."""
        # Note: We put and extra validation here instead of doing it in pipeline._validate()
        # due to group input will be discarded silently if assign it to a non-group parameter.
        group_msg = "'%s' is defined as a parameter group but got input '%s' with type '%s'."
        non_group_msg = "'%s' is defined as a parameter but got a parameter group as input."
        for key, val in inputs.items():
            definition = input_definition_dict.get(key)
            val = GroupInput.custom_class_value_to_attr_dict(val)
            if val is None:
                continue
            # 1. inputs.group = 'a string'
            if isinstance(definition, GroupInput) and not isinstance(val, _GroupAttrDict):
                raise ValidationException(
                    message=group_msg % (key, val, type(val)),
                    no_personal_data_message=group_msg % ("[key]", "[val]", "[type(val)]"),
                    target=ErrorTarget.PIPELINE,
                )
            # 2. inputs.str_param = group
            if not isinstance(definition, GroupInput) and isinstance(val, _GroupAttrDict):
                raise ValidationException(
                    message=non_group_msg % key,
                    no_personal_data_message=non_group_msg % "[key]",
                    target=ErrorTarget.PIPELINE,
                )

    def _build_inputs_dict(
        self,
        input_definition_dict: dict,
        inputs: Dict[str, Union[Input, str, bool, int, float]],
    ) -> InputsAttrDict:
        """Build an input attribute dict so user can get/set inputs by
        accessing attribute, eg: node1.inputs.xxx.

        :param input_definition_dict: Input definition dict from component entity.
        :param inputs: Provided kwargs when parameterizing component func.
        :return: Built input attribute dict.
        """

        def flatten_dict(dct, _type):
            """Flatten inputs/input_definitions dict for inputs dict build."""
            _result = {}
            for key, val in dct.items():
                val = GroupInput.custom_class_value_to_attr_dict(val)
                if isinstance(val, _type):
                    _result.update(val.flatten(group_parameter_name=key))
                    continue
                _result[key] = val
            return _result

        # Validate group mismatch
        self._validate_group_input_type(input_definition_dict, inputs)
        # Flatten all GroupInput(definition) and GroupAttrDict.
        flattened_inputs = flatten_dict(inputs, _GroupAttrDict)
        flattened_definition_dict = flatten_dict(input_definition_dict, GroupInput)
        # Build: zip all flattened parameter with definition
        inputs = super()._build_inputs_dict(flattened_definition_dict, flattened_inputs)
        return InputsAttrDict(GroupInput.restore_flattened_inputs(inputs))


class PipelineIOMixin(PipelineNodeIOMixin):
    """Provides ability to wrap pipeline inputs/outputs and build data bindings
    dynamically."""

    def _build_input(self, name, meta: Input, data) -> "PipelineInput":
        return PipelineInput(name=name, meta=meta, data=data, owner=self)

    def _build_output(self, name, meta: Output, data) -> "PipelineOutput":
        # TODO: settings data to None for un-configured outputs so we won't passing extra fields(eg: default mode)
        return PipelineOutput(name=name, meta=meta, data=data, owner=self)

    def _build_inputs_dict_without_meta(self, inputs: Dict[str, Union[Input, str, bool, int, float]]) -> InputsAttrDict:
        input_dict = {key: self._build_input(name=key, meta=None, data=val) for key, val in inputs.items()}
        input_dict = GroupInput.restore_flattened_inputs(input_dict)
        return InputsAttrDict(input_dict)

    def _build_outputs(self) -> Dict[str, Output]:
        """Build outputs of this pipeline to a dict which maps output to actual
        value.

        The built dictionary's format aligns with component job's output yaml,
        un-configured outputs will be None, eg:
        {"eval_output": "${{jobs.eval.outputs.eval_output}}", "un_configured": None}
        """
        outputs = {}
        for name, output in self.outputs.items():
            if isinstance(output, NodeOutput):
                output = output._to_job_output()
            outputs[name] = output
        return outputs

    def _get_default_input_val(self, val):
        # use Default value as data placeholder for unfilled inputs.
        # client side need to fill the default value for dsl.pipeline
        if isinstance(val, GroupInput):
            # Copy default value dict for group
            return copy.deepcopy(val.default)
        return val.default


class AutoMLNodeIOMixin(NodeIOMixin):
    """Wrap outputs of automl node and build data bindings dynamically."""

    def __init__(self, **kwargs):
        # add a inputs field to align with other nodes
        self.inputs = {}
        super(AutoMLNodeIOMixin, self).__init__(**kwargs)
        if getattr(self, "outputs", None):
            self._outputs = self._build_outputs_dict_without_meta(self.outputs or {})
