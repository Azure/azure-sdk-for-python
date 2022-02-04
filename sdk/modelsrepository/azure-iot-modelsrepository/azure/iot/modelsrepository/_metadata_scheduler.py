# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

class MetadataScheduler(object):
    def __init__(self, enabled=True):
        # type: (bool) -> None
        """ MetadataScheduler tracks when metadata should be fetched from a repository.

        :param enabled: Whether the scheduler should be enabled.
        :type enabled: bool
        """
        self._initial_fetch = True
        self._enabled = enabled

    def should_fetch_metadata(self):
        # type: () -> bool
        """Indicates whether the caller should fetch metadata."""
        return self._enabled and self._initial_fetch

    def mark_as_fetched(self):
        # type: () -> None
        """To be invoked by caller indicating repository metadata has been fetched."""
        if self._initial_fetch:
            self._initial_fetch = False
