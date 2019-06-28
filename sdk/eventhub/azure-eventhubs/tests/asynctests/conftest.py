import sys
import pytest
import os

if sys.version_info >= (3, 5):
    import asyncio
    import logging

    from azure.eventprocessorhost.abstract_event_processor import AbstractEventProcessor
    from azure.eventprocessorhost import EventProcessorHost
    from azure.eventprocessorhost import EventHubPartitionPump
    from azure.eventprocessorhost import AzureStorageCheckpointLeaseManager
    from azure.eventprocessorhost import AzureBlobLease
    from azure.eventprocessorhost import EventHubConfig
    from azure.eventprocessorhost.lease import Lease
    from azure.eventprocessorhost.partition_pump import PartitionPump
    from azure.eventprocessorhost.partition_manager import PartitionManager

    class MockEventProcessor(AbstractEventProcessor):
        """
        Mock Implmentation of AbstractEventProcessor for testing
        """

        def __init__(self, params=None):
            """
            Init Event processor
            """
            self.params = params
            self._msg_counter = 0

        async def open_async(self, context):
            """
            Called by processor host to initialize the event processor.
            """
            logging.info("Connection established {}".format(context.partition_id))

        async def close_async(self, context, reason):
            """
            Called by processor host to indicate that the event processor is being stopped.
            (Params) Context:Information about the partition
            """
            logging.info("Connection closed (reason {}, id {}, offset {}, sq_number {})".format(
                reason, context.partition_id, context.offset, context.sequence_number))

        async def process_events_async(self, context, messages):
            """
            Called by the processor host when a batch of events has arrived.
            This is where the real work of the event processor is done.
            (Params) Context: Information about the partition, Messages: The events to be processed.
            """
            logging.info("Events processed {} {}".format(context.partition_id, messages))
            await context.checkpoint_async()

        async def process_error_async(self, context, error):
            """
            Called when the underlying client experiences an error while receiving.
            EventProcessorHost will take care of recovering from the error and
            continuing to pump messages,so no action is required from
            (Params) Context: Information about the partition, Error: The error that occured.
            """
            logging.error("Event Processor Error {!r}".format(error))

@pytest.fixture()
def eph():
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
    except KeyError:
        pytest.skip("Live EventHub configuration not found.")
    return host