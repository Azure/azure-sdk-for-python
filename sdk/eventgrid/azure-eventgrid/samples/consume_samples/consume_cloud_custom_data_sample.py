import json
from azure.eventgrid import EventGridConsumer, CloudEvent

# all types of CloudEvents below produce same DeserializedEvent
cloud_custom_dict = {
    "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
    "source":"https://egtest.dev/cloudcustomevent",
    "data":{"team": "event grid squad"},
    "type":"Azure.Sdk.Sample",
    "time":"2020-08-07T02:06:08.11969Z",
    "specversion":"1.0"
}
cloud_custom_string = json.dumps(cloud_custom_dict)
cloud_custom_bytes = bytes(cloud_custom_string, "utf-8")

client = EventGridConsumer()
deserialized_dict_event = client.deserialize_event(cloud_custom_dict)
deserialized_str_event = client.deserialize_event(cloud_custom_string)
deserialized_bytes_event = client.deserialize_event(cloud_custom_bytes)

print(deserialized_bytes_event.model == deserialized_str_event.model)
print(deserialized_bytes_event.model == deserialized_dict_event.model)