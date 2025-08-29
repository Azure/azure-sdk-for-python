# The MIT License (MIT)
# Copyright (c) 2024 Microsoft Corporation

"""Module for async completion status tracking."""

import asyncio # pylint: disable=do-not-import-asyncio

from azure.cosmos._request_hedging_completion_status import HedgingCompletionStatus

class AsyncHedgingCompletionStatus(HedgingCompletionStatus):
    """Async-safe implementation of completion status using asyncio.Event."""

    def __init__(self):
        """Initialize completion status with an asyncio.Event."""
        self._completed = asyncio.Event()

    @property
    def is_completed(self) -> bool:
        """Check if request is completed (non-blocking).
        
        :returns: True if request is completed, False otherwise
        :rtype: bool
        """
        return self._completed.is_set()

    def set_completed(self) -> None:
        """Signal request completion (non-blocking)."""
        self._completed.set()

    async def wait(self) -> None:
        """Wait for completion (blocking).
        
        This method is async-specific and not part of the base CompletionStatus interface.
        It allows async code to efficiently wait for completion using asyncio.Event.wait().
        """
        await self._completed.wait()
