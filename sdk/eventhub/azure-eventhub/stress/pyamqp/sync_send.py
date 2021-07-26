# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import time

from azure.eventhub import EventHubProducerClient, EventData


CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


def send_batch_message():

    client = EventHubProducerClient.from_connection_string(conn_str=CONNECTION_STR, eventhub_name=EVENTHUB_NAME)

    run_times = 5
    num_of_events = 100_000
    single_message_size = 512
    data = b'a' * single_message_size
    perf_records = []
    client.create_batch()  # precall to retrieve sender link settings

    for i in range(run_times):  # run run_times and calculate the avg performance
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

    avg_perf = sum(perf_records) / len(perf_records)
    print(
        "Method: {}, The average performance is {} events/s.".format(
            "test_send_batch_message_max_allowed_amount",
            avg_perf
        )
    )


send_batch_message()
