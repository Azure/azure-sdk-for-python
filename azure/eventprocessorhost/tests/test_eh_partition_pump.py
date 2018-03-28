# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import unittest
import asyncio
import logging
from mock_event_processor import MockEventProcessor
from mock_credentials import MockCredentials
from azure.eventprocessorhost.eph import EventProcessorHost
from azure.eventprocessorhost.azure_storage_checkpoint_manager import AzureStorageCheckpointLeaseManager
from azure.eventprocessorhost.azure_blob_lease import AzureBlobLease
from azure.eventprocessorhost.eh_partition_pump import EventHubPartitionPump


def test_partition_pump_async(eh_partition_pump):
    """
    Test that event hub partition pump opens and processess messages sucessfully then closes
    """
    loop = asyncio.get_event_loop()
    is_live, pump = eh_partition_pump
    if is_live:
        loop.run_until_complete(pump.open_async())  # Simulate Open
        loop.run_until_complete(pump.close_async("Finished"))  # Simulate Close
