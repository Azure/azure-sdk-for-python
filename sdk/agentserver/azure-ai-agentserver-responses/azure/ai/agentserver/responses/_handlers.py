# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Handler and context contracts for user-defined response execution."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import inspect
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Mapping, Sequence

from .models._generated import OutputItem
from .models import ResponseModeFlags

OutputItemsLoader = Callable[[], Awaitable[Sequence[OutputItem]]]
RawBodyType = Mapping[str, Any] | Sequence[Any] | str | int | float | bool | None


class ResponseContext:
    """Runtime context exposed to response handlers and used by hosting orchestration.

    This mirrors the referenced .NET ``IResponseContext`` shape:
    - response identifier
    - shutdown signal flag
    - raw body access
    - async input/history resolution
    """

    def __init__(
        self,
        *,
        response_id: str,
        mode_flags: ResponseModeFlags,
        raw_body: RawBodyType = None,
        created_at: datetime | None = None,
    ) -> None:
        self.response_id = response_id
        self.mode_flags = mode_flags
        self.raw_body = raw_body
        self.created_at = created_at if created_at is not None else datetime.now(timezone.utc)
        self._is_shutdown_requested: bool = False
        self._input_items_loader: OutputItemsLoader | None = None
        self._history_loader: OutputItemsLoader | None = None
        self._input_items_cache: Sequence[OutputItem] | None = None
        self._history_cache: Sequence[OutputItem] | None = None

    @property
    def is_shutdown_requested(self) -> bool:
        """Get whether shutdown has been requested by the host.

        :returns: True if shutdown has been requested, False otherwise.
        :rtype: bool
        """
        return self._is_shutdown_requested

    @is_shutdown_requested.setter
    def is_shutdown_requested(self, value: bool) -> None:
        """Set whether shutdown has been requested by the host.

        :param value: Whether shutdown has been requested.
        :type value: bool
        """
        self._is_shutdown_requested = value

    async def get_input_items_async(self) -> Sequence[OutputItem]:
        """Resolve and cache request input items.

        If items have already been loaded, returns the cached result.
        Otherwise, invokes the input items loader and caches the result.

        :returns: A tuple of input items from the request.
        :rtype: Sequence[OutputItem]
        """
        if self._input_items_cache is not None:
            return self._input_items_cache

        if self._input_items_loader is None:
            self._input_items_cache = ()
            return self._input_items_cache

        loaded = await self._input_items_loader()
        self._input_items_cache = tuple(loaded)
        return self._input_items_cache

    async def get_history_async(self) -> Sequence[OutputItem]:
        """Resolve and cache conversation history items.

        If history has already been loaded, returns the cached result.
        Otherwise, invokes the history loader and caches the result.

        :returns: A tuple of conversation history items.
        :rtype: Sequence[OutputItem]
        """
        if self._history_cache is not None:
            return self._history_cache

        if self._history_loader is None:
            self._history_cache = ()
            return self._history_cache

        loaded = await self._history_loader()
        self._history_cache = tuple(loaded)
        return self._history_cache


def response_handler(func: Callable) -> Callable:
    """Register a function as a response handler.

    The decorated function must accept exactly three positional parameters:
    ``(request, context, cancellation_signal)`` and return an
    ``AsyncIterable`` of response stream events.

    Validation is performed at decoration time so configuration errors
    are surfaced immediately when the module is imported.

    :param func: The handler function to register.
    :type func: Callable
    :returns: The same function, marked as a response handler.
    :rtype: Callable
    :raises TypeError: If ``func`` is not callable or does not accept exactly
                        three parameters.
    """
    if not callable(func):
        raise TypeError("@response_handler must be applied to a callable")
    sig = inspect.signature(func)
    params = list(sig.parameters.values())
    if len(params) != 3:
        raise TypeError(
            f"@response_handler: handler must accept exactly 3 parameters "
            f"(request, context, cancellation_signal), got {len(params)}: "
            f"{[p.name for p in params]}"
        )
    func._is_response_handler = True  # type: ignore[attr-defined]
    return func
