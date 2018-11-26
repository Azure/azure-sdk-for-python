# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import logging
import asyncio
import sys
import os
import argparse
from logging.handlers import RotatingFileHandler

from azure.eventprocessorhost import (
    AbstractEventProcessor,
    AzureStorageCheckpointLeaseManager,
    EventHubConfig,
    EventProcessorHost,
    EPHOptions)


def get_logger(filename, level=logging.INFO):
    azure_logger = logging.getLogger("azure")
    azure_logger.setLevel(level)
    uamqp_logger = logging.getLogger("uamqp")
    uamqp_logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    azure_logger.addHandler(console_handler)
    uamqp_logger.addHandler(console_handler)

    if filename:
        file_handler = RotatingFileHandler(filename, maxBytes=20*1024*1024, backupCount=3)
        file_handler.setFormatter(formatter)
        azure_logger.addHandler(file_handler)
        uamqp_logger.addHandler(file_handler)

    return azure_logger

logger = get_logger("eph_test_async.log", logging.INFO)


class EventProcessor(AbstractEventProcessor):
    """
    Example Implmentation of AbstractEventProcessor
    """

    def __init__(self, params=None):
        """
        Init Event processor
        """
        super().__init__(params)
        self._msg_counter = 0

    async def open_async(self, context):
        """
        Called by processor host to initialize the event processor.
        """
        logger.info("Connection established {}".format(context.partition_id))

    async def close_async(self, context, reason):
        """
        Called by processor host to indicate that the event processor is being stopped.
        :param context: Information about the partition
        :type context: ~azure.eventprocessorhost.PartitionContext
        """
        logger.info("Connection closed (reason {}, id {}, offset {}, sq_number {})".format(
            reason,
            context.partition_id,
            context.offset,
            context.sequence_number))

    async def process_events_async(self, context, messages):
        """
        Called by the processor host when a batch of events has arrived.
        This is where the real work of the event processor is done.
        :param context: Information about the partition
        :type context: ~azure.eventprocessorhost.PartitionContext
        :param messages: The events to be processed.
        :type messages: list[~azure.eventhub.common.EventData]
        """
        print("Processing id {}, offset {}, sq_number {})".format(
            context.partition_id,
            context.offset,
            context.sequence_number))
        await context.checkpoint_async()

    async def process_error_async(self, context, error):
        """
        Called when the underlying client experiences an error while receiving.
        EventProcessorHost will take care of recovering from the error and
        continuing to pump messages,so no action is required from
        :param context: Information about the partition
        :type context: ~azure.eventprocessorhost.PartitionContext
        :param error: The error that occured.
        """
        logger.info("Event Processor Error for partition {}, {!r}".format(context.partition_id, error))


async def wait_and_close(host, duration):
    """
    Run EventProcessorHost for 30 seconds then shutdown.
    """
    await asyncio.sleep(duration)
    await host.close_async()


def test_long_running_eph():
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=30)
    parser.add_argument("--storage-account", help="Storage account name", default=os.environ.get('AZURE_STORAGE_ACCOUNT'))
    parser.add_argument("--storage-key", help="Storage account access key", default=os.environ.get('AZURE_STORAGE_ACCESS_KEY'))
    parser.add_argument("--container", help="Lease container name", default="leases")
    parser.add_argument("--eventhub", help="Name of EventHub", default=os.environ.get('EVENT_HUB_NAME'))
    parser.add_argument("--namespace", help="Namespace of EventHub", default=os.environ.get('EVENT_HUB_NAMESPACE'))
    parser.add_argument("--suffix", help="Namespace of EventHub", default="servicebus.windows.net")
    parser.add_argument("--sas-policy", help="Name of the shared access policy to authenticate with", default=os.environ.get('EVENT_HUB_SAS_POLICY'))
    parser.add_argument("--sas-key", help="Shared access key", default=os.environ.get('EVENT_HUB_SAS_KEY'))

    loop = asyncio.get_event_loop()
    args, _ = parser.parse_known_args()
    if not args.namespace or not args.eventhub:
        try:
            import pytest
            pytest.skip("Must specify '--namespace' and '--eventhub'")
        except ImportError:
            raise ValueError("Must specify '--namespace' and '--eventhub'")

    # Eventhub config and storage manager 
    eh_config = EventHubConfig(
        args.namespace,
        args.eventhub,
        args.sas_policy,
        args.sas_key,
        consumer_group="$default",
        namespace_suffix=args.suffix)
    eh_options = EPHOptions()
    eh_options.release_pump_on_timeout = True
    eh_options.debug_trace = False
    eh_options.receive_timeout = 120
    storage_manager = AzureStorageCheckpointLeaseManager(
        storage_account_name=args.storage_account,
        storage_account_key=args.storage_key,
        lease_renew_interval=30,
        lease_container_name=args.container,
        lease_duration=60)

    # Event loop and host
    host = EventProcessorHost(
        EventProcessor,
        eh_config,
        storage_manager,
        ep_params=["param1","param2"],
        eph_options=eh_options,
        loop=loop)

    tasks = asyncio.gather(
        host.open_async(),
        wait_and_close(host, args.duration), return_exceptions=True)
    results = loop.run_until_complete(tasks)
    assert not any(results)


if __name__ == '__main__':
    test_long_running_eph()
