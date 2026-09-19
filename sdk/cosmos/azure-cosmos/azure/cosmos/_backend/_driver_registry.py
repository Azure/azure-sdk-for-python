# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Python client registrations and process-policy reservations for Rust drivers.

Driver identity is supplied by the binding's cache-key function. Canonical
endpoints group registrations for the per-account strict-isolation policy only;
they do not determine whether native drivers share. Matching identities are
allowed in strict mode; default mode also permits distinct identities.

register_driver_client reserves identity, proxy and transport policies as one
transaction. release_driver_client drops provisional holds while retaining live
registrations and settings already frozen by the native runtime. The runtime is
process-wide, not per-driver.

These Python counts are separate from both Python object references and native
driver-handle references. They predict conflicts at construction; native handle
acquisition and driver creation remain lazy and are owned by the binding.
"""
from __future__ import annotations

import threading
from fractions import Fraction
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlsplit, urlunsplit

from .contracts import PreparedClientConfig
from ._binding_conversions import acquire_driver_handle_args


class _StrictDriverIsolationError(ValueError):
    """Raised by this guard (in the python wrapper) when, under strict isolation, a
    later ``CosmosClient`` would make the binding build a *second* driver (rust driver)
    for an account: its native cache identity matches no registered client for
    that account. Endpoint spelling, credential and config all contribute.

    Opt-in: it fires only when strict isolation is enabled (the
    ``COSMOS_RUST_STRICT_ISOLATION`` env var or the factory toggle), and it fires at
    client construction -- before the binding lazily builds any driver. By default the
    second client is allowed and gets its own isolated driver.
    """


class ProxyPolicyConflictError(ValueError):
    """Raised at client construction when a ``CosmosClient`` requests an explicit
    ``proxy_allowed`` that differs from the value already established for this process.

    Why this is separate from the driver-isolation guard above: ``proxy_allowed`` is
    not a per-account setting. It configures the Rust runtime (the Tokio reactor +
    ``CosmosDriverRuntime``), which is a process-global singleton built once -- by
    whichever client triggers the first operation -- and frozen for the life of the
    process (``runtime.rs`` ``OnceLock``). So every Rust-backed client in the process
    that sets ``proxy_allowed`` must agree on one value. The binding does enforce this,
    but only lazily at native initialization. This guard checks current reservations
    at construction, in both default and strict mode (the driver-isolation registry
    cannot catch it because it treats ``proxy_allowed`` as just another per-account
    config field). Clients that leave ``proxy_allowed`` unset (``None``) never set or
    conflict with the policy, matching the binding's ``proxy_allowed_conflicts``.

    Concurrent constructors can still race to reserve the first value. Reservations
    can be released before initialization; ``freeze_runtime_policy`` records the
    effective native settings once available. Constructing an explicit-value
    client does not alone initialize the runtime with that value.
    """


class TransportTimeoutPolicyConflictError(ValueError):
    """Raised when Rust clients request different process-wide transport timeouts."""


# Process-wide policy, reserved by explicit settings or frozen from native state.
# _PROXY_POLICY_SET distinguishes no reservation from a recorded value (including
# None returned by the native runtime). A None-setting client adds no reservation.
# Guarded by _LOCK.
_PROXY_POLICY: Optional[bool] = None
_PROXY_POLICY_SET: bool = False
_CONNECTION_TIMEOUT_POLICY: Optional[float] = None
_CONNECTION_TIMEOUT_POLICY_SET: bool = False
_READ_TIMEOUT_POLICY: Optional[float] = None
_READ_TIMEOUT_POLICY_SET: bool = False


# Canonical account endpoint -> counts for (native identity, config) reservations.
# Config is retained for process-policy reservations, not driver-identity equality.
# Counts include temporary initialization reservations and do not prove a native
# driver exists. Empty identities/accounts are removed on release. Guarded by _LOCK.
_LOCK = threading.RLock()
_REGISTRY: Dict[str, Dict[Tuple[str, Optional[PreparedClientConfig]], int]] = {}
_FROZEN_RUNTIME_POLICY: Optional[tuple[Optional[bool], Optional[float], Optional[float]]] = None


def _timeout_identity(value: Optional[float]) -> Optional[int]:
    # Native Duration rounds the exact float to the nearest nanosecond.
    return None if value is None else round(Fraction.from_float(float(value)) * 1_000_000_000)


def _policy_state() -> tuple:
    return (
        _PROXY_POLICY, _PROXY_POLICY_SET, _CONNECTION_TIMEOUT_POLICY,
        _CONNECTION_TIMEOUT_POLICY_SET, _READ_TIMEOUT_POLICY, _READ_TIMEOUT_POLICY_SET,
    )


def _restore_policy_state(state: tuple) -> None:
    global _PROXY_POLICY, _PROXY_POLICY_SET
    global _CONNECTION_TIMEOUT_POLICY, _CONNECTION_TIMEOUT_POLICY_SET
    global _READ_TIMEOUT_POLICY, _READ_TIMEOUT_POLICY_SET
    (
        _PROXY_POLICY, _PROXY_POLICY_SET, _CONNECTION_TIMEOUT_POLICY,
        _CONNECTION_TIMEOUT_POLICY_SET, _READ_TIMEOUT_POLICY, _READ_TIMEOUT_POLICY_SET,
    ) = state


def register_driver_client(
    endpoint: str, config: Optional[PreparedClientConfig], driver_identity: str, strict: bool = False
) -> None:
    """Reserve all startup policies and driver identity as one transaction."""
    with _LOCK:
        previous = _policy_state()
        try:
            register_proxy_policy(config)
            register_transport_timeout_policy(config)
            _register_client_identity(endpoint, config, driver_identity=driver_identity, strict=strict)
        except BaseException:
            _restore_policy_state(previous)
            raise


def freeze_runtime_policy(settings: tuple[Optional[bool], Optional[float], Optional[float]]) -> None:
    """Record settings actually frozen by the native runtime, even after a failed driver build."""
    global _FROZEN_RUNTIME_POLICY
    with _LOCK:
        _FROZEN_RUNTIME_POLICY = settings
        proxy, connection, read = settings
        _restore_policy_state((proxy, True, connection, True, read, True))


def release_driver_client(
    endpoint: str, config: Optional[PreparedClientConfig], driver_identity: str
) -> None:
    """Release provisional reservations, retaining live clients and native runtime settings."""
    with _LOCK:
        _release_client_identity(endpoint, config, driver_identity=driver_identity)
        if _FROZEN_RUNTIME_POLICY is not None:
            freeze_runtime_policy(_FROZEN_RUNTIME_POLICY)
        else:
            _restore_policy_state((None, False, None, False, None, False))
            for drivers in _REGISTRY.values():
                for _, live_config in drivers:
                    register_proxy_policy(live_config)
                    register_transport_timeout_policy(live_config)


def _canonicalize_endpoint(endpoint: str) -> str:
    """Group account URL variants for strict-policy checks, not cache identity.

    Lowercases scheme and host (DNS is case-insensitive), drops a default port and
    a trailing slash, and discards any query or fragment. Conservative on purpose:
    so two different accounts never collapse, anything that does not parse as a
    scheme+host URL is returned unchanged.
    """
    if not endpoint:
        return endpoint
    try:
        parts = urlsplit(endpoint)
        if not parts.scheme or not parts.netloc:
            return endpoint
        scheme = parts.scheme.lower()
        host = (parts.hostname or "").lower()
        if not host:
            return endpoint
        default_port = {"https": 443, "http": 80}.get(scheme)
        port = parts.port
        netloc = host if port is None or port == default_port else "{0}:{1}".format(host, port)
        path = parts.path.rstrip("/")
        return urlunsplit((scheme, netloc, path, "", ""))
    except ValueError:
        # Malformed URL (e.g. a bad port): fall back to the raw string rather than
        # guessing, so two endpoints the code cannot parse are never treated as
        # the same account.
        return endpoint


def make_driver_identity(
    endpoint: str,
    master_key: Optional[str],
    config: Optional[PreparedClientConfig],
    token_credential: Optional[Any],
) -> str:
    """Ask the binding for its cache identity without acquiring a driver.

    No Python approximation is used when the extension is absent or outdated.
    The returned identity is internal and must not be logged.
    """
    from azure.cosmos import _rust

    identity_function = getattr(_rust, "_driver_identity", None)
    if not callable(identity_function):
        raise RuntimeError(
            "The compiled azure.cosmos._rust extension does not export _driver_identity; "
            "rebuild it from the current source."
        )
    return identity_function(*acquire_driver_handle_args(endpoint, master_key, config, token_credential))


def register_proxy_policy(config: Optional[PreparedClientConfig]) -> None:
    """Enforce a single process-wide ``proxy_allowed`` policy, fail-fast at construction.

    The Rust runtime's proxy setting is process-global (one ``OnceLock``-backed runtime
    per process), so every Rust-backed client that sets ``proxy_allowed`` must agree on
    one value. The lock serializes reservations, but concurrent callers can
    race to establish the first explicit value.

    Rules (matching the binding's ``proxy_allowed_conflicts``):

    * A client that does not set ``proxy_allowed`` (``None``) is always compatible and
      never establishes the policy -- it accepts whatever value wins.
    * The first explicit value reserves the policy if no value is recorded.
    * A later client with a *different* explicit value raises
      ``ProxyPolicyConflictError``. An equal value is accepted (idempotent).

    Called from ``_shared`` at client construction, before ``_register_client_identity``,
    so a proxy conflict fails before the client records any driver registration to
    release. Reservations remain provisional until native initialization.
    An untuned client can initialize the runtime with defaults; the binding
    still checks effective settings when an explicit-value client acquires a
    driver. Construction order alone is not initialization order.
    """
    if config is None or config.proxy_allowed is None:
        return
    requested = config.proxy_allowed
    global _PROXY_POLICY, _PROXY_POLICY_SET  # pylint: disable=global-statement
    with _LOCK:
        if not _PROXY_POLICY_SET:
            _PROXY_POLICY = requested
            _PROXY_POLICY_SET = True
            return
        if _PROXY_POLICY != requested:
            raise ProxyPolicyConflictError(
                "proxy_allowed is process-global for the Rust backend and was already "
                "established as proxy_allowed={established!r} by an earlier CosmosClient; "
                "this client requests proxy_allowed={requested!r}. Set the same "
                "proxy_allowed value on every Rust-backed CosmosClient in the process "
                "(or leave it unset), and construct the client that sets it first, "
                "before any others.".format(established=_PROXY_POLICY, requested=requested)
            )


def register_transport_timeout_policy(config: Optional[PreparedClientConfig]) -> None:
    """Fail fast when Rust clients disagree on process-wide transport timeouts."""
    if config is None:
        return
    requested_connection = config.connection_timeout_seconds
    requested_read = config.read_timeout_seconds
    if requested_connection is None and requested_read is None:
        return

    global _CONNECTION_TIMEOUT_POLICY  # pylint: disable=global-statement
    global _CONNECTION_TIMEOUT_POLICY_SET  # pylint: disable=global-statement
    global _READ_TIMEOUT_POLICY  # pylint: disable=global-statement
    global _READ_TIMEOUT_POLICY_SET  # pylint: disable=global-statement
    with _LOCK:
        conflicts = []
        if (
            requested_connection is not None
            and _CONNECTION_TIMEOUT_POLICY_SET
            and _timeout_identity(_CONNECTION_TIMEOUT_POLICY) != _timeout_identity(requested_connection)
        ):
            conflicts.append(
                "connection_timeout={requested!r} (already {established!r})".format(
                    requested=requested_connection,
                    established=_CONNECTION_TIMEOUT_POLICY,
                )
            )
        if (
            requested_read is not None
            and _READ_TIMEOUT_POLICY_SET
            and _timeout_identity(_READ_TIMEOUT_POLICY) != _timeout_identity(requested_read)
        ):
            conflicts.append(
                "read_timeout={requested!r} (already {established!r})".format(
                    requested=requested_read,
                    established=_READ_TIMEOUT_POLICY,
                )
            )
        if conflicts:
            raise TransportTimeoutPolicyConflictError(
                "Rust transport timeouts are process-global; this CosmosClient "
                "conflicts with an earlier client: {}. Set the same constructor "
                "timeouts on every Rust-backed CosmosClient in the process.".format(
                    ", ".join(conflicts)
                )
            )

        if requested_connection is not None and not _CONNECTION_TIMEOUT_POLICY_SET:
            _CONNECTION_TIMEOUT_POLICY = requested_connection
            _CONNECTION_TIMEOUT_POLICY_SET = True
        if requested_read is not None and not _READ_TIMEOUT_POLICY_SET:
            _READ_TIMEOUT_POLICY = requested_read
            _READ_TIMEOUT_POLICY_SET = True


def _register_client_identity(
    endpoint: str,
    config: Optional[PreparedClientConfig] = None,
    *,
    driver_identity: str,
    strict: bool = False,
) -> None:
    """Record one live client against ``endpoint``. Called by the python wrapper when a
    client is opened, before and independently of the binding building any driver.

    The binding supplies the exact cache identity. A client matching an existing
    identity records its reservation without a strict-isolation error. A new
    identity is handled as follows:

    * strict -- raise ``_StrictDriverIsolationError`` without recording, so the
      failed client never enters a count (it is not built, so it must not be
      released later) and the existing counts stay correct.
    * default -- register the new identity; native acquisition occurs separately.

    The first client to an account always records, whatever its strict flag.
    Config equality is used only to balance process-policy reservations;
    strict-mode acceptance uses native identity alone.

    :param endpoint: The account endpoint the client targets (canonicalized here).
    :param config: The client's prepared config, or ``None`` when untuned.
    :param driver_identity: The binding's cache key from ``make_driver_identity``.
    :param strict: When ``True``, building a new driver raises instead of isolating.
    :raises _StrictDriverIsolationError: In strict mode, when this client's native
        identity matches no registration already live for the account.
    """
    key = _canonicalize_endpoint(endpoint)
    driver = (driver_identity, config)
    with _LOCK:
        live = _REGISTRY.get(key)
        if live is None:
            _REGISTRY[key] = {driver: 1}
            return
        if driver in live:
            live[driver] += 1
            return
        if strict and not any(identity == driver_identity for identity, _ in live):
            # Do NOT record: the client construction is about to fail, so it must not
            # count against the account (it will never call _release_client_identity).
            raise _StrictDriverIsolationError(
                "Strict driver isolation is enabled and another CosmosClient is "
                "already active against {endpoint!r} with a different native driver "
                "identity. The Rust binding would build a "
                "second, separate per-account driver to honor this client's settings "
                "(credential, preferred/excluded locations, consistency level, "
                "throttling, hedging, user-agent suffix). To proceed, give this client "
                "the same account, credential and configuration as an existing one, "
                "change the internal test isolation policy, or build it in a "
                "separate process.".format(endpoint=endpoint)
            )
        live[driver] = 1


def _release_client_identity(
    endpoint: str,
    config: Optional[PreparedClientConfig] = None,
    *,
    driver_identity: str,
) -> None:
    """Drop one registration; remove identity/account entries when counts reach zero.

    Called by explicit cleanup, finalizers, and temporary initialization
    reservations. Match each successful registration with one release.
    Unknown identities are a no-op, but a duplicate release of an identity
    still shared by other clients would decrement their count.
    """
    key = _canonicalize_endpoint(endpoint)
    driver = (driver_identity, config)
    with _LOCK:
        live = _REGISTRY.get(key)
        if live is None:
            return
        count = live.get(driver)
        if count is None:
            return
        count -= 1
        if count <= 0:
            del live[driver]
            if not live:
                del _REGISTRY[key]
        else:
            live[driver] = count


def _live_client_count(endpoint: str) -> int:
    """Total live clients across every driver for ``endpoint`` (0 if none). Test- and
    diagnostics-facing; the strict decision uses the per-driver structure directly."""
    key = _canonicalize_endpoint(endpoint)
    with _LOCK:
        return sum(_REGISTRY.get(key, {}).values())


def _reset_for_tests() -> None:
    """Clear the registry. Tests use this to stay isolated from each other, since
    the registry lives for the whole process.
    """
    global _FROZEN_RUNTIME_POLICY
    global _PROXY_POLICY, _PROXY_POLICY_SET  # pylint: disable=global-statement
    global _CONNECTION_TIMEOUT_POLICY  # pylint: disable=global-statement
    global _CONNECTION_TIMEOUT_POLICY_SET  # pylint: disable=global-statement
    global _READ_TIMEOUT_POLICY  # pylint: disable=global-statement
    global _READ_TIMEOUT_POLICY_SET  # pylint: disable=global-statement
    with _LOCK:
        _FROZEN_RUNTIME_POLICY = None
        _REGISTRY.clear()
        _PROXY_POLICY = None
        _PROXY_POLICY_SET = False
        _CONNECTION_TIMEOUT_POLICY = None
        _CONNECTION_TIMEOUT_POLICY_SET = False
        _READ_TIMEOUT_POLICY = None
        _READ_TIMEOUT_POLICY_SET = False
