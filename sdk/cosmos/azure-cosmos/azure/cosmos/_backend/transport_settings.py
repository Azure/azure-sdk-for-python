# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Validate network settings in the Python wrapper before calling the binding.

The Rust driver manages its own connections and certificate checks. It cannot
use the custom Python network objects rejected here. Raise at client
construction rather than let the customer believe an ignored proxy or
certificate setting is active.

Both public constructors combine connection_policy settings with keyword
overrides before this check, so nesting an option does not bypass validation.

Connection and read timeouts pass through the binding to CosmosDriverRuntime.
Keep None for an unspecified value instead of treating a Python default as a
customer request. Construction checks completed CosmosDriverRuntime
initialization without creating that object or reserving values.
Driver acquisition checks again and initializes CosmosDriverRuntime if needed.

Here, read_timeout limits the complete HTTP attempt, not just
time spent waiting for more response data.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Tuple

from ..documents import ConnectionPolicy

def reject_unsupported_transport_settings(
    *,
    proxy_config: Any = None,
    proxies: Any = None,
    connection_verify: Any = None,
    connection_cert: Any = None,
    ssl_config: Any = None,
    transport: Any = None,
) -> None:
    """Raise ValueError for the unsupported network settings checked below.

    Reject custom proxy objects, trusted-certificate files, client certificates,
    disabled certificate verification, and replacement Python request senders.
    For example, connection_verify="company-certs.pem" must not be accepted if
    Rust will not use that file.

    Default verification (True or None) is allowed. An empty proxies dictionary
    supplies no custom proxy configuration; it does not disable environment
    proxies. The separate proxy_allowed setting controls that permission.
    Other listed settings are rejected when non-None.
    """
    def _fail(setting: str, detail: str) -> None:
        """Name the unsupported setting and why it cannot be used."""
        raise ValueError(
            "The Rust binding cannot honor {setting}= yet: {detail}. "
            "This network/TLS configuration is not supported by this build.".format(
                setting=setting, detail=detail
            )
        )

    if proxy_config is not None:
        _fail("proxy_config", "the Rust driver has no explicit proxy-config object hook")
    if proxies:
        _fail("proxies", "the Rust driver has no explicit proxy-config object hook")
    # Keep default certificate checks; reject disabling them or supplying a file.
    if connection_verify is False:
        _fail(
            "connection_verify",
            "disabling TLS verification is not supported on the Rust path",
        )
    if isinstance(connection_verify, str):
        _fail(
            "connection_verify",
            "a custom CA bundle path is not supported on the Rust path",
        )
    if connection_cert is not None:
        _fail(
            "connection_cert",
            "presenting a client certificate is not supported on the Rust path",
        )
    if ssl_config is not None:
        _fail("ssl_config", "custom SSL configuration is not supported on the Rust path")
    if transport is not None:
        _fail(
            "transport",
            "a custom/stand-in transport is not supported on the Rust path",
        )


def resolve_client_transport_timeouts(kwargs: Mapping[str, Any]) -> Tuple[Any, Any]:
    """Return requested connection/read seconds without changing kwargs.

    request_timeout is the older connection-timeout name, measured in
    milliseconds, and takes precedence over connection_timeout. A
    connection_policy contributes only values differing from a fresh default
    policy; otherwise return None for that setting.

    This function reads values only. The binding later checks them against
    the recorded CosmosDriverRuntime settings; reading them does not reserve them.
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
    if "read_timeout" in kwargs:
        read_timeout = kwargs["read_timeout"]
    elif policy.ReadTimeout != stock_policy.ReadTimeout:
        read_timeout = policy.ReadTimeout
    else:
        read_timeout = None
    return connection_timeout, read_timeout
