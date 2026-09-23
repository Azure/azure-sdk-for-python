# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Construct the asynchronous Python backend using shared preparation rules.

``azure.cosmos._backend.factory._make_backend`` decides which Python backend to
use and checks its startup inputs. It also cleans up the async credential bridge
if construction fails.
This module supplies AsyncRustBackend and the shared AsyncLegacyBackend instance.
Legacy-path selection is a migration control, not a release execution choice.

Construction itself is synchronous: make_async_backend(...) returns a Python
object without acquiring a driver handle. Operations on AsyncRustBackend later
call the binding and await its results.
"""
from __future__ import annotations

from typing import Any, Optional, Sequence

from azure.cosmos._backend.factory import _make_backend

from .cosmos_backend import AsyncCosmosBackend
from .legacy import ASYNC_LEGACY_BACKEND
from .rust_backend import AsyncRustBackend


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
    fault_injection_rules: Any = None,
    proxy_config: Any = None,
    proxies: Any = None,
    connection_verify: Any = None,
    connection_cert: Any = None,
    ssl_config: Any = None,
    transport: Any = None,
) -> AsyncCosmosBackend:
    """Return a Python backend for async operations; this factory is not awaited.

    For example, endpoint and preferred-region inputs become the stored settings
    of AsyncRustBackend. Its construction checks completed CosmosDriverRuntime
    initialization but does not initialize it or reserve its settings.
    """
    return _make_backend(
        explicit,
        rust_backend_type=AsyncRustBackend,
        legacy_backend=ASYNC_LEGACY_BACKEND,
        url=url,
        credential=credential,
        preferred_locations=preferred_locations,
        excluded_locations=excluded_locations,
        throttling_max_retry_count=throttling_max_retry_count,
        throttling_max_retry_wait_time_seconds=throttling_max_retry_wait_time_seconds,
        availability_strategy=availability_strategy,
        user_agent_suffix=user_agent_suffix,
        consistency_level=consistency_level,
        proxy_allowed=proxy_allowed,
        connection_timeout_seconds=connection_timeout_seconds,
        read_timeout_seconds=read_timeout_seconds,
        fault_injection_rules=fault_injection_rules,
        proxy_config=proxy_config,
        proxies=proxies,
        connection_verify=connection_verify,
        connection_cert=connection_cert,
        ssl_config=ssl_config,
        transport=transport,
    )
