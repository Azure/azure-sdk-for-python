# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Preserve Loom's scalar fast path without modifying generated model utilities.

The shared Python generator 0.39.0 still probes temporal protocols for plain
JSON scalars. Remove this maintained customization when unmodified generation
passes tests/test_model_primitive_serialization.py.
"""

from functools import wraps
from typing import Any, Optional

from ._utils import model_base


def install_scalar_serialization() -> None:
    """Install the package-local optimization once, including across reloads."""
    original = model_base._serialize  # pylint: disable=protected-access
    if getattr(original, "_finetuning_scalar_fast_path", False):
        return

    @wraps(original)
    def serialize(o: Any, format: Optional[str] = None) -> Any:
        if o is None or type(o) in (str, float):
            return o
        if type(o) in (int, bool):
            return str(o) if format == "str" else o
        return original(o, format)

    setattr(serialize, "_finetuning_scalar_fast_path", True)
    model_base._serialize = serialize  # pylint: disable=protected-access
