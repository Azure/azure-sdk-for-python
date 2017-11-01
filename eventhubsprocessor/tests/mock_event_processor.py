"""
Author: Aaron (Ari) Bornstien
"""
import logging
from eventhubsprocessor.abstract_event_processor import AbstractEventProcessor

class MockEventProcessor(AbstractEventProcessor):
    """
    Mock Implmentation of AbstractEventProcessor for testing
    """
    def __init__(self):
        """
        Init Event processor
        """
        self._msg_counter = 0
    async def open_async(self, context):
        """
        Called by processor host to initialize the event processor.
        """
        logging.info("Connection established %s", context.partition_id)

    async def close_async(self, context, reason):
        """
        Called by processor host to indicate that the event processor is being stopped.
        (Params) Context:Information about the partition
        """
        logging.info("Connection closed (reason %s, id %s, offset %s, sq_number %s)", reason,
                     context.partition_id, context.offset, context.sequence_number)

    async def process_events_async(self, context, messages):
        """
        Called by the processor host when a batch of events has arrived.
        This is where the real work of the event processor is done.
        (Params) Context: Information about the partition, Messages: The events to be processed.
        """
        logging.info("Events processed %s %s", context.partition_id, messages)
        # print("Events processed", context.partition_id, messages)
        await context.checkpoint_async()

    async def process_error_async(self, context, error):
        """
        Called when the underlying client experiences an error while receiving.
        EventProcessorHost will take care of recovering from the error and
        continuing to pump messages,so no action is required from
        (Params) Context: Information about the partition, Error: The error that occured.
        """
        logging.error("Event Processor Error %s ", repr(error))
        await context.host.close_async()
