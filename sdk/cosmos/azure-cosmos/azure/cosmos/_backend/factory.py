# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""The single entry point for backend selection.

Consistent terms used throughout this file:

* **client** -- the ``CosmosClient`` object a customer creates in their code.
* **backend** -- which engine runs the database calls: ``core-python`` (the
  original all-Python one) or ``rust`` (the new one that hands the work to a
  rust driver).
* **rust driver** -- the engine itself; it owns the network connection pool, the
  auth (request signing), and region routing. The **binding** is the compiled
  ``azure.cosmos._rust`` layer Python calls into to reach it (the compiled file
  holds both). The binding keeps one rust driver per distinct ``(endpoint,
  credential, config)`` and reference-counts it, so same-settings clients share
  one; the **driver handle** is the string that names which rust driver a client
  uses.
* **credential** -- how the customer proves who they are (a master key, or a
  token from ``azure-identity``).

High-level view -- what this file does
--------------------------------------

When a customer writes ``CosmosClient(url, credential, _backend="rust")``,
something has to (1) decide which engine that client will use, and (2) if it is
the Rust engine, check that everything the customer passed is something the Rust
engine can actually handle, and repackage it into the shape the driver expects.
That is this file's whole job. The client calls :func:`make_backend` once, at
construction, and stores what it returns: a :class:`RustBackend` object if Rust
was chosen, or ``None`` if core-python was chosen (the rest of the SDK reads
"no backend object" as "use the original Python path").

If this file didn't exist: that decide-and-check-and-repackage logic would have
to live inside ``CosmosClient`` itself -- and be duplicated in both the sync and
async clients. The moment those two copies diverged, bugs would appear on one
side only. Worse, without the up-front checks, a customer who passed something Rust
can't do yet (say, a custom proxy, or Bounded Staleness consistency) wouldn't
find out at ``CosmosClient(...)``. It would appear to work, then fail on their
first database call with a confusing low-level error far from the real cause.
This file's core value is failing early and clearly, at construction, with a
message that says exactly what to do instead.

Selection precedence (highest wins): the ``_backend=`` kwarg, then the
``COSMOS_BACKEND`` environment variable, then the ``core-python`` default. An
invalid value raises ``ValueError`` at construction time.
"""
from __future__ import annotations

import asyncio
import inspect
import math
import os
from collections.abc import Mapping
from collections.abc import Sequence as _AbcSequence
from numbers import Real
from typing import Any, Optional, Sequence, Tuple

from .._availability_strategy_config import CrossRegionHedgingStrategy, DEFAULT_THRESHOLD_MS
from ..documents import ConnectionPolicy, ConsistencyLevel
from ._async_credential_bridge import AsyncTokenCredentialBridge
from .base import CosmosBackend, PreparedClientConfig
from .constants import (
    BACKEND_ENV_VAR,
    BACKEND_NAME_RUST,
    DEFAULT_BACKEND_NAME,
    RUST_STRICT_ISOLATION_ENV_VAR,
    STRICT_ISOLATION_FALSE_VALUES,
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
    """Decide the engine name from the ``_backend=`` argument, else the
    ``COSMOS_BACKEND`` environment variable, else the ``core-python`` default,
    and return a name in ``VALID_BACKEND_NAMES``.

    Without it: a stray trailing newline or ``"RUST"`` in caps from a
    copy-pasted env var would be treated as a typo and rejected; and a real typo
    would silently fall back to the wrong engine instead of telling the customer.
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
    strict per-account engine isolation.

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
    :class:`~azure.cosmos._backend._driver_registry.StrictEngineIsolationError` at
    construction instead of silently building a second isolated engine.
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


