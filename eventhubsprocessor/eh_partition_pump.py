"""
Author: Aaron (Ari) Bornstien
"""
from queue import Queue
from threading import Thread
from eventhubs.client import EventHubClient, EventData, Receiver
from eventhubsprocessor.partition_pump import PartitionPump

class EventHubPartitionPump(PartitionPump):
    """Pulls and messages from lease partition from eventhub and sends them to processor """
    def __init__(self, host, lease):
        PartitionPump.__init__(self, host, lease)
        self.msg_queue = None
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
                last_exception = err
                _retry_count += 1

        if not _opened_ok:
            await self.processor.process_error_async(self.partition_context, last_exception)
            self.set_pump_status("OpenFailed")

        if self.pump_status == "Opening":
            self.set_pump_status("Running")
            Thread(target=self.eh_client.run).start()  # populate message queue in new thread
            await self.partition_receiver.run() # process message queue using reciever

        if self.pump_status == "OpenFailed":
            self.set_pump_status("Closing")
            await self.clean_up_clients_async()
            self.set_pump_status("Closed")

    async def open_clients_async(self):
        """
        Responsible for establishing connection to event hub client
        throws EventHubsException, IOException, InterruptedException, ExecutionException
        """
        start_at = await self.partition_context.get_initial_offset_async()
        epoch = self.lease.epoch
        self.msg_queue = Queue()
        # Create event hub client and receive handler and set options
        self.partition_receive_handler = PartitionReceiveHandler(self.partition_context.consumer_group_name,
                                                                 self.partition_context.partition_id, start_at, self)
        self.partition_receive_handler.prefetch = self.host.eh_options.prefetch_count
        self.eh_client = EventHubClient(self.host.eh_connection_string,
                                        self.partition_receive_handler)
        self.partition_receive_handler.client = self.eh_client
        self.partition_receiver = PartitionReceiver(self)   # Create a reciever to process the msg_queue

    async def clean_up_clients_async(self):
        """
        Resets the pump swallows all exceptions
        """
        if self.partition_receiver:
            # Taking the lock means that there is no ProcessEventsAsync call in progress. (Lock TBI)
            if self.eh_client:
                self.eh_client.stop()
                self.partition_receiver = None
                self.partition_receive_handler = None
                self.eh_client = None
                self.msg_queue = None

    async def on_closing_async(self, reason):
        """
        Overides partition pump on cleasing
        """
        await self.clean_up_clients_async()

class PartitionReceiveHandler(Receiver):
    """
    Runs the event client to pull n messages and put them in to an
    event queue for processing then terminate. Will want to replace the
    n message mechanism with a time out associated with the leasee 
    """
    def __init__(self, consumer_group, partition, offset, eh_partition_pump):
        super(PartitionReceiveHandler, self).__init__(consumer_group, partition, offset)
        self.eh_partition_pump = eh_partition_pump
        self.max_batch_size = self.eh_partition_pump.host.eh_options.max_batch_size
        self._msg_count = 0
        self.total = 0
        self.last_sn = -1
        self.last_offset = offset

    def on_event_data(self, message):
        """
        Process one event data. This method is called on the thread that the EH client uses
        to run the pump.There is one pump per EventHubClient. Since each PartitionPump
        creates a new EventHubClient, using that thread to call OnEvents does no harm.
        Even if OnEvents is slow, the pump will get control back each time OnEvents returns,
        and be able to receive a new batch of messages with which to make the next OnEvents
        call.The pump gains nothing by running faster than OnEvents. 
        """
        try:
            if self._msg_count < self.max_batch_size:
                self.last_offset = EventData.offset(message)
                self.last_sn = EventData.sequence_number(message)
                self.eh_partition_pump.msg_queue.put(message)
                self._msg_count += 1
                print(message, self._msg_count)
            else:
                self.client.stop()
        except:
            # TBI Push Error to QUEUE
            self.client.stop()

class PartitionReceiver:
    """
    Sends events from a queue until lease is lost
    """
    def __init__(self, eh_partition_pump):
        self.eh_partition_pump = eh_partition_pump
        self.max_batch_size = self.eh_partition_pump.host.eh_options.max_batch_size
        self._msg_count = 0

    async def run(self):
        """
        Runs the async partion reciever event loop to retrive messages from the event queue
        """
        while self._msg_count < self.max_batch_size:
            msg = self.eh_partition_pump.msg_queue.get()
            await self.process_events_async([msg])
            self._msg_count += 1

    async def process_events_async(self, events):
        """
        # This method is called on the thread that the EH client uses to run the pump.
        # There is one pump per EventHubClient. Since each PartitionPump creates a
        # new EventHubClient,using that thread to call OnEvents does no harm. Even if OnEvents
        # is slow, the pump will get control back each time OnEvents returns, and be able to receive
        # a new batch of messages with which to make the next OnEvents call.The pump gains nothing
        # by running faster than OnEvents.
        """
        print(events)
        await self.eh_partition_pump.process_events_async(events)

    async def process_error_async(self, error):
        """
        Handles processing errors this is never called since python recieve client doesn't
        have error handling implemented (TBD add fault pump handling)
        """ 
        try:     
            await self.eh_partition_pump.process_error_async(error) # We would like to deliver all errors in the pump to error handler.     
        finally:                    
            self.eh_partition_pump.set_pump_status("Errored")
