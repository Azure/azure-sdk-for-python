from azure.eventgrid import EventGridPublisherClient
from azure.eventgrid import EventGridEvent, CloudEvent
from azure.core.credentials import AzureKeyCredential

topic_hostname = "<YOUR-TOPIC-NAME>.<REGION-NAME>-1.eventgrid.azure.net"
topic_key = "<YOUR-TOPIC-KEY>"

credential = AzureKeyCredential(topic_key)
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