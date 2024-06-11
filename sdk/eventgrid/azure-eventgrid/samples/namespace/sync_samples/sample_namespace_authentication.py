# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: sample_namespace_authentication.py
DESCRIPTION:
    These samples demonstrate authenticating an EventGridPublisherClient and an EventGridConsumerClient.
USAGE:
    python sample_namespace_authentication.py
    Set the environment variables with your own values before running the sample:
    1) EVENTGRID_KEY - The access key of your eventgrid account.
    2) EVENTGRID_ENDPOINT - The namespace hostname. Typically it exists in the format
    "https://<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
    3) EVENTGRID_TOPIC_NAME - The namespace topic name.
    4) EVENTGRID_EVENT_SUBSCRIPTION_NAME = The event subscription name.
"""
import os
from azure.eventgrid import EventGridPublisherClient, EventGridConsumerClient
from azure.core.credentials import AzureKeyCredential

topic_key = os.environ["EVENTGRID_KEY"]
endpoint = os.environ["EVENTGRID_ENDPOINT"]
topic_name = os.environ["EVENTGRID_TOPIC_NAME"]
event_subscription_name = os.environ["EVENTGRID_EVENT_SUBSCRIPTION_NAME"]

credential_key = AzureKeyCredential(topic_key)
publisher_client = EventGridPublisherClient(endpoint, credential_key, namespace_topic=topic_name)
consumer_client = EventGridConsumerClient(
    endpoint, credential_key, namespace_topic=topic_name, subscription=event_subscription_name
)


from azure.identity import DefaultAzureCredential
from azure.eventgrid import EventGridPublisherClient

default_az_credential = DefaultAzureCredential()
endpoint = os.environ["EVENTGRID_TOPIC_ENDPOINT"]
publisher_client = EventGridPublisherClient(endpoint, default_az_credential, namespace_topic=topic_name)
consumer_client = EventGridConsumerClient(
    endpoint, default_az_credential, namespace_topic=topic_name, subscription=event_subscription_name
)
