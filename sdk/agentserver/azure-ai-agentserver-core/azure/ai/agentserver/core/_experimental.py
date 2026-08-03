# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Experimental API marker for Agent Server public preview features."""

from __future__ import annotations

import functools
import inspect
import logging
import os
import sys
from collections.abc import Callable
from contextvars import ContextVar
from typing import TypeVar, overload

from typing_extensions import ParamSpec, TypeGuard

DOCSTRING_TEMPLATE = ".. note::    {0} {1}\n\n"
DOCSTRING_DEFAULT_INDENTATION = 8
EXPERIMENTAL_CLASS_MESSAGE = "This is an experimental class,"
EXPERIMENTAL_METHOD_MESSAGE = "This is an experimental method,"
EXPERIMENTAL_LINK_MESSAGE = (
    "and may change at any time. Please see https://aka.ms/azure-ai-agentserver-experimental "
    "for more information."
)
DISABLE_EXPERIMENTAL_WARNING_ENV_VAR = "AZURE_AI_AGENTSERVER_DISABLE_EXPERIMENTAL_WARNING"

_warning_cache: set[str] = set()
_experimental_init_active: ContextVar[bool] = ContextVar("experimental_init_active", default=False)
module_logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


@overload
def experimental(wrapped: type[T]) -> type[T]: ...


@overload
def experimental(wrapped: Callable[P, T]) -> Callable[P, T]: ...


def experimental(wrapped: type[T] | Callable[P, T]) -> type[T] | Callable[P, T]:
    """Add an experimental note and runtime warning to a class or function.

    :param wrapped: Class or callable to mark as experimental.
    :type wrapped: type[T] | Callable[P, T]
    :return: The wrapped class or callable.
    :rtype: type[T] | Callable[P, T]
    """

    def is_class(value: type[T] | Callable[P, T]) -> TypeGuard[type[T]]:
        return inspect.isclass(value)

    if is_class(wrapped):
        return _add_class_docstring(wrapped)
    if inspect.isfunction(wrapped):
        return _add_function_docstring(wrapped)
    return wrapped


def _add_class_docstring(cls: type[T]) -> type[T]:
    doc_string = DOCSTRING_TEMPLATE.format(EXPERIMENTAL_CLASS_MESSAGE, EXPERIMENTAL_LINK_MESSAGE)
    if cls.__doc__:
        cls.__doc__ = _add_note_to_docstring(cls.__doc__, doc_string)
    else:
        cls.__doc__ = doc_string + ">"

    original_init = cls.__init__

    def wrapped_init(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        cache_key = f"class:{cls.__module__}.{cls.__qualname__}"
        message = f"Class {cls.__module__}.{cls.__qualname__}: {EXPERIMENTAL_CLASS_MESSAGE} {EXPERIMENTAL_LINK_MESSAGE}"
        active = _experimental_init_active.get()
        if not active and not _should_skip_warning() and not _is_warning_cached(cache_key):
            module_logger.warning(message)
        if active:
            return original_init(self, *args, **kwargs)
        token = _experimental_init_active.set(True)
        try:
            return original_init(self, *args, **kwargs)
        finally:
            _experimental_init_active.reset(token)

    if "__init__" in cls.__dict__ and inspect.isfunction(original_init):
        wrapped_init = functools.wraps(original_init)(wrapped_init)

    cls.__init__ = wrapped_init  # type: ignore[method-assign]
    return cls


def _add_function_docstring(func: Callable[P, T]) -> Callable[P, T]:
    doc_string = DOCSTRING_TEMPLATE.format(EXPERIMENTAL_METHOD_MESSAGE, EXPERIMENTAL_LINK_MESSAGE)
    if func.__doc__:
        func.__doc__ = _add_note_to_docstring(func.__doc__, doc_string)
    else:
        func.__doc__ = doc_string + ">"

    @functools.wraps(func)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        cache_key = f"function:{func.__module__}.{func.__qualname__}"
        message = f"Method {func.__module__}.{func.__qualname__}: {EXPERIMENTAL_METHOD_MESSAGE} {EXPERIMENTAL_LINK_MESSAGE}"
        if not _should_skip_warning() and not _is_warning_cached(cache_key):
            module_logger.warning(message)
        return func(*args, **kwargs)

    return wrapped


def _add_note_to_docstring(doc_string: str, note: str) -> str:
    indent = _get_indentation_size(doc_string)
    doc_string = doc_string.rjust(len(doc_string) + indent)
    return note + doc_string


def _get_indentation_size(doc_string: str) -> int:
    lines = doc_string.expandtabs().splitlines()
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    return indent if indent < sys.maxsize else DOCSTRING_DEFAULT_INDENTATION


def _should_skip_warning() -> bool:
    return os.getenv(DISABLE_EXPERIMENTAL_WARNING_ENV_VAR, "false").lower() == "true"


def _is_warning_cached(cache_key: str) -> bool:
    if cache_key in _warning_cache:
        return True
    _warning_cache.add(cache_key)
    return False
