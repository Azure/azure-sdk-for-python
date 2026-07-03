# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""RetryPolicy — configurable retry behaviour for resilient tasks.

Aligned with industry conventions (Temporal, Celery).
Delay formula: ``min(initial_delay * backoff_coefficient ** attempt, max_delay)``
With jitter: ``delay * uniform(0.75, 1.25)``
"""

from __future__ import annotations

import random
from datetime import timedelta

#: Spec 037 #11 — hard caps on the retry knobs. A misconfiguration must not
# let a task turn retry unboundedly, so values outside these ranges are
# rejected at construction (fail-fast, not clamped). A developer may still
# configure smaller values. Retries remain off by default (no policy ⇒ single
# attempt). Mirrored field-for-field by the .NET port
# (``TaskEngineConstants.MaxRetryAttempts`` / ``MaxRetryDelay``).
_MAX_RETRY_ATTEMPTS = 10
_MAX_RETRY_DELAY = timedelta(hours=1)


class RetryPolicy:
    """Retry configuration for resilient tasks.

    :param initial_delay: Base delay between retries.
    :type initial_delay: ~datetime.timedelta
    :param backoff_coefficient: Multiplier applied per attempt.
    :type backoff_coefficient: float
    :param max_delay: Upper bound on computed delay.
    :type max_delay: ~datetime.timedelta
    :param max_attempts: Total attempts (including the first try). This is a
        single **resilient** budget that counts handler-raised failures across
        ALL lifetimes — the count is persisted to
        ``payload["retry_attempt"]`` and restored on recovery. Crash
        recovery does NOT consume the budget; only handler-raised exceptions
        do. A steering input resets the counter (a steering input is a new
        logical request).
    :type max_attempts: int
    :param retry_on: Exception types that trigger retry. ``None`` means all.
    :type retry_on: type[Exception] | tuple[type[Exception], ...] | None
    :param jitter: Whether to add ±25% randomization to delays.
    :type jitter: bool

    .. versionadded:: 2.1.0
    """

    __slots__ = (
        "initial_delay",
        "backoff_coefficient",
        "max_delay",
        "max_attempts",
        "retry_on",
        "jitter",
        "_linear",
    )

    def __init__(
        self,
        *,
        initial_delay: timedelta | float = timedelta(seconds=1),
        backoff_coefficient: float = 2.0,
        max_delay: timedelta | float = timedelta(seconds=60),
        max_attempts: int = 3,
        retry_on: type[Exception] | tuple[type[Exception], ...] | None = None,
        jitter: bool | float = True,
        _linear: bool = False,
    ) -> None:
        #: accept both timedelta and float (seconds) for
        # initial_delay / max_delay. Store as the type provided so
        # ``policy.initial_delay == 1.0`` works for float callers and
        # ``.total_seconds()`` works for timedelta callers.
        def _seconds(v: timedelta | float) -> float:
            return v.total_seconds() if isinstance(v, timedelta) else float(v)

        if _seconds(initial_delay) < 0:
            raise ValueError(f"initial_delay must be >= 0, got {initial_delay}")
        if backoff_coefficient < 1.0:
            raise ValueError(f"backoff_coefficient must be >= 1.0, got {backoff_coefficient}")
        if _seconds(max_delay) < _seconds(initial_delay):
            raise ValueError(f"max_delay ({max_delay}) must be >= initial_delay ({initial_delay})")
        if max_attempts < 1:
            raise ValueError(f"max_attempts must be >= 1, got {max_attempts}")
        if max_attempts > _MAX_RETRY_ATTEMPTS:
            raise ValueError(f"max_attempts must be <= {_MAX_RETRY_ATTEMPTS}, got {max_attempts}")
        if _seconds(max_delay) > _MAX_RETRY_DELAY.total_seconds():
            raise ValueError(f"max_delay must be <= 1 hour, got {max_delay}")
        normalized_retry_on: tuple[type[Exception], ...] | None = None
        if retry_on is not None:
            # Accept a bare class as a single-element tuple — Pythonic.
            if isinstance(retry_on, type):
                if not issubclass(retry_on, Exception):
                    # Non-Exception class (e.g., str) passed directly — reject.
                    raise TypeError(f"retry_on entries must be Exception subclasses, got {retry_on!r}")
                normalized_retry_on = (retry_on,)
            else:
                normalized_retry_on = tuple(retry_on)
            for exc_type in normalized_retry_on:
                if not isinstance(exc_type, type) or not issubclass(exc_type, Exception):
                    raise TypeError(f"retry_on entries must be Exception subclasses, got {exc_type!r}")

        self.initial_delay = initial_delay
        self.backoff_coefficient = backoff_coefficient
        self.max_delay = max_delay
        self.max_attempts = max_attempts
        self.retry_on = normalized_retry_on
        self.jitter = jitter
        self._linear = _linear

    def compute_delay(self, attempt: int) -> float:
        """Return the delay in seconds for the given attempt (0-indexed).

        :param attempt: The 0-based attempt number that just failed.
        :type attempt: int
        :return: Delay in seconds before the next attempt.
        :rtype: float
        """
        base_seconds = (
            self.initial_delay.total_seconds()
            if isinstance(self.initial_delay, timedelta)
            else float(self.initial_delay)
        )
        max_seconds = self.max_delay.total_seconds() if isinstance(self.max_delay, timedelta) else float(self.max_delay)
        if self._linear:
            raw = base_seconds * (attempt + 1)
        else:
            raw = base_seconds * (self.backoff_coefficient**attempt)

        capped = min(raw, max_seconds)

        if self.jitter:
            capped *= random.uniform(0.75, 1.25)

        return max(0.0, capped)

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Return whether the task should be retried.

        :param attempt: The 0-based attempt number that just failed.
        :type attempt: int
        :param error: The exception that was raised.
        :type error: Exception
        :return: ``True`` if the task should be retried.
        :rtype: bool
        """
        # attempt is 0-indexed; max_attempts includes the first try
        if attempt >= self.max_attempts - 1:
            return False
        if self.retry_on is None:
            return True
        return isinstance(error, self.retry_on)

    def __repr__(self) -> str:
        return (
            f"RetryPolicy(initial_delay={self.initial_delay!r}, "
            f"backoff_coefficient={self.backoff_coefficient}, "
            f"max_delay={self.max_delay!r}, "
            f"max_attempts={self.max_attempts}, "
            f"retry_on={self.retry_on!r}, "
            f"jitter={self.jitter})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RetryPolicy):
            return NotImplemented
        return (
            self.initial_delay == other.initial_delay
            and self.backoff_coefficient == other.backoff_coefficient
            and self.max_delay == other.max_delay
            and self.max_attempts == other.max_attempts
            and self.retry_on == other.retry_on
            and self.jitter == other.jitter
            and self._linear == other._linear
        )

    # ------------------------------------------------------------------
    # Convenience presets
    # ------------------------------------------------------------------

    @classmethod
    def exponential_backoff(
        cls,
        *,
        max_attempts: int = 3,
        initial_delay: timedelta = timedelta(seconds=1),
        max_delay: timedelta = timedelta(seconds=60),
        backoff_coefficient: float = 2.0,
        jitter: bool = True,
    ) -> RetryPolicy:
        """Exponential backoff — the most common pattern.

        Delay doubles per attempt: 1 s → 2 s → 4 s → … capped at *max_delay*.

        :keyword max_attempts: Total attempts including the first try.
        :paramtype max_attempts: int
        :keyword initial_delay: Base delay.
        :paramtype initial_delay: ~datetime.timedelta
        :keyword max_delay: Upper bound.
        :paramtype max_delay: ~datetime.timedelta
        :keyword backoff_coefficient: Multiplier applied per attempt.
        :paramtype backoff_coefficient: float
        :keyword jitter: Add ±25% randomization.
        :paramtype jitter: bool
        :return: A configured ``RetryPolicy``.
        :rtype: RetryPolicy
        """
        return cls(
            initial_delay=initial_delay,
            backoff_coefficient=backoff_coefficient,
            max_delay=max_delay,
            max_attempts=max_attempts,
            jitter=jitter,
        )

    @classmethod
    def fixed_delay(
        cls,
        *,
        delay: timedelta = timedelta(seconds=5),
        max_attempts: int = 3,
    ) -> RetryPolicy:
        """Fixed delay — constant interval between retries.

        Useful for rate-limited APIs where you want to wait a fixed
        amount of time between each attempt.

        :keyword delay: Constant delay between retries.
        :paramtype delay: ~datetime.timedelta
        :keyword max_attempts: Total attempts including the first try.
        :paramtype max_attempts: int
        :return: A configured ``RetryPolicy``.
        :rtype: RetryPolicy
        """
        return cls(
            initial_delay=delay,
            backoff_coefficient=1.0,
            max_delay=delay,
            max_attempts=max_attempts,
            jitter=False,
        )

    @classmethod
    def linear_backoff(
        cls,
        *,
        initial_delay: timedelta = timedelta(seconds=1),
        max_delay: timedelta = timedelta(seconds=60),
        max_attempts: int = 5,
    ) -> RetryPolicy:
        """Linear backoff — delay grows additively.

        Delay is ``initial_delay * (attempt + 1)``: 1 s → 2 s → 3 s → …

        :keyword initial_delay: Base delay unit.
        :paramtype initial_delay: ~datetime.timedelta
        :keyword max_delay: Upper bound.
        :paramtype max_delay: ~datetime.timedelta
        :keyword max_attempts: Total attempts including the first try.
        :paramtype max_attempts: int
        :return: A configured ``RetryPolicy``.
        :rtype: RetryPolicy
        """
        return cls(
            initial_delay=initial_delay,
            backoff_coefficient=1.0,
            max_delay=max_delay,
            max_attempts=max_attempts,
            jitter=False,
            _linear=True,
        )

    @classmethod
    def no_retry(cls) -> RetryPolicy:
        """No retry — the function runs once and fails on exception.

        Equivalent to not setting a retry policy at all.

        :return: A ``RetryPolicy`` that never retries.
        :rtype: RetryPolicy
        """
        return cls(
            initial_delay=timedelta(0),
            backoff_coefficient=1.0,
            max_delay=timedelta(0),
            max_attempts=1,
            jitter=False,
        )


# =========================================================================
#  — module-level convenience wrappers around the preset
# classmethods (documents these as `exponential_backoff` etc.
# with explicit kwargs).
# =========================================================================


def exponential_backoff(
    *,
    initial_delay: "timedelta" = timedelta(seconds=1),
    backoff_coefficient: float = 2.0,
    max_delay: "timedelta" = timedelta(seconds=60),
    max_attempts: int = 3,
    jitter: bool = True,
) -> RetryPolicy:
    """Module-level wrapper for :meth:`RetryPolicy.exponential_backoff`.

    : preset factories enumerate their kwargs explicitly.

        :keyword initial_delay: Initial delay before the first retry.
        :keyword backoff_coefficient: Multiplier applied per attempt.
        :keyword max_delay: Cap on the per-attempt delay.
        :keyword max_attempts: Total attempts including the first try.
        :keyword jitter: When True, add ±25% jitter per attempt.
        :return: A configured :class:`RetryPolicy`.
        :rtype: RetryPolicy
    """
    return RetryPolicy.exponential_backoff(
        initial_delay=initial_delay,
        backoff_coefficient=backoff_coefficient,
        max_delay=max_delay,
        max_attempts=max_attempts,
        jitter=jitter,
    )


def fixed_delay(
    *,
    delay: "timedelta" = timedelta(seconds=5),
    max_attempts: int = 3,
) -> RetryPolicy:
    """Module-level wrapper for :meth:`RetryPolicy.fixed_delay`.

    :keyword delay: Constant delay between retries.
    :keyword max_attempts: Total attempts including the first try.
    :return: A configured :class:`RetryPolicy`.
    :rtype: RetryPolicy
    """
    return RetryPolicy.fixed_delay(delay=delay, max_attempts=max_attempts)


def linear_backoff(
    *,
    initial_delay: "timedelta" = timedelta(seconds=1),
    max_delay: "timedelta" = timedelta(seconds=60),
    max_attempts: int = 5,
) -> RetryPolicy:
    """Module-level wrapper for :meth:`RetryPolicy.linear_backoff`.

    :keyword initial_delay: Delay increment per attempt.
    :keyword max_delay: Cap on the per-attempt delay.
    :keyword max_attempts: Total attempts including the first try.
    :return: A configured :class:`RetryPolicy`.
    :rtype: RetryPolicy
    """
    return RetryPolicy.linear_backoff(
        initial_delay=initial_delay,
        max_delay=max_delay,
        max_attempts=max_attempts,
    )


def no_retry() -> RetryPolicy:
    """Module-level wrapper for :meth:`RetryPolicy.no_retry`.

    :return: A :class:`RetryPolicy` that never retries.
    :rtype: RetryPolicy
    """
    return RetryPolicy.no_retry()
