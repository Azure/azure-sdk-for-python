# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import unittest
import asyncio
from mock_event_processor import MockEventProcessor
from mock_credentials import MockCredentials
from eventhubsprocessor.partition_manager import PartitionManager
from eventhubsprocessor.eph import EventProcessorHost


class PartitionManagerTestCase(unittest.TestCase):
    """Tests for `partition_manager.py`."""

    def __init__(self, *args, **kwargs):
        """
        Simulate partition pump
        """
        super(PartitionManagerTestCase, self).__init__(*args, **kwargs)
        self._credentials = MockCredentials()
        self._consumer_group = "$Default"
        self._host = EventProcessorHost(MockEventProcessor, self._credentials.eh_address,
                                        self._consumer_group, eh_rest_auth=self._credentials.eh_auth)
        self._partition_manager = PartitionManager(self._host)
        self._loop = asyncio.get_event_loop()

    def test_get_partition_ids(self):
        """
        Test that partition manger returns all the partitions for an event hub
        """
        pids = self._loop.run_until_complete(self._partition_manager.get_partition_ids_async())    # Simulate Open
        print(pids)
if __name__ == '__main__':
    unittest.main()