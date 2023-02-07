# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access
# enable protected access for protected helper functions

import copy
from collections import OrderedDict
from enum import Enum as PyEnum
from enum import EnumMeta
from inspect import Parameter, getmro, signature

from azure.ai.ml.constants._component import IOConstants
from azure.ai.ml.exceptions import UserErrorException


def is_group(obj):
    """Return True if obj is a group or an instance of a parameter group class."""
    return hasattr(obj, IOConstants.GROUP_ATTR_NAME)


def _get_annotation_by_value(val):
    # TODO: we'd better remove this potential recursive import
    from .enum_input import EnumInput
    from .input import Input

    def _is_dataset(data):
        from azure.ai.ml.entities._job.job_io_mixin import JobIOMixin

        DATASET_TYPES = JobIOMixin
        return isinstance(data, DATASET_TYPES)

    if _is_dataset(val):
        annotation = Input
    elif val is Parameter.empty or val is None:
        # If no default value or default is None, create val as the basic parameter type,
        # it could be replaced using component parameter definition.
        annotation = Input._get_default_unknown_input()
    elif isinstance(val, PyEnum):
        # Handle enum values
        annotation = EnumInput(enum=val.__class__)
    else:
        annotation = _get_annotation_cls_by_type(type(val), raise_error=False)
        if not annotation:
            # Fall back to default
            annotation = Input._get_default_unknown_input()
    return annotation


def _get_annotation_cls_by_type(t: type, raise_error=False, optional=None):
    # TODO: we'd better remove this potential recursive import
    from .input import Input

    cls = Input._get_input_by_type(t, optional=optional)
    if cls is None and raise_error:
        raise UserErrorException(f"Can't convert type {t} to azure.ai.ml.Input")
    return cls


# pylint: disable=too-many-statements
def _get_param_with_standard_annotation(cls_or_func, is_func=False, skip_params=None):
    """Standardize function parameters or class fields with dsl.types
    annotation."""
    # TODO: we'd better remove this potential recursive import
    from .input import Input
    from .output import Output

    def _is_dsl_type_cls(t: type):
        if type(t) is not type:  # pylint: disable=unidiomatic-typecheck
            return False
        return issubclass(t, (Input, Output))

    def _is_dsl_types(o: object):
        return _is_dsl_type_cls(type(o))

    def _get_fields(annotations):
        """Return field names to annotations mapping in class."""
        annotation_fields = OrderedDict()
        for name, annotation in annotations.items():
            # Skip return type
            if name == "return":
                continue
            # Handle EnumMeta annotation
            if isinstance(annotation, EnumMeta):
                from .enum_input import EnumInput

                annotation = EnumInput(type="string", enum=annotation)
            # Handle Group annotation
            if is_group(annotation):
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
        complete_annotation._port_name = name
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
        if isinstance(complete_annotation, Output) and default is not None:
            msg = (
                f"Default value of Output {complete_annotation._port_name!r} cannot be set:"
                f"Output has no default value."
            )
            raise UserErrorException(msg)
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
            if is_group(base):
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
        @dsl.group
        class SubGroup:
            int_param0: Integer
            int_param1: int
        @dsl.group
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

    skip_params = skip_params or []
    inherited_fields = _get_inherited_fields()
    # From annotations get field with type
    annotations = getattr(cls_or_func, "__annotations__", {})
    annotations = {k: v for k, v in annotations.items() if k not in skip_params}
    annotations = _update_io_from_mldesigner(annotations)
    annotation_fields = _get_fields(annotations)
    # Update fields use class field with defaults from class dict or signature(func).paramters
    if not is_func:
        # Only consider public fields in class dict
        defaults_dict = {
            key: val for key, val in cls_or_func.__dict__.items() if not key.startswith("_") and key not in skip_params
        }
    else:
        # Infer parameter type from value if is function
        defaults_dict = {
            key: val.default
            for key, val in signature(cls_or_func).parameters.items()
            if key not in skip_params and val.kind != val.VAR_KEYWORD
        }
    fields = _update_fields_with_default(annotation_fields, defaults_dict)
    all_fields = _merge_and_reorder(inherited_fields, fields)
    return all_fields


def _update_io_from_mldesigner(annotations: dict) -> dict:
    """This function will translate IOBase from mldesigner package to azure.ml.entities.Input/Output.

    This function depend on `mldesigner._input_output._IOBase._to_io_entity_args_dict` to translate Input/Output
    instance annotations to IO entities.
    This function depend on class names of `mldesigner._input_output` to translate Input/Output class annotations
    to IO entities.
    """
    from azure.ai.ml import Input, Output

    from .enum_input import EnumInput

    mldesigner_pkg = "mldesigner"
    param_name = "_Param"
    return_annotation_key = "return"

    def _is_primitive_type(io: type):
        """Return true if type is subclass of mldesigner._input_output._Param"""
        return any([io.__module__.startswith(mldesigner_pkg) and item.__name__ == param_name for item in getmro(io)])

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
            elif _is_primitive_type(io):
                io = Output(type=io.TYPE_NAME) if key == return_annotation_key else Input(type=io.TYPE_NAME)
        elif hasattr(io, "_to_io_entity_args_dict"):
            try:
                if _is_input_or_output_type(type(io), "Input"):
                    # mldesigner.Input() -> entities.Input()
                    io = Input(**io._to_io_entity_args_dict())
                elif _is_input_or_output_type(type(io), "Output"):
                    # mldesigner.Output() -> entities.Output()
                    io = Output(**io._to_io_entity_args_dict())
                elif _is_primitive_type(type(io)):
                    if io._is_enum():
                        io = EnumInput(**io._to_io_entity_args_dict())
                    else:
                        io = (
                            Output(**io._to_io_entity_args_dict())
                            if key == return_annotation_key
                            else Input(**io._to_io_entity_args_dict())
                        )
            except BaseException as e:
                raise UserErrorException(f"Failed to parse {io} to azure-ai-ml Input/Output: {str(e)}") from e
        result[key] = io
    return result


def _remove_empty_values(data, ignore_keys=None):
    if not isinstance(data, dict):
        return data
    ignore_keys = ignore_keys or {}
    return {
        k: v if k in ignore_keys else _remove_empty_values(v)
        for k, v in data.items()
        if v is not None or k in ignore_keys
    }
