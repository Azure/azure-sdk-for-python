## Authentication

### generate sas and use AzureSasCredential

```Python
from azure.eventgrid import generate_sas, EventGridPublisherClient
from azure.core.credentials import AzureSasCredential
from datetime import datetime
import os


topic_key = os.environ["EG_ACCESS_KEY"]
endpoint = os.environ["EG_TOPIC_HOSTNAME"]
expiration_date_utc = datetime.utcnow()

signature = generate_sas(endpoint, topic_key, expiration_date_utc)

credential = AzureSasCredential(signature)
client = EventGridPublisherClient(endpoint, credential)
```

### use the azure key credential

```Python
from azure.eventgrid import generate_sas, EventGridPublisherClient
from azure.core.credentials import AzureKeyCredential
from datetime import datetime
import os


topic_key = os.environ["EG_ACCESS_KEY"]
endpoint = os.environ["EG_TOPIC_HOSTNAME"]

credential = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential)
```

## Send Scenarios

### Send a single EventGridEvent as a strongly typed object

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

### Send a single CloudEvent as a strongly typed object

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
    "eventTime": datetime.utcnow()
}

event1 = {
    "eventType": "Contoso.Items.ItemReceived",
    "data": {
        "itemSku": "Contoso Item SKU #2"
    },
    "subject": "Door1",
    "dataVersion": "2.0",
    "id": "randomuuid12",
    "eventTime": datetime.utcnow()
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

### Deserialize EventGridEvents from storage queue

```Python
from azure.eventgrid import CloudEvent
from azure.storage.queue import QueueServiceClient, BinaryBase64DecodePolicy
import os
import json

# all types of CloudEvents below produce same DeserializedEvent
connection_str = os.environ['STORAGE_QUEUE_CONN_STR']
queue_name = os.environ['STORAGE_QUEUE_NAME']

with QueueServiceClient.from_connection_string(connection_str) as qsc:
    payload =  qsc.get_queue_client(
        queue=queue_name,
        message_decode_policy=BinaryBase64DecodePolicy()
        ).peek_messages()

    ## deserialize payload into a lost of typed Events
    events = [CloudEvent.from_dict(json.loads(msg.content)) for msg in payload]

    for event in events:
        print(type(event)) ## CloudEvent
```

### Deserialize EventGridEvents from service bus message

```Python
from azure.eventgrid import EventGridEvent
from azure.servicebus import ServiceBusClient
import os
import json

# all types of EventGridEvents below produce same DeserializedEvent
connection_str = os.environ['SERVICE_BUS_CONN_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

with ServiceBusClient.from_connection_string(connection_str) as sb_client:
    payload =  sb_client.get_queue_receiver(queue_name).receive_messages()

    ## deserialize payload into a lost of typed Events
    events = [EventGridEvent.from_dict(json.loads(next(msg.body).decode('utf-8'))) for msg in payload]

    for event in events:
        print(type(event)) ## EventGridEvent

```

### Deserialize CloudEvents payload

```Python
from azure.eventgrid import CloudEvent
import json

# all types of CloudEvents below produce same DeserializedEvent
cloud_custom_dict = """[{
    "id":"de0fd76c-4ef4-4dfb-ab3a-8f24a307e033",
    "source":"https://egtest.dev/cloudcustomevent",
    "data":{
        "team": "event grid squad"
    },
    "type":"Azure.Sdk.Sample",
    "time":"2020-08-07T02:06:08.11969Z",
    "specversion":"1.0"
}]"""

deserialized_dict_events = [CloudEvent(**msg) for msg in json.loads(cloud_custom_dict)]

for event in deserialized_dict_events:
    print(event.data)
    print(type(event))
```
