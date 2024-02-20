# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import dotenv
import time
import logging
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor

from azure.eventhub import EventHubProducerClient, EventData

logger = logging.getLogger('SEND_PERF_TEST')
logger.setLevel(logging.INFO)
logger.addHandler(RotatingFileHandler("send_perf_test.log"))

dotenv.load_dotenv()
CONN_STRS = [
    os.environ["EVENT_HUB_CONN_STR_BASIC_NORTHEU"],
    os.environ["EVENT_HUB_CONN_STR_STANDARD_NORTHEU"],
    os.environ["EVENT_HUB_CONN_STR_BASIC_WESTUS2"],
    os.environ["EVENT_HUB_CONN_STR_STANDARD_WESTUS2"]
]
EVENTHUB_NAME = "pyamqp"

SINGLE_EVENT_SIZE_LIST = [512]
PARALLEL_THREAD_COUNT_LIST = [1]
FIXED_AMOUNT_OF_EVENTS = 100_000
RUN_DURATION = 30


def pre_prepare_client(client, data):
    client.create_batch()  # precall to retrieve sender link settings
    client.send_batch([EventData(data)])  # precall to set up the sender link


def send_batch_message(conn_str, eventhub_name, num_of_events, single_event_size, run_times=1, description=None):

    client = EventHubProducerClient.from_connection_string(
        conn_str=conn_str, eventhub_name=eventhub_name
    )

    data = b'a' * single_event_size
    perf_records = []
    pre_prepare_client(client, data)

    for _ in range(run_times):  # run run_times and calculate the avg performance
        start_time = time.time()
        batch = client.create_batch()
        for _ in range(num_of_events):
            try:
                batch.add(EventData(data))
            except ValueError:
                # Batch full
                client.send_batch(batch)
                batch = client.create_batch()
                batch.add(EventData(data))
        client.send_batch(batch)

        end_time = time.time()

        total_time = end_time - start_time
        speed = num_of_events / total_time
        perf_records.append(speed)

    client.close()
    avg_perf = round(sum(perf_records) / len(perf_records), 2)
    logger.info(
        "Method: {}, The average performance is {} events/s, throughput: {} bytes/s, run times: {}.\n"
        "Configs are: Num of events: {} events, Single message size: {} bytes.".format(
            description or "send_batch_message",
            avg_perf,
            avg_perf * single_event_size,
            run_times,
            num_of_events,
            single_event_size
        )
    )
    return avg_perf


def send_batch_message_worker_thread(client, data, run_flag):
    total_cnt = 0
    while run_flag[0]:
        batch = client.create_batch()
        try:
            while True:
                event_data = EventData(body=data)
                batch.add(event_data)
        except ValueError:
            client.send_batch(batch)
            total_cnt += len(batch)
    return total_cnt


def send_batch_message_in_parallel(conn_str, eventhub_name, single_event_size, parallel_thread_count=4, run_times=1, run_duration=30, description=None):

    perf_records = []

    for _ in range(run_times):

        futures = []
        clients = [
            EventHubProducerClient.from_connection_string(
                conn_str=conn_str, eventhub_name=eventhub_name
            ) for _ in range(parallel_thread_count)
        ]

        data = b'a' * single_event_size

        for client in clients:
            pre_prepare_client(client, data)

        with ThreadPoolExecutor(max_workers=parallel_thread_count) as executor:
            run_flag = [True]
            for i in range(parallel_thread_count):
                futures.append(
                    executor.submit(
                        send_batch_message_worker_thread,
                        clients[i],
                        data,
                        run_flag
                    )
                )

            time.sleep(run_duration)
            run_flag[0] = False
            perf_records.append(sum([future.result() for future in futures]) / run_duration)

            for client in clients:
                client.close()

    avg_perf = round(sum(perf_records) / len(perf_records), 2)

    logger.info(
        "Method: {}, The average performance is {} events/s, throughput: {} bytes/s, run times: {}.\n"
        "Configs are: Single message size: {} bytes, Parallel thread count: {} threads, Run duration: {} seconds.".format(
            description or "send_batch_message_in_parallel",
            avg_perf,
            avg_perf * single_event_size,
            run_times,
            single_event_size,
            parallel_thread_count,
            run_duration
        )
    )


if __name__ == '__main__':
    logger.info('------------------- START OF TEST -------------------')

    for conn_str in CONN_STRS:
        for single_event_size in SINGLE_EVENT_SIZE_LIST:
            print('-------------------  sending fixed amount of message  -------------------')
            send_batch_message(
                conn_str=conn_str,
                eventhub_name=EVENTHUB_NAME,
                num_of_events=FIXED_AMOUNT_OF_EVENTS,
                single_event_size=single_event_size,
                description='sending fixed amount message'
            )

        for parallel_thread_count in PARALLEL_THREAD_COUNT_LIST:
            for single_event_size in SINGLE_EVENT_SIZE_LIST:
                print('-------------------  multiple threads sending messages for a fixed period -------------------')
                send_batch_message_in_parallel(
                    conn_str=conn_str,
                    eventhub_name=EVENTHUB_NAME,
                    single_event_size=single_event_size,
                    parallel_thread_count=parallel_thread_count,
                    run_duration=RUN_DURATION,
                    description='multiple threads sending messages'
                )

    logger.info('------------------- END OF TEST -------------------')
