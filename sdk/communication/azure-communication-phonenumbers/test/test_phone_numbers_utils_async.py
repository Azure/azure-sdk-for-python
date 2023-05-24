# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import asyncio
from unittest.mock import AsyncMock
from azure.communication.phonenumbers._shared.utils_async import AsyncTimer  

@pytest.mark.asyncio
async def test_timer_callback():
    callback = AsyncMock()
    timer = AsyncTimer(0, callback)
    timer.start()
    await asyncio.sleep(0.1)  
    callback.assert_called_once()

@pytest.mark.asyncio
async def test_timer_cancel():
    callback = AsyncMock()
    timer = AsyncTimer(10, callback) 
    timer.start()
    timer.cancel()
    assert timer._task is None
    callback.assert_not_called()

@pytest.mark.asyncio
async def test_timer_restart():
    callback = AsyncMock()
    timer = AsyncTimer(0.5, callback) 
    timer.start()
    timer.cancel()
    callback.assert_not_called()
    timer.start()
    await asyncio.sleep(1)  
    callback.assert_called_once()
