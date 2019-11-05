# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import logging
import asyncio
from azure.eventhub import Offset, EventHubClientAsync
from azure.eventprocessorhost.partition_pump import PartitionPump


_logger = logging.getLogger(__name__)


class EventHubPartitionPump(PartitionPump):
    """
    Pulls and messages from lease partition from eventhub and sends them to processor.
    """

    def __init__(self, host, lease):
        PartitionPump.__init__(self, host, lease)
        self.eh_client = None
        self.partition_receiver = None
        self.partition_receive_handler = None
        self.running = None

    async def on_open_async(self):
        """
        Eventhub Override for on_open_async.
        """
        _opened_ok = False
        _retry_count = 0
        last_exception = None

        while (not _opened_ok) and (_retry_count < 5):
            try:
                await self.open_clients_async()
                _opened_ok = True
            except Exception as err:  # pylint: disable=broad-except
                _logger.warning(
                    "%r,%r PartitionPumpWarning: Failure creating client or receiver, retrying: %r",
                    self.host.guid, self.partition_context.partition_id, err)
                last_exception = err
                _retry_count += 1

        if not _opened_ok:
            await self.processor.process_error_async(self.partition_context, last_exception)
            self.set_pump_status("OpenFailed")

        _started_ok = False
        _retry_count = 0

        if self.pump_status == "Opening":
            loop = asyncio.get_event_loop()
            while (not _started_ok) and (_retry_count < 5):
                try:
                    await self.eh_client.run_async()
                    _started_ok = True
                except Exception as err:
                    _logger.warning(
                        "%r,%r PartitionPumpWarning: Failure starting client or receiver, retrying: %r",
                        self.host.guid, self.partition_context.partition_id, err)
                    last_exception = err
                    _retry_count += 1

            if not _started_ok:
                _logger.warning(
                    "%r,%r PartitionPumpWarning: Failure starting client or receiver: %r",
                    self.host.guid, self.partition_context.partition_id, last_exception)
                await self.process_error_async(self.partition_context, last_exception)
                self.set_pump_status("Errored")
            else:
                self.running = loop.create_task(self.partition_receiver.run())
                self.set_pump_status("Running")

        if self.pump_status in ["OpenFailed", "Errored"]:
            self.set_pump_status("Closing")
            await self.clean_up_clients_async()
            self.set_pump_status("Closed")

    async def open_clients_async(self):
        """
        Responsible for establishing connection to event hub client
        throws EventHubsException, IOException, InterruptedException, ExecutionException.
        """
        await self.partition_context.get_initial_offset_async()
        # Create event hub client and receive handler and set options
        self.eh_client = EventHubClientAsync(
            self.host.eh_config.client_address,
            debug=self.host.eph_options.debug_trace,
            http_proxy=self.host.eph_options.http_proxy)
        self.partition_receive_handler = self.eh_client.add_async_receiver(
            self.partition_context.consumer_group_name,
            self.partition_context.partition_id,
            Offset(self.partition_context.offset),
            prefetch=self.host.eph_options.prefetch_count,
            keep_alive=self.host.eph_options.keep_alive_interval,
            auto_reconnect=self.host.eph_options.auto_reconnect_on_error,
            loop=self.loop)
        self.partition_receiver = PartitionReceiver(self)

    async def clean_up_clients_async(self):
        """
        Resets the pump swallows all exceptions.
        """
        if self.partition_receiver:
            if self.eh_client:
                await self.eh_client.stop_async()
                self.partition_receiver = None
                self.partition_receive_handler = None
                self.eh_client = None

    async def on_closing_async(self, reason):
        """
        Overides partition pump on closing.

        :param reason: The reason for the shutdown.
        :type reason: str
        """
        self.partition_receiver.eh_partition_pump.set_pump_status("Errored")
        try:
            await self.running
        except TypeError:
            _logger.debug("No partition pump running.")
        except Exception as err:  # pylint: disable=broad-except
            _logger.info("Error on closing partition pump: %r", err)
        await self.clean_up_clients_async()


class PartitionReceiver:
    """
    Recieves events asynchronously until lease is lost.
    """

    def __init__(self, eh_partition_pump):
        self.eh_partition_pump = eh_partition_pump
        self.max_batch_size = self.eh_partition_pump.host.eph_options.max_batch_size
        self.recieve_timeout = self.eh_partition_pump.host.eph_options.receive_timeout

    async def run(self):
        """
        Runs the async partion reciever event loop to retrive messages from the event queue.
        """
        # Implement pull max batch from queue instead of one message at a time
        while self.eh_partition_pump.pump_status != "Errored" and not self.eh_partition_pump.is_closing():
            if self.eh_partition_pump.partition_receive_handler:
                try:
                    msgs = await self.eh_partition_pump.partition_receive_handler.receive(
                        max_batch_size=self.max_batch_size,
                        timeout=self.recieve_timeout)
                except Exception as e:  # pylint: disable=broad-except
                    _logger.info("Error raised while attempting to receive messages: %r", e)
                    await self.process_error_async(e)
                else:
                    if not msgs:
                        _logger.info("No events received, queue size %r, release %r",
                                     self.eh_partition_pump.partition_receive_handler.queue_size,
                                     self.eh_partition_pump.host.eph_options.release_pump_on_timeout)
                        if self.eh_partition_pump.host.eph_options.release_pump_on_timeout:
                            await self.process_error_async(TimeoutError("No events received"))
                    else:
                        await self.process_events_async(msgs)

    async def process_events_async(self, events):
        """
        This method is called on the thread that the EH client uses to run the pump.
        There is one pump per EventHubClient. Since each PartitionPump creates a
        new EventHubClient, using that thread to call OnEvents does no harm. Even if OnEvents
        is slow, the pump will get control back each time OnEvents returns, and be able to receive
        a new batch of messages with which to make the next OnEvents call.The pump gains nothing
        by running faster than OnEvents.

        :param events: List of events to be processed.
        :type events: list of ~azure.eventhub.common.EventData
        """
        await self.eh_partition_pump.process_events_async(events)

    async def process_error_async(self, error):
        """
        Handles processing errors this is never called since python recieve client doesn't
        have error handling implemented (TBD add fault pump handling).

        :param error: An error the occurred.
        :type error: Exception
        """
        try:
            await self.eh_partition_pump.process_error_async(error)
        finally:
            self.eh_partition_pump.set_pump_status("Errored")
