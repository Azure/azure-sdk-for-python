# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Preserve operation cancellation across the deadline helper's task boundary."""

import asyncio
import time

import pytest

from azure.cosmos._operation_deadline import run_with_deadline


@pytest.mark.parametrize("has_deadline", [False, True])
def test_operation_cancellation_preserves_original_exception_rust(has_deadline):
    error = asyncio.CancelledError("cancelled by operation")

    async def operation():
        raise error

    async def scenario():
        deadline = time.monotonic() + 1 if has_deadline else None
        with pytest.raises(asyncio.CancelledError) as caught:
            await run_with_deadline(operation, deadline)
        assert caught.value is error

    asyncio.run(scenario())


def test_caller_cancellation_still_drains_operation_rust():
    async def scenario():
        started = asyncio.Event()
        cleaned = asyncio.Event()

        async def operation():
            try:
                started.set()
                await asyncio.Event().wait()
            finally:
                cleaned.set()

        task = asyncio.create_task(run_with_deadline(operation, time.monotonic() + 10))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert cleaned.is_set()

    asyncio.run(scenario())
