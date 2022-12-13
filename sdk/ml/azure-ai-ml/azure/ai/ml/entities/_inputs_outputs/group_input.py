# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import copy
from enum import Enum as PyEnum

from azure.ai.ml.constants._component import IOConstants
from azure.ai.ml.exceptions import ErrorTarget, UserErrorException, ValidationException

from .input import Input
from .output import Output
from .utils import is_group


class GroupInput(Input):
    def __init__(self, values: dict, _group_class):
        super().__init__(type=IOConstants.GROUP_TYPE_NAME)
        self.assert_group_value_valid(values)
        self.values = values
        # Create empty default by values
        # Note Output do not have default so just set a None
        self.default = self._create_default()
        # Save group class for init function generation
        self._group_class = _group_class

    @classmethod
    def _create_group_attr_dict(cls, dct):
        from .._job.pipeline._io import _GroupAttrDict

        return _GroupAttrDict(dct)

    @classmethod
    def _is_group_attr_dict(cls, obj):
        from .._job.pipeline._io import _GroupAttrDict

        return isinstance(obj, _GroupAttrDict)

    def _create_default(self):
        from .._job.pipeline._io import PipelineInput

        default_dict = {}
        # Note: no top-level group names at this time.
        for k, v in self.values.items():
            # skip create default for outputs or port inputs
            if isinstance(v, Output):
                continue

            # Create PipelineInput object if not subgroup
            if not isinstance(v, GroupInput):
                default_dict[k] = PipelineInput(name=k, data=v.default, meta=v)
                continue
            # Copy and insert k into group names for subgroup
            default_dict[k] = copy.deepcopy(v.default)
            default_dict[k].insert_group_name_for_items(k)
        return self._create_group_attr_dict(default_dict)

    @classmethod
    def assert_group_value_valid(cls, values):
        """Check if all value in group is _Param type with unique name."""
        names = set()
        msg = (
            f"Parameter {{!r}} with type {{!r}} is not supported in group. "
            f"Supported types are: {list(IOConstants.INPUT_TYPE_COMBINATION.keys())}"
        )
        for key, value in values.items():
            if not isinstance(value, (Input, Output)):
                raise ValueError(msg.format(key, type(value).__name__))
            if value.type is None:
                # Skip check for parameter translated from pipeline job (lost type)
                continue
            if value.type not in IOConstants.INPUT_TYPE_COMBINATION and not isinstance(value, GroupInput):
                raise UserErrorException(msg.format(key, value.type))
            if key in names:
                raise ValueError(f"Duplicate parameter name {value.name!r} found in Group values.")
            names.add(key)

    def flatten(self, group_parameter_name):
        """Flatten and return all parameters."""
        all_parameters = {}
        group_parameter_name = group_parameter_name if group_parameter_name else ""
        for key, value in self.values.items():
            flattened_name = ".".join([group_parameter_name, key])
            if isinstance(value, GroupInput):
                all_parameters.update(value.flatten(flattened_name))
            else:
                all_parameters[flattened_name] = value
        return all_parameters

    def _to_dict(self, remove_name=True) -> dict:
        attr_dict = super()._to_dict(remove_name)
        attr_dict["values"] = {k: v._to_dict() for k, v in self.values.items()}  # pylint: disable=protected-access
        return attr_dict

    @staticmethod
    def custom_class_value_to_attr_dict(value, group_names=None):
        """Convert custom parameter group class object to GroupAttrDict."""
        if not is_group(value):
            return value
        group_definition = getattr(value, IOConstants.GROUP_ATTR_NAME)
        group_names = [*group_names] if group_names else []
        attr_dict = {}
        from .._job.pipeline._io import PipelineInput

        for k, v in value.__dict__.items():
            if is_group(v):
                attr_dict[k] = GroupInput.custom_class_value_to_attr_dict(v, [*group_names, k])
                continue
            data = v.value if isinstance(v, PyEnum) else v
            if GroupInput._is_group_attr_dict(data):
                attr_dict[k] = data
                continue
            attr_dict[k] = PipelineInput(name=k, meta=group_definition.get(k), data=data, group_names=group_names)
        return GroupInput._create_group_attr_dict(attr_dict)

    @staticmethod
    def validate_conflict_keys(keys):
        """Validate conflict keys like {'a.b.c': 1, 'a.b': 1}."""
        conflict_msg = "Conflict parameter key '%s' and '%s'."

        def _group_count(s):
            return len(s.split(".")) - 1

        # Sort order by group numbers
        keys = sorted(list(keys), key=_group_count)
        for idx, key1 in enumerate(keys[:-1]):
            for key2 in keys[idx + 1 :]:
                if _group_count(key2) == 0:
                    continue
                # Skip case a.b.c and a.b.c1
                if _group_count(key1) == _group_count(key2):
                    continue
                if not key2.startswith(key1):
                    continue
                # Invalid case 'a.b' in 'a.b.c'
                raise ValidationException(
                    message=conflict_msg % (key1, key2),
                    no_personal_data_message=conflict_msg % ("[key1]", "[key2]"),
                    target=ErrorTarget.PIPELINE,
                )

    @staticmethod
    def restore_flattened_inputs(inputs):
        """Restore flattened inputs to structured groups."""
        GroupInput.validate_conflict_keys(inputs.keys())
        restored_inputs = {}
        group_inputs = {}
        # 1. Build all group parameters dict
        for name, data in inputs.items():
            # for a.b.c, group names is [a, b]
            name_splits = name.split(".")
            group_names, param_name = name_splits[:-1], name_splits[-1]
            if not group_names:
                restored_inputs[name] = data
                continue
            # change {'a.b.c': data} -> {'a': {'b': {'c': data}}}
            target_dict = group_inputs
            for group_name in group_names:
                if group_name not in target_dict:
                    target_dict[group_name] = {}
                target_dict = target_dict[group_name]
            target_dict[param_name] = data

        def restore_from_dict_recursively(_data):
            for key, val in _data.items():
                if type(val) == dict:  # pylint: disable=unidiomatic-typecheck
                    _data[key] = restore_from_dict_recursively(val)
            # Create GroupInput for definition and _GroupAttrDict for PipelineInput
            # Regard all Input class as parameter definition, as data will not appear in group now.
            if all(isinstance(val, Input) for val in _data.values()):
                return GroupInput(values=_data, _group_class=None)
            return GroupInput._create_group_attr_dict(dct=_data)

        # 2. Rehydrate dict to GroupInput(definition) or GroupAttrDict.
        for name, data in group_inputs.items():
            restored_inputs[name] = restore_from_dict_recursively(data)
        return restored_inputs

    def _update_default(self, default_value=None):  # pylint: disable=protected-access
        default_cls = type(default_value)

        # Assert '__dsl_group__' must in the class of default value
        if self._is_group_attr_dict(default_value):
            self.default = default_value
            self.optional = False
            return
        if default_value and not is_group(default_cls):
            raise ValueError(f"Default value must be instance of parameter group, got {default_cls}.")
        if hasattr(default_value, "__dict__"):
            # Convert default value with customer type to _AttrDict
            self.default = GroupInput.custom_class_value_to_attr_dict(default_value)
            # Update item annotation
            for key, annotation in self.values.items():
                if not hasattr(default_value, key):
                    continue
                annotation._update_default(getattr(default_value, key))  # pylint: disable=protected-access
        self.optional = default_value is None
