# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access, redefined-builtin, too-many-lines
# disable redefined-builtin to use type/min/max as argument name

"""This file includes the type classes which could be used in dsl.pipeline,
command function, or any other place that requires job inputs/outputs.

.. remarks::

    The following pseudo-code shows how to create a pipeline with such classes.

    .. code-block:: python

        @pipeline()
        def some_pipeline(
            input_param: Input(type="uri_folder", path="xxx", mode="ro_mount"),
            int_param0: Input(type="integer", default=0, min=-3, max=10),
            int_param1 = 2
            str_param = 'abc',
            output_param: Output(type="uri_folder", path="xxx", mode="rw_mount"),
        ):
            pass


    The following pseudo-code shows how to create a command with such classes.

    .. code-block:: python

        my_command = command(
            name="my_command",
            display_name="my_command",
            description="This is a command",
            tags=dict(),
            command="python train.py --input-data ${{inputs.input_data}} --lr ${{inputs.learning_rate}}",
            code="./src",
            compute="cpu-cluster",
            environment="my-env:1",
            distribution=MpiDistribution(process_count_per_instance=4),
            environment_variables=dict(foo="bar"),
            # Customers can still do this:
            # resources=Resources(instance_count=2, instance_type="STANDARD_D2"),
            # limits=Limits(timeout=300),
            inputs={
                "float": Input(type="number", default=1.1, min=0, max=5),
                "integer": Input(type="integer", default=2, min=-1, max=4),
                "integer1": 2,
                "string0": Input(type="string", default="default_str0"),
                "string1": "default_str1",
                "boolean": Input(type="boolean", default=False),
                "uri_folder": Input(type="uri_folder", path="https://my-blob/path/to/data", mode="ro_mount"),
                "uri_file": Input(type="uri_file", path="https://my-blob/path/to/data", mode="download"),
            },
            outputs={"my_model": Output(type="mlflow_model")},
        )
        node = my_command()
"""
import copy
import math
from collections import OrderedDict
from enum import Enum as PyEnum
from enum import EnumMeta
from inspect import Parameter, signature
from typing import Dict, Iterable, Sequence, Union, overload

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationErrorType, ValidationException
from azure.ai.ml._schema.component.input_output import SUPPORTED_PARAM_TYPES
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.constants._component import ComponentParameterTypes, IOConstants
from azure.ai.ml.entities._job.pipeline._exceptions import UserErrorException
from azure.ai.ml.entities._mixins import DictMixin, RestTranslatableMixin


class _InputOutputBase(DictMixin, RestTranslatableMixin):
    def __init__(
        self,
        *,
        type,
        **kwargs,  # pylint: disable=unused-argument
    ):
        """Base class for Input & Output class.

        This class is introduced to support literal output in the future.

        :param type: The type of the Input/Output.
        :type type: str
        """
        self.type = type

    def _is_literal(self) -> bool:
        """Returns True if this input is literal input."""
        return self.type in SUPPORTED_PARAM_TYPES


