# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import pytest
import os
from mock_credentials import MockCredentials
from mock_event_processor import MockEventProcessor
from azure.eventprocessorhost import EventProcessorHost
from azure.eventprocessorhost import EventHubPartitionPump
from azure.eventprocessorhost import AzureStorageCheckpointLeaseManager
from azure.eventprocessorhost import AzureBlobLease
from azure.eventprocessorhost import EventHubConfig
from azure.eventprocessorhost.lease import Lease
from azure.eventprocessorhost.partition_pump import PartitionPump
from azure.eventprocessorhost.partition_manager import PartitionManager


@pytest.fixture()
def empty_eph():
    credentials = MockCredentials()
    host = EventProcessorHost(
        MockEventProcessor,
        credentials.eh_address,
        None)
    return host


@pytest.fixture()
def storage_clm():
    try:
        storage_clm = AzureStorageCheckpointLeaseManager(
            os.environ['AZURE_STORAGE_ACCOUNT'],
            os.environ['AZURE_STORAGE_ACCESS_KEY'],
            "lease")
        return True, storage_clm
    except KeyError:
        credentials = MockCredentials()
        storage_clm = AzureStorageCheckpointLeaseManager(
            credentials.storage_account,
            credentials.storage_key,
            credentials.lease_container,
            "lease")
        return False, storage_clm


@pytest.fixture()
def eph():
    is_live = False
    try:
        storage_clm = AzureStorageCheckpointLeaseManager(
            os.environ['AZURE_STORAGE_ACCOUNT'],
            os.environ['AZURE_STORAGE_ACCESS_KEY'],
            "lease")
        NAMESPACE = os.environ.get('EVENT_HUB_NAMESPACE')
        EVENTHUB = os.environ.get('EVENT_HUB_NAME')
        USER = os.environ.get('EVENT_HUB_SAS_POLICY')
        KEY = os.environ.get('EVENT_HUB_SAS_KEY')

        eh_config = EventHubConfig(NAMESPACE, EVENTHUB, USER, KEY, consumer_group="$default")
        host = EventProcessorHost(
            MockEventProcessor,
            eh_config,
            storage_clm)
        is_live = True
    except KeyError:
        credentials = MockCredentials()
        storage_clm = AzureStorageCheckpointLeaseManager(
            credentials.storage_account,
            credentials.storage_key,
            credentials.lease_container,
            "lease")
        host = EventProcessorHost(
            MockEventProcessor,
            credentials.eh_address,
            storage_clm)
    return is_live, host


@pytest.fixture()
def eh_partition_pump(eph):
    is_live, host = eph
    lease = AzureBlobLease()
    lease.with_partition_id("1")
    partition_pump = EventHubPartitionPump(host, lease)
    return is_live, partition_pump


@pytest.fixture()
def partition_pump(eph):
    is_live, host = eph
    lease = Lease()
    lease.with_partition_id("1")
    partition_pump = PartitionPump(host, lease)
    return is_live, partition_pump


@pytest.fixture()
def partition_manager(eph):
    is_live, host = eph
    partition_manager = PartitionManager(host)
    return is_live, partition_manager