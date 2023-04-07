# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import dotenv
import logging
import threading
from logging.handlers import RotatingFileHandler
import time

from azure.eventhub import EventHubConsumerClient
from azure.eventhub import parse_connection_string

logger = logging.getLogger('RECEIVE_PERF_TEST')
logger.setLevel(logging.INFO)
logger.addHandler(RotatingFileHandler("receive_perf_test.log"))

dotenv.load_dotenv()
CONN_STRS = [
    os.environ["EVENT_HUB_CONN_STR_BASIC_NORTHEU"],
    os.environ["EVENT_HUB_CONN_STR_STANDARD_NORTHEU"],
    os.environ["EVENT_HUB_CONN_STR_BASIC_WESTUS2"],
    os.environ["EVENT_HUB_CONN_STR_STANDARD_WESTUS2"]
]
EH_NAME_EVENT_SIZE_PAIR = [
    ('pyamqp_512', 512),
]
PREFETCH_LIST = [300, 3000]
PARTITION_ID = "0"
RUN_DURATION = 30
FIXED_AMOUNT = 100_000


def receive_fixed_time_interval(
    conn_str,
    eventhub_name,
    single_event_size,
    prefetch=300,
    batch_receiving=False,
    description=None,
    run_duration=30,
    partition_id="0"
):

    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str,
        consumer_group="$Default",
        eventhub_name=eventhub_name
    )

    last_received_count = [0]
    received_count = [0]
    run_flag = [True]
    all_perf_records = []
    check_interval = 1

    def on_event(partition_context, event):
        received_count[0] += 1

    def on_event_batch(partition_context, events):
        received_count[0] += len(events)

    def monitor():
        while run_flag[0]:
            snap = received_count[0]
            perf = (snap - last_received_count[0]) / check_interval
            last_received_count[0] = snap
            all_perf_records.append(perf)
            time.sleep(check_interval)

    target = consumer_client.receive_batch if batch_receiving else consumer_client.receive
    kwargs = {
        "partition_id": partition_id,
        "starting_position": "-1",  # "-1" is from the beginning of the partition.
        "prefetch": prefetch
    }
    if batch_receiving:
        kwargs["max_batch_size"] = prefetch
        kwargs["on_event_batch"] = on_event_batch
    else:
        kwargs["on_event"] = on_event

    thread = threading.Thread(
        target=target,
        kwargs=kwargs
    )

    monitor_thread = threading.Thread(
        target=monitor
    )

    thread.daemon = True
    monitor_thread.daemon = True

    thread.start()
    monitor_thread.start()
    time.sleep(run_duration)
    consumer_client.close()
    run_flag[0] = False

    valid_perf_records = all_perf_records[10:]  # skip the first 10 records to let the receiving program be stable
    avg_perf = sum(valid_perf_records) / len(valid_perf_records)

    logger.info(
        "EH Namespace: {}.\nMethod: {}, The average performance is {} events/s, throughput: {} bytes/s.\n"
        "Configs are: Single message size: {} bytes, Run duration: {} seconds.\n"
        "Prefetch: {}.".format(
            parse_connection_string(conn_str).fully_qualified_namespace,
            description or "receive_fixed_time_interval",
            avg_perf,
            avg_perf * single_event_size,
            single_event_size,
            run_duration,
            prefetch
        )
    )


def receive_fixed_amount(
    conn_str,
    eventhub_name,
    single_event_size,
    prefetch=300,
    batch_receiving=False,
    description=None,
    partition_id="0",
    run_times=1,
    fixed_amount=100_000
):
    consumer_client = EventHubConsumerClient.from_connection_string(
        conn_str,
        consumer_group="$Default",
        eventhub_name=eventhub_name,
        prefetch=prefetch
    )
    perf_records = []
    received_count = [0]

    def on_event(partition_context, event):
        received_count[0] += 1
        if received_count[0] == fixed_amount:
            consumer_client.close()

    def on_event_batch(partition_context, events):
        received_count[0] += len(events)
        if received_count[0] >= fixed_amount:
            consumer_client.close()

    for i in range(run_times):
        start_time = time.time()
        with consumer_client:
            if batch_receiving:
                consumer_client.receive_batch(
                    on_event_batch=on_event_batch,
                    partition_id=partition_id,
                    starting_position="-1",
                    max_batch_size=prefetch,
                    prefetch=prefetch
                )
            else:
                consumer_client.receive(
                    on_event=on_event,
                    partition_id=partition_id,
                    starting_position="-1",
                    prefetch=prefetch
                )
        end_time = time.time()
        total_time = end_time - start_time
        speed = fixed_amount/total_time
        perf_records.append(speed)
        received_count[0] = 0
    avg_perf = sum(perf_records) / len(perf_records)

    logger.info(
        "EH Namespace: {}.\nMethod: {}, The average performance is {} events/s, throughput: {} bytes/s.\n"
        "Configs are: Single message size: {} bytes, Total events to receive: {}.\n"
        "Prefetch:{}.".format(
            parse_connection_string(conn_str).fully_qualified_namespace,
            description or "receive_fixed_amount",
            avg_perf,
            avg_perf * single_event_size,
            single_event_size,
            fixed_amount,
            prefetch
        )
    )


if __name__ == "__main__":
    for conn_str in CONN_STRS:
        for eh_name, single_event_size in EH_NAME_EVENT_SIZE_PAIR:
            for prefetch in PREFETCH_LIST:
                for batch_receiving in [True, False]:
                    print('------------------- receiving fixed amount -------------------')
                    receive_fixed_amount(
                        conn_str=conn_str,
                        eventhub_name=eh_name,
                        single_event_size=single_event_size,
                        prefetch=prefetch,
                        batch_receiving=batch_receiving
                    )
                    print('------------------- receiving fixed interval -------------------')
                    receive_fixed_time_interval(
                        conn_str=conn_str,
                        eventhub_name=eh_name,
                        single_event_size=single_event_size,
                        prefetch=prefetch,
                        batch_receiving=batch_receiving
                    )
