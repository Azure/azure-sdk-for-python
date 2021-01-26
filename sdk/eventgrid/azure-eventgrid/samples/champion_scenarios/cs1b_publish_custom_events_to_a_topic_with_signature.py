# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
FILE: cs1b_publish_custom_events_to_a_topic_with_signature.py
DESCRIPTION:
    These samples demonstrate sending an EventGrid Event using a shared access signature for authentication.
USAGE:
    python cs1b_publish_custom_events_to_a_topic_with_signature.py
    Set the environment variables with your own values before running the sample:
    1) EG_ACCESS_KEY - The access key of your eventgrid account.
    2) EG_TOPIC_HOSTNAME - The topic hostname. Typically it exists in the format
    "<YOUR-TOPIC-NAME>.<REGION-NAME>.eventgrid.azure.net".
"""
import os
from azure.eventgrid import EventGridPublisherClient, EventGridEvent, generate_sas
from azure.core.credentials import AzureKeyCredential, AzureSasCredential
from datetime import datetime, timedelta

topic_key = os.environ["EG_ACCESS_KEY"]
endpoint = os.environ["EG_TOPIC_HOSTNAME"]
expiration_date_utc = datetime.utcnow() + timedelta(hours=1)

signature = generate_sas(endpoint, topic_key, expiration_date_utc)
credential = AzureSasCredential(signature)
client = EventGridPublisherClient(endpoint, credential)

client.send([
	EventGridEvent(
		event_type="Contoso.Items.ItemReceived",
		data={
			"itemSku": "Contoso Item SKU #1"
		},
		subject="Door1",
		data_version="2.0"
	)
])