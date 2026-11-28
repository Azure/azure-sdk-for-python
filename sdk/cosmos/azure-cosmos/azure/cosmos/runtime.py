# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Network connection settings that clients can share: CosmosRuntime and ConnectionPoolOptions."""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._rust import _CosmosRuntime


@dataclass(frozen=True, kw_only=True)
class ConnectionPoolOptions:
    """Connection settings for :class:`CosmosRuntime`. They can't be changed after creation.

    Times are in seconds. A setting left as ``None`` uses its environment
    variable if that is set, and otherwise uses the default. A value set here
    always wins over the environment variable. Environment variables use
    milliseconds and are read when the runtime is created. A bad environment
    variable value raises ValueError.

    Data requests read or write items, or run a stored procedure. All other
    requests, such as reading the account, databases, or containers, are
    metadata requests.

    A request timeout covers one try at sending a request and getting the
    whole response. If the SDK retries, each retry gets its own timeout.

    :keyword float connection_timeout: How long to wait when opening a new
        connection. Between 0.1 and 6 seconds. Default 5.
        Environment variable: AZURE_COSMOS_CONNECTION_POOL_MAX_CONNECT_TIMEOUT_MS.
    :keyword float data_http_request_timeout: How long one try of a data request
        can take. At least 0.1 seconds. Default 6.
        Environment variable: AZURE_COSMOS_CONNECTION_POOL_MAX_DATAPLANE_REQUEST_TIMEOUT_MS.
    :keyword float metadata_http_request_timeout: How long one try of a metadata
        request can take. Between 0.1 and 65 seconds. Default 65.
        Environment variable: AZURE_COSMOS_CONNECTION_POOL_MAX_METADATA_REQUEST_TIMEOUT_MS.
    :keyword float idle_connection_timeout: How long to keep an unused connection
        open. At least 300 seconds. Default 90.
        Environment variable: AZURE_COSMOS_CONNECTION_POOL_IDLE_CONNECTION_TIMEOUT_MS.
    :keyword int max_idle_connections_per_endpoint: The most unused connections
        to keep open for each service address. Between 10 and 64000. Default 1000,
        or 10000 if AZURE_COSMOS_CONNECTION_POOL_IS_HTTP2_ALLOWED is false.
        Environment variable: AZURE_COSMOS_CONNECTION_POOL_MAX_IDLE_CONNECTIONS_PER_ENDPOINT.
    :keyword bool proxy_allowed: Whether the SDK can use a proxy set in the
        environment. Default False.
        Environment variable: AZURE_COSMOS_CONNECTION_POOL_IS_PROXY_ALLOWED.
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
                if maximum == 2**64:
                    message = f"{name} must be a finite number of seconds, at least {minimum}."
                else:
                    message = f"{name} must be a finite number of seconds, between {minimum} and {maximum}."
                raise ValueError(message)
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
    """Holds the network connections and their settings, which several clients can share.

    Create one with :meth:`create` or :meth:`create_async`, then pass it to each
    client, for example ``CosmosClient(url, credential=key, runtime=runtime)``.
    Sync and async clients can both use it. Calling ``CosmosRuntime()`` directly
    raises TypeError.

    If a client is not given a runtime, it uses a default runtime with default
    settings. The default runtime is created the first time such a client
    connects, and all such clients share it.

    A runtime has no close() method. Closing one client does not stop other
    clients that use the same runtime, or operations that are still running.
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

        :keyword connection_pool: Connection settings. If omitted, default settings are used.
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

        :keyword connection_pool: Connection settings. If omitted, default settings are used.
        :paramtype connection_pool: ~azure.cosmos.ConnectionPoolOptions
        :returns: A new initialized runtime, usable by sync or async clients.
        :rtype: ~azure.cosmos.CosmosRuntime
        """
        from ._rust import _create_runtime_async  # pylint: disable=import-outside-toplevel

        options = cls._options(connection_pool)
        return cls._from_handle(await _create_runtime_async(options), options)
