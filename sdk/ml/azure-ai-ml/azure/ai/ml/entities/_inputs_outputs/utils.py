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
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple, Type, Union, cast

from typing_extensions import Annotated, Literal, TypeAlias

from azure.ai.ml.constants._component import IOConstants
from azure.ai.ml.exceptions import UserErrorException

# avoid circular import error
if TYPE_CHECKING:
    from .input import Input
    from .output import Output

SUPPORTED_RETURN_TYPES_PRIMITIVE = list(IOConstants.PRIMITIVE_TYPE_2_STR.keys())


Annotation: TypeAlias = Union[str, Type, Annotated, None]  # type: ignore


def is_group(obj: object) -> bool:
    """Return True if obj is a group or an instance of a parameter group class.

    :param obj: The object to check.
    :type obj: Any
    :return: True if obj is a group or an instance, False otherwise.
    :rtype: bool
    """
    return hasattr(obj, IOConstants.GROUP_ATTR_NAME)


def _get_annotation_by_value(val: Any) -> Union["Input", Type["Input"]]:
    # TODO: we'd better remove this potential recursive import
    from .enum_input import EnumInput
    from .input import Input

    annotation: Any = None

    def _is_dataset(data: Any) -> bool:
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
        _new_annotation = _get_annotation_cls_by_type(type(val), raise_error=False)
        if not _new_annotation:
            # Fall back to default
            annotation = Input._get_default_unknown_input()
        else:
            return _new_annotation
    return cast(Union["Input", Type["Input"]], annotation)


def _get_annotation_cls_by_type(
    t: type, raise_error: bool = False, optional: Optional[bool] = None
) -> Optional["Input"]:
    # TODO: we'd better remove this potential recursive import
    from .input import Input

    cls = Input._get_input_by_type(t, optional=optional)
    if cls is None and raise_error:
        raise UserErrorException(f"Can't convert type {t} to azure.ai.ml.Input")
    return cls


