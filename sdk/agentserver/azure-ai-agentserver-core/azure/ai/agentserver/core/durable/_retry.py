# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""RetryPolicy — configurable retry behaviour for durable tasks.

Aligned with industry conventions (Temporal, Azure Durable Functions, Celery).
Delay formula: ``min(initial_delay * backoff_coefficient ** attempt, max_delay)``
With jitter: ``delay * uniform(0.75, 1.25)``
"""

from __future__ import annotations

import random
from datetime import timedelta
from typing import Any


class RetryPolicy:
    """Retry configuration for durable tasks.

    :param initial_delay: Base delay between retries.
    :type initial_delay: ~datetime.timedelta
    :param backoff_coefficient: Multiplier applied per attempt.
    :type backoff_coefficient: float
    :param max_delay: Upper bound on computed delay.
    :type max_delay: ~datetime.timedelta
    :param max_attempts: Total attempts (including the first try).
    :type max_attempts: int
    :param retry_on: Exception types that trigger retry. ``None`` means all.
    :type retry_on: tuple[type[Exception], ...] | None
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
        initial_delay: timedelta = timedelta(seconds=1),
        backoff_coefficient: float = 2.0,
        max_delay: timedelta = timedelta(seconds=60),
        max_attempts: int = 3,
        retry_on: tuple[type[Exception], ...] | None = None,
        jitter: bool = True,
        _linear: bool = False,
    ) -> None:
        if initial_delay.total_seconds() < 0:
            raise ValueError(f"initial_delay must be >= 0, got {initial_delay}")
        if max_attempts < 1 and not (max_attempts == 1 and initial_delay == timedelta(0)):
            pass  # allow no_retry preset
        if backoff_coefficient < 1.0:
            raise ValueError(f"backoff_coefficient must be >= 1.0, got {backoff_coefficient}")
        if max_delay < initial_delay:
            raise ValueError(
                f"max_delay ({max_delay}) must be >= initial_delay ({initial_delay})"
            )
        if max_attempts < 1:
            raise ValueError(f"max_attempts must be >= 1, got {max_attempts}")
        if retry_on is not None:
            for exc_type in retry_on:
                if not isinstance(exc_type, type) or not issubclass(exc_type, Exception):
                    raise TypeError(
                        f"retry_on entries must be Exception subclasses, got {exc_type!r}"
                    )

        self.initial_delay = initial_delay
        self.backoff_coefficient = backoff_coefficient
        self.max_delay = max_delay
        self.max_attempts = max_attempts
        self.retry_on = retry_on
        self.jitter = jitter
        self._linear = _linear

    def compute_delay(self, attempt: int) -> float:
        """Return the delay in seconds for the given attempt (0-indexed).

        :param attempt: The 0-based attempt number that just failed.
        :type attempt: int
        :return: Delay in seconds before the next attempt.
        :rtype: float
        """
        base_seconds = self.initial_delay.total_seconds()
        if self._linear:
            # Linear: delay = initial_delay * (attempt + 1)
            raw = base_seconds * (attempt + 1)
        else:
            # Exponential: delay = initial_delay * coefficient ^ attempt
            raw = base_seconds * (self.backoff_coefficient ** attempt)

        capped = min(raw, self.max_delay.total_seconds())

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
        :keyword jitter: Add ±25% randomization.
        :paramtype jitter: bool
        :return: A configured ``RetryPolicy``.
        :rtype: RetryPolicy
        """
        return cls(
            initial_delay=initial_delay,
            backoff_coefficient=2.0,
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