def _is_async_credential(credential: Any) -> bool:
    """Detect whether the customer's credential logs in asynchronously: its
    ``get_token`` or ``get_token_info`` is a coroutine, or it is an
    ``azure.identity.aio``-style async context manager.

    Why it matters: the Rust driver calls ``get_token`` on a plain worker thread
    that has no async event loop, so an async credential would crash there.
    Detecting it lets the next step (:func:`_resolve_credential`) wrap it safely
    in an :class:`AsyncTokenCredentialBridge`, which supplies that event loop,
    instead of calling it directly. The token method is unwrapped first in case
    it is decorated.
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
    """Detect the "per-user permission token" style of credential, rather than a
    master key or a token credential.

    Why: the Rust driver has no code to log in that way yet, so this lets the
    factory reject it clearly (in :func:`_resolve_credential`) instead of failing
    deep inside the driver later. These take the shape of a mapping of resource
    link to token (without a ``masterKey`` entry, which is handled earlier), a
    mapping with ``resourceTokens`` / ``permissionFeed`` keys, or a concrete
    sequence (list / tuple) of permission entries.
    """
    if isinstance(credential, str):
        return False
    if isinstance(credential, Mapping):
        # A master-key dict is resolved as a master key before this is reached;
        # any other mapping shape is resource/permission tokens.
        return "masterKey" not in credential
    if isinstance(credential, bytes):
        return False
    # A permission feed is a concrete sequence (list / tuple) of permission
    # entries. Restrict to Sequence rather than any Iterable so an unusual custom
    # credential object that merely happens to be iterable is not mislabeled a
    # resource-token credential -- it falls through to the generic
    # "unsupported shape" message instead.
    return isinstance(credential, _AbcSequence)


def _resolve_credential(credential: Any) -> Tuple[Optional[str], Optional[Any]]:
    """The credential sorter: turn whatever the customer passed into exactly one
    of a master key or a synchronous token credential, or raise ``ValueError``.

    Without it: an unsupported login would blow up on the first request with an
    opaque error, not at the line where the customer created the client. So this
    rejects anything Rust can't do upfront -- at construction. Returns
    ``(master_key, token_credential)`` with exactly one entry set:

    * a ``str`` or a dict with a ``'masterKey'`` entry -> master key (rejected if
      empty or, in the dict case, not a non-empty string);
    * an object with a synchronous ``get_token`` (e.g. an ``azure-identity``
      credential) -> token credential, forwarded to the driver, which calls
      ``get_token`` during request signing;
    * an *async* token credential (coroutine ``get_token`` / ``get_token_info``,
      or the ``azure.identity.aio`` async-context-manager shape) is first wrapped
      in an :class:`AsyncTokenCredentialBridge`, which drives its coroutine on a
      dedicated event-loop thread and presents the synchronous ``get_token`` the
      driver's worker thread calls -- so async credentials work on the Rust path
      with no driver change;
    * a resource-token / permission-feed credential (per-user scoped tokens) is
      rejected: the Rust driver has no resource-token auth support yet;
    * anything else (``None`` and unrecognized shapes) is rejected.
    """
    if isinstance(credential, str):
        if not credential:
            raise ValueError(
                "_backend='rust' requires a non-empty master-key string."
            )
        return credential, None
    if isinstance(credential, Mapping) and "masterKey" in credential:
        master_key = credential["masterKey"]
        if not isinstance(master_key, str) or not master_key:
            # A non-string (or empty) masterKey would otherwise be accepted here and
            # fail later in a murkier place (credential-key computation or the
            # driver). Reject it at construction with a clear message.
            raise ValueError(
                "_backend='rust' requires the 'masterKey' entry to be a non-empty "
                "string; got {!r}.".format(master_key)
            )
        return master_key, None
    # Check async *before* the sync get_token acceptance, since an async
    # credential also exposes a (coroutine) get_token. Wrap it rather than reject
    # it: the bridge drives the coroutine on its own event-loop thread and exposes
    # the synchronous get_token the driver calls, so async credentials work with no
    # driver change.
    if _is_async_credential(credential):
        return None, AsyncTokenCredentialBridge.acquire(credential)
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


# Transport / TLS knobs the legacy pipeline honors but the Rust path still cannot
# accept as explicit objects -- it owns its own HTTP stack. Each maps to a
# constructor kwarg the legacy path
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

    The Rust driver owns its own network/TLS stack, so it can't accept custom
    proxy objects, a custom CA bundle, a client certificate, disabled TLS
    verification, or a stand-in transport. Without this: those settings would be
    silently ignored, and the customer would think their proxy/cert was in effect
    when it wasn't -- a security-relevant surprise. So it raises if any were
    passed.

    It is careful to let the defaults through so a normal client isn't wrongly
    rejected: ``connection_verify`` defaults to ``True``/absent (ordinary
    verification, which the driver already does) and only a custom CA bundle path
    (a ``str``) or an explicit ``False`` (disable verification) is unsupported;
    an empty ``proxies`` dict is "no proxy". Every other setting is rejected when it
    is present (non-``None``).
    """
    def _fail(setting: str, detail: str) -> None:
        """Raise a customer-facing error for one unsupported setting."""
        raise ValueError(
            "_backend='rust' cannot honor {setting}= yet: {detail}. The Rust "
            "driver owns its own HTTP/TLS stack. Remove the setting (for proxy, "
            "use proxy_allowed= with environment variables), or use the "
            "core-python backend.".format(
                setting=setting, detail=detail
            )
        )

    if proxy_config is not None:
        _fail("proxy_config", "the Rust driver has no explicit proxy-config object hook")
    if proxies:
        _fail("proxies", "the Rust driver has no explicit proxy-config object hook")
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



