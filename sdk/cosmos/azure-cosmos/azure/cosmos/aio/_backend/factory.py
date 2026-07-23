# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Factory that picks which async backend a single async client will use.

The async counterpart of ``azure.cosmos._backend.factory``. Same terms:
**client** = the ``CosmosClient`` the customer makes; **backend** =
``core-python`` (original all-Python) or ``rust`` (hands work to a rust driver);
**rust driver** = the engine the binding builds (connection pool, request
signing, region routing), one per ``(endpoint, credential, config)`` and shared
across same-settings clients; **binding** = the compiled ``azure.cosmos._rust``
layer Python calls into.

Same precedence and validation as the sync factory (constructor kwarg
> ``COSMOS_BACKEND`` env var > default ``core-python``). The precedence
and validation logic itself is in
``azure.cosmos._backend.factory.resolve_backend_name`` so the sync and
async factories cannot drift apart.

When ``core-python`` is selected the factory returns ``None``; the async
helper treats absence of a backend as the signal to use the legacy
``client_connection.CreateItem`` path.
"""
from __future__ import annotations

from typing import Any, Optional, Sequence

from azure.cosmos._backend.constants import BACKEND_NAME_RUST
from azure.cosmos._backend.factory import (
    _resolve_credential,
    build_client_config,
    reject_unsupported_transport_settings,
    resolve_backend_name,
    resolve_strict_isolation,
)

from .base import AsyncCosmosBackend
from .rust import AsyncRustBackend


def make_async_backend(
    explicit: Optional[str],
    *,
    url: Optional[str] = None,
    credential: Any = None,
    preferred_locations: Optional[Sequence[str]] = None,
    excluded_locations: Optional[Sequence[str]] = None,
    throttling_max_retry_count: Optional[int] = None,
    throttling_max_retry_wait_time_seconds: Optional[float] = None,
    availability_strategy: Any = None,
    user_agent_suffix: Optional[str] = None,
    consistency_level: Optional[str] = None,
    proxy_allowed: Optional[bool] = None,
    connection_timeout_seconds: Optional[float] = None,
    read_timeout_seconds: Optional[float] = None,
    strict_isolation: Optional[bool] = None,
    proxy_config: Any = None,
    proxies: Any = None,
    connection_verify: Any = None,
    connection_cert: Any = None,
    ssl_config: Any = None,
    transport: Any = None,
) -> Optional[AsyncCosmosBackend]:
    """The one public entry point that builds the backend instance an async
    ``CosmosClient`` will hold -- the async twin of :func:`make_backend`.

    Returns an :class:`AsyncRustBackend` when Rust is selected, or ``None`` when
    core-python is selected. If Rust: it requires the endpoint URL, rejects
    unsupported transport settings, sorts the credential, folds the tuning into a
    config, resolves the isolation switch, and hands back the backend. The keyword
    settings are only consulted for the Rust branch, where they are folded into the
    client config (via the shared :func:`build_client_config`) the backend carries
    to the rust driver. ``strict_isolation`` (kwarg > the
    ``COSMOS_RUST_STRICT_ISOLATION`` env var > off) controls whether a second
    client to an account with a different config raises instead of silently getting
    its own isolated rust driver. The transport/TLS settings the Rust path can't
    honor yet are rejected here, exactly as in the sync factory; ``proxy_allowed``
    is the Rust-path proxy switch carried into the driver runtime. All of this
    reuses the sync factory's functions, so the sync and async paths cannot drift.
    """
    name = resolve_backend_name(explicit)
    if name == BACKEND_NAME_RUST:
        if not url:
            raise ValueError(
                "_backend='rust' requires the account endpoint URL."
            )
        reject_unsupported_transport_settings(
            proxy_config=proxy_config,
            proxies=proxies,
            connection_verify=connection_verify,
            connection_cert=connection_cert,
            ssl_config=ssl_config,
            transport=transport,
        )
        master_key, token_credential = _resolve_credential(credential)
        return AsyncRustBackend(
            endpoint=url,
            master_key=master_key,
            token_credential=token_credential,
            client_config=build_client_config(
                preferred_locations,
                excluded_locations=excluded_locations,
                throttling_max_retry_count=throttling_max_retry_count,
                throttling_max_retry_wait_time_seconds=throttling_max_retry_wait_time_seconds,
                availability_strategy=availability_strategy,
                user_agent_suffix=user_agent_suffix,
                consistency_level=consistency_level,
                proxy_allowed=proxy_allowed,
                connection_timeout_seconds=connection_timeout_seconds,
                read_timeout_seconds=read_timeout_seconds,
            ),
            strict_isolation=resolve_strict_isolation(strict_isolation),
        )
    return None
