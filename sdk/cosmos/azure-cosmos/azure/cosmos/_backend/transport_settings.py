# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Validate runtime selection and connection-timeout placement.

Rust clients select an explicit CosmosRuntime or the default singleton.
Network overrides belong to its ConnectionPoolOptions, not client keywords.
The connection timeout resolver below remains for explicitly selected legacy
clients. Removed options are rejected at the common client boundary.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..documents import ConnectionPolicy
from ..runtime import CosmosRuntime


def validate_client_runtime_settings(kwargs: Mapping[str, Any]) -> None:
    """Keep network settings on explicit runtimes; never reconfigure the default."""
    runtime = kwargs.get("runtime")
    if runtime is not None and not isinstance(runtime, CosmosRuntime):
        raise TypeError("runtime must be a CosmosRuntime created with create() or create_async().")
    for name in (
        "connection_timeout", "request_timeout", "proxy_allowed",
        "data_http_request_timeout", "metadata_http_request_timeout",
        "idle_connection_timeout", "max_idle_connections_per_endpoint",
    ):
        if name in kwargs:
            if name == "request_timeout":
                raise TypeError(
                    "request_timeout is a legacy connection-timeout alias measured in milliseconds. "
                    "Use ConnectionPoolOptions(connection_timeout=value / 1000) to convert its "
                    "value to seconds, create a runtime with CosmosRuntime.create()/create_async(), "
                    "then pass runtime= to CosmosClient."
                )
            raise TypeError(
                f"Configure {name} through ConnectionPoolOptions and "
                "CosmosRuntime.create()/create_async(), then pass runtime= to CosmosClient."
            )
    policy = kwargs.get("connection_policy")
    if policy is not None:
        stock = ConnectionPolicy()
        if policy.RequestTimeout != stock.RequestTimeout:
            raise TypeError(
                "Move connection_policy.RequestTimeout to ConnectionPoolOptions.connection_timeout "
                "in seconds, and pass an explicitly created runtime to CosmosClient."
            )
    timeout = kwargs.get("timeout")
    if timeout is not None:
        from .._helpers._request_settings import is_supported_operation_timeout  # pylint: disable=import-outside-toplevel

        if not is_supported_operation_timeout(timeout):
            raise ValueError("timeout must be finite, non-boolean seconds >= 1 and < 2**64.")

def resolve_client_connection_timeout(kwargs: Mapping[str, Any]) -> Any:
    """Return requested connection seconds without changing kwargs.

    request_timeout is the older connection-timeout name, measured in
    milliseconds, and takes precedence over connection_timeout. A
    connection_policy contributes only values differing from a fresh default
    policy; otherwise return None for that setting.

    Rust client validation rejects explicit overrides before this resolver.
    Reading the remaining default policy does not configure a Rust runtime.
    """
    stock_policy = ConnectionPolicy()
    policy = kwargs.get("connection_policy") or stock_policy
    if "request_timeout" in kwargs:
        connection_timeout = kwargs["request_timeout"] / 1000.0
    elif "connection_timeout" in kwargs:
        connection_timeout = kwargs["connection_timeout"]
    elif policy.RequestTimeout != stock_policy.RequestTimeout:
        connection_timeout = policy.RequestTimeout
    else:
        connection_timeout = None
    return connection_timeout
