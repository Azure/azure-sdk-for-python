"""
Author: Aaron (Ari) Bornstien
"""

import unittest
import asyncio
from mock_event_processor import MockEventProcessor
from mock_credentials import MockCredentials
from eventhubsprocessor.azure_storage_checkpoint_manager import AzureStorageCheckpointLeaseManager
from eventhubsprocessor.eph import EventProcessorHost

class EventProcessorHostTestCase(unittest.TestCase):
    """Tests for `partition_manager.py`."""

    def __init__(self, *args, **kwargs):
        """
        Simulate partition pump
        """
        super(EventProcessorHostTestCase, self).__init__(*args, **kwargs)
        self._credentials = MockCredentials()
        self._consumer_group = "$Default"
        self._storage_clm = AzureStorageCheckpointLeaseManager(self._credentials.storage_account,
                                        self._credentials.storage_key,
                                        self._credentials.lease_container)

        self._host = EventProcessorHost(MockEventProcessor, self._credentials.eh_address,
                                        self._consumer_group, storage_manager=self._storage_clm,
                                        eh_rest_auth=self._credentials.eh_auth)
        self._loop = asyncio.get_event_loop()


    def test_start(self):
        """
        Test that the processing host starts correctly
        """
        self._loop.run_until_complete(self._host.open_async())

if __name__ == '__main__':
    unittest.main()