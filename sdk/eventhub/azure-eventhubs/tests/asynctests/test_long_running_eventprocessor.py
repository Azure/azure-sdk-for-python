# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# -----------------------------------------------------------------------------------

import logging
import asyncio
import sys
import os
import argparse
import time
import pytest
from logging.handlers import RotatingFileHandler

from azure.eventhub.aio import EventHubClient
from azure.eventhub.eventprocessor import EventProcessor, PartitionProcessor, Sqlite3PartitionManager
from azure.eventhub import EventData


def get_logger(filename, level=logging.INFO):
    azure_logger = logging.getLogger("azure.eventhub.eventprocessor")
    azure_logger.setLevel(level)
    uamqp_logger = logging.getLogger("uamqp")
    uamqp_logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    if not azure_logger.handlers:
        azure_logger.addHandler(console_handler)
    if not uamqp_logger.handlers:
        uamqp_logger.addHandler(console_handler)

    if filename:
        file_handler = RotatingFileHandler(filename, maxBytes=20*1024*1024, backupCount=3)
        file_handler.setFormatter(formatter)
        azure_logger.addHandler(file_handler)
        uamqp_logger.addHandler(file_handler)

    return azure_logger


logger = get_logger("eph_test_async.log", logging.INFO)


class MyEventProcessor(PartitionProcessor):
    async def close(self, reason):
        logger.info("PartitionProcessor closed (reason {}, id {})".format(
            reason,
            self._checkpoint_manager.partition_id
        ))

    async def process_events(self, events):
        if events:
            event = events[-1]
            print("Processing id {}, offset {}, sq_number {})".format(
                self._checkpoint_manager.partition_id,
                event.offset,
                event.sequence_number))
            await self._checkpoint_manager.update_checkpoint(event.offset, event.sequence_number)

    async def process_error(self, error):
        logger.info("Event Processor Error for partition {}, {!r}".format(self._checkpoint_manager.partition_id, error))


async def wait_and_close(host, duration):
    """
    Run EventProcessorHost for 30 seconds then shutdown.
    """
    await asyncio.sleep(duration)
    await host.stop()


async def pump(pid, sender, duration):
    deadline = time.time() + duration
    total = 0

    try:
        async with sender:
            event_list = []
            while time.time() < deadline:
                data = EventData(body=b"D" * 512)
                event_list.append(data)
                total += 1
                if total % 100 == 0:
                    await sender.send(event_list)
                    event_list = []
                    logger.info("{}: Send total {}".format(pid, total))
    except Exception as err:
        logger.error("{}: Send failed {}".format(pid, err))
        raise
    print("{}: Final Sent total {}".format(pid, total))


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_long_running_eph(live_eventhub):
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", help="Duration in seconds of the test", type=int, default=30)
    parser.add_argument("--container", help="Lease container name", default="nocontextleases")
    parser.add_argument("--eventhub", help="Name of EventHub", default=live_eventhub['event_hub'])
    parser.add_argument("--namespace", help="Namespace of EventHub", default=live_eventhub['namespace'])
    parser.add_argument("--suffix", help="Namespace of EventHub", default="servicebus.windows.net")
    parser.add_argument("--sas-policy", help="Name of the shared access policy to authenticate with", default=live_eventhub['key_name'])
    parser.add_argument("--sas-key", help="Shared access key", default=live_eventhub['access_key'])

    loop = asyncio.get_event_loop()
    args, _ = parser.parse_known_args()
    if not args.namespace or not args.eventhub:
        try:
            import pytest
            pytest.skip("Must specify '--namespace' and '--eventhub'")
        except ImportError:
            raise ValueError("Must specify '--namespace' and '--eventhub'")

    # Queue up some events in the Eventhub
    conn_str = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
        live_eventhub['hostname'],
        live_eventhub['key_name'],
        live_eventhub['access_key'],
        live_eventhub['event_hub'])
    client = EventHubClient.from_connection_string(conn_str)
    pumps = []
    for pid in ["0", "1"]:
        sender = client.create_producer(partition_id=pid, send_timeout=0)
        pumps.append(pump(pid, sender, 15))
    results = await asyncio.gather(*pumps, return_exceptions=True)

    assert not any(results)

    # Event loop and host
    host = EventProcessor(
        client,
        live_eventhub['consumer_group'],
        MyEventProcessor,
        Sqlite3PartitionManager()
    )

    tasks = asyncio.gather(
        host.start(),
        wait_and_close(host, args.duration), return_exceptions=True)
    results = await tasks
    assert not any(results)


if __name__ == '__main__':
    config = {}
    config['hostname'] = os.environ['EVENT_HUB_HOSTNAME']
    config['event_hub'] = os.environ['EVENT_HUB_NAME']
    config['key_name'] = os.environ['EVENT_HUB_SAS_POLICY']
    config['access_key'] = os.environ['EVENT_HUB_SAS_KEY']
    config['namespace'] = os.environ['EVENT_HUB_NAMESPACE']
    config['consumer_group'] = "$Default"
    config['partition'] = "0"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_long_running_eph(config))