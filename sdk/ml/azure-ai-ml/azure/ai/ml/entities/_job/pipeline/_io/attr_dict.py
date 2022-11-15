# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from enum import Enum
from typing import Union

from azure.ai.ml.entities._assets import Data
from azure.ai.ml.entities._inputs_outputs import GroupInput, Input, Output
from azure.ai.ml.entities._job.pipeline._io.base import NodeInput, NodeOutput, PipelineInput, InputOutputBase
from azure.ai.ml.exceptions import (
    ErrorTarget,
    ErrorCategory,
    ValidationException,
    UnexpectedKeywordError,
    UnexpectedAttributeError,
)
from azure.ai.ml.entities._job.pipeline._attr_dict import K, V


class InputsAttrDict(dict):
    def __init__(self, inputs: dict, **kwargs):
        self._validate_inputs(inputs)
        super(InputsAttrDict, self).__init__(**inputs, **kwargs)

    @classmethod
    def _validate_inputs(cls, inputs):
        msg = "Pipeline/component input should be a \
        azure.ai.ml.entities._job.pipeline._io.NodeInput with owner, got {}."
        for val in inputs.values():
            if isinstance(val, NodeInput) and val._owner is not None:  # pylint: disable=protected-access
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
            if isinstance(val, NodeInput) and val._owner is not None:  # pylint: disable=protected-access
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
            raise UnexpectedAttributeError(keyword=name, keywords=list(self))
        return super().__getitem__(name)

    def __getitem__(self, item: K) -> V:
        # We raise this exception instead of KeyError
        if item not in self:
            raise UnexpectedKeywordError(func_name="ParameterGroup", keyword=item, keywords=list(self))
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
                flattened_parameters[flattened_name] = v._to_job_input()  # pylint: disable=protected-access
            else:
                raise ValidationException(
                    message=msg % (flattened_name, type(v)),
                    no_personal_data_message=msg % ("name", "type"),
                    target=ErrorTarget.PIPELINE,
                )
        return flattened_parameters

    def insert_group_name_for_items(self, group_name):
        # Insert one group name for all items.
        for v in self.values():
            if isinstance(v, _GroupAttrDict):
                v.insert_group_name_for_items(group_name)
            elif isinstance(v, PipelineInput):
                # Insert group names for pipeline input
                v._group_names = [group_name] + v._group_names  # pylint: disable=protected-access


class BaseOutputsAttrDict(dict):
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
        super(BaseOutputsAttrDict, self).__init__(**outputs, **kwargs)

    def __getattr__(self, item) -> NodeOutput:
        return self.__getitem__(item)

    def __getitem__(self, item) -> NodeOutput:
        if item not in self:
            # We raise this exception instead of KeyError as OutputsAttrDict doesn't support add new item after
            # __init__.
            raise UnexpectedAttributeError(keyword=item, keywords=list(self))
        return super().__getitem__(item)


class OutputsAttrDict(BaseOutputsAttrDict):

    def __setattr__(self, key: str, value: Union[Data, Output]):
        if isinstance(value, Output):
            mode = value.mode
            value = Output(type=value.type, path=value.path, mode=mode)
        original_output = self.__getattr__(key)  # Note that an exception will be raised if the keyword is invalid.
        original_output._data = original_output._build_data(value)

    def __setitem__(self, key: str, value: Output):
        return self.__setattr__(key, value)


class DynamicOutputsAttrDict(BaseOutputsAttrDict):
    """A dynamic output dict which returns output objects when accessing a non-existing key."""
    RESERVED_KEYS = ["_owner"]

    def __init__(self, owner, outputs: dict, **kwargs):
        self._owner = owner
        super(DynamicOutputsAttrDict, self).__init__(outputs=outputs, **kwargs)

    def __setitem__(self, key: str, value: Output):
        return self.__setattr__(key, value)

    def __setattr__(self, key: str, value: Union[Data, Output, NodeOutput]):
        # normal setting behavior when setting reserved keys
        if key in self.RESERVED_KEYS:
            return super(DynamicOutputsAttrDict, self).__setattr__(key, value)

        if isinstance(value, Output):
            mode = value.mode
            value = Output(type=value.type, path=value.path, mode=mode)

        if key not in self:
            if isinstance(value, InputOutputBase):
                # if key not exist, only setting NodeOutput is allowed
                return super(DynamicOutputsAttrDict, self).__setitem__(key, value)
            # Raise attribute error when setting other types
            raise UnexpectedAttributeError(keyword=key, keywords=list(self))
        # otherwise, configure the existing output
        original_output = self[key]
        original_output._data = original_output._build_data(value)

    def __getitem__(self, item) -> NodeOutput:

        if item not in self:
            # When the item is not in the dict, we return a new output without data and meta and add to original dict.
            # So it can be configured in node level or reference by other nodes.
            output = self._owner._build_output(name=item, meta=None, data=None)
            self[item] = output
            return output
        return super().__getitem__(item)
