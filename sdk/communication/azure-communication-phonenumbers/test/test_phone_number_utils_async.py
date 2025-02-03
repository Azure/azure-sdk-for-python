# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import asyncio
from azure.communication.phonenumbers._shared.utils_async import AsyncTimer

call_count = 0


async def callback():
    global call_count
    call_count += 1


@pytest.mark.asyncio
async def test_timer_callback():
    global call_count
    call_count = 0
    timer = AsyncTimer(0, callback)
    timer.start()
    await asyncio.sleep(0.1)
    assert call_count == 1


@pytest.mark.asyncio
async def test_timer_cancel():
    global call_count
    call_count = 0
    timer = AsyncTimer(10, callback)
    timer.start()
    timer.cancel()
    assert call_count == 0


@pytest.mark.asyncio
async def test_timer_restart():
    global call_count
    call_count = 0
    timer = AsyncTimer(0.5, callback)
    timer.start()
    timer.cancel()
    timer.start()
    await asyncio.sleep(1)
    assert call_count == 1
