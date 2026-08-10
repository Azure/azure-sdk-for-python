# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Gathering a client's tuning options into one object the driver can read.

A customer can tune a client in several independent ways -- preferred and
excluded regions, retry caps, cross-region hedging, a user-agent label, a
consistency level, whether proxies are allowed, and transport timeout caps. The
driver wants all of that as a single value, not as a scattering of keyword
arguments.

:func:`build_client_config` is that gathering step. It validates each option
against what the Rust path can actually carry, and returns one
:class:`~azure.cosmos._backend.contracts.PreparedClientConfig` -- or ``None``
when the customer tuned nothing at all, which keeps an untuned client on the
simplest path, with the binding building the driver from its own defaults.

The private helpers below it do the per-option validation: rejecting a bare
string where a list of regions was meant, a consistency level with no driver
equivalent, or a timeout outside the connection pool's limits. Both the sync and
async factories call :func:`build_client_config`, so a given set of keyword
arguments produces the same config on either client.
"""
from __future__ import annotations

import math
from numbers import Real
from typing import Any, Optional, Sequence, Tuple

from .._availability_strategy_config import CrossRegionHedgingStrategy, DEFAULT_THRESHOLD_MS
from ..documents import ConsistencyLevel
from .contracts import PreparedClientConfig

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
    Every setting is carried only when the customer actually expressed it:

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
    * ``connection_timeout_seconds`` -- ``None`` carries nothing; a value maps
      exactly to the driver's whole-process connection timeout.
    * ``read_timeout_seconds`` -- ``None`` carries nothing; a value is
      approximate, because Python treats it as socket-read inactivity while the
      Rust transport caps the complete HTTP attempt on both data-plane and
      metadata requests. Both timeouts configure the process-wide driver runtime,
      so carrying one pins it for every later client in the process; that is why
      only an explicitly requested timeout is ever carried here.
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
