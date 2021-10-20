# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from time import time
import logging

_LOGGER = logging.getLogger(__name__)

class MetadataScheduler(object):
    def __init__(self, expiration=None, enabled=True):
        # type: (int, bool) -> None
        """ MetadataScheduler tracks when metadata should be fetched from a repository.

        :param expiration: Amount of time in seconds before the client
            considers the repository metadata stale.
        :type expiration: int
        :param enabled: Whether the scheduler should be enabled.
        :type enabled: bool
        """
        self._last_fetched = None
        self._initial_fetch = True
        self._desired_elapsed_time_span = expiration if expiration else float('inf')
        self._enabled = enabled

    def reset(self):
        # type: () -> None
        """Updates the _last_fetched attribute of the scheduler to current time."""
        if self._initial_fetch:
            self._initial_fetch = False

        self._last_fetched = time()

    def has_elapsed(self):
        # type: () -> bool
        """Determines whether the desired time span has elapsed with respect to the _last_fetched
        and _initial_fetch attributes."""
        if not self._enabled:
            return False

        if self._initial_fetch:
            return True

        return (time() - self._last_fetched) >= self._desired_elapsed_time_span
