# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This file includes the type classes which could be used in dsl.pipeline, command function, or any other place that requires job inputs/outputs

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
import math
from typing import overload
from collections import OrderedDict

from typing import Union, Sequence, Iterable
from enum import EnumMeta, Enum as PyEnum
from inspect import Parameter, signature

from azure.ai.ml.entities._job.pipeline._exceptions import UserErrorException, MldesignerComponentDefiningError
from azure.ai.ml.entities._component.input_output import ComponentInput, ComponentOutput
from azure.ai.ml.constants import InputOutputModes, AssetTypes
from azure.ai.ml._ml_exceptions import ValidationException, ErrorTarget, ErrorCategory, ComponentException
from azure.ai.ml.entities._mixins import DictMixin


class Input(DictMixin):
    """Define an input of a Component or Job.

    Default to be a uri_folder Input.

    :param type: The type of the data input. Possible values include:
                        'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', 'integer', 'number', 'string', 'boolean'
    :type type: str
    :param path: The path to which the input is pointing. Could be pointing to local data, cloud data, a registered name, etc.
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
    :param description: Description of the input
    :type description: str
    """

    # For validation, indicates specific parameters combination for each type
    _TYPE_COMBINATION_MAPPING = {
        "uri_folder": ["path", "mode"],
        "uri_file": ["path", "mode"],
        "mltable": ["path", "mode"],
        "mlflow_model": ["path", "mode"],
        "custom_model": ["path", "mode"],
        "integer": ["default", "min", "max"],
        "number": ["default", "min", "max"],
        "string": ["default"],
        "boolean": ["default"],
    }
    _ALLOWED_TYPES = {
        "integer": (int),
        "string": (str),
        "number": (float),
        "boolean": (bool),
    }
    _DATA_TYPE_MAPPING = {int: "integer", str: "string", float: "number", bool: "boolean"}
    _EMPTY = Parameter.empty

    @overload
    def __init__(self, type: str = "uri_folder", path: str = None, mode: str = "ro_mount", description: str = None):
        """Initialize an input.

        :param type: The type of the data input. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param path: The path to which the input is pointing. Could be pointing to local data, cloud data, a registered name, etc.
        :type path: str
        :param mode: The mode of the data input. Possible values are:
                            'ro_mount': Read-only mount the data,
                            'download': Download the data to the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param description: Description of the input
        :type description: str
        """
        pass

    @overload
    def __init__(
        self, type: str = "number", default: float = None, min: float = None, max: float = None, description: str = None
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
        :param description: Description of the input
        :type description: str
        """
        pass

    @overload
    def __init__(
        self, type: str = "integer", default: int = None, min: int = None, max: int = None, description: str = None
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
        :param description: Description of the input
        :type description: str
        """
        pass

    @overload
    def __init__(self, type: str = "string", default: str = None, description: str = None):
        """Initialize a string input.

        :param type: The type of the data input. Can only be set to "string".
        :type type: str
        :param default: The default value of this input. When a `default` is set, the input will be optional
        :type default: str
        :param description: Description of the input
        :type description: str
        """
        pass

    @overload
    def __init__(self, type: str = "boolean", default: bool = None, description: str = None):
        """Initialize a bool input.

        :param type: The type of the data input. Can only be set to "boolean".
        :type type: str
        :param default: The default value of this input. When a `default` is set, input will be optional
        :type default: bool
        :param description: Description of the input
        :type description: str
        """
        pass

    def __init__(
        self,
        *,
        type: str = "uri_folder",
        path: str = None,
        mode: str = "ro_mount",
        default: Union[str, int, float, bool] = None,
        min: Union[int, float] = None,
        max: Union[int, float] = None,
        enum=None,
        description: str = None,
        **kwargs,
    ):
        # As an annotation, it is not allowed to initialize the name.
        # The name will be updated by the annotated variable name.
        self.name = None
        self.type = type
        self.description = description

        self._is_parameter_type = self.type in self._ALLOWED_TYPES
        if path and not isinstance(path, str):
            # this logic will make dsl data binding expression working in the same way as yaml
            # it's written to handle InputOutputBase, but there will be loop import if we import InputOutputBase here
            self.path = str(path)
        else:
            self.path = path
        self.mode = None if self._is_parameter_type else mode
        self.default = default
        self.min = min
        self.max = max
        self.enum = enum
        self._allowed_types = self._ALLOWED_TYPES.get(self.type)
        self._validate_parameter_combinations()

    @property
    def optional(self) -> bool:
        """Return whether the parameter is optional."""
        return True if self.default is not None else None

    def _to_dict(self, remove_name=True):
        """Convert the Input object to a dict."""
        keys = ["name", "path", "type", "mode", "description", "default", "min", "max", "enum", "optional"]
        if remove_name:
            keys.remove("name")
        result = {key: getattr(self, key) for key in keys}
        return _remove_empty_values(result)

    def _to_component_input(self):
        data = self._to_dict()
        return ComponentInput(data)

    def _parse(self, val):
        """Parse value passed from command line.

        :param val: The input value
        :return: The parsed value.
        """
        if self.type == "integer":
            return int(val)
        elif self.type == "number":
            return float(val)
        elif self.type == "boolean":
            lower_val = str(val).lower()
            if lower_val not in {"true", "false"}:
                msg = "Boolean parameter '{}' only accept True/False, got {}."
                raise ValidationException(
                    message=msg.format(self.name, val),
                    no_personal_data_message=msg.format("[self.name]", "[val]"),
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.PIPELINE,
                )
            return True if lower_val == "true" else False
        return val

    def _parse_and_validate(self, val):
        """Parse the val passed from the command line and validate the value.

        :param str_val: The input string value from the command line.
        :return: The parsed value, an exception will be raised if the value is invalid.
        """
        if self._is_parameter_type:
            val = self._parse(val) if isinstance(val, str) else val
            self._validate_or_throw(val)
        return val

    def _update_name(self, name):
        self.name = name

    def _update_default(self, default_value):
        """Update provided default values."""
        if self.type == "uri_folder" or self.type == "uri_file":
            self.default = default_value
            return
        else:
            if isinstance(default_value, float) and not math.isfinite(default_value):
                # Since nan/inf cannot be stored in the backend, just ignore them.
                # logger.warning("Float default value %r is not allowed, ignored." % default_value)
                return
            """Update provided default values.
            Here we need to make sure the type of default value is allowed or it could be parsed..
            """
            if default_value is not None and not isinstance(default_value, self._allowed_types):
                try:
                    default_value = self._parse(default_value)
                except Exception as e:
                    if self.name is None:
                        msg = "Default value of %s Input cannot be parsed, got '%s', type = %s." % (
                            self.type,
                            default_value,
                            type(default_value),
                        )
                    else:
                        msg = "Default value of %s Input '%s' cannot be parsed, got '%s', type = %s." % (
                            self.type,
                            self.name,
                            default_value,
                            type(default_value),
                        )
                    raise MldesignerComponentDefiningError(cause=msg) from e
            self.default = default_value

    def _validate_or_throw(self, value):
        """Validate input parameter value, throw exception if not as expected.

        It will throw exception if validate failed, otherwise do nothing.
        """
        if not self.optional and value is None:
            msg = "Parameter {} cannot be None since it is not optional."
            raise ValidationException(
                message=msg.format(self.name),
                no_personal_data_message=msg.format("[self.name]"),
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
            )
        if self._allowed_types and value is not None:
            if not isinstance(value, self._allowed_types):
                msg = "Unexpected data type for parameter '{}'. Expected {} but got {}."
                raise ValidationException(
                    message=msg.format(self.name, self._allowed_types, type(value)),
                    no_personal_data_message=msg.format("[name]", self._allowed_types, type(value)),
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.PIPELINE,
                )
        # for numeric values, need extra check for min max value
        if self.type in ("integer", "number"):
            if self.min is not None and value < self.min:
                msg = "Parameter '{}' should not be less than {}."
                raise ValidationException(
                    message=msg.format(self.name, self.min),
                    no_personal_data_message=msg.format("[name]", self.min),
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.PIPELINE,
                )
            if self.max is not None and value > self.max:
                msg = "Parameter '{}' should not be greater than {}."
                raise ValidationException(
                    message=msg.format(self.name, self.max),
                    no_personal_data_message=msg.format("[name]", self.max),
                    error_category=ErrorCategory.USER_ERROR,
                    target=ErrorTarget.PIPELINE,
                )

    def _validate_parameter_combinations(self):
        """Validate different parameter combinations according to type"""
        parameters = ["type", "path", "mode", "default", "min", "max"]
        parameters = {key: getattr(self, key, None) for key in parameters}
        type = parameters.pop("type")

        # validate parameter combination
        if type in self._TYPE_COMBINATION_MAPPING:
            valid_parameters = self._TYPE_COMBINATION_MAPPING[type]
            for key, value in parameters.items():
                if key not in valid_parameters and value is not None:
                    msg = "Invalid parameter for '{}' Input, parameter '{}' should be None but got '{}'"
                    raise ValidationException(
                        message=msg.format(type, key, value),
                        no_personal_data_message=msg.format("[type]", "[parameter]", "[parameter_value]"),
                        error_category=ErrorCategory.USER_ERROR,
                        target=ErrorTarget.PIPELINE,
                    )

    @classmethod
    def _get_input_by_type(cls, t: type):
        if t in cls._DATA_TYPE_MAPPING:
            return cls(type=cls._DATA_TYPE_MAPPING[t])
        return None

    @classmethod
    def _get_default_string_input(cls):
        return cls(type="string")

    @classmethod
    def _get_param_with_standard_annotation(cls, func):
        return _get_param_with_standard_annotation(func, is_func=True)


class Output(DictMixin):
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
    def __init__(self, type="uri_folder", path=None, mode="rw_mount", description=None):
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
        pass

    @overload
    def __init__(self, type="uri_file", path=None, mode="rw_mount", description=None):
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
        pass

    def __init__(
        self, *, type=AssetTypes.URI_FOLDER, path=None, mode=InputOutputModes.RW_MOUNT, description=None, **kwargs
    ):
        # As an annotation, it is not allowed to initialize the name.
        # The name will be updated by the annotated variable name.
        self.name = None
        self.type = type
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

    def _to_component_output(self):
        return ComponentOutput(self._to_dict())


class EnumInput(Input):
    """Enum parameter parse the value according to its enum values."""

    def __init__(self, *, enum: Union[EnumMeta, Sequence[str]] = None, default=None, description=None, **kwargs):
        """Initialize an enum parameter, the options of an enum parameter are the enum values.

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
            self._str2enum = {v: e for v, e in zip(enum_values, enum)}
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
        """Check whether the enum is valid and return the values of the enum."""
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
            )

        if len(enum_values) <= 0:
            msg = "enum must have enum values."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
            )

        if any(not isinstance(v, str) for v in enum_values):
            msg = "enum values must be str type."
            raise ValidationException(
                message=msg,
                no_personal_data_message=msg,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
            )

        return enum_values

    def _parse(self, str_val: str):
        """Parse the enum value from a string value or the enum value."""
        if str_val is None:
            return str_val

        if self._enum_class and isinstance(str_val, self._enum_class):
            return str_val  # Directly return the enum value if it is the enum.

        if str_val not in self._str2enum:
            msg = "Not a valid enum value: '{}', valid values: {}"
            raise ValidationException(
                message=msg.format(str_val, ", ".join(self.enum)),
                no_personal_data_message=msg.format("[val]", "[enum]"),
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.PIPELINE,
            )
        return self._str2enum[str_val]

    def _update_default(self, default_value):
        """Enum parameter support updating values with a string value."""
        enum_val = self._parse(default_value)
        if self._enum_class and isinstance(enum_val, self._enum_class):
            enum_val = enum_val.value
        self.default = enum_val


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


def _get_annotation_cls_by_type(t: type, raise_error=False):
    cls = Input._get_input_by_type(t)
    if cls is None and raise_error:
        raise UserErrorException(f"Can't convert type {t} to azure.ai.ml.Input")
    return cls


def _get_param_with_standard_annotation(
    cls_or_func, is_func=False, non_pipeline_parameter_names=None, dynamic_param_name=None, dynamic_param_value=None
):
    """Standardize function parameters or class fields with dsl.types annotation."""
    non_pipeline_parameter_names = non_pipeline_parameter_names or []

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
            # Try create annotation by type when got like 'param: int'
            if not _is_dsl_type_cls(annotation) and not _is_dsl_types(annotation):
                annotation = _get_annotation_cls_by_type(annotation, raise_error=False)
                if not annotation:
                    # Fall back to string parameter
                    annotation = Input._get_default_string_input()
            annotation_fields[name] = annotation
        return annotation_fields

    def _merge_field_keys(annotation_fields, defaults_dict):
        """Merge field keys from annotations and cls dict to get all fields in class."""
        anno_keys = list(annotation_fields.keys())
        dict_keys = defaults_dict.keys()
        if not dict_keys:
            return anno_keys
        # Fields with default values must follow those without defaults, so find the first key with
        # annotation that appear in the class dict, the previous keys must be in the front of the key list
        all_keys = []
        # Use this flag to guarantee all fields with defaults following fields without defaults.
        seen_default = False
        for key in anno_keys:
            if key in dict_keys:
                seen_default = True
            else:
                if seen_default:
                    raise UserErrorException(f"Non-default argument {key!r} follows default argument.")
                all_keys.append(key)
        # Append all keys in dict
        all_keys.extend(dict_keys)
        return all_keys

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
            if complete_annotation._is_parameter_type and complete_annotation.default is not None:
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

    def _filter_pipeline_parameters(dct):
        """Filter out non pipeline parameters and dynamic parameter key."""
        return {k: v for k, v in dct.items() if k not in non_pipeline_parameter_names and k != dynamic_param_name}

    # From annotations get field with type
    annotations = _filter_pipeline_parameters(getattr(cls_or_func, "__annotations__", {}))
    annotations = _update_io_from_mldesigner(annotations)
    annotation_fields = _get_fields(annotations)
    # Update fields use class field with defaults from class dict or signature(func).paramters
    if not is_func:
        # Only consider public fields in class dict
        defaults_dict = {key: val for key, val in cls_or_func.__dict__.items() if not key.startswith("_")}
        defaults_dict = _filter_pipeline_parameters(defaults_dict)
        # Restrict each field must have annotation(in annotation dict)
        if any(key not in annotation_fields for key in defaults_dict):
            raise UserErrorException(f"Each field in parameter group {cls_or_func!r} must have an annotation.")
    else:
        # Infer parameter type from value if is function
        defaults_dict = {key: val.default for key, val in signature(cls_or_func).parameters.items()}
        defaults_dict = _filter_pipeline_parameters(defaults_dict)
    all_fields = _update_fields_with_default(annotation_fields, defaults_dict)
    return all_fields


def _is_dsl_type_cls(t: type):
    if type(t) is not type:
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


def _update_io_from_mldesigner(annotations: dict) -> dict:
    """This function will translate IOBase from mldesigner package to azure.ml.entities.Input/Output.

    This function depend on `mldesigner._input_output._IOBase._to_io_entity_args_dict` to translate Input/Output
    instance annotations to IO entities.
    This function depend on class names of `mldesigner._input_output` to translate Input/Output class annotations
    to IO entities.
    """
    mldesigner_pkg = "mldesigner"

    def _is_input_or_output_type(io: type, type_str: str):
        """Return true if type name contains type_str"""
        if isinstance(io, type) and io.__module__.startswith(mldesigner_pkg):
            if type_str in io.__name__:
                return True
        return False

    result = {}
    for key, io in annotations.items():
        if isinstance(io, type):
            if _is_input_or_output_type(io, "Input"):
                # mldesigner.Input -> entities.Input
                io = Input
            elif _is_input_or_output_type(io, "Output"):
                # mldesigner.Output -> entities.Output
                io = Output
        elif hasattr(io, "_to_io_entity_args_dict"):
            try:
                if _is_input_or_output_type(type(io), "Input"):
                    # mldesigner.Input() -> entities.Input()
                    io = Input(**io._to_io_entity_args_dict())
                elif _is_input_or_output_type(type(io), "Output"):
                    # mldesigner.Output() -> entities.Output()
                    io = Output(**io._to_io_entity_args_dict())
            except BaseException as e:
                msg = f"Failed to parse {io} to azure-ai-ml Input/Output."
                raise ComponentException(
                    message=msg,
                    target=ErrorTarget.COMPONENT,
                    no_personal_data_message=msg,
                    error_category=ErrorCategory.SYSTEM_ERROR,
                ) from e
        result[key] = io
    return result
