# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Observe SDK cancellation before older asyncio runners replace its exception."""

import asyncio


def run_async(awaitable):
    """Run an awaitable while preserving the cancellation object raised by the SDK."""
    cancellations = []

    async def observe():
        try:
            return await awaitable
        except asyncio.CancelledError as error:
            cancellations.append(error)

    result = asyncio.run(observe())
    if cancellations:
        raise cancellations[0]
    return result
