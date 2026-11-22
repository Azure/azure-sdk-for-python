# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Validate runtime selection, network-setting placement, and operation timeout.

Rust clients select an explicit CosmosRuntime or the default singleton.
Network overrides belong to its ConnectionPoolOptions, not client keywords.
These checks reject client network overrides and invalid operation timeout
values before backend construction. Legacy connection timeouts are handled
separately by the legacy connection-policy builder.
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
