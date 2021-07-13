import os
import time

CONNECTION_STR = os.environ['EVENT_HUB_CONN_STR']
EVENTHUB_NAME = os.environ['EVENT_HUB_NAME']


from azure.eventhub import EventHubProducerClient, EventData

client = EventHubProducerClient.from_connection_string(conn_str=CONNECTION_STR, eventhub_name=EVENTHUB_NAME)


def test_send_small_message_fixed_amount():

    iter_count = 200
    batch_count = 100
    single_message_size = 1

    client.create_batch()  # precall to retrieve sender link settings

    start_time = time.time()

    for i in range(iter_count):

        event_data_batch = client.create_batch()
        for j in range(batch_count):
            ed = EventData(b"d" * single_message_size)
            event_data_batch.add(ed)

        client.send_batch(event_data_batch)

    end_time = time.time()

    total_amount = iter_count * batch_count
    total_time = end_time - start_time
    speed = total_amount / total_time
    print('Sending is speed {} events/s'.format(speed))


test_send_small_message_fixed_amount()