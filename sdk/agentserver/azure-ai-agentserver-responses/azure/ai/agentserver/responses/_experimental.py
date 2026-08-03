# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Compatibility shim for the shared Agent Server experimental decorator."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar, overload

from typing_extensions import ParamSpec

try:
    from azure.ai.agentserver.core import experimental
except ImportError:
    P = ParamSpec("P")
    T = TypeVar("T")

    @overload
    def experimental(wrapped: type[T]) -> type[T]: ...

    @overload
    def experimental(wrapped: Callable[P, T]) -> Callable[P, T]: ...

    def experimental(wrapped: type[T] | Callable[P, T]) -> type[T] | Callable[P, T]:
        return wrapped