# pylint: disable=too-many-statements
def _get_param_with_standard_annotation(
    cls_or_func: Union[Callable, Type], is_func: bool = False, skip_params: Optional[List[str]] = None
) -> Dict[str, Union[Annotation, "Input", "Output"]]:
    """Standardize function parameters or class fields with dsl.types annotation.

    :param cls_or_func: Either a class or a function
    :type cls_or_func: Union[Callable, Type]
    :param is_func: Whether `cls_or_func` is a function. Defaults to False.
    :type is_func: bool
    :param skip_params:
    :type skip_params: Optional[List[str]]
    :return: A dictionary of field annotations
    :rtype: Dict[str, Union[Annotation, "Input", "Output"]]
    """
    # TODO: we'd better remove this potential recursive import
    from .group_input import GroupInput
    from .input import Input
    from .output import Output

    def _is_dsl_type_cls(t: Any) -> bool:
        if type(t) is not type:  # pylint: disable=unidiomatic-typecheck
            return False
        return issubclass(t, (Input, Output))

    def _is_dsl_types(o: object) -> bool:
        return _is_dsl_type_cls(type(o))

    def _get_fields(annotations: Dict) -> Dict:
        """Return field names to annotations mapping in class.

        :param annotations: The annotations
        :type annotations: Dict[str, Union[Annotation, Input, Output]]
        :return: The field dict
        :rtype: Dict[str, Union[Annotation, Input, Output]]
        """
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
                _deep_copy: GroupInput = copy.deepcopy(getattr(annotation, IOConstants.GROUP_ATTR_NAME))
                annotation = _deep_copy
            # Try creating annotation by type when got like 'param: int'
            if not _is_dsl_type_cls(annotation) and not _is_dsl_types(annotation):
                origin_annotation = annotation
                annotation = cast(Input, _get_annotation_cls_by_type(annotation, raise_error=False))
                if not annotation:
                    msg = f"Unsupported annotation type {origin_annotation!r} for parameter {name!r}."
                    raise UserErrorException(msg)
            annotation_fields[name] = annotation
        return annotation_fields

    def _merge_field_keys(
        annotation_fields: Dict[str, Union[Annotation, Input, Output]], defaults_dict: Dict[str, Any]
    ) -> List[str]:
        """Merge field keys from annotations and cls dict to get all fields in class.

        :param annotation_fields: The field annotations
        :type annotation_fields: Dict[str, Union[Annotation, Input, Output]]
        :param defaults_dict: The map of variable name to default value
        :type defaults_dict: Dict[str, Any]
        :return: A list of field keys
        :rtype: List[str]
        """
        anno_keys = list(annotation_fields.keys())
        dict_keys = defaults_dict.keys()
        if not dict_keys:
            return anno_keys
        return [*anno_keys, *[key for key in dict_keys if key not in anno_keys]]

    def _update_annotation_with_default(
        anno: Union[Annotation, Input, Output], name: str, default: Any
    ) -> Union[Annotation, Input, Output]:
        """Create annotation if is type class and update the default.

        :param anno: The annotation
        :type anno: Union[Annotation, Input, Output]
        :param name: The port name
        :type name: str
        :param default: The default value
        :type default: Any
        :return: The updated annotation
        :rtype: Union[Annotation, Input, Output]
        """
        # Create instance if is type class
        complete_annotation = anno
        if _is_dsl_type_cls(anno):
            if anno is not None and not isinstance(anno, (str, Input, Output)):
                complete_annotation = anno()
        if complete_annotation is not None and not isinstance(complete_annotation, str):
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

    def _update_fields_with_default(
        annotation_fields: Dict[str, Union[Annotation, Input, Output]], defaults_dict: Dict[str, Any]
    ) -> Dict[str, Union[Annotation, Input, Output]]:
        """Use public values in class dict to update annotations.

        :param annotation_fields: The field annotations
        :type annotation_fields: Dict[str, Union[Annotation, Input, Output]]
        :param defaults_dict: A map of variable name to default value
        :type defaults_dict: Dict[str, Any]
        :return: List of field names
        :rtype: List[str]
        """
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

    def _merge_and_reorder(
        inherited_fields: Dict[str, Union[Annotation, Input, Output]],
        cls_fields: Dict[str, Union[Annotation, Input, Output]],
    ) -> Dict[str, Union[Annotation, Input, Output]]:
        """Merge inherited fields with cls fields.

        The order inside each part will not be changed. Order will be:

        {inherited_no_default_fields} + {cls_no_default_fields} + {inherited_default_fields} + {cls_default_fields}.


        :param inherited_fields: The inherited fields
        :type inherited_fields: Dict[str, Union[Annotation, Input, Output]]
        :param cls_fields: The class fields
        :type cls_fields: Dict[str, Union[Annotation, Input, Output]]
        :return: The merged fields
        :rtype: Dict[str, Union[Annotation, Input, Output]]

        .. admonition:: Additional Note

           :class: note

           If cls overwrite an inherited no default field with default, it will be put in the
           cls_default_fields part and deleted from inherited_no_default_fields:

           .. code-block:: python

              @dsl.group
              class SubGroup:
                  int_param0: Integer
                  int_param1: int

              @dsl.group
              class Group(SubGroup):
                  int_param3: Integer
                  int_param1: int = 1

           The init function of Group will be `def __init__(self, *, int_param0, int_param3, int_param1=1)`.
        """

        def _split(
            _fields: Dict[str, Union[Annotation, Input, Output]]
        ) -> Tuple[Dict[str, Union[Annotation, Input, Output]], Dict[str, Union[Annotation, Input, Output]]]:
            """Split fields to two parts from the first default field.

            :param _fields: The fields
            :type _fields: Dict[str, Union[Annotation, Input, Output]]
            :return: A 2-tuple of (fields with no defaults, fields with defaults)
            :rtype: Tuple[Dict[str, Union[Annotation, Input, Output]], Dict[str, Union[Annotation, Input, Output]]]
            """
            _no_defaults_fields, _defaults_fields = {}, {}
            seen_default = False
            for key, val in _fields.items():
                if val is not None and not isinstance(val, str):
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

    def _get_inherited_fields() -> Dict[str, Union[Annotation, Input, Output]]:
        """Get all fields inherited from @group decorated base classes.

        :return: The field dict
        :rtype: Dict[str, Union[Annotation, Input, Output]]
        """
        # Return value of _get_param_with_standard_annotation
        _fields: Dict[str, Union[Annotation, Input, Output]] = OrderedDict({})
        if is_func:
            return _fields
        # In reversed order so that more derived classes
        # override earlier field definitions in base classes.
        if isinstance(cls_or_func, type):
            for base in cls_or_func.__mro__[-1:0:-1]:
                if is_group(base):
                    # merge and reorder fields from current base with previous
                    _fields = _merge_and_reorder(
                        _fields, copy.deepcopy(getattr(base, IOConstants.GROUP_ATTR_NAME).values)
                    )
        return _fields

    skip_params = skip_params or []
    inherited_fields = _get_inherited_fields()
    # From annotations get field with type
    annotations: Dict[str, Annotation] = getattr(cls_or_func, "__annotations__", {})
    annotations = {k: v for k, v in annotations.items() if k not in skip_params}
    annotations = _update_io_from_mldesigner(annotations)
    annotation_fields = _get_fields(annotations)
    defaults_dict: Dict[str, Any] = {}
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


