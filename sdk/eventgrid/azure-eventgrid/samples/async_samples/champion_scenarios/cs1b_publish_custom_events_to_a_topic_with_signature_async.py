# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: cs1b_publish_custom_events_to_a_topic_with_signature_async.py
DESCRIPTION:
    These samples demonstrate sending an EventGrid Event using a shared access signature for authentication asynchronously.
USAGE:
    python cs1b_publish_custom_events_to_a_topic_with_signature_async.py
    Set the environment variables with your own values before running the sample:
    1) EG_ACCESS_KEY - The access key of your eventgrid account.
    2) EG_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
"""
import os
import asyncio

from azure.eventgrid.aio import EventGridPublisherClient
from azure.eventgrid import EventGridEvent, generate_shared_access_signature, EventGridSharedAccessSignatureCredential
from azure.core.credentials import AzureKeyCredential
from datetime import datetime, timedelta

async def publish():
	topic_key = os.environ["EG_ACCESS_KEY"]
	topic_hostname = os.environ["EG_TOPIC_HOSTNAME"]
	expiration_date_utc = datetime.utcnow() + timedelta(hours=1)

	signature = generate_shared_access_signature(topic_hostname, topic_key, expiration_date_utc)
	credential = EventGridSharedAccessSignatureCredential(signature)
	client = EventGridPublisherClient(topic_hostname, credential)
	await client.send([
		EventGridEvent(
			event_type="Contoso.Items.ItemReceived",
			data={
				"itemSku": "Contoso Item SKU #1"
			},
			subject="Door1",
			data_version="2.0"
		)
	])

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(publish())
