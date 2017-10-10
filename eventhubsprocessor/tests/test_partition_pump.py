"""
Author: Aaron (Ari) Bornstien
"""

import unittest
import asyncio
from mock_event_processor import MockEventProcessor
from eventhubsprocessor.eph import EventProcessorHost
from eventhubsprocessor.lease import Lease
from eventhubsprocessor.partition_pump import PartitionPump

class PartitionPumpTestCase(unittest.TestCase):
    """Tests for `partition_pump.py`."""

    def __init__(self, *args, **kwargs):
        """
        Simulate partition pump
        """
        super(PartitionPumpTestCase, self).__init__(*args, **kwargs)
        self._host = EventProcessorHost(MockEventProcessor, "fake eventHubPath",
                                        "fake consumerGroupName")
        self._lease = Lease()
        self._lease.with_partition_id("1")
        self._partition_pump = PartitionPump(self._host, self._lease)
        self._loop = asyncio.get_event_loop()

    def test_open_async(self):
        """
        Test that partition pump opens sucessfully
        """
        print("\nTest that partition pump opens sucessfully:")
        self._loop.run_until_complete(self._partition_pump.open_async())    # Simulate Open
        return True

    def test_process_events_async(self):
        """
        Test that the partition pump processes a list of mock events (["event1", "event2"])
        properly
        """
        print("\nTest that the partition pump processes a list of mock events:")
        self._loop.run_until_complete(self._partition_pump.open_async())    # Simulate Open
        _mock_events = ["event1", "event2"] # Mock Events
        self._loop.run_until_complete(self._partition_pump.process_events_async(_mock_events))  # Simulate Process
        return True

    def test_close_async(self):
        """
        Test that partition pump closes
        """
        print("\nTest that partition pump closes:")
        self._loop.run_until_complete(self._partition_pump.open_async())    # Simulate Open
        _mock_events = ["event1", "event2"] # Mock Events
        self._loop.run_until_complete(self._partition_pump.process_events_async(_mock_events))  # Simulate Process
        self._loop.run_until_complete(self._partition_pump.close_async("Finished")) # Simulate Close
        return True

if __name__ == '__main__':
    unittest.main()
