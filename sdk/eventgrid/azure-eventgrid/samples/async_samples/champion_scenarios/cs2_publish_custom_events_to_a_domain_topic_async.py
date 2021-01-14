# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: cs2_publish_custom_events_to_a_domain_topic_async.py
DESCRIPTION:
    These samples demonstrate creating a list of EventGrid Events and sending them as a list asynchronously.
USAGE:
    python cs2_publish_custom_events_to_a_domain_topic_async.py
    Set the environment variables with your own values before running the sample:
    1) EG_ACCESS_KEY - The access key of your eventgrid account.
    2) EG_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
"""
import os
import asyncio

from azure.eventgrid.aio import EventGridPublisherClient
from azure.eventgrid import EventGridEvent
from azure.core.credentials import AzureKeyCredential
	
async def publish():
	domain_key = os.environ["EG_DOMAIN_ACCESS_KEY"]
	domain_hostname = os.environ["EG_DOMAIN_HOSTNAME"]

	credential = AzureKeyCredential(domain_key)
	client = EventGridPublisherClient(domain_hostname, credential)

	await client.send([
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

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publish())
