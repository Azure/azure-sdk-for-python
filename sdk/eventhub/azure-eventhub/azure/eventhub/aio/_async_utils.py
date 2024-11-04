# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import asyncio
import sys
from asyncio import Semaphore


def get_dict_with_loop_if_needed(loop):
    if sys.version_info >= (3, 10):
        if loop:
            raise ValueError("Starting Python 3.10, asyncio no longer supports loop as a parameter.")
    elif loop:
        return {"loop": loop}
    return {}


async def semaphore_acquire_with_timeout(semaphore: Semaphore, timeout=None):
    try:
        return await asyncio.wait_for(semaphore.acquire(), timeout=timeout)
    except asyncio.TimeoutError:
        return False
