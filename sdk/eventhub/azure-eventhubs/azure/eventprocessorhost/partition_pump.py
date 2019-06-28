# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# ---------------------

from abc import  abstractmethod
import logging
import asyncio
from azure.eventprocessorhost.partition_context import PartitionContext


_logger = logging.getLogger(__name__)


class PartitionPump():
    """
    Manages individual connection to a given partition.
    """

    def __init__(self, host, lease):
        self.host = host
        self.lease = lease
        self.pump_status = "Uninitialized"
        self.partition_context = None
        self.processor = None
        self.loop = None

    def run(self):
        """
        Makes pump sync so that it can be run in a thread.
        """
        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self.open_async())

    def set_pump_status(self, status):
        """
        Updates pump status and logs update to console.
        """
        self.pump_status = status
        _logger.info("%r partition %r", status, self.lease.partition_id)

    def set_lease(self, new_lease):
        """
        Sets a new partition lease to be processed by the pump.

        :param lease: The lease to set.
        :type lease: ~azure.eventprocessorhost.lease.Lease
        """
        if self.partition_context:
            self.partition_context.lease = new_lease
            self.partition_context.event_processor_context = new_lease.event_processor_context

    async def open_async(self):
        """
        Opens partition pump.
        """
        self.set_pump_status("Opening")
        self.partition_context = PartitionContext(self.host, self.lease.partition_id,
                                                  self.host.eh_config.client_address,
                                                  self.host.eh_config.consumer_group,
                                                  self.loop)
        self.partition_context.lease = self.lease
        self.partition_context.event_processor_context = self.lease.event_processor_context
        self.processor = self.host.event_processor(self.host.event_processor_params)
        try:
            await self.processor.open_async(self.partition_context)
        except Exception as err:  # pylint: disable=broad-except
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
        Event handler for on open event.
        """

    def is_closing(self):
        """
        Returns whether pump is closing.

        :rtype: bool
        """
        return self.pump_status == "Closing" or self.pump_status == "Closed"

    async def close_async(self, reason):
        """
        Safely closes the pump.

        :param reason: The reason for the shutdown.
        :type reason: str
        """
        self.set_pump_status("Closing")
        try:
            await self.on_closing_async(reason)
            if self.processor:
                _logger.info("PartitionPumpInvokeProcessorCloseStart %r %r %r",
                             self.host.guid, self.partition_context.partition_id, reason)
                await self.processor.close_async(self.partition_context, reason)
                _logger.info("PartitionPumpInvokeProcessorCloseStart %r %r",
                             self.host.guid, self.partition_context.partition_id)
        except Exception as err:  # pylint: disable=broad-except
            await self.process_error_async(err)
            _logger.error("%r %r %r", self.host.guid, self.partition_context.partition_id, err)
            raise err

        if reason == "LeaseLost":
            try:
                _logger.info("Lease Lost releasing ownership")
                await self.host.storage_manager.release_lease_async(self.partition_context.lease)
            except Exception as err:  # pylint: disable=broad-except
                _logger.error("%r %r %r", self.host.guid, self.partition_context.partition_id, err)
                raise err

        self.set_pump_status("Closed")

    @abstractmethod
    async def on_closing_async(self, reason):
        """
        Event handler for on closing event.

        :param reason: The reason for the shutdown.
        :type reason: str
        """

    async def process_events_async(self, events):
        """
        Process pump events.

        :param events: List of events to be processed.
        :type events: list[~azure.eventhub.common.EventData]
        """
        if events:
            # Synchronize to serialize calls to the processor. The handler is not installed until
            # after OpenAsync returns, so ProcessEventsAsync cannot conflict with OpenAsync. There
            # could be a conflict between ProcessEventsAsync and CloseAsync, however. All calls to
            # CloseAsync are protected by synchronizing too.
            try:
                last = events[-1]
                if last is not None:
                    self.partition_context.set_offset_and_sequence_number(last)
                    await self.processor.process_events_async(self.partition_context, events)
            except Exception as err:  # pylint: disable=broad-except
                await self.process_error_async(err)

    async def process_error_async(self, error):
        """
        Passes error to the event processor for processing.

        :param error: An error the occurred.
        :type error: Exception
        """
        await self.processor.process_error_async(self.partition_context, error)
