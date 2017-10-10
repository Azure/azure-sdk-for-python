"""
Author: Aaron (Ari) Bornstien
"""
from abc import  abstractmethod
from eventhubsprocessor.partition_context import PartitionContext

class PartitionPump():
    """
    Manages individual connection to a given partition
    Note to self might be missing a lock check if you run in to race condtion
    """
    def __init__(self, host, lease):
        self.host = host
        self.lease = lease
        self.pump_status = "Uninitialized"
        self.partition_context = None
        self.processor = None
        # self.ProcessingAsyncLock = Lock()

    def set_pump_status(self, status):
        """
        Updates pump status and prints/logs update to console
        """
        self.pump_status = status
        print(status, "partition ", self.lease.partition_id)

    def set_lease(self, new_lease):
        """
        Sets a new partition lease to be processed by the pump
        """
        if self.partition_context:
            self.partition_context.lease = new_lease

    async def open_async(self):
        """
        Opens partition pump
        """
        self.set_pump_status("Opening")
        self.partition_context = PartitionContext(self.host, self.lease.partition_id,
                                                  self.host.eh_connection_string,
                                                  self.host.consumer_group_name)
        self.partition_context.lease = self.lease
        self.processor = self.host.event_processor()
        try:
            await self.processor.open_async(self.partition_context)
        except Exception as err:
            # If the processor won't create or open, only thing we can do here is pass the buck.
            # Null it out so we don't try to operate on it further.
            await self.process_error_async(err)
            self.processor = None
            self.set_pump_status("OpenFailed")

        # If Open Async Didn't Fail call OnOpenAsync
        if self.pump_status == "Opening":
            await self.on_open_async()

    @abstractmethod
    async def on_open_async(self):
        """
        Event handler for on open event
        """
        pass

    def is_closing(self):
        """
        Returns whether pump is closing
        """
        return self.pump_status == "Closing" or self.pump_status == "Closed"

    async def close_async(self, reason):
        """
        Safely closes the pump
        """
        self.set_pump_status("Closing")
        try:
            await self.on_closing_async(reason)
            if self.processor:
                # Might need a ProcessingAsyncLock here to prevent sync conflicts with
                # ProcessEventsAsync will investigate with (yield from self.ProcessingAsyncLock):
                # When we take the lock, any existing ProcessEventsAsync call has finished.
                # Because the client has been closed, there will not be any more
                # calls to onEvents in the future. Therefore we can safely call CloseAsync.
                await self.processor.close_async(self.partition_context, reason)

        except Exception as err:
            await self.process_error_async(err) #put exception condition handleing here

        if reason == "LeaseLost":
            pass #release the lease here

        self.set_pump_status("Closed")

    @abstractmethod
    async def on_closing_async(self, reason):
        """
        Event handler for on closing event
        """
        pass

    async def process_events_async(self, events):
        """
        Process pump events.
        """
        if events:
            # Synchronize to serialize calls to the processor. The handler is not installed until
            # after OpenAsync returns, so ProcessEventsAsync cannot conflict with OpenAsync. There
            # could be a conflict between ProcessEventsAsync and CloseAsync, however. All calls to
            # CloseAsync are protected by synchronizing too.Might need a ProcessingAsyncLock here to
            # prevent sync conflicts with closeAsync will investigate
            # with (yield from self.ProcessingAsyncLock):
            try:
                last = events[-1:]
                if last != None:
                    self.partition_context.set_offset_and_sequence_number(last)
                    await self.processor.process_events_async(self.partition_context, events)
            except Exception as err:
                await self.process_error_async(err)

    async def process_error_async(self, error):
        """
        Passes error to the event processor for processing.
        """
        return self.processor.process_error_async(self.partition_context, error)
