# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Optional, Type, get_origin, get_args, Union, List, Dict, Tuple
import builtins

def _is_builtin_type(x: Type) -> bool:
    global _builtin_types
    if (_builtin_types is None):
        _builtin_types = {obj for obj in vars(builtins).values() if isinstance(obj, type)}
        _builtin_types.add(type(None))
    return isinstance(x, type) and x in _builtin_types

def _is_union_type(x: Type) -> bool:
    return get_origin(x) is Union

def _is_list_type(x: Type) -> bool:
    return get_origin(x) is list

def _is_dict_type(x: Type) -> bool:
    return get_origin(x) is dict

def _is_tuple_type(x: Type) -> bool:
    return get_origin(x) is Tuple

def _is_optional_type(x: Type) -> bool:
    return _is_union_type(x) and type(None) in get_args(x)

def _as_msrest_serializable(x: Type) -> None:
    if "_attribute_map" in x.__dict__ or _is_builtin_type(x):
        return
    
    if _is_union_type(x) or _is_list_type(x) or _is_dict_type(x) or _is_tuple_type(x):
        for t in get_args(x):
            as_msrest_serializable(t)
        return
    
    if not (isinstance(x, Type) and (dataclass_params := x.__dataclass_params__)):
        raise Exception("This function only works with @dataclass Types")

    attributes = {}
    validation = {}
    for name,value in x.__dataclass_fields__.items():
        attributes[name] = {
            "key": name,
            "type": value.type,
        }

        if dataclass_params.frozen:
            validation.setdefault(name, {}).update({"readonly": True})
        
        if not _is_optional_type(value.type):
            validation.setdefault(name, {}).update({"required": True})
        
        # recurse on types
        as_msrest_serializable(value.type)
    
    # Monkey patching oh my 😱
    x._attribute_map = attributes
    x._validation = validation

def deserialize_json(json: Dict[str, Any], x: Type) -> object:
    if _is_builtin_type(x):
        return x(json)
    
    if _is_union_type(x):
        for t in get_args(x):
            try:
                return deserialize_json(json, t)
            except:
                pass
        raise Exception("Could not deserialize json into any of the union types")
    
    if _is_list_type(x):
        return [deserialize_json(j, get_args(x)[0]) for j in json]
    
    if _is_dict_type(x):
        return {k: deserialize_json(v, get_args(x)[1]) for k,v in json.items()}
    
    if _is_tuple_type(x):
        return tuple(deserialize_json(j, t) for j,t in zip(json, get_args(x)))
    
    if _is_optional_type(x):
        if json is None:
            return None
        return deserialize_json(json, get_args(x)[0])
    
    if not (isinstance(x, Type) and (dataclass_params := x.__dataclass_params__)):
        raise Exception("This function only works with @dataclass Types")
    
    instance = x()
    for name,value in x.__dataclass_fields__.items():
        setattr(instance, name, deserialize_json(json[value.name], value.type))
    
    return instance