# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Helper for running async code from a normal (non-async) test."""

import asyncio


def run_async(awaitable):
    """Run ``awaitable`` and return its result.

    ``awaitable`` is usually the result of calling an ``async def`` function,
    for example ``run_async(container.read())``.

    If it is cancelled, raise the exact ``asyncio.CancelledError`` it raised.
    On some older Python versions ``asyncio.run`` raises a new
    ``CancelledError`` instead, and tests that check for the original error
    would fail.
    """
    cancellations = []

    async def capture_cancellation():
        try:
            return await awaitable
        except asyncio.CancelledError as error:
            cancellations.append(error)

    result = asyncio.run(capture_cancellation())
    if cancellations:
        raise cancellations[0]
    return result