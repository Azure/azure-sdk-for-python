# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_consume_custom_payload.py
DESCRIPTION:
    These samples demonstrate consuming a raw json with a list of jsons and
    deserializing them into typed objects of CloudEvents.
USAGE:
    python sample_consume_custom_payload.py
"""

from azure.core.messaging import CloudEvent
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
