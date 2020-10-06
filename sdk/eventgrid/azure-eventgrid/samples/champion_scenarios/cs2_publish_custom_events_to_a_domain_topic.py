# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: cs2_publish_custom_events_to_a_domain_topic.py
DESCRIPTION:
    These samples demonstrate creating a list of EventGrid Events and sending them as a list.
USAGE:
    python cs2_publish_custom_events_to_a_domain_topic.py
    Set the environment variables with your own values before running the sample:
    1) EG_ACCESS_KEY - The access key of your eventgrid account.
    2) EG_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
"""
import os
from azure.eventgrid import EventGridPublisherClient, EventGridEvent
from azure.core.credentials import AzureKeyCredential

domain_key = os.environ["EG_ACCESS_KEY"]
domain_hostname = os.environ["EG_TOPIC_HOSTNAME"]

credential = AzureKeyCredential(domain_key)
client = EventGridPublisherClient(domain_hostname, credential)

client.send([
	EventGridEvent(
		topic="MyCustomDomainTopic1",
		event_type="Contoso.Items.ItemReceived",
		data={
			"itemSku": "Contoso Item SKU #1"
		},
		subject="Door1",
		data_version="2.0"
	),
	EventGridEvent(
		topic="MyCustomDomainTopic2",
		event_type="Contoso.Items.ItemReceived",
		data={
			"itemSku": "Contoso Item SKU #2"
		},
		subject="Door1",
		data_version="2.0"
	)
])