def _normalize_locations(
    value: Optional[Sequence[str]], arg_name: str
) -> Tuple[str, ...]:
    """Turn a locations argument into a tuple of region strings, or reject a bare
    string/bytes.

    A bare string like ``"West US"`` is iterable, so ``tuple("West US")`` would
    silently become ``('W', 'e', 's', 't', ...)`` -- seven bogus one-character
    "regions" the customer never meant, with no error. Reject that shape up front
    and require a real sequence of region names (e.g. ``["West US"]``). An empty or
    absent value means "no preference" and carries nothing.
    """
    if not value:
        return ()
    if isinstance(value, (str, bytes)):
        raise ValueError(
            "{name} must be a sequence of region-name strings (e.g. ['West US']), "
            "not a bare string; got {val!r}. A bare string is read one character "
            "at a time, which is never what you want here.".format(
                name=arg_name, val=value
            )
        )
    return tuple(value)


def build_client_config(
    preferred_locations: Optional[Sequence[str]] = None,
    *,
    excluded_locations: Optional[Sequence[str]] = None,
    throttling_max_retry_count: Optional[int] = None,
    throttling_max_retry_wait_time_seconds: Optional[float] = None,
    availability_strategy: Any = None,
    user_agent_suffix: Optional[str] = None,
    consistency_level: Optional[str] = None,
    proxy_allowed: Optional[bool] = None,
    connection_timeout_seconds: Optional[float] = None,
    read_timeout_seconds: Optional[float] = None,
) -> Optional[PreparedClientConfig]:
    """Gather the tuning options the Rust path can carry (preferred/excluded
    regions, retry caps, region-hedging, user-agent label, consistency level,
    proxy on/off, and transport timeout caps) into one
    :class:`PreparedClientConfig`, and return ``None``
    when the customer tuned nothing.

    Why the ``None`` matters: an untuned client takes the simplest path -- the
    binding builds the driver with its defaults -- so a customer who asked for
    no tuning gets no behavior change. Shared by the sync and async factories so
    the kwarg-to-config mapping lives in exactly one place.

    Most settings are carried only when the customer actually expressed them.
    The public clients always pass the effective transport timeouts, including
    the legacy defaults, because the Rust transport defaults differ:

    * ``preferred_locations`` / ``excluded_locations`` -- empty means "no
      preference / no exclusion".
    * throttling caps -- ``None`` means "untuned"; the driver keeps its own
      defaults (9 retries / 30 s), which match Python-core's.
    * ``availability_strategy`` -- ``None`` (absent) and ``False`` carry
      nothing, so the driver keeps its default; ``True`` or a dict carries the
      hedging threshold. Carrying an explicit disable requires a separate
      config field that does not exist yet.
    * ``user_agent_suffix`` -- ``None`` or an empty string carries nothing, so
      the driver keeps its default SDK User-Agent; any non-empty label is carried
      for the driver to stamp on every request's User-Agent.
    * ``consistency_level`` -- ``None`` carries nothing, so the driver keeps the
      account default; one of the supported levels (Eventual / Session / Strong)
      is carried so the chosen level actually reaches the driver. Bounded
      Staleness / Consistent Prefix (and any unrecognized value) are rejected
      loudly rather than silently dropped (see :func:`_resolve_consistency_level`).
    * ``proxy_allowed`` -- ``None`` carries nothing; ``True`` lets the Rust driver
      use proxy settings from environment variables; ``False`` forces a direct
      connection (no proxy).
    * ``connection_timeout_seconds`` maps exactly to the driver's whole-process
      connection timeout.
    * ``read_timeout_seconds`` is approximate: Python treats it as socket-read
      inactivity, while the Rust transport caps the complete HTTP attempt on
      both data-plane and metadata requests.
    """
    if proxy_allowed is not None and not isinstance(proxy_allowed, bool):
        raise ValueError(
            "proxy_allowed must be a bool when provided; got {!r}.".format(
                type(proxy_allowed).__name__
            )
        )
    preferred = _normalize_locations(preferred_locations, "preferred_locations")
    excluded = _normalize_locations(excluded_locations, "excluded_locations")
    hedging_threshold_ms = _resolve_hedging(availability_strategy)
    # An empty string carries nothing, matching the "no preference" treatment of
    # the location tuples; only a non-empty label is worth carrying to the driver.
    suffix = user_agent_suffix or None
    consistency = _resolve_consistency_level(consistency_level)
    connection_timeout = _normalize_transport_timeout(
        connection_timeout_seconds,
        "connection_timeout",
        maximum=6.0,
    )
    read_timeout = _normalize_transport_timeout(
        read_timeout_seconds,
        "read_timeout",
    )
    if (
        not preferred
        and not excluded
        and throttling_max_retry_count is None
        and throttling_max_retry_wait_time_seconds is None
        and hedging_threshold_ms is None
        and suffix is None
        and consistency is None
        and proxy_allowed is None
        and connection_timeout is None
        and read_timeout is None
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
        proxy_allowed=proxy_allowed,
        connection_timeout_seconds=connection_timeout,
        read_timeout_seconds=read_timeout,
    )


