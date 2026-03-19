"""Handler and context contracts for user-defined response execution."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncIterable, Awaitable, Callable, Mapping, Protocol, Sequence, runtime_checkable

from .models._generated import CreateResponse, OutputItem, ResponseStreamEvent
from .models import ResponseModeFlags

OutputItemsLoader = Callable[[], Awaitable[Sequence[OutputItem]]]
RawBodyType = Mapping[str, Any] | Sequence[Any] | str | int | float | bool | None


@runtime_checkable
class ResponseContext(Protocol):
    """Runtime context exposed to response handlers.

    This mirrors the referenced .NET ``IResponseContext`` shape:
    - response identifier
    - shutdown signal flag
    - raw body access
    - async input/history resolution
    """

    @property
    def response_id(self) -> str:
        """Get the unique response identifier."""

    @property
    def is_shutdown_requested(self) -> bool:
        """Get whether shutdown has been requested by the host."""

    @is_shutdown_requested.setter
    def is_shutdown_requested(self, value: bool) -> None:
        """Set whether shutdown has been requested by the host."""

    @property
    def raw_body(self) -> RawBodyType:
        """Get the raw request body payload for extension field access."""

    async def get_input_items_async(self) -> Sequence[OutputItem]:
        """Resolve and return request input items."""

    async def get_history_async(self) -> Sequence[OutputItem]:
        """Resolve and return conversation history items."""


@dataclass(slots=True)
class RuntimeResponseContext:
    """Default runtime context implementation used by hosting orchestration."""

    response_id: str
    mode_flags: ResponseModeFlags
    raw_body: RawBodyType = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _is_shutdown_requested: bool = False
    _input_items_loader: OutputItemsLoader | None = None
    _history_loader: OutputItemsLoader | None = None
    _input_items_cache: Sequence[OutputItem] | None = None
    _history_cache: Sequence[OutputItem] | None = None

    @property
    def is_shutdown_requested(self) -> bool:
        """Get whether shutdown has been requested by the host."""
        return self._is_shutdown_requested

    @is_shutdown_requested.setter
    def is_shutdown_requested(self, value: bool) -> None:
        """Set whether shutdown has been requested by the host."""
        self._is_shutdown_requested = value

    async def get_input_items_async(self) -> Sequence[OutputItem]:
        """Resolve and cache request input items."""
        if self._input_items_cache is not None:
            return self._input_items_cache

        if self._input_items_loader is None:
            self._input_items_cache = ()
            return self._input_items_cache

        loaded = await self._input_items_loader()
        self._input_items_cache = tuple(loaded)
        return self._input_items_cache

    async def get_history_async(self) -> Sequence[OutputItem]:
        """Resolve and cache conversation history items."""
        if self._history_cache is not None:
            return self._history_cache

        if self._history_loader is None:
            self._history_cache = ()
            return self._history_cache

        loaded = await self._history_loader()
        self._history_cache = tuple(loaded)
        return self._history_cache


@runtime_checkable
class ResponseHandler(Protocol):
    """Primary async handler contract consumed by route orchestration.

    Mirrors the referenced .NET ``IResponseHandler`` single-method design.
    """

    def create_async(
        self,
        request: CreateResponse,
        context: ResponseContext,
        cancellation_signal: asyncio.Event,
    ) -> AsyncIterable[ResponseStreamEvent]:
        """Yield the full response event stream for one create request."""
