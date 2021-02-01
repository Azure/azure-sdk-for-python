## Send Scenarios

### Send a Single EventGridEvent as a strongly typed object

```Python
import os
from azure.eventgrid import EventGridPublisherClient, EventGridEvent
from azure.core.credentials import AzureKeyCredential

topic_key = os.environ["EG_ACCESS_KEY"]
endpoint = os.environ["EG_TOPIC_HOSTNAME"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential)

event = EventGridEvent(
		event_type="Contoso.Items.ItemReceived",
		data={
			"itemSku": "Contoso Item SKU #1"
		},
		subject="Door1",
		data_version="2.0"
	)

client.send(event)
```

### Send a Single CloudEvent as a strongly typed object

```Python
import os
from azure.eventgrid import EventGridPublisherClient, CloudEvent
from azure.core.credentials import AzureKeyCredential

topic_key = os.environ["CLOUD_ACCESS_KEY"]
endpoint = os.environ["CLOUD_TOPIC_HOSTNAME"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential)

event = CloudEvent(
        type="Contoso.Items.ItemReceived",
        source="/contoso/items",
        data={
            "itemSku": "Contoso Item SKU #1"
        },
        subject="Door1"
    )

client.send(event)
```

### Send multiple EventGridEvents as strongly typed objects

```Python
import os
from azure.eventgrid import EventGridPublisherClient, EventGridEvent
from azure.core.credentials import AzureKeyCredential

topic_key = os.environ["EG_ACCESS_KEY"]
endpoint = os.environ["EG_TOPIC_HOSTNAME"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential)

event0 = EventGridEvent(
		event_type="Contoso.Items.ItemReceived",
		data={
			"itemSku": "Contoso Item SKU #1"
		},
		subject="Door1",
		data_version="2.0"
	)

event1 = EventGridEvent(
		event_type="Contoso.Items.ItemReceived",
		data={
			"itemSku": "Contoso Item SKU #2"
		},
		subject="Door1",
		data_version="2.0"
	)

client.send([event0, event1])
```

### Send multiple CloudEvents as a strongly typed objects

```Python
import os
from azure.eventgrid import EventGridPublisherClient, CloudEvent
from azure.core.credentials import AzureKeyCredential

topic_key = os.environ["CLOUD_ACCESS_KEY"]
endpoint = os.environ["CLOUD_TOPIC_HOSTNAME"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential)

event0 = CloudEvent(
        type="Contoso.Items.ItemReceived",
        source="/contoso/items",
        data={
            "itemSku": "Contoso Item SKU #1"
        },
        subject="Door1"
    )
event1 = CloudEvent(
        type="Contoso.Items.ItemReceived",
        source="/contoso/items",
        data={
            "itemSku": "Contoso Item SKU #2"
        },
        subject="Door1"
    )

client.send([event0, event1])
```

### Send multiple EventGridEvents as dictionaries

```Python
import os
from azure.eventgrid import EventGridPublisherClient, EventGridEvent
from azure.core.credentials import AzureKeyCredential
from datetime import datetime

topic_key = os.environ["EG_ACCESS_KEY"]
endpoint = os.environ["EG_TOPIC_HOSTNAME"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential)

event0 = {
    "eventType": "Contoso.Items.ItemReceived",
    "data": {
		"itemSku": "Contoso Item SKU #1"
	},
	"subject": "Door1",
	"dataVersion": "2.0",
    "id": "randomuuid11",
    "eventTime": datetime(2021, 1, 21, 17, 37)
}

event1 = {
    "eventType": "Contoso.Items.ItemReceived",
    "data": {
		"itemSku": "Contoso Item SKU #2"
	},
	"subject": "Door1",
	"dataVersion": "2.0",
    "id": "randomuuid12",
    "eventTime": datetime(2021, 1, 21, 17, 37)
}

client.send([event0, event1])
```

### Send multiple CloudEvents as dictionaries

```Python
import os
from azure.eventgrid import EventGridPublisherClient, CloudEvent
from azure.core.credentials import AzureKeyCredential

topic_key = os.environ["CLOUD_ACCESS_KEY"]
endpoint = os.environ["CLOUD_TOPIC_HOSTNAME"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential)

event0 = {
        "type": "Contoso.Items.ItemReceived",
        "source": "/contoso/items",
        "data": {
            "itemSku": "Contoso Item SKU #1"
        },
        "subject": "Door1",
        "specversion": "1.0",
        "id": "randomclouduuid11"
}

event1 = {
        "type": "Contoso.Items.ItemReceived",
        "source": "/contoso/items",
        "data": {
            "itemSku": "Contoso Item SKU #2"
        },
        "subject": "Door1",
        "specversion": "1.0",
        "id": "randomclouduuid12"
}

client.send([event0, event1])
```

### Send a CustomEvent schema

```Python
import os
from azure.eventgrid import EventGridPublisherClient
from azure.core.credentials import AzureKeyCredential

topic_key = os.environ["CUSTOM_SCHEMA_ACCESS_KEY"]
endpoint = os.environ["CUSTOM_SCHEMA_TOPIC_HOSTNAME"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential)

event = {
		"custom_event_type":"Contoso.Items.ItemReceived",
		"data":{
			"itemSku": "Contoso Item SKU #2"
		},
		"custom_subject":"Door1",
		"custom_data_version":"2.0"
}
client.send(event)
```

## Receive Scenarios

### Deserialize CloudEvents from storage queue

```Python
from azure.eventgrid import CloudEvent
from azure.storage.queue import QueueServiceClient
import os
import json
from base64 import b64decode

# all types of CloudEvents below produce same DeserializedEvent
connection_str = os.environ['STORAGE_QUEUE_CONN_STR']
queue_name = os.environ['STORAGE_QUEUE_NAME']

with QueueServiceClient.from_connection_string(connection_str) as qsc:
    payload =  qsc.get_queue_client("eventgrid").peek_messages()

    ## deserialize payload into a lost of typed Events
    events = [CloudEvent(**json.loads(b64decode(msg.content))) for msg in payload]

    for event in events:
        print(type(event)) ## CloudEvent
```

### Deserialize CloudEvents from service bus message

```Python
from azure.eventgrid import CloudEvent
from azure.servicebus import ServiceBusClient
import os
import json

# all types of CloudEvents below produce same DeserializedEvent
connection_str = os.environ['SERVICE_BUS_CONN_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

with ServiceBusClient.from_connection_string(connection_str) as sb_client:
    payload =  sb_client.get_queue_receiver(queue_name).receive_messages()

    ## deserialize payload into a lost of typed Events
    events = [CloudEvent(**json.loads(next(msg.body).decode('utf-8'))) for msg in payload]

    for event in events:
        print(type(event)) ## CloudEvent

```

### Deserialize CloudEvents payload

```Python
from azure.eventgrid import CloudEvent
import json

# all types of CloudEvents below produce same DeserializedEvent
cloud_custom_dict = "[{ \"id\":\"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033\",\
    \"source\":\"https://egtest.dev/cloudcustomevent\",\
    \"data\":{\"team\": \"event grid squad\"},\
    \"type\":\"Azure.Sdk.Sample\",\
    \"time\":\"2020-08-07T02:06:08.11969Z\",\
    \"specversion\":\"1.0\" }]"

deserialized_dict_events = [CloudEvent(**msg) for msg in json.loads(cloud_custom_dict)]

for event in deserialized_dict_events:
	print(event.data)
	print(type(event))
```
