# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import logging
import threading
import time

logger = logging.getLogger(__name__)

# Default maximum envelopes per second across all telemetry types.
# This is a client-side safety cap to prevent self-inflicted overload
# of shared ingestion infrastructure during telemetry bursts.
_DEFAULT_MAX_ENVELOPES_PER_SECOND = 10000

# Minimum allowed value to prevent misconfiguration
_MIN_MAX_ENVELOPES_PER_SECOND = 1


class _TokenBucketRateLimiter:
    """Thread-safe token bucket rate limiter for outbound telemetry.

    The bucket refills at ``max_per_second`` tokens per second and holds
    at most ``max_per_second`` tokens (i.e. one second of burst capacity).

    :param float max_per_second: Maximum tokens (envelopes) allowed per second.
    """

    def __init__(self, max_per_second: float) -> None:
        if max_per_second < _MIN_MAX_ENVELOPES_PER_SECOND:
            raise ValueError(f"max_per_second must be at least {_MIN_MAX_ENVELOPES_PER_SECOND}")
        self._max_per_second = float(max_per_second)
        self._tokens = self._max_per_second  # start full
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def try_consume(self, count: int) -> int:
        """Try to consume *count* tokens from the bucket.

        Returns the number of tokens actually consumed (i.e. how many
        envelopes may be sent).  The caller should handle the remainder
        (e.g. store for retry or drop).

        :param int count: Number of tokens requested.
        :return: Number of tokens granted (<= *count*).
        :rtype: int
        """
        if count <= 0:
            return 0

        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_refill
            self._last_refill = now

            # Refill tokens based on elapsed time, capped at bucket capacity
            self._tokens = min(
                self._max_per_second,
                self._tokens + elapsed * self._max_per_second,
            )

            granted = min(count, int(self._tokens))
            self._tokens -= granted

        return granted