class Input(_InputOutputBase):  # pylint: disable=too-many-instance-attributes
    """Define an input of a Component or Job.

    Default to be a uri_folder Input.

    :param type: The type of the data input. Possible values include:
        'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', 'integer', 'number', 'string', 'boolean'
    :type type: str
    :param path: The path to which the input is pointing.
        Could be pointing to local data, cloud data, a registered name, etc.
    :type path: str
    :param mode: The mode of the data input. Possible values are:
                        'ro_mount': Read-only mount the data,
                        'download': Download the data to the compute target,
                        'direct': Pass in the URI as a string
    :type mode: str
    :param default: The default value of this input. When a `default` is set, the input will be optional
    :type default: Union[str, integer, float, bool]
    :param min: The min value -- if a smaller value is passed to a job, the job execution will fail
    :type min: Union[integer, float]
    :param max: The max value -- if a larger value is passed to a job, the job execution will fail
    :type max: Union[integer, float]
    :param optional: Determine if this input is optional
    :type optional: bool
    :param description: Description of the input
    :type description: str
    """

    _EMPTY = Parameter.empty

    @overload
    def __init__(
        self,
        *,
        type: str = "uri_folder",
        path: str = None,
        mode: str = None,
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize an input.

        :param type: The type of the data input. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param path: The path to which the input is pointing.
            Could be pointing to local data, cloud data, a registered name, etc.
        :type path: str
        :param mode: The mode of the data input. Possible values are:
                            'ro_mount': Read-only mount the data,
                            'download': Download the data to the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        :param datastore: The datastore to upload local files to.
        :type datastore: str
        """

    @overload
    def __init__(
        self,
        *,
        type: str = "number",
        default: float = None,
        min: float = None,
        max: float = None,
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize a number input.

        :param type: The type of the data input. Can only be set to "number".
        :type type: str
        :param default: The default value of this input. When a `default` is set, input will be optional
        :type default: float
        :param min: The min value -- if a smaller value is passed to a job, the job execution will fail
        :type min: float
        :param max: The max value -- if a larger value is passed to a job, the job execution will fail
        :type max: float
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    @overload
    def __init__(
        self,
        *,
        type: str = "integer",
        default: int = None,
        min: int = None,
        max: int = None,
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize an integer input.

        :param type: The type of the data input. Can only be set to "integer".
        :type type: str
        :param default: The default value of this input. When a `default` is set, the input will be optional
        :type default: integer
        :param min: The min value -- if a smaller value is passed to a job, the job execution will fail
        :type min: integer
        :param max: The max value -- if a larger value is passed to a job, the job execution will fail
        :type max: integer
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    @overload
    def __init__(
        self,
        *,
        type: str = "string",
        default: str = None,
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize a string input.

        :param type: The type of the data input. Can only be set to "string".
        :type type: str
        :param default: The default value of this input. When a `default` is set, the input will be optional
        :type default: str
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    @overload
    def __init__(
        self,
        *,
        type: str = "boolean",
        default: bool = None,
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize a bool input.

        :param type: The type of the data input. Can only be set to "boolean".
        :type type: str
        :param default: The default value of this input. When a `default` is set, input will be optional
        :type default: bool
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    def __init__(
        self,
        *,
        type: str = "uri_folder",
        path: str = None,
        mode: str = None,
        default: Union[str, int, float, bool] = None,
        optional: bool = None,
        min: Union[int, float] = None,
        max: Union[int, float] = None,
        enum=None,
        description: str = None,
        datastore: str = None,
        **kwargs,
    ):
        super(Input, self).__init__(type=type)
        # As an annotation, it is not allowed to initialize the name.
        # The name will be updated by the annotated variable name.
        self.name = None
        self.description = description

        if self._multiple_types:
            # note: we suppose that no primitive type will be included when there are multiple types
            self._allowed_types = None
            self._is_primitive_type = False
        else:
            self._allowed_types = IOConstants.PRIMITIVE_STR_2_TYPE.get(self.type)
            self._is_primitive_type = self.type in IOConstants.PRIMITIVE_STR_2_TYPE
        if path and not isinstance(path, str):
            # this logic will make dsl data binding expression working in the same way as yaml
            # it's written to handle InputOutputBase, but there will be loop import if we import InputOutputBase here
            self.path = str(path)
        else:
            self.path = path
        self.mode = None if self._is_primitive_type else mode
        self._update_default(default)
        self.optional = optional
        # set the flag to mark if the optional=True is inferred by us.
        self._is_inferred_optional = False
        self.min = min
        self.max = max
        self.enum = enum
        self.datastore = datastore
        # normalize properties like ["default", "min", "max", "optional"]
        self._normalize_self_properties()

        self._validate_parameter_combinations()

    @property
    def _multiple_types(self) -> bool:
        """Returns True if this input has multiple types.

        Currently, there are two scenarios that need to check this property:
        1. before `in` as it may throw exception; there will be `in` operation for validation/transformation.
        2. `str()` of list is not ideal, so we need to manually create its string result.
        """
        return isinstance(self.type, list)

    def _is_literal(self) -> bool:
        """Override this function as `self.type` can be list and not hashable for operation `in`."""
        return not self._multiple_types and super(Input, self)._is_literal()

    def _is_enum(self):
        """returns true if the input is enum."""
        return self.type == ComponentParameterTypes.STRING and self.enum

    def _to_dict(self, remove_name=True):
        """Convert the Input object to a dict."""
        keys = ["name", "path", "type", "mode", "description", "default", "min", "max", "enum", "optional", "datastore"]
        if remove_name:
            keys.remove("name")
        result = {key: getattr(self, key) for key in keys}
        return _remove_empty_values(result)

    def _parse(self, val):
        """Parse value passed from command line.

        :param val: The input value
        :return: The parsed value.
        """
        if self.type == "integer":
            return int(val)
        if self.type == "number":
            return float(val)
        if self.type == "boolean":
            lower_val = str(val).lower()
            if lower_val not in {"true", "false"}:
                msg = "Boolean parameter '{}' only accept True/False, got {}."
                raise ValidationException(
                    message=msg.format(self.name, val),
                    no_personal_data_message=msg.format("[self.name]", "[val]"),
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.PIPELINE,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
            return lower_val == "true"
        if self.type == "string":
            return val if isinstance(val, str) else str(val)
        return val

    def _parse_and_validate(self, val):
        """Parse the val passed from the command line and validate the value.

        :param str_val: The input string value from the command line.
        :return: The parsed value, an exception will be raised if the value is invalid.
        """
        if self._is_primitive_type:
            val = self._parse(val) if isinstance(val, str) else val
            self._validate_or_throw(val)
        return val

    def _update_name(self, name):
        self.name = name

    def _update_default(self, default_value):
        """Update provided default values."""
        name = "" if not self.name else f"{self.name!r} "
        if not self._multiple_types:
            msg_prefix = f"Default value of {self.type} Input {name}"
        else:
            msg_prefix = "Default value of [" + ", ".join(self.type) + f"] Input {name}"
        if not self._is_primitive_type and default_value is not None:
            msg = f"{msg_prefix}cannot be set: Non-primitive type Input has no default value."
            raise UserErrorException(msg)
        if isinstance(default_value, float) and not math.isfinite(default_value):
            # Since nan/inf cannot be stored in the backend, just ignore them.
            # logger.warning("Float default value %r is not allowed, ignored." % default_value)
            return
        # pylint: disable=pointless-string-statement
        """Update provided default values.
        Here we need to make sure the type of default value is allowed or it could be parsed..
        """
        if default_value is not None:
            if type(default_value) not in IOConstants.PRIMITIVE_TYPE_2_STR:
                msg = (
                    f"{msg_prefix}cannot be set: type must be one of "
                    f"{list(IOConstants.PRIMITIVE_TYPE_2_STR.values())}, got '{type(default_value)}'."
                )
                raise UserErrorException(msg)

            if not isinstance(default_value, self._allowed_types):
                try:
                    default_value = self._parse(default_value)
                # return original validation exception which is custom defined if raised by self._parse
                except ValidationException as e:
                    raise e
                except Exception as e:
                    msg = f"{msg_prefix}cannot be parsed, got '{default_value}', type = {type(default_value)!r}."
                    raise UserErrorException(msg) from e
        self.default = default_value

    def _validate_or_throw(self, value):
        """Validate input parameter value, throw exception if not as expected.

        It will throw exception if validate failed, otherwise do
        nothing.
        """
        if not self.optional and value is None:
            msg = "Parameter {} cannot be None since it is not optional."
            raise ValidationException(
                message=msg.format(self.name),
                no_personal_data_message=msg.format("[self.name]"),
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        if self._allowed_types and value is not None:
            if not isinstance(value, self._allowed_types):
                msg = "Unexpected data type for parameter '{}'. Expected {} but got {}."
                raise ValidationException(
                    message=msg.format(self.name, self._allowed_types, type(value)),
                    no_personal_data_message=msg.format("[name]", self._allowed_types, type(value)),
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.PIPELINE,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
        # for numeric values, need extra check for min max value
        if not self._multiple_types and self.type in ("integer", "number"):
            if self.min is not None and value < self.min:
                msg = "Parameter '{}' should not be less than {}."
                raise ValidationException(
                    message=msg.format(self.name, self.min),
                    no_personal_data_message=msg.format("[name]", self.min),
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.PIPELINE,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
            if self.max is not None and value > self.max:
                msg = "Parameter '{}' should not be greater than {}."
                raise ValidationException(
                    message=msg.format(self.name, self.max),
                    no_personal_data_message=msg.format("[name]", self.max),
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.PIPELINE,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )

    def _get_python_builtin_type_str(self) -> str:
        """Get python builtin type for current input in string, eg: str.

        Return yaml type if not available.
        """
        if not self._multiple_types:
            return IOConstants.PRIMITIVE_STR_2_TYPE[self.type].__name__ if self._is_primitive_type else self.type
        return "[" + ", ".join(self.type) + "]"

    def _validate_parameter_combinations(self):
        """Validate different parameter combinations according to type."""
        parameters = ["type", "path", "mode", "default", "min", "max"]
        parameters = {key: getattr(self, key, None) for key in parameters}
        type = parameters.pop("type")

        # validate parameter combination
        if not self._multiple_types and type in IOConstants.INPUT_TYPE_COMBINATION:
            valid_parameters = IOConstants.INPUT_TYPE_COMBINATION[type]
            for key, value in parameters.items():
                if key not in valid_parameters and value is not None:
                    msg = "Invalid parameter for '{}' Input, parameter '{}' should be None but got '{}'"
                    raise ValidationException(
                        message=msg.format(type, key, value),
                        no_personal_data_message=msg.format("[type]", "[parameter]", "[parameter_value]"),
                        error_category=ErrorCategory.USER_ERROR,
                        target=ErrorTarget.PIPELINE,
                        error_type=ValidationErrorType.INVALID_VALUE,
                    )

    def _normalize_self_properties(self):
        # parse value from string to it's original type. eg: "false" -> False
        if not self._multiple_types and self.type in IOConstants.PARAM_PARSERS:
            for key in ["min", "max"]:
                if getattr(self, key) is not None:
                    origin_value = getattr(self, key)
                    new_value = IOConstants.PARAM_PARSERS[self.type](origin_value)
                    setattr(self, key, new_value)
        self.optional = IOConstants.PARAM_PARSERS["boolean"](getattr(self, "optional", "false"))
        self.optional = True if self.optional is True else None

    @classmethod
    def _get_input_by_type(cls, t: type, optional=None):
        if t in IOConstants.PRIMITIVE_TYPE_2_STR:
            return cls(type=IOConstants.PRIMITIVE_TYPE_2_STR[t], optional=optional)
        return None

    @classmethod
    def _get_default_string_input(cls, optional=None):
        return cls(type="string", optional=optional)

    @classmethod
    def _get_param_with_standard_annotation(cls, func):
        return _get_param_with_standard_annotation(func, is_func=True)

    def _to_rest_object(self) -> Dict:
        # this is for component rest object when using Input as component inputs, as for job input usage,
        # rest object is generated by extracting Input's properties, see details in to_rest_dataset_literal_inputs()
        result = self._to_dict()
        # parse string -> String, integer -> Integer, etc.
        if result["type"] in IOConstants.TYPE_MAPPING_YAML_2_REST:
            result["type"] = IOConstants.TYPE_MAPPING_YAML_2_REST[result["type"]]
        return result

    @classmethod
    def _from_rest_object(cls, obj: Dict) -> "Input":
        # this is for component rest object when using Input as component inputs
        reversed_data_type_mapping = {v: k for k, v in IOConstants.TYPE_MAPPING_YAML_2_REST.items()}
        # parse String -> string, Integer -> integer, etc
        if not isinstance(obj["type"], list) and obj["type"] in reversed_data_type_mapping:
            obj["type"] = reversed_data_type_mapping[obj["type"]]

        return Input(**obj)


class Output(_InputOutputBase):
    """Define an output of a Component or Job.

    :param type: The type of the data output. Possible values include:
                        'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
    :type type: str
    :param path: The path to which the output is pointing. Needs to point to a cloud path.
    :type path: str
    :param mode: The mode of the data output. Possible values are:
                        'rw_mount': Read-write mount the data,
                        'upload': Upload the data from the compute target,
                        'direct': Pass in the URI as a string
    :type mode: str
    :param description: Description of the output
    :type description: str
    """

    @overload
    def __init__(self, type="uri_folder", path=None, mode=None, description=None):
        """Define a uri_folder output.

        :param type: The type of the data output. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param path: The path to which the output is pointing. Needs to point to a cloud path.
        :type path: str
        :param mode: The mode of the data output. Possible values are:
                            'rw_mount': Read-write mount the data,
                            'upload': Upload the data from the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param description: Description of the output
        :type description: str
        """

    @overload
    def __init__(self, type="uri_file", path=None, mode=None, description=None):
        """Define a uri_file output.

        :param type: The type of the data output. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param path: The path to which the output is pointing. Needs to point to a cloud path.
        :type path: str
        :param mode: The mode of the data output. Possible values are:
                            'rw_mount': Read-write mount the data,
                            'upload': Upload the data from the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param description: Description of the output
        :type description: str
        """

    def __init__(self, *, type=AssetTypes.URI_FOLDER, path=None, mode=None, description=None, **kwargs):
        super(Output, self).__init__(type=type)
        # As an annotation, it is not allowed to initialize the name.
        # The name will be updated by the annotated variable name.
        self.name = None
        self._is_primitive_type = self.type in IOConstants.PRIMITIVE_STR_2_TYPE
        self.description = description

        self.path = path
        self.mode = mode

    def _get_hint(self, new_line_style=False):
        comment_str = self.description.replace('"', '\\"') if self.description else self.type
        return '"""%s"""' % comment_str if comment_str and new_line_style else comment_str

    def _to_dict(self, remove_name=True):
        """Convert the Output object to a dict."""
        keys = ["name", "path", "type", "mode", "description"]
        if remove_name:
            keys.remove("name")
        result = {key: getattr(self, key) for key in keys}
        return _remove_empty_values(result)

    def _to_rest_object(self) -> Dict:
        # this is for component rest object when using Output as component outputs, as for job output usage,
        # rest object is generated by extracting Output's properties, see details in to_rest_data_outputs()
        return self._to_dict()

    @classmethod
    def _from_rest_object(cls, obj: Dict) -> "Output":
        # this is for component rest object when using Output as component outputs
        return Output(**obj)


class EnumInput(Input):
    """Enum parameter parse the value according to its enum values."""

    def __init__(
        self,
        *,
        enum: Union[EnumMeta, Sequence[str]] = None,
        default=None,
        description=None,
        **kwargs,
    ):
        """Initialize an enum parameter, the options of an enum parameter are
        the enum values.

        :param enum: Enum values.
        :type Union[EnumMeta, Sequence[str]]
        :param description: Description of the param.
        :type description: str
        :param optional: If the param is optional.
        :type optional: bool
        """
        enum_values = self._assert_enum_valid(enum)
        # This is used to parse enum class instead of enum str value if a enum class is provided.
        if isinstance(enum, EnumMeta):
            self._enum_class = enum
            self._str2enum = dict(zip(enum_values, enum))
        else:
            self._enum_class = None
            self._str2enum = {v: v for v in enum_values}
        super().__init__(type="string", default=default, enum=enum_values, description=description)
        self._allowed_types = (
            (str,)
            if not self._enum_class
            else (
                self._enum_class,
                str,
            )
        )

    @classmethod
    def _assert_enum_valid(cls, enum):
        """Check whether the enum is valid and return the values of the
        enum."""
        if isinstance(enum, EnumMeta):
            enum_values = [str(option.value) for option in enum]
        elif isinstance(enum, Iterable):
            enum_values = list(enum)
        else:
            msg = "enum must be a subclass of Enum or an iterable."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        if len(enum_values) <= 0:
            msg = "enum must have enum values."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        if any(not isinstance(v, str) for v in enum_values):
            msg = "enum values must be str type."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
                error_type=ValidationErrorType.INVALID_VALUE,
            )

        return enum_values

    def _parse(self, val: str):
        """Parse the enum value from a string value or the enum value."""
        if val is None:
            return val

        if self._enum_class and isinstance(val, self._enum_class):
            return val  # Directly return the enum value if it is the enum.

        if val not in self._str2enum:
            msg = "Not a valid enum value: '{}', valid values: {}"
            raise ValidationException(
                message=msg.format(val, ", ".join(self.enum)),
                no_personal_data_message=msg.format("[val]", "[enum]"),
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        return self._str2enum[val]

    def _update_default(self, default_value):
        """Enum parameter support updating values with a string value."""
        enum_val = self._parse(default_value)
        if self._enum_class and isinstance(enum_val, self._enum_class):
            enum_val = enum_val.value
        self.default = enum_val


def is_parameter_group(obj):
    """Return True if obj is a parameter group or an instance of a parameter group class."""
    return hasattr(obj, IOConstants.GROUP_ATTR_NAME)


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
        from ._job.pipeline._io import _GroupAttrDict

        return _GroupAttrDict(dct)

    @classmethod
    def _is_group_attr_dict(cls, obj):
        from ._job.pipeline._io import _GroupAttrDict

        return isinstance(obj, _GroupAttrDict)

    def _create_default(self):
        from ._job.pipeline._io import PipelineInput

        default_dict = {}
        for k, v in self.values.items():
            # Assign directly if is subgroup, else create PipelineInput object
            default_dict[k] = v.default if isinstance(v, GroupInput) else PipelineInput(name=k, data=v.default, meta=v)
        return self._create_group_attr_dict(default_dict)

    @classmethod
    def assert_group_value_valid(cls, values):
        """Check if all value in group is _Param type with unique name."""
        names = set()
        msg = (
            f"Parameter {{!r}} with type {{!r}} is not supported in parameter group. "
            f"Supported types are: {list(IOConstants.PRIMITIVE_STR_2_TYPE.keys())}"
        )
        for key, value in values.items():
            if not isinstance(value, Input):
                raise ValueError(msg.format(key, type(value).__name__))
            if value.type == "unknown":
                # Skip check for parameter translated from pipeline job (lost type)
                continue
            if value.type not in IOConstants.PRIMITIVE_STR_2_TYPE and not isinstance(value, GroupInput):
                raise UserErrorException(msg.format(key, value.type))
            if key in names:
                raise ValueError(f"Duplicate parameter name {value.name!r} found in ParameterGroup values.")
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
        attr_dict["values"] = {k: v._to_dict() for k, v in self.values.items()}
        return attr_dict

    @staticmethod
    def custom_class_value_to_attr_dict(value, group_names=None):
        """Convert custom parameter group class object to GroupAttrDict."""
        if not is_parameter_group(value):
            return value
        group_definition = getattr(value, IOConstants.GROUP_ATTR_NAME)
        group_names = [*group_names] if group_names else []
        attr_dict = {}
        from ._job.pipeline._io import PipelineInput

        for k, v in value.__dict__.items():
            if is_parameter_group(v):
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

    def _update_default(self, default_value=None):
        default_cls = type(default_value)

        # Assert '__parameter_group__' must in the class of default value
        if self._is_group_attr_dict(default_value):
            self.default = default_value
            self.optional = False
            return
        if default_value and not is_parameter_group(default_cls):
            raise ValueError(f"Default value must be instance of parameter group, got {default_cls}.")
        if hasattr(default_value, "__dict__"):
            # Convert default value with customer type to _AttrDict
            self.default = GroupInput.custom_class_value_to_attr_dict(default_value)
            # Update item annotation
            for key, annotation in self.values.items():
                if not hasattr(default_value, key):
                    continue
                annotation._update_default(getattr(default_value, key))
        self.optional = default_value is None


def _get_annotation_by_value(val):
    def _is_dataset(data):
        from azure.ai.ml.entities._job.job_io_mixin import JobIOMixin

        DATASET_TYPES = JobIOMixin
        return isinstance(data, DATASET_TYPES)

    if _is_dataset(val):
        annotation = Input
    elif val is Parameter.empty or val is None:
        # If no default value or default is None, create val as the basic parameter type,
        # it could be replaced using component parameter definition.
        annotation = Input._get_default_string_input()
    elif isinstance(val, PyEnum):
        # Handle enum values
        annotation = EnumInput(enum=val.__class__)
    else:
        annotation = _get_annotation_cls_by_type(type(val), raise_error=False)
        if not annotation:
            # Fall back to default
            annotation = Input._get_default_string_input()
    return annotation


def _get_annotation_cls_by_type(t: type, raise_error=False, optional=None):
    cls = Input._get_input_by_type(t, optional=optional)
    if cls is None and raise_error:
        raise UserErrorException(f"Can't convert type {t} to azure.ai.ml.Input")
    return cls


# pylint: disable=too-many-statements
def _get_param_with_standard_annotation(cls_or_func, is_func=False):
    """Standardize function parameters or class fields with dsl.types
    annotation."""

    def _get_fields(annotations):
        """Return field names to annotations mapping in class."""
        annotation_fields = OrderedDict()
        for name, annotation in annotations.items():
            # Skip return type
            if name == "return":
                continue
            # Handle EnumMeta annotation
            if isinstance(annotation, EnumMeta):
                annotation = EnumInput(type="string", enum=annotation)
            # Handle Group annotation
            if is_parameter_group(annotation):
                annotation = copy.deepcopy(getattr(annotation, IOConstants.GROUP_ATTR_NAME))
            # Try creating annotation by type when got like 'param: int'
            if not _is_dsl_type_cls(annotation) and not _is_dsl_types(annotation):
                origin_annotation = annotation
                annotation = _get_annotation_cls_by_type(annotation, raise_error=False)
                if not annotation:
                    msg = f"Unsupported annotation type {origin_annotation!r} for parameter {name!r}."
                    raise UserErrorException(msg)
            annotation_fields[name] = annotation
        return annotation_fields

    def _merge_field_keys(annotation_fields, defaults_dict):
        """Merge field keys from annotations and cls dict to get all fields in
        class."""
        anno_keys = list(annotation_fields.keys())
        dict_keys = defaults_dict.keys()
        if not dict_keys:
            return anno_keys
        return [*anno_keys, *[key for key in dict_keys if key not in anno_keys]]

    def _update_annotation_with_default(anno, name, default):
        """Create annotation if is type class and update the default."""
        # Create instance if is type class
        complete_annotation = anno
        if _is_dsl_type_cls(anno):
            complete_annotation = anno()
        complete_annotation.name = name
        if default is Input._EMPTY:
            return complete_annotation
        if isinstance(complete_annotation, Input):
            # Non-parameter Input has no default attribute
            if complete_annotation._is_primitive_type and complete_annotation.default is not None:
                # logger.warning(
                #     f"Warning: Default value of f{complete_annotation.name!r} is set twice: "
                #     f"{complete_annotation.default!r} and {default!r}, will use {default!r}"
                # )
                pass
            complete_annotation._update_default(default)
        return complete_annotation

    def _update_fields_with_default(annotation_fields, defaults_dict):
        """Use public values in class dict to update annotations."""
        all_fields = OrderedDict()
        all_filed_keys = _merge_field_keys(annotation_fields, defaults_dict)
        for name in all_filed_keys:
            # Get or create annotation
            annotation = (
                annotation_fields[name]
                if name in annotation_fields
                else _get_annotation_by_value(defaults_dict.get(name, Input._EMPTY))
            )
            # Create annotation if is class type and update default
            annotation = _update_annotation_with_default(annotation, name, defaults_dict.get(name, Input._EMPTY))
            all_fields[name] = annotation
        return all_fields

    def _get_inherited_fields():
        """Get all fields inherit from bases parameter group class."""
        _fields = OrderedDict({})
        if is_func:
            return _fields
        # In reversed order so that more derived classes
        # override earlier field definitions in base classes.
        for base in cls_or_func.__mro__[-1:0:-1]:
            if is_parameter_group(base):
                # merge and reorder fields from current base with previous
                _fields = _merge_and_reorder(_fields, copy.deepcopy(getattr(base, IOConstants.GROUP_ATTR_NAME).values))
        return _fields

    def _merge_and_reorder(inherited_fields, cls_fields):
        """Merge inherited fields with cls fields. The order inside each part
        will not be changed. Order will be.

        {inherited_no_default_fields} + {cls_no_default_fields} + {inherited_default_fields} + {cls_default_fields}.
        Note: If cls overwrite an inherited no default field with default, it will be put in the
        cls_default_fields part and deleted from inherited_no_default_fields:
        e.g.
        @dsl.parameter_group
        class SubGroup:
            int_param0: Integer
            int_param1: int
        @dsl.parameter_group
        class Group(SubGroup):
            int_param3: Integer
            int_param1: int = 1
        The init function of Group will be 'def __init__(self, *, int_param0, int_param3, int_param1=1)'.
        """

        def _split(_fields):
            """Split fields to two parts from the first default field."""
            _no_defaults_fields, _defaults_fields = {}, {}
            seen_default = False
            for key, val in _fields.items():
                if val.get("default", None) or seen_default:
                    seen_default = True
                    _defaults_fields[key] = val
                else:
                    _no_defaults_fields[key] = val
            return _no_defaults_fields, _defaults_fields

        inherited_no_default, inherited_default = _split(inherited_fields)
        cls_no_default, cls_default = _split(cls_fields)
        # Cross comparison and delete from inherited_fields if same key appeared in cls_fields
        # pylint: disable=consider-iterating-dictionary
        for key in cls_default.keys():
            if key in inherited_no_default.keys():
                del inherited_no_default[key]
        for key in cls_no_default.keys():
            if key in inherited_default.keys():
                del inherited_default[key]
        return OrderedDict(
            {
                **inherited_no_default,
                **cls_no_default,
                **inherited_default,
                **cls_default,
            }
        )

    inherited_fields = _get_inherited_fields()
    # From annotations get field with type
    annotations = getattr(cls_or_func, "__annotations__", {})
    annotation_fields = _get_fields(annotations)
    # Update fields use class field with defaults from class dict or signature(func).paramters
    if not is_func:
        # Only consider public fields in class dict
        defaults_dict = {key: val for key, val in cls_or_func.__dict__.items() if not key.startswith("_")}
    else:
        # Infer parameter type from value if is function
        defaults_dict = {key: val.default for key, val in signature(cls_or_func).parameters.items()}
    fields = _update_fields_with_default(annotation_fields, defaults_dict)
    all_fields = _merge_and_reorder(inherited_fields, fields)
    return all_fields


def _is_dsl_type_cls(t: type):
    if type(t) is not type:  # pylint: disable=unidiomatic-typecheck
        return False
    return issubclass(t, (Input, Output))


def _is_dsl_types(o: object):
    return _is_dsl_type_cls(type(o))


def _remove_empty_values(data, ignore_keys=None):
    if not isinstance(data, dict):
        return data
    ignore_keys = ignore_keys or {}
    return {
        k: v if k in ignore_keys else _remove_empty_values(v)
        for k, v in data.items()
        if v is not None or k in ignore_keys
    }
