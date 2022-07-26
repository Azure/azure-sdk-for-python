#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Examples to show sending events in buffered mode to an Event Hub asynchronously.
"""

import time
import asyncio
import os

from azure.eventhub.aio import EventHubProducerClient, EventHubConsumerClient
from azure.eventhub import EventData
import logging
import sys

CONNECTION_STR = 'Endpoint=sb://eh-kashifk.servicebus.windows.net/;SharedAccessKeyName=eh-kashifk-hub-auth-rule;SharedAccessKey=S/C7Flbd12GnG/B/HeKDKukdtMU1RCXq7f5XmvIy2Nk=;EntityPath=eh-kashifk-hub'
EVENTHUB_NAME = 'eh-kashifk-hub'

logging.basicConfig(format=logging.BASIC_FORMAT)
log = logging.getLogger("azure")
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
log.addHandler(handler)

sent_count = 0
received_count = 0

async def on_success(events, pid):
    # sending succeeded
    #print(events, pid)
    global sent_count
    log.info("flushed")
    sent_count += len(events)


async def on_error(events, pid, error):
    # sending failed
    #print(events, pid, error)
    log.error("error flushing")

async def on_event(partition_context, event):
    global received_count
    received_count += 1




payload = """
{
  "idImagem": "02032asdfasdfasdfasdfa1090-F01.jpg",
  "dataHoraTz": "2022-07-21T16:50:25-03:00",
  "camera": {
    "numero": "Lasdfasdfasdf325"
  },
  "empresa": "AasdfasdfsRIS",
  "dataHora": "2022-07-21 16:50:25",
  "key": "4asdfasdfasasdfasdfas4BD7Fasdfasdfasdfas",
  "placa": "Rasdfasdfasdfasdf3",
  "dataRecebimento": "2022-07-21T16:50:45.499461-03:00",
  "codigoLog": "2022072asdfasdfasdfasdfasdfas20325"
}
"""

producer = EventHubProducerClient.from_connection_string(
    conn_str=CONNECTION_STR,
    auth_timeout=3, 
    retry_total=3, 
    retry_mode='fixed',
    retry_backoff_factor=0.01,
    eventhub_name=EVENTHUB_NAME,
    buffered_mode=True,
    on_success=on_success,
    on_error=on_error,
    max_wait_time = 10,
    max_buffer_length=100,
    logging_enable=True
)

consumer = EventHubConsumerClient.from_connection_string(conn_str=CONNECTION_STR, consumer_group="$default")
receive_thread = asyncio.ensure_future(consumer.receive(on_event=on_event))

async def publish(timeout):
    for i in range(100):
        await producer.send_event(EventData(payload))
        log.info("Enqueued message")
        await asyncio.sleep(timeout)

    print("Sleeping")
    await asyncio.sleep(11)


if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(publish(.1))
        print(f"Sent {sent_count}")
        print(f"Received {received_count}")
    except Exception as err:
        log.exception(err)