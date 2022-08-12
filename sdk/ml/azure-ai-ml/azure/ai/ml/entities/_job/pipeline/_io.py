# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import copy
from abc import ABC, abstractmethod
from typing import Dict, Union

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml._restclient.v2022_02_01_preview.models import JobInput as RestJobInput
from azure.ai.ml._restclient.v2022_02_01_preview.models import JobOutput as RestJobOutput
from azure.ai.ml._utils.utils import is_data_binding_expression
from azure.ai.ml.constants import AssetTypes, ComponentJobConstants, IOConstants
from azure.ai.ml.entities._assets._artifacts.data import Data
from azure.ai.ml.entities._inputs_outputs import Input, Output
from azure.ai.ml.entities._job.pipeline._pipeline_expression import PipelineExpressionMixin
from azure.ai.ml.entities._job._input_output_helpers import (
    from_rest_data_outputs,
    from_rest_inputs_to_dataset_literal,
    to_rest_data_outputs,
    to_rest_dataset_literal_inputs,
)
from azure.ai.ml.entities._job.pipeline._exceptions import UserErrorException
from azure.ai.ml.entities._job.pipeline._pipeline_job_helpers import from_dict_to_rest_io, process_sdk_component_job_io

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
    elif isinstance(data, list):
        resolved_data = []
        for val in data:
            resolved_data.append(_resolve_builders_2_data_bindings(val))
        return resolved_data
    else:
        return _build_data_binding(data)


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
    def _build_data(self, data):
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
    def type(self, type):
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
        else:
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


