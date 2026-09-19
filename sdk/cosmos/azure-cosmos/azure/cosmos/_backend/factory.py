# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Temporary migration selection and shared sync/async construction.

``_backend``, ``COSMOS_BACKEND`` and ``COSMOS_RUST_STRICT_ISOLATION`` are
internal migration/test controls, not supported customer switches. LR-09 in
LEGACY_CODE_RETIREMENT.md owns their removal before the Rust-only release.

Selection precedence is explicit keyword, environment, then core-python.
Both factories use ``_make_backend`` to preserve validation order and credential
ownership. Rust selection creates a ``RustBinding`` or ``AsyncRustBinding``;
native driver acquisition remains lazy.
"""
from __future__ import annotations

import os
from typing import Any, Callable, Optional, Sequence, TypeVar

from .cosmos_backend import CosmosBackend
from .client_config import build_client_config
from .constants import (
    BACKEND_ENV_VAR,
    BACKEND_NAME_RUST,
    DEFAULT_BACKEND_NAME,
    RUST_STRICT_ISOLATION_ENV_VAR,
    STRICT_ISOLATION_FALSE_VALUES,
    STRICT_ISOLATION_TRUE_VALUES,
    VALID_BACKEND_NAMES,
)
from .credentials import resolved_credential
from .legacy import LEGACY_BACKEND
from .binding import RustBinding
from .transport_settings import reject_unsupported_transport_settings

_BackendT = TypeVar("_BackendT")

def resolve_backend_name(explicit: Optional[str]) -> str:
    """Select the backend name from the ``_backend=`` argument, else the
    ``COSMOS_BACKEND`` environment variable, else the ``core-python`` default,
    and return a name in ``VALID_BACKEND_NAMES``.

    Without it: a stray trailing newline or ``"RUST"`` in caps from a
    copy-pasted env var would be treated as a typo and rejected; and a real typo
    would silently fall back to the wrong backend instead of telling the customer.
    So surrounding whitespace and case are tolerated (``RUST``, `` rust`` all
    work), an empty or whitespace-only value counts as "not specified" and uses
    ``DEFAULT_BACKEND_NAME``, but a non-empty value that is not a known backend
    (a genuine typo) raises ``ValueError`` loudly. There are no aliases: one
    canonical spelling per backend.

    Shared between the sync and async factories so the rules, valid
    values, and error message live in one place.
    """
    raw = explicit if explicit is not None else os.environ.get(BACKEND_ENV_VAR)
    if raw is not None and not isinstance(raw, str):
        # The env var is always a string; only the constructor kwarg can be a
        # non-string. Raise the same clear ValueError the typo path raises, rather
        # than letting .strip() throw an opaque AttributeError.
        raise ValueError(
            "Invalid backend {!r}. Expected one of {} as a string. "
            "Set the constructor kwarg _backend=, or the {} environment variable.".format(
                raw, VALID_BACKEND_NAMES, BACKEND_ENV_VAR
            )
        )
    choice = raw.strip().lower() if raw is not None else ""
    if not choice:
        return DEFAULT_BACKEND_NAME
    if choice not in VALID_BACKEND_NAMES:
        raise ValueError(
            "Invalid backend {!r}. Expected one of {}. "
            "Set the constructor kwarg _backend=, or the {} environment variable.".format(
                raw, VALID_BACKEND_NAMES, BACKEND_ENV_VAR
            )
        )
    return choice


def resolve_strict_isolation(explicit: Optional[bool]) -> bool:
    """Read an on/off safety switch that controls whether the Rust backend uses
    strict per-account driver isolation.

    Precedence (highest wins): an explicit factory toggle, then the
    ``COSMOS_RUST_STRICT_ISOLATION`` environment variable, then off. Without it:
    an unrecognized value like ``"treu"`` would quietly leave the safety switch
    off, which is exactly the outcome a safety switch must never have -- so it
    raises instead. The env var is matched case-insensitively after trimming
    whitespace: ``STRICT_ISOLATION_TRUE_VALUES`` turn it on,
    ``STRICT_ISOLATION_FALSE_VALUES`` (and unset or empty) turn it off, and any
    other value raises ``ValueError``. Shared by the sync and async factories so
    the rule lives in one place.

    When on, a second ``CosmosClient`` to an account whose config differs from the
    first live client's raises
    :class:`~azure.cosmos._backend._driver_registry._StrictDriverIsolationError` at
    construction instead of silently building a second isolated driver.
    """
    if explicit is not None:
        if not isinstance(explicit, bool):
            # A safety toggle must never be driven by an ambiguous truthy value
            # (a non-empty string like "false" is truthy and would turn the guard
            # ON). Require a real bool, matching how the env-var path rejects
            # unrecognized values below.
            raise ValueError(
                "strict_isolation must be a bool when provided; got {!r}. A safety "
                "toggle is never driven by an ambiguous truthy value.".format(
                    type(explicit).__name__
                )
            )
        return explicit
    value = os.environ.get(RUST_STRICT_ISOLATION_ENV_VAR)
    if value is None:
        return False
    normalized = value.strip().lower()
    if normalized in STRICT_ISOLATION_TRUE_VALUES:
        return True
    if normalized == "" or normalized in STRICT_ISOLATION_FALSE_VALUES:
        return False
    raise ValueError(
        "Invalid {} value {!r}. Expected one of {} (on) or {} (off), or leave it "
        "unset. A safety toggle is never silently disabled by an unrecognized "
        "value.".format(
            RUST_STRICT_ISOLATION_ENV_VAR,
            value,
            STRICT_ISOLATION_TRUE_VALUES,
            STRICT_ISOLATION_FALSE_VALUES,
        )
    )


def _make_backend(
    explicit: Optional[str],
    *,
    rust_backend_type: Callable[..., _BackendT],
    legacy_backend: _BackendT,
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
    strict_isolation: Optional[bool] = None,
    proxy_config: Any = None,
    proxies: Any = None,
    connection_verify: Any = None,
    connection_cert: Any = None,
    ssl_config: Any = None,
    transport: Any = None,
) -> _BackendT:
    """Select and construct either backend under the same credential cleanup guard.

    Legacy selection does not validate Rust-only settings. On the Rust path,
    validate the endpoint and transport before resolving credentials, then keep
    their ownership guard active through config validation and construction.
    """
    name = resolve_backend_name(explicit)
    if name == BACKEND_NAME_RUST:
        if not url:
            raise ValueError(
                "The Rust binding requires the account endpoint URL."
            )
        reject_unsupported_transport_settings(
            proxy_config=proxy_config,
            proxies=proxies,
            connection_verify=connection_verify,
            connection_cert=connection_cert,
            ssl_config=ssl_config,
            transport=transport,
        )
        # Sort the credential inside the guard: an async credential becomes a
        # bridge holding a background thread, and everything below can still raise
        # (config validation, process-wide policy conflicts, strict isolation), which
        # would otherwise strand that thread with no owner left to close it.
        with resolved_credential(credential) as (master_key, token_credential):
            return rust_backend_type(
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
                    fault_injection_rules=fault_injection_rules,
                ),
                strict_isolation=resolve_strict_isolation(strict_isolation),
            )
    return legacy_backend


def make_backend(
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
    strict_isolation: Optional[bool] = None,
    proxy_config: Any = None,
    proxies: Any = None,
    connection_verify: Any = None,
    connection_cert: Any = None,
    ssl_config: Any = None,
    transport: Any = None,
) -> CosmosBackend:
    """Build a synchronous backend using the shared selection and startup policy."""
    return _make_backend(
        explicit,
        rust_backend_type=RustBinding,
        legacy_backend=LEGACY_BACKEND,
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
        strict_isolation=strict_isolation,
        proxy_config=proxy_config,
        proxies=proxies,
        connection_verify=connection_verify,
        connection_cert=connection_cert,
        ssl_config=ssl_config,
        transport=transport,
    )