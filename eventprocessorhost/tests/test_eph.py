# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import unittest
import logging
import asyncio
import sys
from mock_event_processor import MockEventProcessor
from mock_credentials import MockCredentials
from eventprocessorhost.azure_storage_checkpoint_manager import AzureStorageCheckpointLeaseManager
from eventprocessorhost.eph import EventProcessorHost

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

        self._loop = asyncio.get_event_loop()

        self._host = EventProcessorHost(MockEventProcessor, self._credentials.eh_address,
                                        self._consumer_group, storage_manager=self._storage_clm,
                                        eh_rest_auth=self._credentials.eh_auth, loop = self._loop)
        logging.basicConfig(filename='eph.log', level=logging.INFO,
                            format='%(asctime)s:%(msecs)03d, \'%(message)s\' ',
                            datefmt='%Y-%m-%d:%H:%M:%S')
        logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


    def test_start(self):
        """
        Test that the processing host starts correctly
        """
        try:
            self._loop.run_until_complete(self._host.open_async())
            self._loop.run_until_complete(self._host.close_async())
        finally:
            self._loop.stop()


if __name__ == '__main__':
    unittest.main()
