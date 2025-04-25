# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import re
from typing import Any, Mapping, Sequence, Tuple


def normalize_identifier_name(name: str) -> str:
    """Normalize the identifier name to a valid Python variable name.

    Args:
        name (str): The identifier name to normalize.

    Returns:
        str: The normalized identifier name.
    """
    normalized = re.sub(r"\W", "_", name.strip())
    if normalized[0].isdigit():
        normalized = f"_{normalized}"
    return normalized


def get_int_env_var(env_var_name: str, default_value: int = 0) -> int:
    """Get the integer value of the environment variable.

    Args:
        env_var_name (str): The name of the environment variable.
        default_value (int): The default value if the environment variable is not set.

    Returns:
        int: The integer value of the environment variable.
    """
    try:
        value = os.getenv(env_var_name, default_value)
        return int(value)
    except ValueError:
        return default_value


def get_value_from_path(path: str, data: Mapping[str, Any]) -> Tuple[bool, Any]:
    """Tried to get a value from a mapping based on the specified path. The path is a
    string with dot-separated keys (e.g. data.nested_1.nested_2).

    This will interpret the path prioritizing a depth first search with the shortest
    key possible at each level. If for example you had the following data:
    {
        "foo": {
            "bar": {
                "happy": 12
            }
        },
        "foo.bar": {
            "none": 14,
            "random": { "some": 15 }
        },
        "foo.bar.none": 16
    }
    And you asked for foo.bar.none, the returned value would be 14"
    """

    def _get_value(data: Mapping[str, Any], parts: Sequence[str]) -> Tuple[bool, Any]:
        if len(parts) == 0:
            return True, data

        for i in range(1, len(parts) + 1):
            key = ".".join(parts[:i])
            if isinstance(data, Mapping) and key in data:
                found, match = _get_value(data[key], parts[i:])
                if found:
                    return found, match

        return False, None

    if path is None or data is None:
        return False, None

    parts = path.strip().split(".")
    if len(parts) == 0:
        return False, None
    return _get_value(data, parts)
