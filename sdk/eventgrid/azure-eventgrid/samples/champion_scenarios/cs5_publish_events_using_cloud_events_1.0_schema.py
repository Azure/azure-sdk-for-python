from azure.eventgrid import EventGridPublisherClient, CloudEvent
from azure.core.credentials import AzureKeyCredential

topic_hostname = "<YOUR-TOPIC-NAME>.<REGION-NAME>-1.eventgrid.azure.net"
topic_key = "<YOUR-TOPIC-KEY>"

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(topic_hostname, credential)

client.send([
    CloudEvent(
        type="Contoso.Items.ItemReceived",
        source="/contoso/items",
        data={
            "itemSku": "Contoso Item SKU #1"
        },
        subject="Door1"
    )
])
