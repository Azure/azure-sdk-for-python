# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Initialize retained legacy requests and clean up failed construction.

Legacy-only request builders initialize account state before preparing headers.
Rust operations do not use those builders.

For example, a client can retain an async credential bridge before a later
startup check raises. unwind_client_construction asks the Python backend to
release that resource. It also works for the async client because its
constructor is synchronous; it does not await the client's normal close method.

unwind_connection_construction handles the synchronous legacy connection's
routing-map provider and pipeline client instead. Neither decorator creates
resources just to clean them up.
"""
import logging
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar
from typing_extensions import Concatenate, ParamSpec

_LOGGER = logging.getLogger(__name__)
_P = ParamSpec("_P")
_T = TypeVar("_T")


def initialize_legacy_connection(
    operation: Callable[Concatenate[Any, _P], _T],
) -> Callable[Concatenate[Any, _P], _T]:
    """Prepare legacy state before a legacy-only request builder runs."""
    @wraps(operation)
    def invoke(self: Any, /, *args: _P.args, **kwargs: _P.kwargs) -> _T:
        self._setup()
        return operation(self, *args, **kwargs)
    return invoke


def initialize_async_legacy_connection(
    operation: Callable[Concatenate[Any, _P], Awaitable[_T]],
) -> Callable[Concatenate[Any, _P], Awaitable[_T]]:
    """Await legacy setup before preparing a legacy-only request."""
    @wraps(operation)
    async def invoke(self: Any, /, *args: _P.args, **kwargs: _P.kwargs) -> _T:
        await self._setup()
        return await operation(self, *args, **kwargs)
    return invoke


def _cleanup(action: Callable[[], Any]) -> None:
    """Run one cleanup action, logging an Exception rather than raising it."""
    try:
        action()
    except Exception:  # Cleanup must not replace the original startup exception.
        _LOGGER.warning("Failed to release resources after client startup failure", exc_info=True)


def unwind_client_construction(
    constructor: Callable[Concatenate[Any, _P], None],
) -> Callable[Concatenate[Any, _P], None]:
    """Ask an already stored Python backend to clean up failed client construction.

    If it provides abort_construction, call that method before re-raising the
    startup error. The Rust Python backends release their async credential
    bridge use, not the customer app's credential.
    """
    @wraps(constructor)
    def initialize(self: Any, /, *args: _P.args, **kwargs: _P.kwargs) -> None:
        try:
            constructor(self, *args, **kwargs)
        except BaseException:
            backend = vars(self).get("_backend")
            abort = getattr(backend, "abort_construction", None)
            if callable(abort):
                _cleanup(abort)
            raise
    return initialize


def unwind_connection_construction(
    constructor: Callable[Concatenate[Any, _P], None],
) -> Callable[Concatenate[Any, _P], None]:
    """Release the legacy connection's resources if its constructor raises.

    Only inspect fields already stored on the connection. For example, if
    pipeline_client was never assigned, there is no pipeline client to close.
    """
    @wraps(constructor)
    def initialize(self: Any, /, *args: _P.args, **kwargs: _P.kwargs) -> None:
        try:
            constructor(self, *args, **kwargs)
        except BaseException:
            for name, method in (("_routing_map_provider", "release"), ("pipeline_client", "close")):
                resource = vars(self).get(name)
                if resource is not None:
                    _cleanup(getattr(resource, method))
            raise
    return initialize
