# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin
# disable redefined-builtin to use type/min/max as argument name

import math
from inspect import Parameter
from typing import Dict, Optional, Union, overload

from typing_extensions import Literal

from azure.ai.ml.constants._component import ComponentParameterTypes, IOConstants
from azure.ai.ml.entities._assets.intellectual_property import IntellectualProperty
from azure.ai.ml.exceptions import (
    ErrorCategory,
    ErrorTarget,
    UserErrorException,
    ValidationErrorType,
    ValidationException,
)

from .base import _InputOutputBase
from .utils import _get_param_with_standard_annotation, _remove_empty_values


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
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Input cannot be successfully validated.
        Details will be provided in the error message.
    """

    _EMPTY = Parameter.empty

    @overload
    def __init__(
        self,
        *,
        type: Literal["uri_folder"] = "uri_folder",
        path: Optional[str] = None,
        mode: Optional[str] = None,
        optional: Optional[bool] = None,
        description: Optional[str] = None,
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
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Input cannot be successfully validated.
            Details will be provided in the error message.
        """

    @overload
    def __init__(
        self,
        *,
        type: Literal["number"] = "number",
        default: Optional[float] = None,
        min: Optional[float] = None,
        max: Optional[float] = None,
        optional: Optional[bool] = None,
        description: Optional[str] = None,
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
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Input cannot be successfully validated.
            Details will be provided in the error message.
        """

    @overload
    def __init__(
        self,
        *,
        type: Literal["integer"] = "integer",
        default: Optional[int] = None,
        min: Optional[int] = None,
        max: Optional[int] = None,
        optional: Optional[bool] = None,
        description: Optional[str] = None,
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
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Input cannot be successfully validated.
            Details will be provided in the error message.
        """

    @overload
    def __init__(
        self,
        *,
        type: Literal["string"] = "string",
        default: Optional[str] = None,
        optional: Optional[bool] = None,
        description: Optional[str] = None,
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
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Input cannot be successfully validated.
            Details will be provided in the error message.
        """

    @overload
    def __init__(
        self,
        *,
        type: Literal["boolean"] = "boolean",
        default: Optional[bool] = None,
        optional: Optional[bool] = None,
        description: Optional[str] = None,
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
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Input cannot be successfully validated.
            Details will be provided in the error message.
        """

    def __init__(
        self,
        *,
        type: str = "uri_folder",
        path: Optional[str] = None,
        mode: Optional[str] = None,
        default: Optional[Union[str, int, float, bool]] = None,
        optional: Optional[bool] = None,
        min: Optional[Union[int, float]] = None,
        max: Optional[Union[int, float]] = None,
        enum=None,
        description: Optional[str] = None,
        datastore: Optional[str] = None,
        **kwargs,
    ):
        super(Input, self).__init__(type=type)
        # As an annotation, it is not allowed to initialize the _port_name.
        self._port_name = None
        self.description = description

        if path is not None and not isinstance(path, str):
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
        intellectual_property = kwargs.pop("intellectual_property", None)
        if intellectual_property:
            self._intellectual_property = (
                intellectual_property
                if isinstance(intellectual_property, IntellectualProperty)
                else IntellectualProperty(**intellectual_property)
            )
        # normalize properties like ["default", "min", "max", "optional"]
        self._normalize_self_properties()

        self._validate_parameter_combinations()

    @property
    def _allowed_types(self):
        if self._multiple_types:
            return None
        return IOConstants.PRIMITIVE_STR_2_TYPE.get(self.type)

    @property
    def _is_primitive_type(self):
        if self._multiple_types:
            # note: we suppose that no primitive type will be included when there are multiple types
            return False
        return self.type in IOConstants.PRIMITIVE_STR_2_TYPE

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

    def _to_dict(self):
        """Convert the Input object to a dict."""
        keys = ["path", "type", "mode", "description", "default", "min", "max", "enum", "optional", "datastore"]
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
                    message=msg.format(self._port_name, val),
                    no_personal_data_message=msg.format("[self._port_name]", "[val]"),
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
        self._port_name = name

    def _update_default(self, default_value):
        """Update provided default values."""
        name = "" if not self._port_name else f"{self._port_name!r} "
        msg_prefix = f"Default value of Input {name}"

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

        It will throw exception if validate failed, otherwise do nothing.
        """
        if not self.optional and value is None:
            msg = "Parameter {} cannot be None since it is not optional."
            raise ValidationException(
                message=msg.format(self._port_name),
                no_personal_data_message=msg.format("[self._port_name]"),
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
                error_type=ValidationErrorType.INVALID_VALUE,
            )
        if self._allowed_types and value is not None:
            if not isinstance(value, self._allowed_types):
                msg = "Unexpected data type for parameter '{}'. Expected {} but got {}."
                raise ValidationException(
                    message=msg.format(self._port_name, self._allowed_types, type(value)),
                    no_personal_data_message=msg.format("[_port_name]", self._allowed_types, type(value)),
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.PIPELINE,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
        # for numeric values, need extra check for min max value
        if not self._multiple_types and self.type in ("integer", "number"):
            if self.min is not None and value < self.min:
                msg = "Parameter '{}' should not be less than {}."
                raise ValidationException(
                    message=msg.format(self._port_name, self.min),
                    no_personal_data_message=msg.format("[_port_name]", self.min),
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.PIPELINE,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )
            if self.max is not None and value > self.max:
                msg = "Parameter '{}' should not be greater than {}."
                raise ValidationException(
                    message=msg.format(self._port_name, self.max),
                    no_personal_data_message=msg.format("[_port_name]", self.max),
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.PIPELINE,
                    error_type=ValidationErrorType.INVALID_VALUE,
                )

    def _get_python_builtin_type_str(self) -> str:
        """Get python builtin type for current input in string, eg: str.

        Return yaml type if not available.
        """
        if self._multiple_types:
            return "[" + ", ".join(self.type) + "]"
        if self._is_primitive_type:
            return IOConstants.PRIMITIVE_STR_2_TYPE[self.type].__name__
        return self.type

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

    def _simple_parse(self, value, _type=None):
        if self._multiple_types:
            return value
        if _type is None:
            _type = self.type
        if _type in IOConstants.PARAM_PARSERS:
            return IOConstants.PARAM_PARSERS[_type](value)
        return value

    def _normalize_self_properties(self):
        # parse value from string to its original type. eg: "false" -> False
        for key in ["min", "max"]:
            if getattr(self, key) is not None:
                origin_value = getattr(self, key)
                new_value = self._simple_parse(origin_value)
                setattr(self, key, new_value)
        if self.optional:
            self.optional = self._simple_parse(getattr(self, "optional", "false"), _type="boolean")

    @classmethod
    def _get_input_by_type(cls, t: type, optional=None):
        if t in IOConstants.PRIMITIVE_TYPE_2_STR:
            return cls(type=IOConstants.PRIMITIVE_TYPE_2_STR[t], optional=optional)
        return None

    @classmethod
    def _get_default_unknown_input(cls, optional=None):
        # Set type as None here to avoid schema validation failed
        return cls(type=None, optional=optional)

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
    def _map_from_rest_type(cls, _type):
        # this is for component rest object when using Input as component inputs
        reversed_data_type_mapping = {v: k for k, v in IOConstants.TYPE_MAPPING_YAML_2_REST.items()}
        # parse String -> string, Integer -> integer, etc
        if not isinstance(_type, list) and _type in reversed_data_type_mapping:
            return reversed_data_type_mapping[_type]
        return _type

    @classmethod
    def _from_rest_object(cls, obj: Dict) -> "Input":
        obj["type"] = cls._map_from_rest_type(obj["type"])

        return cls(**obj)