def resolve_client_transport_timeouts(kwargs: Mapping[str, Any]) -> Tuple[Any, Any]:
    """Return the effective constructor-level connection and read timeouts.

    This matches ``_build_connection_policy`` without consuming ``kwargs`` so the
    legacy client still receives the same values. ``request_timeout`` is the older
    millisecond alias for ``connection_timeout`` and therefore keeps precedence.
    """
    policy = kwargs.get("connection_policy") or ConnectionPolicy()
    if "request_timeout" in kwargs:
        connection_timeout = kwargs["request_timeout"] / 1000.0
    else:
        connection_timeout = kwargs.get("connection_timeout", policy.RequestTimeout)
    read_timeout = kwargs.get("read_timeout", policy.ReadTimeout)
    return connection_timeout, read_timeout


def _normalize_transport_timeout(
    value: Optional[float],
    name: str,
    *,
    maximum: Optional[float] = None,
) -> Optional[float]:
    """Validate a Python timeout against the Rust connection-pool limits."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError("{} must be a number of seconds; got {!r}.".format(name, value))
    timeout = float(value)
    if not math.isfinite(timeout):
        raise ValueError("{} must be finite; got {!r}.".format(name, value))
    if timeout < 0.1:
        raise ValueError(
            "{} must be at least 0.1 seconds on the Rust backend; got {!r}.".format(
                name, value
            )
        )
    if maximum is not None and timeout > maximum:
        raise ValueError(
            "{} must be at most {} seconds on the Rust backend; got {!r}.".format(
                name, maximum, value
            )
        )
    return timeout


def _resolve_consistency_level(consistency_level: Optional[str]) -> Optional[str]:
    """Check the requested client consistency level for the Rust path and return
    the level to carry, or ``None`` when the customer expressed none.

    Without it: the customer would ask for one consistency guarantee and silently
    get a different one -- a correctness problem they'd never see coming. So
    ``None`` (or an empty string) carries nothing -- the driver keeps the account
    default, so an untuned client is unchanged. Eventual, Session and Strong are
    carried through as-is (the binding maps ``"Strong"`` to the driver's
    ``GlobalStrong``). Bounded Staleness and Consistent Prefix have no Rust
    equivalent yet and are rejected here with a clear message rather than silently
    dropped. Any other value is not a recognized Cosmos consistency level and is
    likewise rejected.
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
    """Translate the ``availability_strategy`` option into a single millisecond
    threshold the driver understands, or ``None`` to carry nothing.

    Why: it reuses the existing validator (:class:`CrossRegionHedgingStrategy`)
    so a bad threshold fails the same way it always did, keeping old and new paths
    consistent. Carries a threshold only when the customer *enabled* hedging:
    ``True`` uses the default threshold and a dict uses its ``threshold_ms``
    (validated ``> 0``). ``None`` (absent) and ``False`` carry nothing -- matching
    Python-core, where the client default is "no strategy" -- so sync (kwarg) and
    async (an explicit ``False``-default parameter) behave identically. Python's
    ``threshold_steps_ms`` has no driver equivalent and is intentionally dropped.
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
) -> Optional[CosmosBackend]:
    """The one public entry point that combines the rest of this file: build
    the backend instance a sync ``CosmosClient`` will hold.

    Without it: the client constructor would have to do all of the below itself,
    in two places (sync and async), which invites one-sided bugs when the two
    copies diverge. So this resolves the name; if Rust, requires the endpoint URL,
    rejects unsupported transport settings, sorts the credential, combines the
    tuning into a config, resolves the isolation switch, and returns a
    :class:`RustBackend`. If core-python, it returns ``None``.

    The keyword settings are only consulted for the Rust branch, where they are
    combined into the client config the backend carries to the driver.
    ``strict_isolation`` (kwarg > the ``COSMOS_RUST_STRICT_ISOLATION`` env var >
    off) controls whether a second client to an account with a different config
    raises instead of silently getting its own isolated engine. The transport/TLS
    settings (``proxy_config`` / ``proxies`` / ``connection_verify`` /
    ``connection_cert`` / ``ssl_config`` / ``transport``) are not combined into the
    config -- the Rust path still can't honor explicit proxy/transport objects, so
    they are rejected here; they are ignored entirely on the core-python branch,
    which honors them as before. ``proxy_allowed`` is the Rust-path proxy switch
    carried into the driver runtime.
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
                proxy_allowed=proxy_allowed,
                connection_timeout_seconds=connection_timeout_seconds,
                read_timeout_seconds=read_timeout_seconds,
            ),
            strict_isolation=resolve_strict_isolation(strict_isolation),
        )
    return None
