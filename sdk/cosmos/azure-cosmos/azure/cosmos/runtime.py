# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Explicitly configure and share the Rust driver's connection resources."""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._rust import _CosmosRuntime


@dataclass(frozen=True, kw_only=True)
class ConnectionPoolOptions:
    """Immutable connection settings for :class:`CosmosRuntime`.

    Durations are seconds. ``None`` uses the Rust driver's environment/default
    value. Without overrides, connection, data HTTP-request, and metadata
    HTTP-request timeouts are respectively 5, 6, and 65 seconds.
    HTTP-request timeouts cover one attempt, not retries or read inactivity.

    :keyword float connection_timeout: Connection establishment limit (0.1-6 seconds).
    :keyword float data_http_request_timeout: Complete data HTTP-attempt limit,
        at least 0.1 seconds.
    :keyword float metadata_http_request_timeout: Complete metadata HTTP-attempt limit,
        between 0.1 and 65 seconds.
    :keyword float idle_connection_timeout: Time to retain an idle connection,
        at least 300 seconds.
    :keyword int max_idle_connections_per_endpoint: Idle connections retained per endpoint,
        between 10 and 64000.
    :keyword bool proxy_allowed: Whether the driver may use the environment proxy.
    """

    connection_timeout: Optional[float] = None
    data_http_request_timeout: Optional[float] = None
    metadata_http_request_timeout: Optional[float] = None
    idle_connection_timeout: Optional[float] = None
    max_idle_connections_per_endpoint: Optional[int] = None
    proxy_allowed: Optional[bool] = None

    # APIView needs constructor source to distinguish keyword-only parameters.
    def __init__(
        self,
        *,
        connection_timeout: Optional[float] = None,
        data_http_request_timeout: Optional[float] = None,
        metadata_http_request_timeout: Optional[float] = None,
        idle_connection_timeout: Optional[float] = None,
        max_idle_connections_per_endpoint: Optional[int] = None,
        proxy_allowed: Optional[bool] = None,
    ) -> None:
        object.__setattr__(self, "connection_timeout", connection_timeout)
        object.__setattr__(self, "data_http_request_timeout", data_http_request_timeout)
        object.__setattr__(self, "metadata_http_request_timeout", metadata_http_request_timeout)
        object.__setattr__(self, "idle_connection_timeout", idle_connection_timeout)
        object.__setattr__(self, "max_idle_connections_per_endpoint", max_idle_connections_per_endpoint)
        object.__setattr__(self, "proxy_allowed", proxy_allowed)
        self.__post_init__()

    def __post_init__(self) -> None:
        for name, minimum, maximum in (
            ("connection_timeout", 0.1, 6),
            ("data_http_request_timeout", 0.1, 2**64),
            ("metadata_http_request_timeout", 0.1, 65),
            ("idle_connection_timeout", 300, 2**64),
        ):
            value = getattr(self, name)
            if value is None:
                continue
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(f"{name} must be a number of seconds or None.")
            if value < minimum or value > maximum or value >= 2**64 or not math.isfinite(value):
                raise ValueError(
                    f"{name} must be finite seconds in the supported range {minimum}-{maximum}."
                )
        count = self.max_idle_connections_per_endpoint
        if count is not None:
            if isinstance(count, bool) or not isinstance(count, int):
                raise TypeError("max_idle_connections_per_endpoint must be an integer or None.")
            if not 10 <= count <= 64000:
                raise ValueError("max_idle_connections_per_endpoint must be between 10 and 64000.")
        if self.proxy_allowed is not None and not isinstance(self.proxy_allowed, bool):
            raise TypeError("proxy_allowed must be a bool or None.")


@dataclass(frozen=True, init=False, eq=False)
class CosmosRuntime:
    """An initialized runtime explicitly shared by synchronous or async clients.

    Use :meth:`create` or :meth:`create_async`; direct construction is not
    supported. Pass the result as ``CosmosClient(..., runtime=runtime)``.
    Omitting that client option uses the default process-wide singleton.

    Clients retain the runtime independently of the customer's reference.
    There is no runtime ``close()``: releasing one client does not shut down
    other clients, and native ownership keeps in-flight operations alive.
    """

    _handle: _CosmosRuntime = field(repr=False, compare=False)
    connection_pool: ConnectionPoolOptions

    def __init__(self) -> None:
        raise TypeError("Use CosmosRuntime.create() or await CosmosRuntime.create_async().")

    @staticmethod
    def _options(connection_pool: Optional[ConnectionPoolOptions]) -> ConnectionPoolOptions:
        if connection_pool is None:
            return ConnectionPoolOptions()
        if not isinstance(connection_pool, ConnectionPoolOptions):
            raise TypeError("connection_pool must be ConnectionPoolOptions or None.")
        return connection_pool

    @classmethod
    def _from_handle(cls, handle: _CosmosRuntime, options: ConnectionPoolOptions) -> CosmosRuntime:
        result = object.__new__(cls)
        object.__setattr__(result, "_handle", handle)
        object.__setattr__(result, "connection_pool", options)
        return result

    @classmethod
    def create(cls, *, connection_pool: Optional[ConnectionPoolOptions] = None) -> CosmosRuntime:
        """Build a custom runtime synchronously, raising if initialization fails.

        :keyword connection_pool: Immutable connection settings, or driver defaults.
        :paramtype connection_pool: ~azure.cosmos.ConnectionPoolOptions
        :returns: A new initialized runtime, not the default singleton.
        :rtype: ~azure.cosmos.CosmosRuntime
        """
        from ._rust import _create_runtime  # pylint: disable=import-outside-toplevel

        options = cls._options(connection_pool)
        return cls._from_handle(_create_runtime(options), options)

    @classmethod
    async def create_async(
        cls, *, connection_pool: Optional[ConnectionPoolOptions] = None
    ) -> CosmosRuntime:
        """Build a custom runtime without blocking the Python event loop.

        :keyword connection_pool: Immutable connection settings, or driver defaults.
        :paramtype connection_pool: ~azure.cosmos.ConnectionPoolOptions
        :returns: A new initialized runtime, usable by sync or async clients.
        :rtype: ~azure.cosmos.CosmosRuntime
        """
        from ._rust import _create_runtime_async  # pylint: disable=import-outside-toplevel

        options = cls._options(connection_pool)
        return cls._from_handle(await _create_runtime_async(options), options)
