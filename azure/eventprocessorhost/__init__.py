# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
The module provides a means to process Azure Event Hubs events at scale.
"""
try:
    from azure.eventprocessorhost.abstract_event_processor import AbstractEventProcessor
    from azure.eventprocessorhost.azure_storage_checkpoint_manager import AzureStorageCheckpointLeaseManager
    from azure.eventprocessorhost.azure_blob_lease import AzureBlobLease
    from azure.eventprocessorhost.checkpoint import Checkpoint
    from azure.eventprocessorhost.eh_config import EventHubConfig
    from azure.eventprocessorhost.eh_partition_pump import EventHubPartitionPump, PartitionReceiver
    from azure.eventprocessorhost.eph import EventProcessorHost, EPHOptions
    from azure.eventprocessorhost.partition_manager import PartitionManager
    from azure.eventprocessorhost.partition_context import PartitionContext
    from azure.eventprocessorhost.partition_pump import PartitionPump
except (SyntaxError, ImportError):
    raise ImportError("EventProcessHost is only compatible with Python 3.5 and above.")
