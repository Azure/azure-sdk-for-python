# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_use_raw_response_hook.py
DESCRIPTION:
    These samples demonstrate sending a list of CloudEvents and printing the status code of the response.
    A list of all azure-core configurations can be seen here:
    https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core#configurations

USAGE:
    python sample_use_raw_response_hook.py
    Set the environment variables with your own values before running the sample:
    1) EG_ACCESS_KEY - The access key of your eventgrid account.
    2) EG_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net/api/events".
"""
import os
from azure.eventgrid import EventGridPublisherClient, EventGridEvent
from azure.core.credentials import AzureKeyCredential
from azure.core.messaging import CloudEvent

topic_key = os.environ["EG_ACCESS_KEY"]
endpoint = os.environ["EG_TOPIC_HOSTNAME"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential)

def callback(response):
    var = response.http_response.status_code
    return var

print(client.send(
        EventGridEvent(
            event_type="Contoso.Items.ItemReceived",
            data={
                "itemSku": "Contoso Item SKU #1"
            },
            subject="Door1",
            data_version="2.0"
        ),
        raw_response_hook=callback
    ))
