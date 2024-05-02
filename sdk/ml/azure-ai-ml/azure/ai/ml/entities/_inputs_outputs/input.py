# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=redefined-builtin
# disable redefined-builtin to use type/min/max as argument name

import math
from inspect import Parameter
from typing import Any, Dict, List, Optional, Union, overload

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
    """Initialize an Input object.

    :keyword type: The type of the data input. Accepted values are
        'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', 'integer', 'number', 'string', and
        'boolean'. Defaults to 'uri_folder'.
    :paramtype type: str
    :keyword path: The path to the input data. Paths can be local paths, remote data uris, or a registered AzureML asset
        ID.
    :paramtype path: Optional[str]
    :keyword mode: The access mode of the data input. Accepted values are:
        * 'ro_mount': Mount the data to the compute target as read-only,
        * 'download': Download the data to the compute target,
        * 'direct': Pass in the URI as a string to be accessed at runtime
    :paramtype mode: Optional[str]
    :keyword path_on_compute: The access path of the data input for compute
    :paramtype path_on_compute: Optional[str]
    :keyword default: The default value of the input. If a default is set, the input data will be optional.
    :paramtype default: Union[str, int, float, bool]
    :keyword min: The minimum value for the input. If a value smaller than the minimum is passed to the job, the job
        execution will fail.
    :paramtype min: Union[int, float]
    :keyword max: The maximum value for the input. If a value larger than the maximum is passed to a job, the job
        execution will fail.
    :paramtype max: Union[int, float]
    :keyword optional: Specifies if the input is optional.
    :paramtype optional: Optional[bool]
    :keyword description: Description of the input
    :paramtype description: Optional[str]
    :keyword datastore: The datastore to upload local files to.
    :paramtype datastore: str
    :keyword intellectual_property: Intellectual property for the input.
    :paramtype intellectual_property: IntellectualProperty
    :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Input cannot be successfully validated.
        Details will be provided in the error message.

    .. admonition:: Example:

        .. literalinclude:: ../samples/ml_samples_misc.py
            :start-after: [START create_inputs_outputs]
            :end-before: [END create_inputs_outputs]
            :language: python
            :dedent: 8
            :caption: Creating a CommandJob with two inputs.
    """

    _EMPTY = Parameter.empty
    _IO_KEYS = [
        "path",
        "type",
        "mode",
        "path_on_compute",
        "description",
        "default",
        "min",
        "max",
        "enum",
        "optional",
        "datastore",
    ]

    @overload
    def __init__(
        self,
        *,
        type: str,
        path: Optional[str] = None,
        mode: Optional[str] = None,
        optional: Optional[bool] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """"""

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
        **kwargs: Any,
    ) -> None:
        """Initialize a number input.

        :keyword type: The type of the data input. Can only be set to "number".
        :paramtype type: str
        :keyword default: The default value of the input. If a default is set, the input data will be optional.
        :paramtype default: Union[str, int, float, bool]
        :keyword min: The minimum value for the input. If a value smaller than the minimum is passed to the job, the job
            execution will fail.
        :paramtype min: Optional[float]
        :keyword max: The maximum value for the input. If a value larger than the maximum is passed to a job, the job
            execution will fail.
        :paramtype max: Optional[float]
        :keyword optional: Specifies if the input is optional.
        :paramtype optional: bool
        :keyword description: Description of the input
        :paramtype description: str
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
        **kwargs: Any,
    ) -> None:
        """Initialize an integer input.

        :keyword type: The type of the data input. Can only be set to "integer".
        :paramtype type: str
        :keyword default: The default value of the input. If a default is set, the input data will be optional.
        :paramtype default: Union[str, int, float, bool]
        :keyword min: The minimum value for the input. If a value smaller than the minimum is passed to the job, the job
            execution will fail.
        :paramtype min: Optional[int]
        :keyword max: The maximum value for the input. If a value larger than the maximum is passed to a job, the job
            execution will fail.
        :paramtype max: Optional[int]
        :keyword optional: Specifies if the input is optional.
        :paramtype optional: bool
        :keyword description: Description of the input
        :paramtype description: str
        """

    @overload
    def __init__(
        self,
        *,
        type: Literal["string"] = "string",
        default: Optional[str] = None,
        optional: Optional[bool] = None,
        description: Optional[str] = None,
        path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a string input.

        :keyword type: The type of the data input. Can only be set to "string".
        :paramtype type: str
        :keyword default: The default value of this input. When a `default` is set, the input will be optional.
        :paramtype default: str
        :keyword optional: Determine if this input is optional.
        :paramtype optional: bool
        :keyword description: Description of the input.
        :paramtype description: str
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
        **kwargs: Any,
    ) -> None:
        """Initialize a bool input.

        :keyword type: The type of the data input. Can only be set to "boolean".
        :paramtype type: str
        :keyword path: The path to the input data. Paths can be local paths, remote data uris, or a registered AzureML
            asset id.
        :paramtype path: str
        :keyword default: The default value of the input. If a default is set, the input data will be optional.
        :paramtype default: Union[str, int, float, bool]
        :keyword optional: Specifies if the input is optional.
        :paramtype optional: bool
        :keyword description: Description of the input
        :paramtype description: str
        :raises ~azure.ai.ml.exceptions.ValidationException: Raised if Input cannot be successfully validated.
            Details will be provided in the error message.
        """

    def __init__(
        self,
        *,
        type: str = "uri_folder",
        path: Optional[str] = None,
        mode: Optional[str] = None,
        path_on_compute: Optional[str] = None,
        default: Optional[Union[str, int, float, bool]] = None,
        optional: Optional[bool] = None,
        min: Optional[Union[int, float]] = None,
        max: Optional[Union[int, float]] = None,
        enum: Any = None,
        description: Optional[str] = None,
        datastore: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super(Input, self).__init__(type=type)
        # As an annotation, it is not allowed to initialize the _port_name.
        self._port_name = None
        self.description = description
        self.path: Any = None

        if path is not None and not isinstance(path, str):
            # this logic will make dsl data binding expression working in the same way as yaml
            # it's written to handle InputOutputBase, but there will be loop import if we import InputOutputBase here
            self.path = str(path)
        else:
            self.path = path
        self.path_on_compute = path_on_compute
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
    def _allowed_types(self) -> Any:
        if self._multiple_types:
            return None
        return IOConstants.PRIMITIVE_STR_2_TYPE.get(self.type)

    @property
    def _is_primitive_type(self) -> bool:
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

        :return: Whether this input has multiple types
        :rtype: bool
        """
        return isinstance(self.type, list)

    def _is_literal(self) -> bool:
        """Whether this input is a literal

        Override this function as `self.type` can be list and not hashable for operation `in`.

        :return: Whether is a literal
        :rtype: bool
        """
        return not self._multiple_types and super(Input, self)._is_literal()

    def _is_enum(self) -> bool:
        """Whether input is an enum

        :return: True if the input is enum.
        :rtype: bool
        """
        res: bool = self.type == ComponentParameterTypes.STRING and self.enum
        return res

    def _to_dict(self) -> Dict:
        """Convert the Input object to a dict.

        :return: Dictionary representation of Input
        :rtype: Dict
        """
        keys = self._IO_KEYS
        result = {key: getattr(self, key) for key in keys}
        res: dict = _remove_empty_values(result)
        return res

    def _parse(self, val: Any) -> Union[int, float, bool, str, Any]:
        """Parse value passed from command line.

        :param val: The input value
        :type val: T
        :return: The parsed value.
        :rtype: Union[int, float, bool, str, T]
        """
        if self.type == "integer":
            return int(float(val))  # backend returns 10.0，for integer， parse it to float before int
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

    def _parse_and_validate(self, val: Any) -> Union[int, float, bool, str, Any]:
        """Parse the val passed from the command line and validate the value.

        :param val: The input string value from the command line.
        :type val: T
        :return: The parsed value, an exception will be raised if the value is invalid.
        :rtype: Union[int, float, bool, str, T]
        """
        if self._is_primitive_type:
            val = self._parse(val) if isinstance(val, str) else val
            self._validate_or_throw(val)
        return val

    def _update_name(self, name: Any) -> None:
        self._port_name = name

    def _update_default(self, default_value: Any) -> None:
        """Update provided default values.

        :param default_value: The default value of the Input
        :type default_value: Any
        """
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

    def _validate_or_throw(self, value: Any) -> None:
        """Validate input parameter value, throw exception if not as expected.

        It will throw exception if validate failed, otherwise do nothing.

        :param value: A value to validate
        :type value: Any
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

        :return: The name of the input type
        :rtype: str
        """
        if self._multiple_types:
            return "[" + ", ".join(self.type) + "]"
        if self._is_primitive_type:
            res_primitive_type: str = IOConstants.PRIMITIVE_STR_2_TYPE[self.type].__name__
            return res_primitive_type
        res: str = self.type
        return res

    def _validate_parameter_combinations(self) -> None:
        """Validate different parameter combinations according to type."""
        parameters = ["type", "path", "mode", "default", "min", "max"]
        parameters_dict: dict = {key: getattr(self, key, None) for key in parameters}
        type = parameters_dict.pop("type")

        # validate parameter combination
        if not self._multiple_types and type in IOConstants.INPUT_TYPE_COMBINATION:
            valid_parameters = IOConstants.INPUT_TYPE_COMBINATION[type]
            for key, value in parameters_dict.items():
                if key not in valid_parameters and value is not None:
                    msg = "Invalid parameter for '{}' Input, parameter '{}' should be None but got '{}'"
                    raise ValidationException(
                        message=msg.format(type, key, value),
                        no_personal_data_message=msg.format("[type]", "[parameter]", "[parameter_value]"),
                        error_category=ErrorCategory.USER_ERROR,
                        target=ErrorTarget.PIPELINE,
                        error_type=ValidationErrorType.INVALID_VALUE,
                    )

    def _simple_parse(self, value: Any, _type: Any = None) -> Any:
        if self._multiple_types:
            return value
        if _type is None:
            _type = self.type
        if _type in IOConstants.PARAM_PARSERS:
            return IOConstants.PARAM_PARSERS[_type](value)
        return value

    def _normalize_self_properties(self) -> None:
        # parse value from string to its original type. eg: "false" -> False
        for key in ["min", "max"]:
            if getattr(self, key) is not None:
                origin_value = getattr(self, key)
                new_value = self._simple_parse(origin_value)
                setattr(self, key, new_value)
        if self.optional:
            self.optional = self._simple_parse(getattr(self, "optional", "false"), _type="boolean")

    @classmethod
    def _get_input_by_type(cls, t: type, optional: Any = None) -> Optional["Input"]:
        if t in IOConstants.PRIMITIVE_TYPE_2_STR:
            return cls(type=IOConstants.PRIMITIVE_TYPE_2_STR[t], optional=optional)
        return None

    @classmethod
    def _get_default_unknown_input(cls, optional: Optional[bool] = None) -> "Input":
        # Set type as None here to avoid schema validation failed
        res: Input = cls(type=None, optional=optional)  # type: ignore
        return res

    @classmethod
    def _get_param_with_standard_annotation(cls, func: Any) -> Dict:
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
    def _map_from_rest_type(cls, _type: Union[str, List]) -> Union[str, List]:
        # this is for component rest object when using Input as component inputs
        reversed_data_type_mapping = {v: k for k, v in IOConstants.TYPE_MAPPING_YAML_2_REST.items()}
        # parse String -> string, Integer -> integer, etc
        if not isinstance(_type, list) and _type in reversed_data_type_mapping:
            res: str = reversed_data_type_mapping[_type]
            return res
        return _type

    @classmethod
    def _from_rest_object(cls, obj: Dict) -> "Input":
        obj["type"] = cls._map_from_rest_type(obj["type"])

        return cls(**obj)
