"""
Author: Aaron (Ari) Bornstien
"""
import logging
import asyncio
from eventhubs import EventHubClient, Offset
from eventhubs.async import AsyncReceiver
from eventhubsprocessor.partition_pump import PartitionPump

class EventHubPartitionPump(PartitionPump):
    """
    Pulls and messages from lease partition from eventhub and sends them to processor
    """
    def __init__(self, host, lease):
        PartitionPump.__init__(self, host, lease)
        self.eh_client = None
        self.partition_receiver = None
        self.partition_receive_handler = None

    async def on_open_async(self):
        """
        Eventhub Override for on_open_async
        """
        _opened_ok = False
        _retry_count = 0
        while (not _opened_ok) and (_retry_count < 5):
            try:
                await self.open_clients_async()
                _opened_ok = True
            except Exception as err:
                logging.warning("%s,%s PartitionPumpWarning: Failure creating client or receiver,\
                                retrying: %s", self.host.guid, self.partition_context.partition_id,
                                repr(err))
                last_exception = err
                _retry_count += 1

        if not _opened_ok:
            await self.processor.process_error_async(self.partition_context, last_exception)
            self.set_pump_status("OpenFailed")

        if self.pump_status == "Opening":
            self.set_pump_status("Running")
            self.eh_client.run_daemon()
            await self.partition_receiver.run()

        if self.pump_status == "OpenFailed":
            self.set_pump_status("Closing")
            await self.clean_up_clients_async()
            self.set_pump_status("Closed")

    async def open_clients_async(self):
        """
        Responsible for establishing connection to event hub client
        throws EventHubsException, IOException, InterruptedException, ExecutionException
        """
        await self.partition_context.get_initial_offset_async()
        # Create event hub client and receive handler and set options
 
        self.partition_receive_handler = AsyncReceiver()
        self.eh_client = EventHubClient(self.host.eh_connection_string) \
                        .subscribe(self.partition_receive_handler,
                                   self.partition_context.consumer_group_name,
                                   self.partition_context.partition_id,
                                   Offset(self.partition_context.offset))
        self.partition_receiver = PartitionReceiver(self)

    async def clean_up_clients_async(self):
        """
        Resets the pump swallows all exceptions
        """
        if self.partition_receiver:
            if self.eh_client:
                self.eh_client.stop()
                self.partition_receiver = None
                self.partition_receive_handler = None
                self.eh_client = None

    async def on_closing_async(self, reason):
        """
        Overides partition pump on cleasing
        """
        await self.clean_up_clients_async()

class PartitionReceiver:
    """
    Sends events from a async until lease is lost
    """
    def __init__(self, eh_partition_pump):
        self.eh_partition_pump = eh_partition_pump
        self.max_batch_size = self.eh_partition_pump.host.eh_options.max_batch_size
        self.recieve_timeout = self.eh_partition_pump.host.eh_options.receive_timeout

    async def run(self):
        """
        Runs the async partion reciever event loop to retrive messages from the event queue
        """
        # Implement pull max batch from queue instead of one message at a time
        while not self.eh_partition_pump.is_closing() \
              or self.eh_partition_pump.pump_status == "Errored":
            try:
                msgs = await asyncio.wait_for(self.eh_partition_pump.\
                                                   partition_receive_handler. \
                                                   receive(self.max_batch_size),
                                              self.recieve_timeout)
                await self.process_events_async(msgs)
            except asyncio.TimeoutError:
                if self.eh_partition_pump.partition_receive_handler.messages:
                    logging.info("No events received, queue size %d, delivered %d",
                                self.eh_partition_pump.partition_receive_handler.messages.qsize(),
                                self.eh_partition_pump.partition_receive_handler.delivered)

    async def process_events_async(self, events):
        """
        # This method is called on the thread that the EH client uses to run the pump.
        # There is one pump per EventHubClient. Since each PartitionPump creates a
        # new EventHubClient,using that thread to call OnEvents does no harm. Even if OnEvents
        # is slow, the pump will get control back each time OnEvents returns, and be able to receive
        # a new batch of messages with which to make the next OnEvents call.The pump gains nothing
        # by running faster than OnEvents.
        """
        await self.eh_partition_pump.process_events_async(events)

    async def process_error_async(self, error):
        """
        Handles processing errors this is never called since python recieve client doesn't
        have error handling implemented (TBD add fault pump handling)
        """
        try:
            await self.eh_partition_pump.process_error_async(error)
        finally:
            self.eh_partition_pump.set_pump_status("Errored")
