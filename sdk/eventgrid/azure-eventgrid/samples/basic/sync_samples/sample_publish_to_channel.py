# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_publish_to_channel.py
DESCRIPTION:
    These samples demonstrate creating a list of CloudEvents and sending them as a list to a partner channel.
USAGE:
    python sample_publish_to_channel.py
    Set the environment variables with your own values before running the sample:
    1) EVENTGRID_PARTNER_NAMESPACE_TOPIC_KEY - The access key of your eventgrid account.
    2) EVENTGRID_PARTNER_NAMESPACE_TOPIC_ENDPOINT - The topic hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net/api/events".
    3) EVENTGRID_PARTNER_CHANNEL_NAME - The name of the channel to which the event should be published.
"""
# [START publish_cloud_event_to_topic]
import os
from azure.eventgrid import EventGridPublisherClient
from azure.core.credentials import AzureKeyCredential
from azure.core.messaging import CloudEvent

topic_key = os.environ["EVENTGRID_PARTNER_NAMESPACE_TOPIC_KEY"]
endpoint = os.environ["EVENTGRID_PARTNER_NAMESPACE_TOPIC_ENDPOINT"]

channel_name = os.environ["EVENTGRID_PARTNER_CHANNEL_NAME"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential)

client.send(
    [
        CloudEvent(
            type="Contoso.Items.ItemReceived",
            source="/contoso/items",
            data={"itemSku": "Contoso Item SKU #1"},
            subject="Door1",
        )
    ],
    channel_name=channel_name,
)
# [END publish_cloud_event_to_topic]
