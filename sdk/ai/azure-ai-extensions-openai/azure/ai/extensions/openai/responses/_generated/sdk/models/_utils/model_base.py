# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Minimal model_base compatibility for TypedDict generation."""

from typing import Any

Model = dict[str, Any]


def rest_field(*args: Any, **kwargs: Any) -> None:  # pylint: disable=unused-argument
    """Return a placeholder field marker for generated patch classes."""
    return None
