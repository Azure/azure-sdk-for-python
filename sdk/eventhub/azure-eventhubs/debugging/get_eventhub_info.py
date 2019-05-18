import logging
from azure.eventhub import EventHubClient, Offset

logging.basicConfig(level=logging.DEBUG)

ADDRESS = "amqp://yijun-eventh.servicebus.windows.net/test_eventhub"
USER = "RootManageSharedAccessKey"
KEY = "a4xbgNrqFT3tlN5Ak1jWvhSXmnuClOjkNMTQ81posWA="
client = EventHubClient(ADDRESS, username=USER, password=KEY, debug=True)
print(client.get_eventhub_info())