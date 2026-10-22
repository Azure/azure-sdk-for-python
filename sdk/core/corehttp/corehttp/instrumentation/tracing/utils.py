# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Common tracing functionality for SDK libraries."""
from typing import Any, Callable

from ._tracer import get_tracer
from ...settings import settings


__all__ = [
    "with_current_context",
]


def with_current_context(func: Callable) -> Any:
    """Passes the current spans to the new context the function will be run in.

    :param func: The function that will be run in the new context
    :type func: callable
    :return: The func wrapped with correct context
    :rtype: callable
    """
    if not settings.tracing_enabled:
        return func

    tracer = get_tracer()
    if not tracer:
        return func
    return tracer.with_current_context(func)
