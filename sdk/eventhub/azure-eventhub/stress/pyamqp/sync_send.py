# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time

from azure.eventhub import EventHubProducerClient, EventData

CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


def test_send_small_message_fixed_amount():

    client = EventHubProducerClient.from_connection_string(conn_str=CONNECTION_STR, eventhub_name=EVENTHUB_NAME)

    run_times = 5
    iter_count = 200
    batch_count = 100
    single_message_size = 1
    perf_records = []
    client.create_batch()  # precall to retrieve sender link settings

    for _ in range(run_times):  # run run_times and calculate the avg performance
        start_time = time.time()

        for _ in range(iter_count):
            event_data_batch = client.create_batch()
            for j in range(batch_count):
                ed = EventData(b"d" * single_message_size)
                event_data_batch.add(ed)
            client.send_batch(event_data_batch)

        end_time = time.time()

        total_amount = iter_count * batch_count
        total_time = end_time - start_time
        speed = total_amount / total_time
        perf_records.append(speed)

    avg_perf = sum(perf_records) / len(perf_records)
    print("The average performance is {} events/s".format(avg_perf))


test_send_small_message_fixed_amount()