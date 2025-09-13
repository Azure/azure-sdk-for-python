# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import random
import time


class RefreshTimer:
    """
    A timer that tracks the next refresh time and the number of attempts.
    """

    def __init__(self, **kwargs):
        """
        Initialize the refresh timer with the specified configuration.

        :keyword kwargs: Configuration options including refresh_interval, min_backoff, and max_backoff.
        :paramtype kwargs: Dict[str, Any]
        :raises ValueError: If refresh_interval is less than 1 second.
        """
        self._interval: int = kwargs.pop("refresh_interval", 30)
        if self._interval < 1:
            raise ValueError("Refresh interval must be greater than or equal to 1 second.")
        self._next_refresh_time: float = time.time() + self._interval
        self._attempts: int = 1
        self._min_backoff: int = (
            kwargs.get("min_backoff", 30) if kwargs.get("min_backoff", 30) <= self._interval else self._interval
        )
        self._max_backoff: int = 600 if 600 <= self._interval else self._interval

    def reset(self) -> None:
        """
        Reset the refresh timer to its initial state.
        """
        self._next_refresh_time = time.time() + self._interval
        self._attempts = 1

    def backoff(self) -> None:
        """
        Apply exponential backoff to the next refresh time.
        """
        self._next_refresh_time = time.time() + self._calculate_backoff() / 1000
        self._attempts += 1

    def needs_refresh(self) -> bool:
        """
        Check if a refresh is needed based on the current time.

        :return: True if a refresh is needed, False otherwise.
        :rtype: bool
        """
        return time.time() >= self._next_refresh_time

    def _calculate_backoff(self) -> float:
        """
        Calculate the exponential backoff time in milliseconds.

        :return: The backoff time in milliseconds.
        :rtype: float
        """
        max_attempts = 63
        millisecond = 1000  # 1 Second in milliseconds

        min_backoff_milliseconds = self._min_backoff * millisecond
        max_backoff_milliseconds = self._max_backoff * millisecond

        if self._max_backoff <= self._min_backoff:
            return min_backoff_milliseconds

        calculated_milliseconds = max(1, min_backoff_milliseconds) * (1 << min(self._attempts, max_attempts))

        if calculated_milliseconds > max_backoff_milliseconds or calculated_milliseconds <= 0:
            calculated_milliseconds = max_backoff_milliseconds

        return min_backoff_milliseconds + (
            random.uniform(0.0, 1.0) * (calculated_milliseconds - min_backoff_milliseconds)  # nosec
        )
