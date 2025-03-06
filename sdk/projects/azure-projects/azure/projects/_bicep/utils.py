# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import List, Dict, Any
import json
import random
import string


def resolve_value(value: Any) -> str:
    try:
        value: str = value.value
    except AttributeError:
        value: str = json.dumps(value).replace('"', "'")
    return value


def resolve_key(key: Any) -> str:
    try:
        return key.value
    except AttributeError:
        if key.isidentifier():
            return key
        return f"'{key}'"


def clean_name(name: str) -> str:
    return "".join(c for c in name if c.isalnum())


def generate_suffix(length: int = 5, /) -> str:
    return "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length)).lower()


def generate_name(seed: str, max_length: int = 20) -> str:
    random_gen = random.Random(resolve_value(seed))
    return "".join([random_gen.choice(string.ascii_lowercase) for _ in range(max_length)])


def serialize(value: Any, indent: str = "") -> str:
    bicep = ""
    if isinstance(value, dict):
        bicep += "{\n"
        bicep += serialize_dict(value, indent + "  ")
        bicep += indent + "}\n"
    elif isinstance(value, list):
        bicep += "[\n"
        bicep += serialize_list(value, indent + "  ")
        bicep += indent + "]\n"
    else:
        bicep += resolve_value(value)
    return bicep


def serialize_list(list_val: List[Any], indent: str) -> str:
    bicep = ""
    for item in list_val:
        if isinstance(item, dict):
            bicep += f"{indent}{{\n"
            bicep += serialize_dict(item, indent + "  ")
            bicep += f"{indent}}}\n"
        elif isinstance(item, list):
            bicep += f"{indent}[\n"
            bicep += serialize_list(item, indent + "  ")
            bicep += f"{indent}]\n"
        else:
            bicep += f"{indent}{resolve_value(item)}\n"
    return bicep


def serialize_dict(dict_val: Dict[str, Any], indent: str) -> str:
    bicep = ""
    for key, value in dict_val.items():
        if isinstance(value, dict) and value:
            bicep += f"{indent}{key}: {{\n"
            bicep += serialize_dict(value, indent + "  ")
            bicep += f"{indent}}}\n"
        elif isinstance(value, list) and value:
            bicep += f"{indent}{key}: [\n"
            bicep += serialize_list(value, indent + "  ")
            bicep += f"{indent}]\n"
        else:
            bicep += f"{indent}{resolve_key(key)}: {resolve_value(value)}\n"
    return bicep
