# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Initialize retained legacy requests and clean up failed construction.

Legacy-only request builders initialize account state before preparing headers.
Rust operations do not use those builders.

For example, a client can store its Python adapter before a later setting
check raises. unwind_client_construction asks that adapter to mark itself
closed and clear its runtime and credential references. Rust-client construction
does not acquire a driver handle or an async credential bridge. Both client
constructors are synchronous, so this cleanup does not await normal close.

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
    """Prepare legacy state before a legacy-only request builder runs.

    :param operation: Connection method that requires initialized account state.
    :type operation: typing.Callable
    :return: Wrapped method that runs setup before forwarding its arguments.
    :rtype: typing.Callable
    """
    @wraps(operation)
    def invoke(self: Any, /, *args: _P.args, **kwargs: _P.kwargs) -> _T:
        self._setup()  # pylint: disable=protected-access
        return operation(self, *args, **kwargs)
    return invoke


def initialize_async_legacy_connection(
    operation: Callable[Concatenate[Any, _P], Awaitable[_T]],
) -> Callable[Concatenate[Any, _P], Awaitable[_T]]:
    """Await legacy setup before preparing a legacy-only request.

    :param operation: Async connection method that requires initialized account state.
    :type operation: typing.Callable
    :return: Wrapped async method that awaits setup before forwarding its arguments.
    :rtype: typing.Callable
    """
    @wraps(operation)
    async def invoke(self: Any, /, *args: _P.args, **kwargs: _P.kwargs) -> _T:
        await self._setup()  # pylint: disable=protected-access
        return await operation(self, *args, **kwargs)
    return invoke


def _cleanup(action: Callable[[], Any]) -> None:
    """Run one cleanup action, logging an Exception rather than raising it.

    :param action: Resource-release callback invoked after a startup failure.
    :type action: typing.Callable
    """
    try:
        action()
    # Cleanup must not replace the original startup exception.
    except Exception:  # pylint: disable=broad-exception-caught
        _LOGGER.warning("Failed to release resources after client startup failure", exc_info=True)


def unwind_client_construction(
    constructor: Callable[Concatenate[Any, _P], None],
) -> Callable[Concatenate[Any, _P], None]:
    """Ask an already stored Python adapter to clean up failed client construction.

    Call its abort_construction method, if present, before re-raising the
    startup error. The Rust adapters clear their runtime and credential
    references without closing the customer app's credential.

    :param constructor: Client initializer whose partially created adapter may need cleanup.
    :type constructor: typing.Callable
    :return: Initializer that aborts adapter construction before re-raising startup errors.
    :rtype: typing.Callable
    """
    @wraps(constructor)
    def initialize(self: Any, /, *args: _P.args, **kwargs: _P.kwargs) -> None:
        try:
            constructor(self, *args, **kwargs)
        except BaseException:
            adapter = vars(self).get("_adapter")
            abort = getattr(adapter, "abort_construction", None)
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

    :param constructor: Connection initializer whose partially created resources may need cleanup.
    :type constructor: typing.Callable
    :return: Initializer that releases stored resources before re-raising startup errors.
    :rtype: typing.Callable
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
