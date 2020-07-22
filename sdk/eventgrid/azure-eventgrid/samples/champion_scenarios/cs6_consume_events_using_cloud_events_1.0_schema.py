import os
from azure.eventgrid import EventGridConsumer

req = os.environ.get("HTTP_REQUEST")
consumer = EventGridConsumer()

# returns List[DeserializedEvent]
deserialized_events = consumer.deserialize_events(req)

# CloudEvent schema
for event in deserialized_events:

    # both allow access to raw properties as strings
    time_string = event.time
    time_string = event["time"]

    # model returns CloudEvent object
    cloud_event = event.model

    # all model properties are strongly typed
    datetime_object = event.model.time
    storage_blobcreated_object = event.model.data