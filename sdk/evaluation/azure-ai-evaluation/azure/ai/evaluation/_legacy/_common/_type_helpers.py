# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from dataclasses import fields, is_dataclass, MISSING
from enum import Enum, EnumMeta
from inspect import Parameter, Signature, isclass, signature
from typing import (
    Mapping,
    Optional,
    Sequence,
    Type,
    TypedDict,
    Union,
    Dict,
    Any,
    Callable,
    cast,
    get_args,
    get_origin,
    get_type_hints
)


class TypeMetadata(TypedDict):
    """Metadata for a type.
    
    :param str name: The name of the type.
    :param str description: The description of the type.
    :param str type: The type of the value.
    :param Any default: The default value of the value.
    """
    name: str
    """The name of argument/field/entry"""
    type: Optional[Type]
    """The type of the argument/field/entry"""
    value_type: Optional["ValueType"]
    """The value type of the argument/field/entry. This is used to determine the type of the value."""
    default: Union[Any, Parameter.empty]
    """The default value of the argument/field/entry. This uses Parameter.empty to indicate that the
    default value is not specified."""


class ValueType(Enum):
    """Value types."""
    INT = "int"
    DOUBLE = "double"
    BOOL = "boolean"
    STRING = "string"
    LIST = "array"
    OBJECT = "object"

    @staticmethod
    def from_type(t: Optional[Type]) -> Optional["ValueType"]:
        """Parse a type into a corresponding ValueType.

        :param Optional[Type] t: The type to parse.
        :return: The corresponding ValueType of the given type,or None if the type is not supported.
        :rtype: Optional[ValueType]
        """

        if t is Parameter.empty: return ValueType.OBJECT
        if t is None: return ValueType.OBJECT

        def type_or_subclass(t: Type, cls: Type) -> bool:
            return t is cls or (isclass(t) and issubclass(t, cls))

        t = ValueType.resolve_type(cast(Type, t))
        if type_or_subclass(t, int): return ValueType.INT
        if type_or_subclass(t, float): return ValueType.DOUBLE
        if type_or_subclass(t, bool): return ValueType.BOOL
        if type_or_subclass(t, str): return ValueType.STRING
        if type_or_subclass(t, EnumMeta):
            return ValueType.STRING
        if type_or_subclass(t, list) or type_or_subclass(t, Sequence):
            return ValueType.LIST
        if type_or_subclass(t, dict) or type_or_subclass(t, Mapping):
            return ValueType.OBJECT
        if t is Parameter.empty:
            return ValueType.OBJECT
        if t is Any:
            return ValueType.OBJECT

        return None

    @staticmethod
    def resolve_type(t: Optional[Type]) -> Type:
        """Resolve a type to its base type. For example, if the type is List[int], it will be resolved to
        List. If the type is Optional[int], it will be resolved to int.
        
        :param Optional[Type] t: The type to resolve.
        :return: The resolved type.
        :rtype: Type"""

        origin = get_origin(t)
        if origin is None:
            return t or type(None)
        
        if origin is Union:
            # Handle Optional[T] which is Union[T, None] by removing NoneType
            types = [arg for arg in get_args(t) if arg is not type(None)]
            if len(types) != 1:
                raise ValueError("Only optional unions (aka Union[X, None]) are supported")
            return types[0]
        else:
            return origin


def extract_type_metadata(item: Any, **kwargs) -> Mapping[str, TypeMetadata]:
    """Extracts metadata from a type.

    :param Any type: The type to extract metadata from.
    :return: A list of dictionaries containing the metadata. Will be empty if no metadata is found.
    :rtype: Mapping[str, TypeMetadata]
    """

    if item is None or item is Parameter.empty:
        return {}

    # NOTE: We use get_type_hints to get the type hints because:
    # - It handles forward references and string annotations
    # - It works for both classes, functions, dataclasses, TypeDicts, and so on
    # - It handles nested types and generics
    # The downsides are that it doesn't handle the fields/arguments without type hints (they are
    # excluded from the metadata dictionary it generates), and that it doesn't handle default values
    type_hints: Mapping[str, Type] = get_type_hints(
        item,
        globalns=kwargs.pop("globalns", None),
        localns=kwargs.pop("localns", None))

    if is_dataclass(item):
        return {
            f.name: {
                "name": f.name,
                "type": f.type if isinstance(f.type, type) else type_hints.get(f.name, None),
                "value_type": ValueType.from_type(f.type) if isinstance(f.type, type) else None,
                "default": f.default if f.default != MISSING else Parameter.empty,
            }
            for f in fields(item)
        }
    elif isinstance(item, Callable) and not _is_dict(item):
        def get_type(name: str, param: Parameter) -> Optional[Type]:
            resolved = type_hints.get(name, param.annotation)
            if param.default is not Parameter.empty and resolved is Parameter.empty:
                resolved = param.default.__class__ if isinstance(param.default, Enum) else type(param.default)
            return resolved if resolved is not Parameter.empty else None

        try:
            sig: Signature = signature(item)
            items: Dict[str, TypeMetadata] = {
                name: {
                    "name": name,
                    "type": (item_type := get_type(name, param)),
                    "value_type": ValueType.from_type(item_type),
                    "default": param.default,
                }
                for name, param in sig.parameters.items()
                if name not in ["self", "cls"] and param.kind not in [param.VAR_POSITIONAL, param.VAR_KEYWORD]
            }

            # also handle the return type
            items.update({
                "return": {
                    "name": "return",
                    "type": (item_type := type_hints.get("return", sig.return_annotation)),
                    "value_type": ValueType.from_type(item_type),
                    "default": Parameter.empty,
                }
            })
            return items
        except ValueError:
            # If the signature cannot be resolved, we fall back to the type hints
            pass

    return {
        k: {
            "name": k,
            "type": v,
            "value_type": ValueType.from_type(v),
            "default": Parameter.empty,
        }
        for k, v in type_hints.items()
    }

def _is_dict(t: Any) -> bool:
    """Check if the type is a dict.

    :param Any t: The type to check.
    :return: True if the type is a dict, False otherwise.
    :rtype: bool
    """
    return (get_origin(t) is dict
        or (isclass(t) and issubclass(t, dict))
        or (isclass(t) and issubclass(t, Mapping))
        or isinstance(t, dict))