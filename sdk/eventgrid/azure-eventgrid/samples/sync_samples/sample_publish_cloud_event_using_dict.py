# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_publish_cloud_event_using_dict.py
DESCRIPTION:
    These samples demonstrate creating a list of CloudEvents using dict representations
    and sending them as a list.
USAGE:
    python sample_publish_cloud_event_using_dict.py
    Set the environment variables with your own values before running the sample:
    1) EVENTGRID_CLOUD_EVENT_TOPIC_KEY - The access key of your eventgrid account.
    2) EVENTGRID_CLOUD_EVENT_TOPIC_ENDPOINT - The topic hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net/api/events".
"""
import os
from azure.eventgrid import EventGridPublisherClient
from azure.core.credentials import AzureKeyCredential

topic_key = os.environ["EVENTGRID_CLOUD_EVENT_TOPIC_KEY"]
endpoint = os.environ["EVENTGRID_CLOUD_EVENT_TOPIC_ENDPOINT"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential)

# [START publish_cloud_event_dict]
client.send([
    {
        "type": "Contoso.Items.ItemReceived",
        "source": "/contoso/items",	
        "data": {	
            "itemSku": "Contoso Item SKU #1"	
        },	
        "subject": "Door1",	
        "specversion": "1.0",	
        "id": "randomclouduuid11"
    }
])
# [END publish_cloud_event_dict]
