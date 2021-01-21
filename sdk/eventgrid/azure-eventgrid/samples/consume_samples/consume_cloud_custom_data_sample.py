# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: consume_cloud_custom_data_sample.py
DESCRIPTION:
    These samples demonstrate consuming custom cloud data
USAGE:
    python consume_cloud_custom_data_sample.py
    Set the environment variables with your own values before running the sample:
"""
import json
from azure.eventgrid import EventGridDeserializer, CloudEvent

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
cloud_custom_bytes = str(cloud_custom_string).encode("utf-8")

client = EventGridDeserializer()
deserialized_dict_event = client.deserialize_cloud_events(cloud_custom_dict)

# to return raw json, we use the data param
print(deserialized_dict_event.data)
print(type(deserialized_dict_event.data)) # this is a dictionary

# use system_event_data to get a strongly typed model
print(deserialized_dict_event.system_event_data)
print(type(deserialized_dict_event.system_event_data)) # this is a strongly typed model

deserialized_str_event = client.deserialize_cloud_events(cloud_custom_string)
print(deserialized_str_event)

deserialized_bytes_event = client.deserialize_cloud_events(cloud_custom_bytes)
print(deserialized_bytes_event)
