# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import os
import dotenv
import logging
from logging.handlers import RotatingFileHandler
import time

from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub import parse_connection_string

logger = logging.getLogger('RECEIVE_PERF_TEST')
logger.setLevel(logging.INFO)
logger.addHandler(RotatingFileHandler("async_receive_perf_test.log"))

dotenv.load_dotenv()
CONN_STRS = [
    os.environ["EVENT_HUB_CONN_STR_BASIC_NORTHEU"],
    os.environ["EVENT_HUB_CONN_STR_STANDARD_NORTHEU"],
    os.environ["EVENT_HUB_CONN_STR_BASIC_WESTUS2"],
    os.environ["EVENT_HUB_CONN_STR_STANDARD_WESTUS2"]
]
EH_NAME_EVENT_SIZE_PAIR = [
    ('pyamqp_16', 16),
    ('pyamqp_128', 128),
    ('pyamqp_1024', 1024)
]
PREFETCH_LIST = [300, 3000, 30000]
PARTITION_ID = "0"


async def receive_fixed_time_interval(
    conn_str,
    eventhub_name,
    single_event_size,
    prefetch=300,
    batch_receiving=False,
    description=None,
    partition_id="0"
):

    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str,
        consumer_group="$Default",
        eventhub_name=eventhub_name,
        prefetch=prefetch
    )

    last_received_count = [0]
    received_count = [0]
    run_flag = [True]
    all_perf_records = []
    check_interval = 1
    run_duration = 60

    async def on_event(partition_context, event):
        received_count[0] += 1

    async def on_event_batch(partition_context, events):
        received_count[0] += len(events)

    async def monitor():
        while run_flag[0]:
            snap = received_count[0]
            perf = (snap - last_received_count[0]) / check_interval
            last_received_count[0] = snap
            all_perf_records.append(perf)
            await asyncio.sleep(check_interval)

    target_method = consumer_client.receive_batch if batch_receiving else consumer_client.receive
    kwargs = {
        "partition_id": partition_id,
        "starting_position": "-1",  # "-1" is from the beginning of the partition.
    }
    if batch_receiving:
        kwargs["on_event_batch"] = on_event_batch
    else:
        kwargs["on_event"] = on_event

    receive_future = asyncio.create_task(
        target_method(**kwargs)
    )

    monitor_future = asyncio.create_task(
        monitor()
    )

    await asyncio.sleep(run_duration)
    run_flag[0] = False
    await consumer_client.close()
    await receive_future
    await monitor_future

    print(all_perf_records)
    valid_perf_records = all_perf_records[5:-5]  # skip the first 10 records to let the receiving program be stable
    print(valid_perf_records)
    avg_perf = sum(valid_perf_records) / len(valid_perf_records)

    logger.info(
        "EH Namespace: {}.\nMethod: {}, The average performance is {} events/s, throughput: {} bytes/s.\n"
        "Configs are: Single message size: {} bytes, Run duration: {} seconds.".format(
            parse_connection_string(conn_str).fully_qualified_namespace,
            description or "receive_fixed_time_interval",
            avg_perf,
            avg_perf * single_event_size,
            single_event_size,
            run_duration
        )
    )


async def receive_fixed_amount(
    conn_str,
    eventhub_name,
    single_event_size,
    prefetch=300,
    batch_receiving=False,
    description=None,
    partition_id="0"
):
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str,
        consumer_group="$Default",
        eventhub_name=eventhub_name,
        prefetch=prefetch
    )
    run_times = 1
    fixed_amount = 100_000
    perf_records = []
    received_count = [0]

    async def on_event(partition_context, event):
        received_count[0] += 1
        if received_count[0] == fixed_amount:
            await consumer_client.close()

    async def on_event_batch(partition_context, events):
        received_count[0] += len(events)
        if received_count[0] >= fixed_amount:
            await consumer_client.close()

    for i in range(run_times):
        start_time = time.time()
        async with consumer_client:
            if batch_receiving:
                await consumer_client.receive_batch(
                    on_event_batch=on_event_batch,
                    partition_id=partition_id,
                    starting_position="-1",
                    max_batch_size=prefetch
                )
            else:
                await consumer_client.receive(
                    on_event=on_event,
                    partition_id=partition_id,
                    starting_position="-1"
                )
        end_time = time.time()
        total_time = end_time - start_time
        speed = fixed_amount/total_time
        perf_records.append(speed)
        received_count[0] = 0
    avg_perf = sum(perf_records) / len(perf_records)

    logger.info(
        "EH Namespace: {}.\nMethod: {}, The average performance is {} events/s, throughput: {} bytes/s.\n"
        "Configs are: Single message size: {} bytes, Total events to receive: {}.".format(
            parse_connection_string(conn_str).fully_qualified_namespace,
            description or "receive_fixed_amount",
            avg_perf,
            avg_perf * single_event_size,
            single_event_size,
            fixed_amount
        )
    )


if __name__ == "__main__":
    CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
    EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']

    for conn_str in CONN_STRS:
        for eh_name, single_event_size in EH_NAME_EVENT_SIZE_PAIR:
            for prefetch in PREFETCH_LIST:
                for batch_receiving in [True, False]:
                    print('------------------- receiving fixed amount -------------------')
                    asyncio.run(
                        receive_fixed_amount(
                            conn_str=conn_str,
                            eventhub_name=eh_name,
                            single_event_size=single_event_size,
                            prefetch=prefetch,
                            batch_receiving=batch_receiving
                        )
                    )
                    print('------------------- receiving fixed interval -------------------')
                    asyncio.run(
                        receive_fixed_time_interval(
                            conn_str=conn_str,
                            eventhub_name=eh_name,
                            single_event_size=single_event_size,
                            prefetch=prefetch,
                            batch_receiving=batch_receiving
                        )
                    )
