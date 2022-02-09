# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import dotenv
import time
import logging
from concurrent.futures import ThreadPoolExecutor

from azure.eventhub import EventHubProducerClient, EventData

logger = logging.getLogger('PRELOAD_EVENTS')
logger.setLevel(logging.INFO)

dotenv.load_dotenv()
connect_strs = [
    os.environ["EVENT_HUB_CONN_STR_BASIC_NORTHEU"],
    os.environ["EVENT_HUB_CONN_STR_STANDARD_NORTHEU"],
    os.environ["EVENT_HUB_CONN_STR_BASIC_WESTUS2"],
    os.environ["EVENT_HUB_CONN_STR_STANDARD_WESTUS2"]
]

eh_name_size_pairs = [
    ('pyamqp_512', 512),
]

EVENT_DATA_COUNT = 2_000_000
PARTITION_ID = "0"


def pre_prepare_client(client, data):
    client.create_batch()  # precall to retrieve sender link settings
    client.send_batch([EventData(data)])  # precall to set up the sender link


def send_batch_message(conn_str, eventhub_name, num_of_events, single_event_size, run_times=1, description=None):
    client = EventHubProducerClient.from_connection_string(
        conn_str=conn_str, eventhub_name=eventhub_name
    )

    data = b'a' * single_event_size
    pre_prepare_client(client, data)

    for _ in range(run_times):  # run run_times and calculate the avg performance
        start_time = time.time()
        batch = client.create_batch(partition_id="0")
        for _ in range(num_of_events):
            try:
                batch.add(EventData(data))
            except ValueError:
                # Batch full
                client.send_batch(batch)
                logger.info(
                    'Time{}: {} events of size {} sent to eh {}/{}'.format(
                        time.time(), len(batch), single_event_size, conn_str, eventhub_name
                    )
                )
                batch = client.create_batch(partition_id=PARTITION_ID)
                batch.add(EventData(data))

        client.send_batch(batch)
        logger.info(
            'Finished! Time{}: {} events of size {} sent to eh {}/{}'.format(
                time.time(), len(batch), single_event_size, conn_str, eventhub_name
            )
        )

    client.close()
    return "Success for {}".format(eventhub_name)


if __name__ == '__main__':
    logger.info('------------------- START PREPARATION -------------------')

    executor = ThreadPoolExecutor()

    futures = []
    for conn_str in connect_strs:
        for eh_name, event_size in eh_name_size_pairs:
            futures.append(
                executor.submit(
                    send_batch_message,
                    conn_str,
                    eh_name,
                    EVENT_DATA_COUNT,
                    event_size
                )
            )

    for future in futures:
        print(future.result())

    logger.info('------------------- END PREPARATION -------------------')