class PipelineInputBase(InputOutputBase):
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

    def _build_data(self, data):
        """Build input data according to assigned input, eg: node.inputs.key = data"""
        if data is None:
            return data
        elif type(data) is PipelineInputBase:
            msg = "Can not bind input to another component's input."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                target=ErrorTarget.PIPELINE,
                error_category=ErrorCategory.USER_ERROR,
            )
        elif isinstance(data, (PipelineInput, PipelineOutputBase)):
            # If value is input or output, it's a data binding, we require it have a owner so we can convert it to
            # a data binding, eg: ${{inputs.xxx}}
            if isinstance(data, PipelineOutputBase) and data._owner is None:
                msg = "Setting input binding {} to output without owner is not allowed."
                raise ValidationException(
                    message=msg.format(data),
                    no_personal_data_message=msg.format("[data]"),
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
            else:
                return data
        # for data binding case, set is_singular=False for case like "${{parent.inputs.job_in_folder}}/sample1.csv"
        elif isinstance(data, Input) or is_data_binding_expression(data, is_singular=False):
            return data
        elif isinstance(self._meta, Input) and not self._meta._is_primitive_type:
            if isinstance(data, str):
                return Input(type=self._meta.type, path=data)
            else:
                msg = "only path input is supported now but get {}: {}."
                raise UserErrorException(
                    message=msg.format(type(data), data),
                    no_personal_data_message=msg.format(type(data), "[data]"),
                )
        else:
            return data

    def _to_job_input(self):
        """convert the input to Input, this logic will change if backend
        contract changes."""
        if self._data is None:
            # None data means this input is not configured.
            result = None
        elif isinstance(self._data, (PipelineInput, PipelineOutputBase)):
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
        raise ValidationException(
            message=msg.format(self._name, self._owner),
            target=ErrorTarget.PIPELINE,
            no_personal_data_message=msg.format("[name]", "[owner]"),
            error_category=ErrorCategory.USER_ERROR,
        )

    def _copy(self, owner):
        return PipelineInputBase(
            name=self._name,
            data=self._data,
            owner=owner,
            meta=self._meta,
        )

    def _deepcopy(self):
        return PipelineInputBase(
            name=self._name,
            data=copy.copy(self._data),
            owner=self._owner,
            meta=self._meta,
        )


class PipelineOutputBase(InputOutputBase):
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

    def _build_default_data(self):
        """Build default data when output not configured."""
        if self._data is None:
            self._data = Output()

    def _build_data(self, data):
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
            result = Output(path=self._data._data_binding(), mode=self.mode)
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
        return PipelineOutputBase(
            name=self._name,
            data=self._data,
            owner=owner,
            meta=self._meta,
        )

    def _deepcopy(self):
        return PipelineOutputBase(
            name=self._name,
            data=copy.copy(self._data),
            owner=self._owner,
            meta=self._meta,
        )


class PipelineInput(PipelineInputBase, PipelineExpressionMixin):
    """Define one input of a Pipeline."""

    def __init__(self, name: str, meta: Input, **kwargs):
        super(PipelineInput, self).__init__(name=name, meta=meta, **kwargs)

    def __str__(self) -> str:
        return self._data_binding()

    def _build_data(self, data):
        """Build data according to input type."""
        if data is None:
            return data
        if type(data) is PipelineInputBase:
            msg = "Can not bind input to another component's input."
            raise ValidationException(message=msg, no_personal_data_message=msg, target=ErrorTarget.PIPELINE)
        if isinstance(data, (PipelineInput, PipelineOutputBase)):
            # If value is input or output, it's a data binding, we require it have a owner so we can convert it to
            # a data binding, eg: ${{parent.inputs.xxx}}
            if isinstance(data, PipelineOutputBase) and data._owner is None:
                msg = "Setting input binding {} to output without owner is not allowed."
                raise ValidationException(
                    message=msg.format(data),
                    no_personal_data_message=msg.format("[data]"),
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
            else:
                return data
        elif isinstance(data, Data):
            msg = "Data input is not supported for now."
            raise UserErrorException(message=msg, no_personal_data_message=msg)
        return data

    def _data_binding(self):
        return f"${{{{parent.inputs.{self._name}}}}}"

    def _to_input(self) -> Input:
        """Convert pipeline input to component input for pipeline component."""
        if self._data is None:
            # None data means this input is not configured.
            return None
        if isinstance(self._meta, Input):
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


class PipelineOutput(PipelineOutputBase):
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
        for key, val in inputs.items():
            if not isinstance(val, PipelineInputBase) or val._owner is None:
                msg = "Pipeline/component input should be a azure.ai.ml.dsl.Input with owner, got {}."
                raise ValidationException(
                    message=msg.format(val),
                    no_personal_data_message=msg.format("[val]"),
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
        super(InputsAttrDict, self).__init__(**inputs, **kwargs)

    def __setattr__(
        self,
        key: str,
        value: Union[int, bool, float, str, PipelineOutputBase, PipelineInput, Input],
    ):
        original_input = self.__getattr__(key)  # Note that an exception will be raised if the keyword is invalid.
        original_input._data = original_input._build_data(value)

    def __getitem__(self, item) -> PipelineInputBase:
        return super().__getitem__(item)

    def __getattr__(self, item) -> PipelineInputBase:
        return self.__getitem__(item)


class OutputsAttrDict(dict):
    def __init__(self, outputs: dict, **kwargs):
        for key, val in outputs.items():
            if not isinstance(val, PipelineOutputBase) or val._owner is None:
                msg = "Pipeline/component output should be a azure.ai.ml.dsl.Output with owner, got {}."
                raise ValidationException(
                    message=msg.format(val),
                    no_personal_data_message=msg.format("[val]"),
                    target=ErrorTarget.PIPELINE,
                    error_category=ErrorCategory.USER_ERROR,
                )
        super(OutputsAttrDict, self).__init__(**outputs, **kwargs)

    def __getitem__(self, item) -> PipelineOutputBase:
        # TODO: Handle key error here?
        return super().__getitem__(item)

    def __getattr__(self, item) -> PipelineOutputBase:
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
    """Provides ability to warp node inputs/outputs and build data bindings
    dynamically."""

    def __init__(self, **kwargs):
        super(NodeIOMixin, self).__init__(**kwargs)

    def _build_input(self, name, meta: Input, data) -> PipelineInputBase:
        return PipelineInputBase(name=name, meta=meta, data=data, owner=self)

    def _build_output(self, name, meta: Output, data) -> PipelineOutputBase:
        # For un-configured outputs, settings it to None so we won't passing extra fields(eg: default mode)
        return PipelineOutputBase(name=name, meta=meta, data=data, owner=self)

    def _get_default_input_val(self, val):
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
                data = self._get_default_input_val(val)

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
        inputs = {name: input._to_job_input() for name, input in self.inputs.items()}
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
            if isinstance(output, PipelineOutputBase):
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
        rest_inputs = to_rest_dataset_literal_inputs(rest_inputs)

        # convert rest io to dict
        rest_dataset_literal_inputs = {name: val.as_dict() for name, val in rest_inputs.items()}
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
        # parse output_bindings to {"value": binding, "type": "Literal"} since there's no mode for it
        rest_output_bindings = {}
        for key, binding in output_bindings.items():
            rest_output_bindings[key] = {"value": binding["value"], "type": "Literal"}
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


class PipelineIOMixin(NodeIOMixin):
    """Provides ability to warp pipeline inputs/outputs and build data bindings
    dynamically."""

    def _build_input(self, name, meta: Input, data) -> "PipelineInput":
        return PipelineInput(name=name, meta=meta, data=data, owner=self)

    def _build_output(self, name, meta: Output, data) -> "PipelineOutput":
        # TODO: settings data to None for un-configured outputs so we won't passing extra fields(eg: default mode)
        return PipelineOutput(name=name, meta=meta, data=data, owner=self)

    def _build_outputs(self) -> Dict[str, Output]:
        """Build outputs of this pipeline to a dict which maps output to actual
        value.

        The built dictionary's format aligns with component job's output yaml,
        un-configured outputs will be None, eg:
        {"eval_output": "${{jobs.eval.outputs.eval_output}}", "un_configured": None}
        """
        outputs = {}
        for name, output in self.outputs.items():
            if isinstance(output, PipelineOutputBase):
                output = output._to_job_output()
            outputs[name] = output
        return outputs

    def _get_default_input_val(self, val):
        # use Default value as data placeholder for unfilled inputs.
        # client side need to fill the default value for dsl.pipeline
        return val.default


class AutoMLNodeIOMixin(NodeIOMixin):
    """Wrap outputs of automl node and build data bindings dynamically."""

    def __init__(self, **kwargs):
        # add a inputs field to align with other nodes
        self.inputs = {}
        super(AutoMLNodeIOMixin, self).__init__(**kwargs)
        if getattr(self, "outputs", None):
            self._outputs = self._build_outputs_dict_without_meta(self.outputs or {})
