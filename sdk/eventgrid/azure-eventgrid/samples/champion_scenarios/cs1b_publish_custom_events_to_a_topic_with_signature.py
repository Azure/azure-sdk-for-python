from azure.eventgrid import EventGridPublisherClient, EventGridEvent, CloudEvent, generate_shared_access_signature, EventGridSharedAccessSignatureCredential
from azure.core.credentials import AzureKeyCredential

topic_hostname = "<YOUR-TOPIC-NAME>.<REGION-NAME>-1.eventgrid.azure.net"
topic_key = "<YOUR-TOPIC-KEY>"
expiration_date_utc = dt.datetime.now(tzutc()) + timedelta(hours=1)

signature = generate_shared_access_signature(topic_hostname, topic_key, expiration_date_utc)
credential = EventGridSharedAccessSignatureCredential(signature)
client = EventGridPublisherClient(topic_hostname, credential)

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