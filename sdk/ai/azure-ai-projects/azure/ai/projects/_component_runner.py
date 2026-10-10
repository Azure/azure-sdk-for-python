# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Execute a source-backed component from a mounted Code snapshot."""

import importlib
import sys
from typing import Callable, Dict


def _boolean(value: str) -> bool:
    return value == "True"


_CONVERSIONS: Dict[str, Callable[[str], object]] = {
    "str": str,
    "int": int,
    "float": float,
    "bool": _boolean,
}


def main() -> None:
    module_name, function_name, port_spec = sys.argv[1:4]
    ports = [] if port_spec == "-" else [port.split(":", 1) for port in port_spec.split(",")]
    values = sys.argv[4:]
    if len(ports) != len(values):
        raise ValueError(f"Component '{function_name}' expected {len(ports)} arguments, got {len(values)}.")

    wrapped = getattr(importlib.import_module(module_name), function_name)
    function = getattr(wrapped, "__wrapped__", None)
    if function is None:
        raise TypeError(f"Component '{module_name}.{function_name}' is not decorated with @component.")
    function(**{name: _CONVERSIONS[conversion](value) for (name, conversion), value in zip(ports, values)})


if __name__ == "__main__":
    main()
