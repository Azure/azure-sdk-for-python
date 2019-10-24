import logging
import os
import time
import threading
from azure.eventhub import EventHubConsumerClient, FileBasedPartitionManager, InMemoryPartitionManager

RECEIVE_TIMEOUT = 5  # timeout in seconds for a receiving operation. 0 or None means no timeout
RETRY_TOTAL = 3  # max number of retries for receive operations within the receive timeout. Actual number of retries clould be less if RECEIVE_TIMEOUT is too small
CONNECTION_STR = os.environ["EVENT_HUB_CONN_STR"]

logging.basicConfig(level=logging.INFO)


def do_operation(event):
    pass
    # do some sync or async operations. If the operation is i/o intensive, async will have better performance
    #print(event)


def process_events(partition_context, events):
    if events:
        print("received events: {} from partition: {}".format(len(events), partition_context.partition_id))
        # for event in events:
        #     do_operation(event)

        partition_context.update_checkpoint(events[-1])
    else:
        print("empty events received", "partition:", partition_context.partition_id)


if __name__ == '__main__':
    partition_manager = FileBasedPartitionManager('test_file_name')
    #partition_manager = InMemoryPartitionManager()
    client = EventHubConsumerClient.from_connection_string(
        CONNECTION_STR, partition_manager=partition_manager, receive_timeout=RECEIVE_TIMEOUT, retry_total=RETRY_TOTAL
    )
    work_thread_0 = threading.Thread(target=client.receive, args=(process_events, '$Default'), kwargs={'partition_id': '0'})
    work_thread_1 = threading.Thread(target=client.receive, args=(process_events, '$Default'),
                                   kwargs={'partition_id': '1'})
    try:
        #client.receive(process_events, '$Default')

        work_thread_0.start()
        work_thread_1.start()
        time.sleep(5)
        print('############################## 5 seconds ##############################')
        client.close()
        work_thread_0.join()
        work_thread_1.join()

    except KeyboardInterrupt:
        print('KeyboardInterrupt')
        client.close()
        work_thread_0.join()
        work_thread_1.join()


