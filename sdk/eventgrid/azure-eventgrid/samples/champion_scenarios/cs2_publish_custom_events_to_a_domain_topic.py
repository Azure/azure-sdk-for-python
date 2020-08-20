from azure.eventgrid import EventGridPublisherClient, EventGridEvent
from azure.core.credentials import AzureKeyCredential

domain_hostname = "<YOUR-DOMAIN-NAME>.<REGION-NAME>-1.eventgrid.azure.net"
domain_key = "<YOUR-DOMAIN-KEY>"

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