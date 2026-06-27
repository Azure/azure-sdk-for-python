# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Factory that picks which backend a single client will use.

``CosmosClient`` calls ``make_backend(...)`` exactly once at
construction time and stores the returned object.

Selection precedence (highest wins):

1. ``_backend=`` kwarg passed to the client constructor.
2. ``COSMOS_BACKEND`` environment variable.
3. Default: ``core-python``.

An invalid value raises ``ValueError`` at construction time.

When ``rust`` is selected the factory needs the account endpoint and either a
master-key credential or a token credential (Entra/AAD via ``azure-identity``).
Both synchronous and asynchronous token credentials are accepted: an async
credential is wrapped in an :class:`AsyncTokenCredentialBridge` so the driver's
synchronous ``get_token`` can drive it (see ``_async_credential_bridge``).
Resource-token auth (per-user / permission credentials) is still rejected
upfront -- the Rust driver has no resource-token auth branch yet.

When ``core-python`` is selected the factory returns ``None``; the
helper layer treats absence-of-backend as the signal to use the legacy
``client_connection.CreateItem`` path.
"""
from __future__ import annotations

import asyncio
import inspect
import os
from collections.abc import Iterable, Mapping
from typing import Any, Optional, Sequence, Tuple

from .._availability_strategy_config import CrossRegionHedgingStrategy, DEFAULT_THRESHOLD_MS
from ..documents import ConsistencyLevel
from ._async_credential_bridge import AsyncTokenCredentialBridge
from .base import CosmosBackend, PreparedClientConfig
from .constants import (
    BACKEND_ENV_VAR,
    BACKEND_NAME_RUST,
    DEFAULT_BACKEND_NAME,
    RUST_STRICT_ISOLATION_ENV_VAR,
    STRICT_ISOLATION_TRUE_VALUES,
    VALID_BACKEND_NAMES,
)
from .rust import RustBackend


# Consistency levels the Rust path can carry today. They map to the driver's
# ``ReadConsistencyStrategy`` in the binding (``"Eventual"`` / ``"Session"``
# directly, ``"Strong"`` to the driver's ``GlobalStrong``). Bounded Staleness and
# Consistent Prefix have no driver equivalent yet, so they are rejected (see
# ``_resolve_consistency_level``) rather than silently dropped.
_RUST_SUPPORTED_CONSISTENCY_LEVELS = (
    ConsistencyLevel.Eventual,
    ConsistencyLevel.Session,
    ConsistencyLevel.Strong,
)

# Every consistency level the public API recognizes, used to tell an out-of-scope
# (but valid) level apart from an outright-unknown string in the error messages.
_ALL_CONSISTENCY_LEVELS = (
    ConsistencyLevel.Strong,
    ConsistencyLevel.BoundedStaleness,
    ConsistencyLevel.Session,
    ConsistencyLevel.Eventual,
    ConsistencyLevel.ConsistentPrefix,
)


def resolve_backend_name(explicit: Optional[str]) -> str:
    """Apply the precedence rules above and return a name in ``VALID_BACKEND_NAMES``.

    Shared between the sync and async factories so the rules, valid
    values, and error message live in one place.
    """
    if explicit is not None:
        choice = explicit
    else:
        choice = os.environ.get(BACKEND_ENV_VAR, DEFAULT_BACKEND_NAME)
    if choice not in VALID_BACKEND_NAMES:
        raise ValueError(
            "Invalid backend {!r}. Expected one of {}. "
            "Set the constructor kwarg _backend=, or the {} environment variable.".format(
                choice, VALID_BACKEND_NAMES, BACKEND_ENV_VAR
            )
        )
    return choice


def resolve_strict_isolation(explicit: Optional[bool]) -> bool:
    """Decide whether the Rust backend uses strict per-account engine isolation.

    Precedence (highest wins): an explicit factory toggle, then the
    ``COSMOS_RUST_STRICT_ISOLATION`` environment variable, then off. The env var is
    truthy only for the values in ``STRICT_ISOLATION_TRUE_VALUES`` (case-insensitive);
    anything else -- including unset and the empty string -- is off. Shared by the
    sync and async factories so the rule lives in one place.

    When on, a second ``CosmosClient`` to an account whose config differs from the
    first live client's raises
    :class:`~azure.cosmos._backend._driver_registry.StrictEngineIsolationError` at
    construction instead of silently building a second isolated engine.
    """
    if explicit is not None:
        return explicit
    value = os.environ.get(RUST_STRICT_ISOLATION_ENV_VAR)
    if value is None:
        return False
    return value.strip().lower() in STRICT_ISOLATION_TRUE_VALUES


def _is_async_credential(credential: Any) -> bool:
    """True when ``credential`` authenticates asynchronously: its ``get_token`` or
    ``get_token_info`` is a coroutine, or it is an ``azure.identity.aio``-style
    async context manager.

    The binding calls ``get_token`` synchronously on a driver worker thread that
    has no event loop, so an async credential can't run there directly. When this
    returns ``True`` the factory wraps the credential in an
    :class:`AsyncTokenCredentialBridge`, which supplies that event loop, instead
    of calling it directly. The token method is unwrapped first in case it is
    decorated.
    """
    for attr in ("get_token", "get_token_info"):
        method = getattr(credential, attr, None)
        if method is None:
            continue
        if asyncio.iscoroutinefunction(method) or inspect.iscoroutinefunction(method):
            return True
        unwrapped = inspect.unwrap(method) if callable(method) else method
        if asyncio.iscoroutinefunction(unwrapped) or inspect.iscoroutinefunction(unwrapped):
            return True
    # Async-only credentials are async context managers; treat that as async even
    # if the token-method check above did not catch it.
    if hasattr(credential, "__aenter__") and (
        hasattr(credential, "get_token") or hasattr(credential, "get_token_info")
    ):
        return True
    return False


def _is_resource_token_credential(credential: Any) -> bool:
    """True when ``credential`` is a resource-token or permission credential rather
    than a master key or a token credential.

    These take the shape of a mapping of resource link to token (without a
    ``masterKey`` entry, which is handled earlier), a mapping with
    ``resourceTokens`` / ``permissionFeed`` keys, or an iterable of permission
    entries. The Rust driver has no resource-token auth yet, so the factory
    rejects them at construction instead of failing on the first request.
    """
    if isinstance(credential, str):
        return False
    if isinstance(credential, Mapping):
        # A master-key dict is resolved as a master key before this is reached;
        # any other mapping shape is resource/permission tokens.
        return "masterKey" not in credential
    # A non-string iterable of permission entries is a permission feed.
    return isinstance(credential, Iterable)


def _resolve_credential(credential: Any) -> Tuple[Optional[str], Optional[Any]]:
    """Classify the credential for the Rust backend into either a master key or a
    synchronous token credential, or raise ``ValueError``.

    Returns ``(master_key, token_credential)`` with exactly one entry set:

    * a ``str`` or a dict with a ``'masterKey'`` entry -> master key;
    * an object with a synchronous ``get_token`` (e.g. an ``azure-identity``
      credential) -> token credential, forwarded to the driver, which calls
      ``get_token`` during request signing;
    * an *async* token credential (coroutine ``get_token`` / ``get_token_info``,
      or the ``azure.identity.aio`` async-context-manager shape) is wrapped in an
      :class:`AsyncTokenCredentialBridge`, which drives its coroutine on a
      dedicated event-loop thread and presents the synchronous ``get_token`` the
      driver calls during request signing -- so async credentials work on the
      Rust path with no driver change;
    * a resource-token / permission-feed credential (per-user scoped tokens) is
      rejected: the Rust driver has no resource-token auth support yet;
    * anything else (``None`` and unrecognized shapes) is rejected.

    Rejecting upfront -- at client construction -- means an unsupported auth
    shape fails loudly and immediately rather than on the first request.
    """
    if isinstance(credential, str):
        return credential, None
    if isinstance(credential, Mapping) and "masterKey" in credential:
        return credential["masterKey"], None
    # Check async *before* the sync get_token acceptance, since an async
    # credential also exposes a (coroutine) get_token. Wrap it rather than reject
    # it: the bridge drives the coroutine on its own event-loop thread and exposes
    # the synchronous get_token the driver calls, so async credentials work with no
    # driver change.
    if _is_async_credential(credential):
        return None, AsyncTokenCredentialBridge(credential)
    get_token = getattr(credential, "get_token", None)
    if callable(get_token):
        return None, credential
    if _is_resource_token_credential(credential):
        raise ValueError(
            "_backend='rust' does not support resource-token (per-user / "
            "permission) credentials yet -- that needs Rust-driver auth support "
            "that isn't available. Use a master-key credential or a synchronous "
            "token credential, or the core-python backend."
        )
    # Falls through for None and any other unrecognized shape.
    raise ValueError(
        "_backend='rust' requires a master-key credential (a string, or a dict "
        "with a 'masterKey' entry) or a synchronous token credential. The Rust "
        "backend does not support resource-token auth."
    )


# Transport / TLS knobs the legacy pipeline honors but the Rust driver cannot yet
# -- it owns its own HTTP stack. Each maps to a constructor kwarg the legacy path
# consumes (``proxy_config`` / ``ssl_config`` via ``_build_connection_policy``;
# ``proxies`` / ``transport`` via the connection; ``connection_verify`` /
# ``connection_cert`` for TLS). On the Rust path they are rejected at construction
# rather than silently ignored and left to fail later with opaque certificate or
# connection errors far from the call site.
def reject_unsupported_transport_settings(
    *,
    proxy_config: Any = None,
    proxies: Any = None,
    connection_verify: Any = None,
    connection_cert: Any = None,
    ssl_config: Any = None,
    transport: Any = None,
) -> None:
    """Raise ``ValueError`` if any transport/TLS setting the Rust path can't honor
    was passed; do nothing when none were (the common case).

    Defaults must *not* trip: ``connection_verify`` defaults to ``True``/absent
    (ordinary verification, which the driver already does) and only a custom CA
    bundle path (a ``str``) or an explicit ``False`` (disable verification) is
    unsupported; an empty ``proxies`` dict is "no proxy". Every other knob trips
    when it is present (non-``None``).
    """
    def _fail(setting: str, detail: str) -> None:
        raise ValueError(
            "_backend='rust' cannot honor {setting}= yet: {detail}. The Rust "
            "driver owns its own HTTP/TLS stack and has no hook for it. Remove "
            "the setting, or use the core-python backend.".format(
                setting=setting, detail=detail
            )
        )

    if proxy_config is not None:
        _fail("proxy_config", "the Rust driver has no proxy configuration hook")
    if proxies:
        _fail("proxies", "the Rust driver has no proxy configuration hook")
    # connection_verify defaults to True/None (verify) -- only a custom CA path or
    # an explicit disable is unsupported.
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



def build_client_config(
    preferred_locations: Optional[Sequence[str]] = None,
    *,
    excluded_locations: Optional[Sequence[str]] = None,
    throttling_max_retry_count: Optional[int] = None,
    throttling_max_retry_wait_time_seconds: Optional[float] = None,
    availability_strategy: Any = None,
    user_agent_suffix: Optional[str] = None,
    consistency_level: Optional[str] = None,
) -> Optional[PreparedClientConfig]:
    """Collect the client-construction settings the Rust backend can carry into
    a :class:`PreparedClientConfig`, or ``None`` when there is nothing to carry.

    Returning ``None`` keeps the no-config path identical to the original
    two-argument ``init_client`` call (the binding then builds the driver with
    its defaults). Shared by the sync and async factories so the
    kwarg-to-config mapping lives in exactly one place.

    Each setting is carried only when the customer actually expressed it, so an
    untuned client behaves exactly as before:

    * ``preferred_locations`` / ``excluded_locations`` -- empty means "no
      preference / no exclusion".
    * throttling caps -- ``None`` means "untuned"; the driver keeps its own
      defaults (9 retries / 30 s), which match Python-core's.
    * ``availability_strategy`` -- ``None`` (absent) carries nothing, so the
      driver keeps its default; ``False`` carries an explicit disable; ``True``
      or a dict carries the hedging threshold.
    * ``user_agent_suffix`` -- ``None`` or an empty string carries nothing, so
      the driver keeps its default SDK User-Agent; any non-empty label is carried
      for the driver to stamp on every request's User-Agent.
    * ``consistency_level`` -- ``None`` carries nothing, so the driver keeps the
      account default; one of the supported levels (Eventual / Session / Strong)
      is carried so the chosen level actually reaches the driver. Bounded
      Staleness / Consistent Prefix (and any unrecognized value) are rejected
      loudly rather than silently dropped (see :func:`_resolve_consistency_level`).
    """
    preferred = tuple(preferred_locations) if preferred_locations else ()
    excluded = tuple(excluded_locations) if excluded_locations else ()
    hedging_threshold_ms = _resolve_hedging(availability_strategy)
    # An empty string carries nothing, mirroring the "no preference" treatment of
    # the location tuples; only a non-empty label is worth carrying to the driver.
    suffix = user_agent_suffix or None
    consistency = _resolve_consistency_level(consistency_level)
    if (
        not preferred
        and not excluded
        and throttling_max_retry_count is None
        and throttling_max_retry_wait_time_seconds is None
        and hedging_threshold_ms is None
        and suffix is None
        and consistency is None
    ):
        return None
    return PreparedClientConfig(
        preferred_locations=preferred,
        excluded_locations=excluded,
        throttling_max_retry_count=throttling_max_retry_count,
        throttling_max_retry_wait_time_seconds=throttling_max_retry_wait_time_seconds,
        hedging_threshold_ms=hedging_threshold_ms,
        user_agent_suffix=suffix,
        consistency_level=consistency,
    )


def _resolve_consistency_level(consistency_level: Optional[str]) -> Optional[str]:
    """Validate the requested client consistency level for the Rust path and
    return the level to carry, or ``None`` when the customer expressed none.

    ``None`` (or an empty string) carries nothing -- the driver keeps the account
    default, so an untuned client is unchanged. The three levels the driver
    supports today (Eventual, Session, Strong) are carried as-is; the binding maps
    ``"Strong"`` to the driver's ``GlobalStrong``.

    Bounded Staleness and Consistent Prefix have no driver equivalent yet, so they
    are rejected here with a clear message rather than silently dropped. Any other
    value is not a recognized Cosmos consistency level and is likewise rejected.
    """
    if not consistency_level:
        return None
    if consistency_level in _RUST_SUPPORTED_CONSISTENCY_LEVELS:
        return consistency_level
    if consistency_level in _ALL_CONSISTENCY_LEVELS:
        raise ValueError(
            "consistency_level {!r} is not yet supported on the Rust backend "
            "(_backend='rust'); supported levels are {}. Use the core-python "
            "backend if you need {!r}.".format(
                consistency_level,
                ", ".join(_RUST_SUPPORTED_CONSISTENCY_LEVELS),
                consistency_level,
            )
        )
    raise ValueError(
        "consistency_level {!r} is not a recognized Cosmos consistency level; "
        "expected one of {}.".format(
            consistency_level, ", ".join(_ALL_CONSISTENCY_LEVELS)
        )
    )


def _resolve_hedging(availability_strategy: Any) -> Optional[int]:
    """Map the ``availability_strategy`` kwarg to a hedge threshold in ms, or
    ``None`` to carry nothing.

    Carries a threshold only when the customer *enabled* hedging: ``True`` uses
    the default threshold and a dict uses its ``threshold_ms`` (validated ``> 0``
    by reusing :class:`CrossRegionHedgingStrategy`). ``None`` (absent) and
    ``False`` carry nothing -- matching Python-core, where the client default is
    "no strategy" -- so sync (kwarg) and async (an explicit ``False``-default
    parameter) behave identically. Python's ``threshold_steps_ms`` has no driver
    equivalent and is intentionally dropped.
    """
    if availability_strategy is True:
        return DEFAULT_THRESHOLD_MS
    if isinstance(availability_strategy, dict):
        # Reuse the existing validator so an invalid threshold_ms raises the same
        # ValueError it would on the legacy path.
        return CrossRegionHedgingStrategy(availability_strategy).threshold_ms
    # None, False, or an unrecognized shape: carry nothing.
    return None


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
    strict_isolation: Optional[bool] = None,
    proxy_config: Any = None,
    proxies: Any = None,
    connection_verify: Any = None,
    connection_cert: Any = None,
    ssl_config: Any = None,
    transport: Any = None,
) -> Optional[CosmosBackend]:
    """Build the backend instance a sync ``CosmosClient`` will hold.

    Returns a :class:`RustBackend` when Rust is selected, or ``None``
    when core-python is selected. The keyword settings are only consulted
    for the Rust branch, where they are folded into the client config the
    backend carries to the driver. ``strict_isolation`` (kwarg > the
    ``COSMOS_RUST_STRICT_ISOLATION`` env var > off) controls whether a second
    client to an account with a different config raises instead of silently
    getting its own isolated engine. The transport/TLS settings
    (``proxy_config`` / ``proxies`` / ``connection_verify`` / ``connection_cert``
    / ``ssl_config`` / ``transport``) are not folded into the config -- the Rust
    path can't honor them yet, so they are rejected here; they are ignored
    entirely on the core-python branch, which honors them as before.
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
        return RustBackend(
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
            ),
            strict_isolation=resolve_strict_isolation(strict_isolation),
        )
    return None


