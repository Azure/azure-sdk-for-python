# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import unittest
import asyncio
import logging
import pytest


async def wait_and_close(host):
    """
    Run EventProcessorHost for 2 minutes then shutdown.
    """
    await asyncio.sleep(60)
    await host.close_async()


@pytest.mark.liveTest
def test_partition_pump_async(eh_partition_pump):
    """
    Test that event hub partition pump opens and processess messages sucessfully then closes
    """
    pytest.skip("Not working yet")
    loop = asyncio.get_event_loop()
    tasks = asyncio.gather(
        eh_partition_pump.open_async(),
        wait_and_close(eh_partition_pump))
    loop.run_until_complete(tasks)
