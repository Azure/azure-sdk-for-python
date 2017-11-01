"""
Author: Aaron (Ari) Bornstien
"""

import unittest
import logging
import asyncio
import time
from mock_credentials import MockCredentials
from mock_event_processor import MockEventProcessor
from eventhubsprocessor.eph import EventProcessorHost
from eventhubsprocessor.azure_storage_checkpoint_manager import AzureStorageCheckpointLeaseManager

class AzureStorageCheckpointLeaseManagerTestCase(unittest.TestCase):
    """Tests for `eh_partition_pump.py`."""

    def __init__(self, *args, **kwargs):
        """
        Simulate AzureStorageCheckpointLeaseManager
        """
        super(AzureStorageCheckpointLeaseManagerTestCase, self).__init__(*args, **kwargs)
        self._loop = None
        self._credentials = MockCredentials()
        self._consumer_group = "$Default"
        self._host = EventProcessorHost(MockEventProcessor, self._credentials.eh_address,
                                        self._consumer_group)

        self._storage_clm = AzureStorageCheckpointLeaseManager(self._credentials.storage_account,
                                                               self._credentials.storage_key,
                                                               self._credentials.lease_container,
                                                               "lease")
    def test_init(self):
        """
        Test that the AzureStorageCheckpointLeaseManager initializes correctly
        """
        self._storage_clm.initialize(self._host)

    def test_create_store(self):
        """
        Test the store is created correctly if not exists
        """
        self._storage_clm.initialize(self._host)
        self._loop = asyncio.get_event_loop()
        self._loop.run_until_complete(self._storage_clm.create_checkpoint_store_if_not_exists_async())

    # def test_create_lease(self):
    #     """
    #     Test lease creation
    #     """
    #     self._storage_clm.initialize(self._host)
    #     self._loop = asyncio.get_event_loop()
    #     self._loop.run_until_complete(self._storage_clm.create_checkpoint_store_if_not_exists_async())
    #     self._loop.run_until_complete(self._storage_clm.create_lease_if_not_exists_async("1"))

    # def test_get_lease(self):
    #     """
    #     Test get lease
    #     """
    #     self._storage_clm.initialize(self._host)
    #     self._loop = asyncio.get_event_loop()
    #     self._loop.run_until_complete(self._storage_clm.get_lease_async("1"))

    # def test_aquire_renew_release_lease(self):
    #     """
    #     Test aquire lease
    #     """
    #     self._storage_clm.initialize(self._host)
    #     self._loop = asyncio.get_event_loop()
    #     lease = self._loop.run_until_complete(self._storage_clm.get_lease_async("1"))
    #     self._loop.run_until_complete(self._storage_clm.acquire_lease_async(lease))
    #     self._loop.run_until_complete(self._storage_clm.renew_lease_async(lease))
    #     self._loop.run_until_complete(self._storage_clm.release_lease_async(lease))
    #     print(lease.__dict__)

    # def test_delete_lease(self):
    #     """
    #     Test delete lease
    #     """
    #     self._storage_clm.initialize(self._host)
    #     self._loop = asyncio.get_event_loop()
    #     self._loop.run_until_complete(self._storage_clm.delete_lease_async("1"))

    # def test_checkpointing(self):
    #     """
    #     Test checkpointing
    #     """
    #     self._storage_clm.initialize(self._host)
    #     self._loop = asyncio.get_event_loop()
    #     local_checkpoint = self._loop.run_until_complete(self._storage_clm.create_checkpoint_if_not_exists_async("1"))
    #     print("Local CheckPoint", local_checkpoint.__dict__)
    #     lease = self._loop.run_until_complete(self._storage_clm.get_lease_async("1"))
    #     self._loop.run_until_complete(self._storage_clm.acquire_lease_async(lease))
    #     self._loop.run_until_complete(self._storage_clm.update_checkpoint_async(lease, local_checkpoint))
    #     cloud_checkpoint = self._loop.run_until_complete(self._storage_clm.get_checkpoint_async("1"))
    #     lease.offset = cloud_checkpoint.offset
    #     lease.sequence_number = cloud_checkpoint.sequence_number
    #     # print("Cloud Checkpoint", cloud_checkpoint.__dict__)
    #     # modify_checkpoint = cloud_checkpoint
    #     # modify_checkpoint.offset = "512"
    #     # modify_checkpoint.sequence_number = "32"
    #     # time.sleep(35)
    #     # self._loop.run_until_complete(self._storage_clm.update_checkpoint_async(lease, modify_checkpoint))
    #     print("Release Lease")
    #     self._loop.run_until_complete(self._storage_clm.release_lease_async(lease))


    # def test_create_checkpoint(self):
    #     logging.basicConfig(filename='testcheckpoint.log', level=logging.INFO,
    #                         format='%(asctime)s %(message)s')
    #     self._storage_clm.initialize(self._host)
    #     self._loop = asyncio.get_event_loop()
    #     local_checkpoint = self._loop.run_until_complete(self._storage_clm.create_checkpoint_if_not_exists_async("1"))
    

    #     # self._loop.run_until_complete(self._storage_clm.delete_lease_async(lease))


if __name__ == '__main__':
    unittest.main()