def _update_io_from_mldesigner(annotations: Dict[str, Annotation]) -> Dict[str, Union[Annotation, "Input", "Output"]]:
    """Translates IOBase from mldesigner package to azure.ml.entities.Input/Output.

    This function depends on:

    * `mldesigner._input_output._IOBase._to_io_entity_args_dict` to translate Input/Output instance annotations
      to IO entities.
    * class names of `mldesigner._input_output` to translate Input/Output class annotations
      to IO entities.

    :param annotations: A map of variable names to annotations
    :type annotations: Dict[str, Annotation]
    :return: Dict with mldesigner IO types converted to azure-ai-ml Input/Output
    :rtype: Dict[str, Union[Annotation, Input, Output]]
    """
    from typing_extensions import get_args, get_origin

    from azure.ai.ml import Input, Output

    from .enum_input import EnumInput

    mldesigner_pkg = "mldesigner"
    param_name = "_Param"
    return_annotation_key = "return"

    def _is_primitive_type(io: type) -> bool:
        """Checks whether type is a primitive type

        :param io: A type
        :type io: type
        :return: Return true if type is subclass of mldesigner._input_output._Param
        :rtype: bool
        """
        return any(io.__module__.startswith(mldesigner_pkg) and item.__name__ == param_name for item in getmro(io))

    def _is_input_or_output_type(io: type, type_str: Literal["Input", "Output", "Meta"]) -> bool:
        """Checks whether a type is an Input or Output type

        :param io: A type
        :type io: type
        :param type_str: The kind of type to check for
        :type type_str: Literal["Input", "Output", "Meta"]
        :return: Return true if type name contains type_str
        :rtype: bool
        """
        if isinstance(io, type) and io.__module__.startswith(mldesigner_pkg):
            if type_str in io.__name__:
                return True
        return False

    result = {}
    for key, io in annotations.items():  # pylint: disable=too-many-nested-blocks
        if isinstance(io, type):
            if _is_input_or_output_type(io, "Input"):
                # mldesigner.Input -> entities.Input
                io = Input
            elif _is_input_or_output_type(io, "Output"):
                # mldesigner.Output -> entities.Output
                io = Output
            elif _is_primitive_type(io):
                io = (
                    Output(type=io.TYPE_NAME)  # type: ignore
                    if key == return_annotation_key
                    else Input(type=io.TYPE_NAME)  # type: ignore
                )
        elif hasattr(io, "_to_io_entity_args_dict"):
            try:
                if _is_input_or_output_type(type(io), "Input"):
                    # mldesigner.Input() -> entities.Input()
                    if io is not None:
                        io = Input(**io._to_io_entity_args_dict())
                elif _is_input_or_output_type(type(io), "Output"):
                    # mldesigner.Output() -> entities.Output()
                    if io is not None:
                        io = Output(**io._to_io_entity_args_dict())
                elif _is_primitive_type(type(io)):
                    if io is not None and not isinstance(io, str):
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
                # Handle Annotated annotation
        elif get_origin(io) is Annotated:
            hint_type, arg, *hint_args = get_args(io)  # pylint: disable=unused-variable
            if hint_type in SUPPORTED_RETURN_TYPES_PRIMITIVE:
                if not _is_input_or_output_type(type(arg), "Meta"):
                    raise UserErrorException(
                        f"Annotated Metadata class only support "
                        f"mldesigner._input_output.Meta, "
                        f"it is {type(arg)} now."
                    )
                if arg.type is not None and arg.type != hint_type:
                    raise UserErrorException(
                        f"Meta class type {arg.type} should be same as Annotated type: " f"{hint_type}"
                    )
                arg.type = hint_type
                io = (
                    Output(**arg._to_io_entity_args_dict())
                    if key == return_annotation_key
                    else Input(**arg._to_io_entity_args_dict())
                )
        result[key] = io
    return result


def _remove_empty_values(data: Any) -> Any:
    """Recursively removes None values from a dict

    :param data: The value to remove None from
    :type data: T
    :return:
      * `data` if `data` is not a dict
      * `data` with None values recursively filtered out if data is a dict
    :rtype: T
    """
    if not isinstance(data, dict):
        return data
    return {k: _remove_empty_values(v) for k, v in data.items() if v is not None}
