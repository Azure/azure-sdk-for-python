# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Regeneration-safe compatibility for earlier operation keyword arguments."""

from copy import copy
from functools import wraps
from inspect import iscoroutinefunction
from typing import Any


def _prepare_call(operation: Any, aliases: dict[str, str], kwargs: dict[str, Any]) -> Any:
    for old, new in aliases.items():
        if old in kwargs:
            if new in kwargs:
                raise TypeError(f"Pass either {old!r} or {new!r}, not both.")
            kwargs[new] = kwargs.pop(old)

    # Earlier previews accepted api_version per operation. The generator now
    # reads it from the client configuration. A private shallow copy avoids
    # leaking that kwarg to the HTTP transport or mutating a shared client.
    if "api_version" in kwargs:
        operation = copy(operation)
        operation._config = copy(operation._config)
        operation._config.api_version = kwargs.pop("api_version")
    return operation


def patch_operation_keywords(operation_type: type, aliases: dict[str, dict[str, str]]) -> None:
    """Preserve legacy keywords without modifying emitted operation methods."""
    for name, method in list(vars(operation_type).items()):
        if name.startswith("_") or not callable(method) or getattr(method, "_legacy_keywords", False):
            continue
        method_aliases = aliases.get(name, {})

        def wrap_sync(original: Any, keyword_aliases: dict[str, str]) -> Any:
            @wraps(original)
            def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
                operation = _prepare_call(self, keyword_aliases, kwargs)
                return original(operation, *args, **kwargs)

            return wrapped

        def wrap_async(original: Any, keyword_aliases: dict[str, str]) -> Any:
            @wraps(original)
            async def wrapped(self: Any, *args: Any, **kwargs: Any) -> Any:
                operation = _prepare_call(self, keyword_aliases, kwargs)
                return await original(operation, *args, **kwargs)

            return wrapped

        wrapper = wrap_async if iscoroutinefunction(method) else wrap_sync
        patched = wrapper(method, method_aliases)
        patched._legacy_keywords = True
        setattr(operation_type, name, patched)
