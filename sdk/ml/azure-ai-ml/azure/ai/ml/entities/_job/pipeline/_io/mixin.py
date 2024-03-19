# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import copy
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from azure.ai.ml._restclient.v2023_04_01_preview.models import JobInput as RestJobInput
from azure.ai.ml._restclient.v2023_04_01_preview.models import JobOutput as RestJobOutput
from azure.ai.ml.constants._component import ComponentJobConstants
from azure.ai.ml.entities._inputs_outputs import GroupInput, Input, Output
from azure.ai.ml.entities._util import copy_output_setting
from azure.ai.ml.exceptions import ErrorTarget, ValidationErrorType, ValidationException

from ..._input_output_helpers import (
    from_rest_data_outputs,
    from_rest_inputs_to_dataset_literal,
    to_rest_data_outputs,
    to_rest_dataset_literal_inputs,
)
from .._pipeline_job_helpers import from_dict_to_rest_io, process_sdk_component_job_io
from .attr_dict import InputsAttrDict, OutputsAttrDict, _GroupAttrDict
from .base import NodeInput, NodeOutput, PipelineInput, PipelineOutput


class NodeIOMixin:
    """Provides ability to wrap node inputs/outputs and build data bindings
    dynamically."""

    @classmethod
    def _get_supported_inputs_types(cls) -> Optional[Any]:
        return None

    @classmethod
    def _get_supported_outputs_types(cls) -> Optional[Any]:
        return None

    @classmethod
    def _validate_io(cls, value: Any, allowed_types: Optional[tuple], *, key: Optional[str] = None) -> None:
        if allowed_types is None:
            return

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

    def _build_input(
        self,
        name: str,
        meta: Optional[Input],
        data: Optional[Union[dict, int, bool, float, str, Output, "PipelineInput", Input]],
    ) -> NodeInput:
        # output mode of last node should not affect input mode of next node
        if isinstance(data, NodeOutput):
            # Decoupled input and output
            # value = copy.deepcopy(value)
            data = data._deepcopy()  # pylint: disable=protected-access
            data.mode = None
        elif isinstance(data, dict):
            # Use type comparison instead of is_instance to skip _GroupAttrDict
            # when loading from yaml io will be a dict,
            # like {'job_data_path': '${{parent.inputs.pipeline_job_data_path}}'}
            # parse dict to allowed type
            data = Input(**data)

            # parameter group can be of custom type, so we don't check it here
            if meta is not None and not isinstance(meta, GroupInput):
                self._validate_io(data, self._get_supported_inputs_types(), key=name)
        return NodeInput(port_name=name, meta=meta, data=data, owner=self)

    def _build_output(self, name: str, meta: Optional[Output], data: Optional[Union[Output, str]]) -> NodeOutput:
        if isinstance(data, dict):
            data = Output(**data)

        self._validate_io(data, self._get_supported_outputs_types(), key=name)
        # For un-configured outputs, settings it to None, so we won't pass extra fields(eg: default mode)
        return NodeOutput(port_name=name, meta=meta, data=data, owner=self)

    # pylint: disable=unused-argument
    def _get_default_input_val(self, val: Any):  # type: ignore
        # use None value as data placeholder for unfilled inputs.
        # server side will fill the default value
        return None

    def _build_inputs_dict(
        self,
        inputs: Dict[str, Union[Input, str, bool, int, float]],
        *,
        input_definition_dict: Optional[dict] = None,
    ) -> InputsAttrDict:
        """Build an input attribute dict so user can get/set inputs by
        accessing attribute, eg: node1.inputs.xxx.

        :param inputs: Provided kwargs when parameterizing component func.
        :type inputs: Dict[str, Union[Input, str, bool, int, float]]
        :keyword input_definition_dict: Static input definition dict. If not provided, will build inputs without meta.
        :paramtype input_definition_dict: dict
        :return: Built dynamic input attribute dict.
        :rtype: InputsAttrDict
        """
        if input_definition_dict is not None:
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
        else:
            input_dict = {key: self._build_input(name=key, meta=None, data=val) for key, val in inputs.items()}
        return InputsAttrDict(input_dict)

    def _build_outputs_dict(
        self, outputs: Dict, *, output_definition_dict: Optional[dict] = None, none_data: bool = False
    ) -> OutputsAttrDict:
        """Build an output attribute dict so user can get/set outputs by
        accessing attribute, eg: node1.outputs.xxx.

        :param outputs: Provided kwargs when parameterizing component func.
        :type outputs: Dict[str, Output]
        :keyword output_definition_dict: Static output definition dict.
        :paramtype output_definition_dict: Dict
        :keyword none_data: If True, will set output data to None.
        :paramtype none_data: bool
        :return: Built dynamic output attribute dict.
        :rtype: OutputsAttrDict
        """
        if output_definition_dict is not None:
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
        else:
            output_dict = {}
            for key, val in outputs.items():
                output_val = self._build_output(name=key, meta=None, data=val if not none_data else None)
                output_dict[key] = output_val
        return OutputsAttrDict(output_dict)

    def _build_inputs(self) -> Dict:
        """Build inputs of this component to a dict dict which maps output to
        actual value.

        The built input dict will have same input format as other jobs, eg:
        {
           "input_data": Input(path="path/to/input/data", mode="Mount"),
           "input_value": 10,
           "learning_rate": "${{jobs.step1.inputs.learning_rate}}"
        }

        :return: The input dict
        :rtype: Dict[str, Union[Input, str, bool, int, float]]
        """
        inputs = {}
        # pylint: disable=redefined-builtin
        for name, input in self.inputs.items():  # type: ignore
            if isinstance(input, _GroupAttrDict):
                # Flatten group inputs into inputs dict
                inputs.update(input.flatten(group_parameter_name=name))
                continue
            inputs[name] = input._to_job_input()  # pylint: disable=protected-access
        return inputs

    def _build_outputs(self) -> Dict[str, Output]:
        """Build outputs of this component to a dict which maps output to
        actual value.

        The built output dict will have same output format as other jobs, eg:
        {
            "eval_output": "${{jobs.eval.outputs.eval_output}}"
        }

        :return: The output dict
        :rtype: Dict[str, Output]
        """
        outputs = {}
        for name, output in self.outputs.items():  # type: ignore
            if isinstance(output, NodeOutput):
                output = output._to_job_output()  # pylint: disable=protected-access
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

        :return: The REST inputs
        :rtype: Dict[str, Dict]
        """
        built_inputs = self._build_inputs()
        return self._input_entity_to_rest_inputs(input_entity=built_inputs)

    @classmethod
    def _input_entity_to_rest_inputs(cls, input_entity: Dict[str, Input]) -> Dict[str, Dict]:
        # Convert io entity to rest io objects
        input_bindings, dataset_literal_inputs = process_sdk_component_job_io(
            input_entity, [ComponentJobConstants.INPUT_PATTERN]
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

        :return: The REST outputs
        :rtype: Dict[str, Dict]
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
            if "name" in binding:
                rest_output_bindings[key].update({"name": binding["name"]})
            if "version" in binding:
                rest_output_bindings[key].update({"version": binding["version"]})

        def _rename_name_and_version(output_dict: Dict) -> Dict:
            # NodeOutput can only be registered with name and version, therefore we rename here
            if "asset_name" in output_dict.keys():
                output_dict["name"] = output_dict.pop("asset_name")
            if "asset_version" in output_dict.keys():
                output_dict["version"] = output_dict.pop("asset_version")
            return output_dict

        rest_data_outputs = {name: _rename_name_and_version(val.as_dict()) for name, val in rest_data_outputs.items()}
        self._update_output_types(rest_data_outputs)
        rest_data_outputs.update(rest_output_bindings)
        return rest_data_outputs

    @classmethod
    def _from_rest_inputs(cls, inputs: Dict) -> Dict[str, Union[Input, str, bool, int, float]]:
        """Load inputs from rest inputs.

        :param inputs: The REST inputs
        :type inputs: Dict[str, Union[str, dict]]
        :return: Input dict
        :rtype: Dict[str, Union[Input, str, bool, int, float]]
        """

        # JObject -> RestJobInput/RestJobOutput
        input_bindings, rest_inputs = from_dict_to_rest_io(inputs, RestJobInput, [ComponentJobConstants.INPUT_PATTERN])

        # RestJobInput/RestJobOutput -> Input/Output
        dataset_literal_inputs = from_rest_inputs_to_dataset_literal(rest_inputs)

        return {**dataset_literal_inputs, **input_bindings}

    @classmethod
    def _from_rest_outputs(cls, outputs: Dict[str, Union[str, dict]]) -> Dict:
        """Load outputs from rest outputs.

        :param outputs: The REST outputs
        :type outputs: Dict[str, Union[str, dict]]
        :return: Output dict
        :rtype: Dict[str, Output]
        """

        # JObject -> RestJobInput/RestJobOutput
        output_bindings, rest_outputs = from_dict_to_rest_io(
            outputs, RestJobOutput, [ComponentJobConstants.OUTPUT_PATTERN]
        )

        # RestJobInput/RestJobOutput -> Input/Output
        data_outputs = from_rest_data_outputs(rest_outputs)

        return {**data_outputs, **output_bindings}

    def _update_output_types(self, rest_data_outputs: dict) -> None:
        """Update output types in rest_data_outputs according to meta level output.

        :param rest_data_outputs: The REST data outputs
        :type rest_data_outputs: Dict
        """

        for name, rest_output in rest_data_outputs.items():
            original_output = self.outputs[name]  # type: ignore
            # for configured output with meta, "correct" the output type to file to avoid the uri_folder default value
            if original_output and original_output.type:
                if original_output.type in ["AnyFile", "uri_file"]:
                    rest_output["job_output_type"] = "uri_file"


def flatten_dict(
    dct: Optional[Dict],
    _type: Union[Type["_GroupAttrDict"], Type[GroupInput]],
    *,
    allow_dict_fields: Optional[List[str]] = None,
) -> Dict:
    """Flatten inputs/input_definitions dict for inputs dict build.

    :param dct: The dictionary to flatten
    :type dct: Dict
    :param _type: Either _GroupAttrDict or GroupInput (both have the method `flatten`)
    :type _type: Union[Type["_GroupAttrDict"], Type[GroupInput]]
    :keyword allow_dict_fields: A list of keys for dictionary values that will be included in flattened output
    :paramtype allow_dict_fields: Optional[List[str]]
    :return: The flattened dict
    :rtype: Dict
    """
    _result = {}
    if dct is not None:
        for key, val in dct.items():
            # to support passing dict value as parameter group
            if allow_dict_fields and key in allow_dict_fields and isinstance(val, dict):
                # for child dict, all values are allowed to be dict
                for flattened_key, flattened_val in flatten_dict(
                    val, _type, allow_dict_fields=list(val.keys())
                ).items():
                    _result[key + "." + flattened_key] = flattened_val
                continue
            val = GroupInput.custom_class_value_to_attr_dict(val)
            if isinstance(val, _type):
                _result.update(val.flatten(group_parameter_name=key))
                continue
            _result[key] = val
    return _result


class NodeWithGroupInputMixin(NodeIOMixin):
    """This class provide build_inputs_dict for a node to use ParameterGroup as an input."""

    @classmethod
    def _validate_group_input_type(
        cls,
        input_definition_dict: dict,
        inputs: Dict[str, Union[Input, str, bool, int, float]],
    ) -> None:
        """Raise error when group input receive a value not group type.

        :param input_definition_dict: The input definition dict
        :type input_definition_dict: dict
        :param inputs: The inputs
        :type inputs: Dict[str, Union[Input, str, bool, int, float]]
        """
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
            if isinstance(definition, GroupInput) and not isinstance(val, (_GroupAttrDict, dict)):
                raise ValidationException(
                    message=group_msg % (key, val, type(val)),
                    no_personal_data_message=group_msg % ("[key]", "[val]", "[type(val)]"),
                    target=ErrorTarget.PIPELINE,
                    type=ValidationErrorType.INVALID_VALUE,
                )
            # 2. inputs.str_param = group
            if not isinstance(definition, GroupInput) and isinstance(val, _GroupAttrDict):
                raise ValidationException(
                    message=non_group_msg % key,
                    no_personal_data_message=non_group_msg % "[key]",
                    target=ErrorTarget.PIPELINE,
                    type=ValidationErrorType.INVALID_VALUE,
                )

    @classmethod
    def _flatten_inputs_and_definition(
        cls,
        inputs: Dict[str, Union[Input, str, bool, int, float]],
        input_definition_dict: dict,
    ) -> Tuple[Dict, Dict]:
        """
        Flatten all GroupInput(definition) and GroupAttrDict recursively and build input dict.
        For example:
        input_definition_dict = {
            "group1": GroupInput(
                values={
                    "param1": GroupInput(
                         values={
                             "param1_1": Input(type="str"),
                         }
                    ),
                    "param2": Input(type="int"),
                }
            ),
            "group2": GroupInput(
                values={
                    "param3": Input(type="str"),
                }
            ),
        } => {
            "group1.param1.param1_1": Input(type="str"),
            "group1.param2": Input(type="int"),
            "group2.param3": Input(type="str"),
        }
        inputs = {
            "group1": {
                "param1": {
                    "param1_1": "value1",
                },
                "param2": 2,
            },
            "group2": {
                "param3": "value3",
            },
        } => {
            "group1.param1.param1_1": "value1",
            "group1.param2": 2,
            "group2.param3": "value3",
        }
        :param inputs: The inputs
        :type inputs: Dict[str, Union[Input, str, bool, int, float]]
        :param input_definition_dict: The input definition dict
        :type input_definition_dict: dict
        :return: The flattened inputs and definition
        :rtype: Tuple[Dict, Dict]
        """
        group_input_names = [key for key, val in input_definition_dict.items() if isinstance(val, GroupInput)]
        flattened_inputs = flatten_dict(inputs, _GroupAttrDict, allow_dict_fields=group_input_names)
        flattened_definition_dict = flatten_dict(input_definition_dict, GroupInput)
        return flattened_inputs, flattened_definition_dict

    def _build_inputs_dict(
        self,
        inputs: Dict[str, Union[Input, str, bool, int, float]],
        *,
        input_definition_dict: Optional[dict] = None,
    ) -> InputsAttrDict:
        """Build an input attribute dict so user can get/set inputs by
        accessing attribute, eg: node1.inputs.xxx.

        :param inputs: Provided kwargs when parameterizing component func.
        :type inputs: Dict[str, Union[Input, str, bool, int, float]]
        :keyword input_definition_dict: Input definition dict from component entity.
        :paramtype input_definition_dict: dict
        :return: Built input attribute dict.
        :rtype: InputsAttrDict
        """

        # TODO: should we support group input when there is no local input definition?
        if input_definition_dict is not None:
            # Validate group mismatch
            self._validate_group_input_type(input_definition_dict, inputs)

            # Flatten inputs and definition
            flattened_inputs, flattened_definition_dict = self._flatten_inputs_and_definition(
                inputs, input_definition_dict
            )
            # Build: zip all flattened parameter with definition
            inputs = super()._build_inputs_dict(flattened_inputs, input_definition_dict=flattened_definition_dict)
            return InputsAttrDict(GroupInput.restore_flattened_inputs(inputs))
        return super()._build_inputs_dict(inputs)


class PipelineJobIOMixin(NodeWithGroupInputMixin):
    """Provides ability to wrap pipeline job inputs/outputs and build data bindings
    dynamically."""

    def _build_input(self, name: str, meta: Optional[Input], data: Any) -> "PipelineInput":
        return PipelineInput(name=name, meta=meta, data=data, owner=self)

    def _build_output(
        self, name: str, meta: Optional[Union[Input, Output]], data: Optional[Union[Output, str]]
    ) -> "PipelineOutput":
        # TODO: settings data to None for un-configured outputs so we won't passing extra fields(eg: default mode)
        result = PipelineOutput(port_name=name, meta=meta, data=data, owner=self)
        return result

    def _build_inputs_dict(
        self,
        inputs: Dict[str, Union[Input, str, bool, int, float]],
        *,
        input_definition_dict: Optional[dict] = None,
    ) -> InputsAttrDict:
        """Build an input attribute dict so user can get/set inputs by
        accessing attribute, eg: node1.inputs.xxx.

        :param inputs: Provided kwargs when parameterizing component func.
        :type inputs: Dict[str, Union[Input, str, bool, int, float]]
        :keyword input_definition_dict: Input definition dict from component entity.
        :return: Built input attribute dict.
        :rtype: InputsAttrDict
        """
        input_dict = super()._build_inputs_dict(inputs, input_definition_dict=input_definition_dict)
        # TODO: should we do this when input_definition_dict is not None?
        # TODO: should we put this in super()._build_inputs_dict?
        if input_definition_dict is None:
            return InputsAttrDict(GroupInput.restore_flattened_inputs(input_dict))
        return input_dict

    def _build_output_for_pipeline(self, name: str, data: Optional[Union[Output, NodeOutput]]) -> "PipelineOutput":
        """Build an output object for pipeline and copy settings from source output.

        :param name: Output name.
        :type name: str
        :param data: Output data.
        :type data: Optional[Union[Output, NodeOutput]]
        :return: Built output object.
        :rtype: PipelineOutput
        """
        # pylint: disable=protected-access
        if data is None:
            # For None output, build an empty output builder
            output_val = self._build_output(name=name, meta=None, data=None)
        elif isinstance(data, Output):
            # For output entity, build an output builder with data points to it
            output_val = self._build_output(name=name, meta=data, data=data)
        elif isinstance(data, NodeOutput):
            # For output builder, build a new output builder and copy settings from it
            output_val = self._build_output(name=name, meta=data._meta, data=None)
            copy_output_setting(source=data, target=output_val)
        else:
            message = "Unsupported output type: {} for pipeline output: {}: {}"
            raise ValidationException(
                message=message.format(type(data), name, data),
                no_personal_data_message=message,
                target=ErrorTarget.PIPELINE,
            )
        return output_val

    def _build_pipeline_outputs_dict(self, outputs: Dict) -> OutputsAttrDict:
        """Build an output attribute dict without output definition metadata.
        For pipeline outputs, its setting should be copied from node level outputs.

        :param outputs: Node output dict or pipeline component's outputs.
        :type outputs: Dict[str, Union[Output, NodeOutput]]
        :return: Built dynamic output attribute dict.
        :rtype: OutputsAttrDict
        """
        output_dict = {}
        for key, val in outputs.items():
            output_dict[key] = self._build_output_for_pipeline(name=key, data=val)
        return OutputsAttrDict(output_dict)

    def _build_outputs(self) -> Dict[str, Output]:
        """Build outputs of this pipeline to a dict which maps output to actual
        value.

        The built dictionary's format aligns with component job's output yaml,
        un-configured outputs will be None, eg:
        {"eval_output": "${{jobs.eval.outputs.eval_output}}", "un_configured": None}

        :return: The output dict
        :rtype: Dict[str, Output]
        """
        outputs = {}
        for name, output in self.outputs.items():  # type: ignore
            if isinstance(output, NodeOutput):
                output = output._to_job_output()  # pylint: disable=protected-access
            outputs[name] = output
        return outputs

    def _get_default_input_val(self, val: Any):  # type: ignore
        # use Default value as data placeholder for unfilled inputs.
        # client side need to fill the default value for dsl.pipeline
        if isinstance(val, GroupInput):
            # Copy default value dict for group
            return copy.deepcopy(val.default)
        return val.default

    def _update_output_types(self, rest_data_outputs: Dict) -> None:
        """Won't clear output type for pipeline level outputs since it's required in rest object.

        :param rest_data_outputs: The REST data outputs
        :type rest_data_outputs: Dict
        """


class AutoMLNodeIOMixin(NodeIOMixin):
    """Wrap outputs of automl node and build data bindings dynamically."""

    def __init__(self, **kwargs):  # type: ignore
        # add a inputs field to align with other nodes
        self.inputs = {}
        super(AutoMLNodeIOMixin, self).__init__(**kwargs)
        if getattr(self, "outputs", None):
            self._outputs = self._build_outputs_dict(self.outputs or {})
