# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_publish_eg_event_using_dict.py
DESCRIPTION:
    These samples demonstrate sending an EventGrid Event as a dict representation
    directly to a topic. The dict representation should be that of the serialized
    model of EventGridEvent.
USAGE:
    python sample_publish_eg_event_using_dict.py
    Set the environment variables with your own values before running the sample:
    1) EG_ACCESS_KEY - The access key of your eventgrid account.
    2) EG_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net/api/events".
"""
import os
from datetime import datetime
from msrest.serialization import UTC
from azure.eventgrid import EventGridPublisherClient, EventGridEvent
from azure.core.credentials import AzureKeyCredential

topic_key = os.environ["EG_ACCESS_KEY"]
endpoint = os.environ["EG_TOPIC_HOSTNAME"]

def publish():
    # [START publish_eg_event_dict]
    credential = AzureKeyCredential(topic_key)
    client = EventGridPublisherClient(endpoint, credential)

    event0 = {	
        "eventType": "Contoso.Items.ItemReceived",	
        "data": {	
            "itemSku": "Contoso Item SKU #1"	
        },	
        "subject": "Door1",	
        "dataVersion": "2.0",	
        "id": "randomuuid11",	
        "eventTime": datetime.now(UTC())
    }	
    event1 = {	
        "eventType": "Contoso.Items.ItemReceived",	
        "data": {	
            "itemSku": "Contoso Item SKU #2"	
        },	
        "subject": "Door1",	
        "dataVersion": "2.0",	
        "id": "randomuuid12",	
        "eventTime": datetime.now(UTC())
    }	
    client.send([event0, event1])
    # [END publish_eg_event_dict]

if __name__ == '__main__':
    publish()
