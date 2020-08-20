import os
from azure.eventgrid import EventGridConsumer

consumer = EventGridConsumer()

# returns List[DeserializedEvent]
deserialized_events = consumer.deserialize_events(service_bus_received_message)

# EventGridEvent schema, with custom event type
for event in deserialized_events:

    # both allow access to raw properties as strings
    time_string = event.event_time
    time_string = event["event_time"]

    # model returns EventGridEvent object
    event_grid_event = event.model

    # returns { "itemSku": "Contoso Item SKU #1" }
    data_dict = event.data

    # custom event not pre-defined in system event registry, returns None
    returns_none = event.model.data
