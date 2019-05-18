import logging
from azure.eventhub import EventHubClient, EventData, MessageSendResult
import uuid

#logging.basicConfig(level=logging.DEBUG)
ADDRESS = "amqp://yijun-eventh.servicebus.windows.net/test_eventhub"
USER = "RootManageSharedAccessKey"
KEY = "a4xbgNrqFT3tlN5Ak1jWvhSXmnuClOjkNMTQ81posWA="
client = EventHubClient(ADDRESS, username=USER, password=KEY, debug=True)

def send():
    with client.create_sender() as sender:
        for i in range(1):
            print("Sending message: {}".format(i))
            ed = EventData("Message with different content {}".format(i))
            ed.partition_key = "20"
            ed.application_properties = {"partition_test": "same partition key 20"}
            sender.send(ed)


def send_batch():
    with client.create_sender() as sender:
        batch_event_data = []
        for i in range(5):
            event_data = EventData("Message with different content {}".format(i))
            event_data.application_properties = {"batch_send_index": str(i)}
            event_data.partition_key = "aaa"
            batch_event_data.append(event_data)
        send_result = sender.send_batch(batch_event_data)
        if send_result == MessageSendResult.Ok:
            print("Sent")


send_batch()
