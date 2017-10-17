"""
Author: Aaron (Ari) Bornstien
"""

import unittest
import asyncio
from mock_event_processor import MockEventProcessor
from mock_credentials import MockCredentials
from eventhubsprocessor.eph import EventProcessorHost
from eventhubsprocessor.azure_storage_checkpoint_manager import AzureStorageCheckpointLeaseManager
from eventhubsprocessor.azure_blob_lease import AzureBlobLease
from eventhubsprocessor.eh_partition_pump import EventHubPartitionPump

class PartitionPumpTestCase(unittest.TestCase):
    """Tests for `eh_partition_pump.py`."""

    def __init__(self, *args, **kwargs):
        """
        Simulate partition pump
        """
        super(PartitionPumpTestCase, self).__init__(*args, **kwargs)
        self._credentials = MockCredentials()
        self._consumer_group = "$Default"
        self._storage_clm = AzureStorageCheckpointLeaseManager(self._credentials.storage_account,
                                                self._credentials.storage_key,
                                                self._credentials.lease_container)
                                                
        self._host = EventProcessorHost(MockEventProcessor, self._credentials.eh_address,
                                        self._consumer_group, storage_manager=self._storage_clm)
        
        self._lease = AzureBlobLease()
        self._lease.with_partition_id("1")
        self._partition_pump = EventHubPartitionPump(self._host, self._lease)

        self._loop = asyncio.get_event_loop()

    def test_epp_async(self):
        """
        Test that event hub partition pump opens and processess messages sucessfully then closes
        """
        print("\nTest that event hub partition pump opens and processess messages sucessfully then closes:")
        self._loop.run_until_complete(self._partition_pump.open_async())    # Simulate Open
        self._loop.run_until_complete(self._partition_pump.close_async("Finished")) # Simulate Close
        return True

    # def test_bad_credentials(self):
    #     """
    #     Test that the pipe shuts down as expected if given bad credentials
    #     This is failing since eh client api doesn't give a way to check if connection failed and is running in seperate thread
    #     """
    #     print("\nTest that the pipe shuts down as expected if given bad credentials:")
    #     self._host = EventProcessorHost(MockEventProcessor, "Fake Credentials",
    #                             self._consumer_group)
    #     self._partition_pump = EventHubPartitionPump(self._host, self._lease)
    #     self._loop.run_until_complete(self._partition_pump.open_async())    # Simulate Open
    #     return True

if __name__ == '__main__':
    unittest.main()
