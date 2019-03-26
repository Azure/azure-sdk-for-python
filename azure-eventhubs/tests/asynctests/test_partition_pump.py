# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import asyncio


def test_open_async(partition_pump):
    """
    Test that partition pump opens sucessfully
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(partition_pump.open_async())  # Simulate Open

def test_process_events_async(partition_pump):
    """
    Test that the partition pump processes a list of mock events (["event1", "event2"])
    properly
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(partition_pump.open_async())  # Simulate Open
    _mock_events = ["event1", "event2"]  # Mock Events
    loop.run_until_complete(partition_pump.process_events_async(_mock_events))  # Simulate Process

def test_close_async(partition_pump):
    """
    Test that partition pump closes
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(partition_pump.open_async())  # Simulate Open
    _mock_events = ["event1", "event2"]  # Mock Events
    loop.run_until_complete(partition_pump.process_events_async(_mock_events))  # Simulate Process
    loop.run_until_complete(partition_pump.close_async("Finished"))  # Simulate Close
