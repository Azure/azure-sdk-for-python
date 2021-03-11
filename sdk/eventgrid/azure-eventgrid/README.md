# Azure Event Grid client library for Python

Azure Event Grid is a fully-managed intelligent event routing service that allows for uniform event consumption using a publish-subscribe model.

[Source code][python-eg-src] | [Package (PyPI)][python-eg-pypi] | [API reference documentation][python-eg-ref-docs] | [Product documentation][python-eg-product-docs] | [Samples][python-eg-samples] | [Changelog][python-eg-changelog]

## Getting started

### Prerequisites
* Python 2.7, or 3.6 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and an Event Grid Topic resource to use this package. Follow this [step-by-step tutorial](https://docs.microsoft.com/azure/event-grid/custom-event-quickstart-portal) to register the Event Grid resource provider and create Event Grid topics using the [Azure portal](https://portal.azure.com/). There is a [similar tutorial](https://docs.microsoft.com/azure/event-grid/custom-event-quickstart) using [Azure CLI](https://docs.microsoft.com/cli/azure).


### Install the package
Install the Azure Event Grid client library for Python with [pip][pip]:

```bash
pip install azure-eventgrid
```

* An existing Event Grid topic or domain is required. You can create the resource using [Azure Portal][azure_portal_create_EG_resource] or [Azure CLI][azure_cli_link]

If you use Azure CLI, replace `<resource-group-name>` and `<resource-name>` with your own unique names.

#### Create an Event Grid Topic

```
az eventgrid topic --create --location <location> --resource-group <resource-group-name> --name <resource-name>
```

#### Create an Event Grid Domain

```
az eventgrid domain --create --location <location> --resource-group <resource-group-name> --name <resource-name>
```

### Authenticate the client
In order to interact with the Event Grid service, you will need to create an instance of a client.
An **endpoint** and **credential** are necessary to instantiate the client object.

#### Looking up the endpoint
You can find the topic endpoint within the Event Grid Topic resource on the Azure portal. This will look like:
`"https://<event-grid-topic-name>.<topic-location>.eventgrid.azure.net/api/events"`

#### Create the client with AzureKeyCredential

To use an Access key as the `credential` parameter,
pass the key as a string into an instance of [AzureKeyCredential][azure-key-credential].

> **Note:** The Access Key may be found in the azure portal in the "Access Keys" menu of the Event Grid Topic resource.  They may also be obtained via the azure CLI, or the `azure-mgmt-eventgrid` library. A guide for getting access keys can be found [here](https://docs.microsoft.com/azure/event-grid/get-access-keys).

```python
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient

endpoint = "https://<name>.<region>.eventgrid.azure.net/api/events"
credential = AzureKeyCredential("<access_key>")
eg_publisher_client = EventGridPublisherClient(endpoint, credential)
```
> **Note:** A client may also be authenticated via SAS signature, using the `AzureSasCredential`. A sample demonstrating this, is available [here][python-eg-sample-send-using-sas] ([async_version][python-eg-sample-send-using-sas-async]).

> **Note:** The `generate_sas` method can be used to generate a shared access signature. A sample demonstrating this can be seen [here][python-eg-generate-sas].

## Key concepts

### Topic
A **[topic](https://docs.microsoft.com/azure/event-grid/concepts#topics)** is a channel within the EventGrid service to send events. The event schema that a topic accepts is decided at topic creation time. If events of a schema type are sent to a topic that requires a different schema type, errors will be raised.

### Domain
An event **[domain](https://docs.microsoft.com/azure/event-grid/event-domains)** is a management tool for large numbers of Event Grid topics related to the same application. They allow you to publish events to thousands of topics. Domains also give you authorization and authentication control over each topic. For more information, visit [Event domain overview](https://docs.microsoft.com/azure/event-grid/event-domains).

When you create an event domain, a publishing endpoint for this domain is made available to you. This process is similar to creating an Event Grid Topic. The only difference is that, when publishing to a domain, you must specify the topic within the domain that you'd like the event to be delivered to.

### Event schemas
An **[event](https://docs.microsoft.com/azure/event-grid/concepts#events)** is the smallest amount of information that fully describes something that happened in the system. When a custom topic or domain is created, you must specify the schema that will be used when publishing events.

Event Grid supports multiple schemas for encoding events.

#### Event Grid schema
While you may configure your topic to use a [custom schema](https://docs.microsoft.com/azure/event-grid/input-mappings), it is more common to use the already-defined Event Grid schema. See the specifications and requirements [here](https://docs.microsoft.com/azure/event-grid/event-schema).

#### CloudEvents v1.0 schema
Another option is to use the CloudEvents v1.0 schema. [CloudEvents](https://cloudevents.io/) is a Cloud Native Computing Foundation project which produces a specification for describing event data in a common way. The service summary of CloudEvents can be found [here](https://docs.microsoft.com/azure/event-grid/cloud-event-schema).

### EventGridPublisherClient
`EventGridPublisherClient` provides operations to send event data to a topic hostname specified during client initialization.

Regardless of the schema that your topic or domain is configured to use, `EventGridPublisherClient` will be used to publish events to it. Use the `send` method publishing events.

The following formats of events are allowed to be sent:
- A list or a single instance of strongly typed EventGridEvents.
- A dict representation of a serialized EventGridEvent object.
- A list or a single instance of strongly typed CloudEvents.
- A dict representation of a serialized CloudEvent object.

- A dict representation of any Custom Schema.

Please have a look at the [samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventgrid/azure-eventgrid/samples) for detailed examples.


 **Note:** It is important to know if your topic supports CloudEvents or EventGridEvents before publishing. If you send to a topic that does not support the schema of the event you are sending, send() will throw an exception.

### System Topics
A **[system topic](https://docs.microsoft.com/azure/event-grid/system-topics)** in Event Grid represents one or more events published by Azure services such as Azure Storage or Azure Event Hubs. For example, a system topic may represent all blob events or only blob creation and blob deletion events published for a specific storage account.

The names of the various event types for the system events published to Azure Event Grid are available in `azure.eventgrid.SystemEventNames`.
For complete list of recognizable system topics, visit [System Topics](https://docs.microsoft.com/azure/event-grid/system-topics).

 For more information about the key concepts on Event Grid, see [Concepts in Azure Event Grid][publisher-service-doc].

## Examples

The following sections provide several code snippets covering some of the most common Event Grid tasks, including:

* [Send an Event Grid Event](#send-an-event-grid-event)
* [Send a Cloud Event](#send-a-cloud-event)
* [Send Multiple Events](#send-multiple-events)
* [Send events as Dictionaries](#send-events-as-dictionaries)
* [Consume a payload from storage queue](#consume-from-storage-queue)
* [Consume from ServiceBus](#consume-from-servicebus)

### Send an Event Grid Event

This example publishes an Event Grid event.

```Python
import os
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient, EventGridEvent

key = os.environ["EG_ACCESS_KEY"]
endpoint = os.environ["EG_TOPIC_HOSTNAME"]

event = EventGridEvent(
    data={"team": "azure-sdk"},
    subject="Door1",
    event_type="Azure.Sdk.Demo",
    data_version="2.0"
)

credential = AzureKeyCredential(key)
client = EventGridPublisherClient(endpoint, credential)

client.send(event)
```

### Send a Cloud Event

This example publishes a Cloud event.

```Python
import os
from azure.core.credentials import AzureKeyCredential
from azure.core.messaging import CloudEvent
from azure.eventgrid import EventGridPublisherClient

key = os.environ["CLOUD_ACCESS_KEY"]
endpoint = os.environ["CLOUD_TOPIC_HOSTNAME"]

event = CloudEvent(
    type="Azure.Sdk.Sample",
    source="https://egsample.dev/sampleevent",
    data={"team": "azure-sdk"}
)

credential = AzureKeyCredential(key)
client = EventGridPublisherClient(endpoint, credential)

client.send(event)
```

### Send Multiple events

It is possible to send events as a batch when sending multiple events to a topic or a domain. This example sends a list of CloudEvents using the send method.

**WARNING:** When sending a list of multiple events at one time, iterating over and sending each event will not result in optimal performance. For best performance, it is highly recommended to send a list of events.

```Python
import os
from azure.core.credentials import AzureKeyCredential
from azure.core.messaging import CloudEvent
from azure.eventgrid import EventGridPublisherClient

key = os.environ["CLOUD_ACCESS_KEY"]
endpoint = os.environ["CLOUD_TOPIC_HOSTNAME"]

event0 = CloudEvent(
    type="Azure.Sdk.Sample",
    source="https://egsample.dev/sampleevent",
    data={"team": "azure-sdk"}
)
event1 = CloudEvent(
    type="Azure.Sdk.Sample",
    source="https://egsample.dev/sampleevent",
    data={"team2": "azure-eventgrid"}
)

events = [event0, event1]

credential = AzureKeyCredential(key)
client = EventGridPublisherClient(endpoint, credential)

client.send(events)
```

### Send events as dictionaries

A dict representation of respective serialized models can also be used to publish CloudEvent(s) or EventGridEvent(s) apart from the strongly typed objects.

Use a dict-like representation to send to a topic with custom schema as shown below.

```Python
import os
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient

key = os.environ["CUSTOM_SCHEMA_ACCESS_KEY"]
endpoint = os.environ["CUSTOM_SCHEMA_TOPIC_HOSTNAME"]

event = custom_schema_event = {
    "customSubject": "sample",
    "customEventType": "sample.event",
    "customDataVersion": "2.0",
    "customId": uuid.uuid4(),
    "customEventTime": dt.datetime.now(UTC()).isoformat(),
    "customData": "sample data"
    }

credential = AzureKeyCredential(key)
client = EventGridPublisherClient(endpoint, credential)

client.send(event)
```

### Consume from storage queue

This example consumes a message received from storage queue and deserializes it to a CloudEvent object.

```Python
from azure.core.messaging import CloudEvent
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

    ## deserialize payload into a list of typed Events
    events = [CloudEvent.from_dict(json.loads(msg.content)) for msg in payload]
```

### Consume from servicebus

This example consumes a payload message received from ServiceBus and deserializes it to an EventGridEvent object.

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

    ## deserialize payload into a list of typed Events
    events = [EventGridEvent.from_dict(json.loads(next(msg.body).decode('utf-8'))) for msg in payload]
```

## Distributed Tracing with EventGrid

You can use opentelemetry for Python as usual with EventGrid since it's compatible with azure-core tracing integration.

Here is an example of using OpenTelemetry to trace sending a CloudEvent.

First, set OpenTelemetry as enabled tracing plugin for EventGrid.

```python
from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan

settings.tracing_implementation = OpenTelemetrySpan
```

Regular open telemetry usage from here. See [OpenTelemetry](https://github.com/open-telemetry/opentelemetry-python) for details.
This example uses a simple console exporter to export the traces. Any exporter can be used here including `azure-monitor-opentelemetry-exporter`, `jaeger`, `zipkin` etc.

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor

# Simple console exporter
exporter = ConsoleSpanExporter()

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(
    SimpleExportSpanProcessor(exporter)
)
```

Once the `tracer` and `exporter` are set, please follow the example below to start collecting traces while using the `send` method from the `EventGridPublisherClient` to send a CloudEvent object.

```python
import os
from azure.eventgrid import EventGridPublisherClient
from azure.core.messaging import CloudEvent
from azure.core.credentials import AzureKeyCredential

hostname = os.environ['CLOUD_TOPIC_HOSTNAME']
key = AzureKeyCredential(os.environ['CLOUD_ACCESS_KEY'])
cloud_event = CloudEvent(
    source = 'demo',
    type = 'sdk.demo',
    data = {'test': 'hello'},
)
with tracer.start_as_current_span(name="MyApplication"):
    client = EventGridPublisherClient(hostname, key)
    client.send(cloud_event)
```

## Troubleshooting

- Enable `azure.eventgrid` logger to collect traces from the library.

### General
Event Grid client library will raise exceptions defined in [Azure Core][azure_core_exceptions].

### Logging
This library uses the standard
[logging][python_logging] library for logging.
Basic information about HTTP sessions (URLs, headers, etc.) is logged at INFO
level.

### Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs]
describes available configurations for retries, logging, transport protocols, and more.

## Next steps

The following section provides several code snippets illustrating common patterns used in the Event Grid Python API.

### More sample code

These code samples show common champion scenario operations with the Azure Event Grid client library.

* Generate Shared Access Signature: [sample_generate_sas.py][python-eg-generate-sas]

* Authenticate the client: [sample_authentication.py][python-eg-auth] ([async_version][python-eg-auth-async])

* Publish events to a topic using SAS: [sample_publish_events_to_a_topic_using_sas_credential_async.py][python-eg-sample-send-using-sas] ([async_version][python-eg-sample-send-using-sas-async])
* Publish Event Grid Events to a topic: [sample_publish_eg_events_to_a_topic.py][python-eg-sample-eg-event] ([async_version][python-eg-sample-eg-event-async])
* Publish EventGrid Events to a domain topic: [sample_publish_eg_events_to_a_domain_topic.py][python-eg-sample-eg-event-to-domain] ([async_version][python-eg-sample-eg-event-to-domain-async])
* Publish a Cloud Event: [sample_publish_events_using_cloud_events_1.0_schema.py][python-eg-sample-send-cloudevent] ([async_version][python-eg-sample-send-cloudevent-async])
* Publish a Custom Schema: [sample_publish_custom_schema_to_a_topic.py][python-eg-publish-custom-schema] ([async_version][python-eg-publish-custom-schema-async])

The following samples cover publishing and consuming `dict` representations of EventGridEvents and CloudEvents.
* Publish EventGridEvent as dict like representation: [sample_publish_eg_event_using_dict.py][python-eg-sample-send-eg-as-dict] ([async_version][python-eg-sample-send-eg-as-dict-async])

* Publish CloudEvent as dict like representation: [sample_publish_cloud_event_using_dict.py][python-eg-sample-send-cloudevent-as-dict] ([async_version][python-eg-sample-send-cloudevent-as-dict-async])

* Consume a Custom Payload of raw cloudevent data: [sample_consume_custom_payload.py][python-eg-sample-consume-custom-payload]

More samples can be found [here][python-eg-samples].

* More samples related to the send scenario can be seen [here][python-eg-publish-samples].
* To see more samples related to consuming a payload from different messaging services as a typed object, please visit [Consume Samples][python-eg-consume-samples]

### Additional documentation

For more extensive documentation on Azure Event Grid, see the [Event Grid documentation][python-eg-product-docs] on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_cli_link]: https://pypi.org/project/azure-cli/
[python-eg-src]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/
[python-eg-pypi]: https://pypi.org/project/azure-eventgrid
[python-eg-product-docs]: https://docs.microsoft.com/azure/event-grid/overview
[python-eg-ref-docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventgrid/latest/index.html
[publisher-service-doc]: https://docs.microsoft.com/azure/event-grid/concepts
[python-eg-samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventgrid/azure-eventgrid/samples
[python-eg-changelog]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventgrid/azure-eventgrid/CHANGELOG.md
[pip]: https://pypi.org/project/pip/

[azure_portal_create_EG_resource]: https://ms.portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.EventGrid%2Ftopics
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_subscription]: https://azure.microsoft.com/free/

[python-eg-auth]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_authentication.py
[python-eg-generate-sas]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_generate_sas.py
[python-eg-sample-send-using-sas]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_events_to_a_topic_using_sas_credential.py
[python-eg-sample-eg-event]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_eg_events_to_a_topic.py
[python-eg-sample-eg-event-to-domain]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_eg_events_to_a_domain.py
[python-eg-sample-send-cloudevent]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_events_using_cloud_events_1.0_schema.py
[python-eg-publish-custom-schema]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_custom_schema_to_a_topic.py
[python-eg-sample-send-eg-as-dict]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_eg_event_using_dict.py
[python-eg-sample-send-cloudevent-as-dict]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_cloud_event_using_dict.py

[python-eg-auth-async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_authentication_async.py
[python-eg-sample-send-using-sas-async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_events_to_a_topic_using_sas_credential_async.py
[python-eg-sample-eg-event-async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_eg_events_to_a_topic_async.py
[python-eg-sample-eg-event-to-domain-async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_eg_events_to_a_domain_async.py
[python-eg-sample-send-cloudevent-async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_events_using_cloud_events_1.0_schema_async.py
[python-eg-publish-custom-schema-async]:https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_custom_schema_to_a_topic_async.py
[python-eg-sample-send-eg-as-dict-async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_eg_event_using_dict_async.py
[python-eg-sample-send-cloudevent-as-dict-async]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/async_samples/sample_publish_cloud_event_using_dict_async.py

[python-eg-publish-samples]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/publish_samples
[python-eg-consume-samples]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/consume_samples
[python-eg-sample-consume-custom-payload]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_consume_custom_payload.py

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
