from azure.eventgrid import CloudEvent
import json

# all types of CloudEvents below produce same DeserializedEvent
cloud_custom_dict = """[{
    "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
    "source":"https://egtest.dev/cloudcustomevent",
    "data":{
        "team": "event grid squad"
    },
    "type":"Azure.Sdk.Sample",
    "time":"2020-08-07T02:06:08.11969Z",
    "specversion":"1.0"
}]"""

deserialized_dict_events = [CloudEvent(**msg) for msg in json.loads(cloud_custom_dict)]

for event in deserialized_dict_events:
    print(event.data)
    print(type(event))
