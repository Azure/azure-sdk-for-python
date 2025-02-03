# Azure Event Grid client library for Python

Azure Event Grid is a fully-managed intelligent event routing service that allows for uniform event consumption using a publish-subscribe model.

[Source code][python-eg-src]
| [Package (PyPI)][python-eg-pypi]
| [Package (Conda)](https://anaconda.org/microsoft/azure-eventgrid/)
| [API reference documentation][python-eg-ref-docs]
| [Product documentation][python-eg-product-docs]
| [Samples][python-eg-samples]
| [Changelog][python-eg-changelog]

## _Disclaimer_

This is a GA release of Azure Event Grid's `EventGridPublisherClient` and `EventGridConsumerClient`. `EventGridPublisherClient` supports `send` for Event Grid Basic and Event Grid Namespaces. `EventGridConsumerClient` supports `receive`, `acknowledge` , `release`, `reject`, and `renew_locks` operations for Event Grid Namespaces. Please refer to the [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventgrid/azure-eventgrid/samples) for further information.

## Getting started

### Prerequisites
* Python 3.8 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and at least one of the following:
    * an Event Grid Namespace resource. To create an Event Grid Namespace resource follow [this tutorial](https://learn.microsoft.com/azure/event-grid/create-view-manage-namespaces).
    * an Event Grid Basic resource. To create an Event Grid Basic resource via the Azure portal follow this [step-by-step tutorial](https://learn.microsoft.com/azure/event-grid/custom-event-quickstart-portal). To create an Event Grid Basic resource via the [Azure CLI](https://learn.microsoft.com/cli/azure) follow this [tutorial](https://learn.microsoft.com/azure/event-grid/custom-event-quickstart)

### Event Grid Resources

Azure Event Grid Namespaces supports both pull and push delivery. Azure Event Grid Basic supports only push delivery.
More information on the two resource tiers can be found [here](https://learn.microsoft.com/azure/event-grid/choose-right-tier).

**Note:** Azure Event Grid Namespaces only supports the Cloud Event v1.0 Schema.

### Install the package
Install the Azure Event Grid client library for Python with [pip][pip]:

```bash
pip install azure-eventgrid
```

* An existing Event Grid Basic topic or domain, or Event Grid Namespace topic is required. You can create the resource using [Azure Portal][azure_portal_create_EG_resource] or [Azure CLI][azure_cli_link]

If you use Azure CLI, replace `<resource-group-name>` and `<resource-name>` with your own unique names.

#### Create an Event Grid Namespace

```
az eventgrid namespace create --location <location> --resource-group <resource-group-name> --name <resource-name>
```

#### Create an Event Grid Namespace Topic

```
az eventgrid namespace create topic --location <location> --resource-group <resource-group-name> --name <resource-name>
```

### Authenticate the client
In order to interact with the Event Grid service, you will need to create an instance of a client.
An **endpoint** and **credential** are necessary to instantiate the client object.


The default EventGridPublisherClient created is compatible with an Event Grid Basic Resource. To create an Event Grid Namespace compatible client, specify `namespace_topic="YOUR_TOPIC_NAME"` when instantiating the client.

```python
# Event Grid Namespace client
client = EventGridPublisherClient(endpoint, credential, namespace_topic=YOUR_TOPIC_NAME)

# Event Grid Basic Client
client = EventGridPublisherClient(endpoint, credential)
```

EventGridConsumerClient only supports Event Grid Namespaces.
```python
# Event Grid Namespace Client
client = EventGridConsumerClient(endpoint, credential, namespace_topic=YOUR_TOPIC_NAME, subscription=YOUR_SUBSCRIPTION_NAME)
```

#### Using Azure Active Directory (AAD)

Azure Event Grid provides integration with Azure Active Directory (Azure AD) for identity-based authentication of requests. With Azure AD, you can use role-based access control (RBAC) to grant access to your Azure Event Grid resources to users, groups, or applications.

To send events to a topic or domain with a `TokenCredential`, the authenticated identity should have the "Event Grid Data Sender" role assigned.
To receive events from a topic event subscription with a `TokenCredential`, the authenticated identity should have the "Event Grid Data Receiver" role assigned.
To send and receive events to/from a topic with a `TokenCredential`, the authenticated identity should have the "Event Grid Data Contributor" role assigned.

More about RBAC setup can be found [here](https://learn.microsoft.com/azure/role-based-access-control/role-assignments-steps).

With the `azure-identity` package, you can seamlessly authorize requests in both development and production environments. To learn more about Azure Active Directory, see the [`azure-identity` README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md).

For example, you can use `DefaultAzureCredential` to construct a client which will authenticate using Azure Active Directory:

<!-- SNIPPET:sample_authentication.client_auth_with_token_cred -->

```python
from azure.identity import DefaultAzureCredential
from azure.eventgrid import EventGridPublisherClient, EventGridEvent

default_az_credential = DefaultAzureCredential()
endpoint = os.environ["EVENTGRID_TOPIC_ENDPOINT"]
client = EventGridPublisherClient(endpoint, default_az_credential)
```

<!-- END SNIPPET -->

### Looking up the endpoint

#### Event Grid Namespace
You can find the Namespace endpoint within the Event Grid Namespace resource on the Azure portal. This will look like:
`"<event-grid-namespace-name>.<namespace-location>.eventgrid.azure.net"`

#### Event Grid Basic
You can find the topic endpoint within the Event Grid Topic resource on the Azure portal. This will look like:
`"https://<event-grid-topic-name>.<topic-location>.eventgrid.azure.net/api/events"`

### Create the client with AzureKeyCredential

To use an Access key as the `credential` parameter,
pass the key as a string into an instance of [AzureKeyCredential][azure-key-credential].

> **Note:** The Access Key may be found in the azure portal in the "Access Keys" menu of the Event Grid Topic resource.  They may also be obtained via the azure CLI, or the `azure-mgmt-eventgrid` library. A guide for getting access keys can be found [here](https://learn.microsoft.com/azure/event-grid/get-access-keys).

<!-- SNIPPET:sample_authentication.client_auth_with_key_cred -->

```python
import os
from azure.eventgrid import EventGridPublisherClient
from azure.core.credentials import AzureKeyCredential

topic_key = os.environ["EVENTGRID_TOPIC_KEY"]
endpoint = os.environ["EVENTGRID_TOPIC_ENDPOINT"]

credential_key = AzureKeyCredential(topic_key)
client = EventGridPublisherClient(endpoint, credential_key)
```

<!-- END SNIPPET -->

> **Note:** A Basic client may also be authenticated via SAS signature, using the `AzureSasCredential`. A sample demonstrating this, is available [here][python-eg-sample-send-using-sas] ([async_version][python-eg-sample-send-using-sas-async]).

> **Note:** The `generate_sas` method can be used to generate a shared access signature. A sample demonstrating this can be seen [here][python-eg-generate-sas].

## Key concepts

### Event Grid Namespace

A **[namespace](https://learn.microsoft.com/azure/event-grid/concepts-event-grid-namespaces#namespaces)** is a management container for other resources. It allows for grouping of related resources in order to manage them under one subscription.

#### Namespace Topic

A **[namespace topic](https://learn.microsoft.com/azure/event-grid/concepts-event-grid-namespaces#namespace-topics)** is a topic that is created within an Event Grid namespace. The client publishes events to an HTTP namespace endpoint specifying a namespace topic where published events are logically contained. A namespace topic only supports the CloudEvent v1.0 schema.

#### Event Subscription

An **[event subscription](https://learn.microsoft.com/azure/event-grid/concepts-event-grid-namespaces#event-subscriptions)** is a configuration resource associated with a single topic.


### Event Grid Basic

#### Topic
A **[topic](https://learn.microsoft.com/azure/event-grid/concepts#topics)** is a channel within the Event Grid service to send events. The event schema that a topic accepts is decided at topic creation time. If events of a schema type are sent to a topic that requires a different schema type, errors will be raised.

#### Domain
An event **[domain](https://learn.microsoft.com/azure/event-grid/event-domains)** is a management tool for large numbers of Event Grid topics related to the same application. They allow you to publish events to thousands of topics. Domains also give you authorization and authentication control over each topic. For more information, visit [Event domain overview](https://learn.microsoft.com/azure/event-grid/event-domains).

#### Event schemas
An **[event](https://learn.microsoft.com/azure/event-grid/concepts#events)** is the smallest amount of information that fully describes something that happened in the system. When a custom topic or domain is created, you must specify the schema that will be used when publishing events.

Event Grid supports multiple schemas for encoding events.

#### System Topics
A **[system topic](https://learn.microsoft.com/azure/event-grid/system-topics)** in Event Grid represents one or more events published by Azure services such as Azure Storage or Azure Event Hubs. For example, a system topic may represent all blob events or only blob creation and blob deletion events published for a specific storage account.

The names of the various event types for the system events published to Azure Event Grid are available in `azure.eventgrid.SystemEventNames`.
For complete list of recognizable system topics, visit [System Topics](https://learn.microsoft.com/azure/event-grid/system-topics).

 For more information about the key concepts on Event Grid, see [Concepts in Azure Event Grid][publisher-service-doc].

## EventGridPublisherClient

`EventGridPublisherClient` provides operations to send event data to a resource specified during client initialization.

If you are using Event Grid Basic, regardless of the schema that your topic or domain is configured to use, `EventGridPublisherClient` will be used to publish events to it. Use the `send` method to publish events.

The following formats of events are allowed to be sent to an Event Grid Basic resource:
- A list or a single instance of strongly typed EventGridEvents.
- A dict representation of a serialized EventGridEvent object.
- A list or a single instance of strongly typed CloudEvents.
- A dict representation of a serialized CloudEvent object.

- A dict representation of any Custom Schema.

The following formats of events are allowed to be sent to an Event Grid Namespace resource, when a namespace topic is specified:

* A list of single instance of strongly typed CloudEvents.
* A dict representation of a serialized CloudEvent object.

Please have a look at the [samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventgrid/azure-eventgrid/samples) for detailed examples.

## Event Grid on Kubernetes with Azure Arc

Event Grid on Kubernetes with Azure Arc is an offering that allows you to run Event Grid on your own Kubernetes cluster. This capability is enabled by the use of Azure Arc enabled Kubernetes. Through Azure Arc enabled Kubernetes, a supported Kubernetes cluster connects to Azure. Once connected, you are able to install Event Grid on it. Learn more about it [here](https://learn.microsoft.com/azure/event-grid/kubernetes/overview).

## Examples

The following sections provide several code snippets covering some of the most common Event Grid tasks, including:

* [Send a Cloud Event](#send-a-cloud-event)
* [Send Multiple Events](#send-multiple-events)
* [Receive and Process Events from Namespace](#receive-and-process-events-from-namespace)

### Send a Cloud Event

This example publishes a Cloud event.

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.core.messaging import CloudEvent
from azure.eventgrid import EventGridPublisherClient

key = os.environ["EVENTGRID_KEY"]
endpoint = os.environ["EVENTGRID_ENDPOINT"]
topic_name = os.environ["EVENTGRID_TOPIC_NAME"]


event = CloudEvent(
    type="Azure.Sdk.Sample",
    source="https://egsample.dev/sampleevent",
    data={"team": "azure-sdk"}
)

credential = AzureKeyCredential(key)
client = EventGridPublisherClient(endpoint, credential, namespace_topic=topic_name)

client.send(event)
```

### Send Multiple events

It is possible to send events as a batch when sending multiple events to a topic or a domain. This example sends a list of CloudEvents using the send method.

**WARNING:** When sending a list of multiple events at one time, iterating over and sending each event will not result in optimal performance. For best performance, it is highly recommended to send a list of events.

```python
import os
from azure.core.credentials import AzureKeyCredential
from azure.core.messaging import CloudEvent
from azure.eventgrid import EventGridPublisherClient

key = os.environ["EVENTGRID_KEY"]
endpoint = os.environ["EVENTGRID_ENDPOINT"]
topic_name = os.environ["EVENTGRID_TOPIC_NAME"]

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
client = EventGridPublisherClient(endpoint, credential, namespace_topic=topic_name)

client.send(events)
```

### Receive and Process Events from Namespace

Use EventGridConsumerClient's receive function to receive CloudEvents from a Namespace event subscription. Then try to acknowledge, reject, release or renew the locks. 

```python
import os
import uuid
import datetime as dt
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridConsumerClient

key = os.environ["EVENTGRID_KEY"]
endpoint = os.environ["EVENTGRID_ENDPOINT"]
topic_name = os.environ["EVENTGRID_TOPIC_NAME"]
sub_name = os.environ["EVENTGRID_EVENT_SUBSCRIPTION_NAME"]

credential = AzureKeyCredential(key)
client = EventGridConsumerClient(endpoint, credential, namespace_topic=topic_name, subscription=sub_name)

events = client.receive(max_events=4)

for detail in events.value:
    data = detail.event.data
    broker_properties = detail.broker_properties
    if data == "release":
        release_events.append(broker_properties.lock_token)
    elif data == "acknowledge":
        acknowledge_events.append(broker_properties.lock_token)
    else:
        reject_events.append(broker_properties.lock_token)

    # Renew all Locks
    renew_tokens = e.broker_properties.lock_token
    renew_result = client.renew_locks(
        lock_tokens=renew_tokens,
    )


release_result = client.release(
    lock_tokens=release_events,
)

ack_result = client.acknowledge(
    lock_tokens=acknowledge_events,
)

reject_result = client.reject(
    lock_tokens=reject_events,
)

```

## Distributed Tracing with Event Grid

You can use OpenTelemetry for Python as usual with Event Grid since it's compatible with azure-core tracing integration.

Here is an example of using OpenTelemetry to trace sending a CloudEvent.

First, set OpenTelemetry as enabled tracing plugin for Event Grid.

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
from opentelemetry.sdk.trace.export import SimpleSpanProcessor  # this requires opentelemetry >= 1.0.0

# Simple console exporter
exporter = ConsoleSpanExporter()

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(exporter)
)
```

Once the `tracer` and `exporter` are set, please follow the example below to start collecting traces while using the `send` method from the `EventGridClient` to send a CloudEvent object.

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

#### Additional Namespace Event Grid Scenarios

* Authenticate the client: [sample_namespace_authentication_async.py][python-eg-namespace-authenticate-async]
* Publish to the namespace topic: [sample_publish_cloud_event_async.py][python-eg-namespace-publish-cloud-async]
* Consume and Process from an event subscription: [sample_consume_process_events.py][python-eg-namespace-consume-async]


#### Additional Basic Event Grid Scenarios

* Generate Shared Access Signature: [sample_generate_sas.py][python-eg-generate-sas]

* Authenticate the client: [sample_authentication.py][python-eg-auth] ([async_version][python-eg-auth-async])

* Publish events to a topic using SAS: [sample_publish_events_to_a_topic_using_sas_credential_async.py][python-eg-sample-send-using-sas] ([async_version][python-eg-sample-send-using-sas-async])
* Publish Event Grid Events to a topic: [sample_publish_eg_events_to_a_topic.py][python-eg-sample-eg-event] ([async_version][python-eg-sample-eg-event-async])
* Publish Event Grid Events to a domain topic: [sample_publish_eg_events_to_a_domain_topic.py][python-eg-sample-eg-event-to-domain] ([async_version][python-eg-sample-eg-event-to-domain-async])
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

For more extensive documentation on Azure Event Grid, see the [Event Grid documentation][python-eg-product-docs] on learn.microsoft.com.

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[azure_cli_link]: https://pypi.org/project/azure-cli/
[python-eg-src]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventgrid/azure-eventgrid
[python-eg-pypi]: https://pypi.org/project/azure-eventgrid
[python-eg-product-docs]: https://learn.microsoft.com/azure/event-grid/overview
[python-eg-ref-docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-eventgrid/latest/index.html
[publisher-service-doc]: https://learn.microsoft.com/azure/event-grid/concepts
[python-eg-samples]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventgrid/azure-eventgrid/samples
[python-eg-changelog]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/eventgrid/azure-eventgrid/CHANGELOG.md
[pip]: https://pypi.org/project/pip/

[azure_portal_create_EG_resource]: https://ms.portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.EventGrid%2Ftopics
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[azure_core_ref_docs]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core#configurations
[azure_subscription]: https://azure.microsoft.com/free/

[python-eg-auth]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/sync_samples/sample_authentication.py
[python-eg-generate-sas]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/sync_samples/sample_generate_sas.py
[python-eg-sample-send-using-sas]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/sync_samples/sample_publish_events_to_a_topic_using_sas_credential.py
[python-eg-sample-eg-event]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/sync_samples/sample_publish_eg_events_to_a_topic.py
[python-eg-sample-eg-event-to-domain]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/sync_samples/sample_publish_eg_events_to_a_domain.py
[python-eg-sample-send-cloudevent]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/sync_samples/sample_publish_events_using_cloud_events_1.0_schema.py
[python-eg-publish-custom-schema]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/sync_samples/sample_publish_custom_schema_to_a_topic.py
[python-eg-sample-send-eg-as-dict]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/sync_samples/sample_publish_eg_event_using_dict.py
[python-eg-sample-send-cloudevent-as-dict]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/sync_samples/sample_publish_cloud_event_using_dict.py

[python-eg-auth-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/async_samples/sample_authentication_async.py
[python-eg-sample-send-using-sas-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/async_samples/sample_publish_events_to_a_topic_using_sas_credential_async.py
[python-eg-sample-eg-event-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/async_samples/sample_publish_eg_events_to_a_topic_async.py
[python-eg-sample-eg-event-to-domain-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/async_samples/sample_publish_eg_events_to_a_domain_async.py
[python-eg-sample-send-cloudevent-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/async_samples/sample_publish_events_using_cloud_events_1.0_schema_async.py
[python-eg-publish-custom-schema-async]:https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/async_samples/sample_publish_custom_schema_to_a_topic_async.py
[python-eg-sample-send-eg-as-dict-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/async_samples/sample_publish_eg_event_using_dict_async.py
[python-eg-sample-send-cloudevent-as-dict-async]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/async_samples/sample_publish_cloud_event_using_dict_async.py

[python-eg-publish-samples]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/publish_samples
[python-eg-consume-samples]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/consume_samples
[python-eg-sample-consume-custom-payload]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/basic/sync_samples/sample_consume_custom_payload.py


[python-eg-namespace-authenticate]:https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/namespace/sync_samples/sample_namespace_authentication.py
[python-eg-namespace-publish-cncf]:https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/namespace/sync_samples/sample_publish_cncf_events.py
[python-eg-namespace-publish-cloud]:https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/namespace/sync_samples/sample_publish_cloud_event.py
[python-eg-namespace-consume]:https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/namespace/samples/sync_samples/sample_consume_process_events.py


[python-eg-namespace-authenticate-async]:https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/namespace/async_samples/sample_namespace_authentication_async.py
[python-eg-namespace-publish-cncf-async]:https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/namespace/async_samples/sample_publish_cncf_events_async.py
[python-eg-namespace-publish-cloud-async]:https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/namespace/async_samples/sample_publish_cloud_event_async.py
[python-eg-namespace-consume-async]:https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/eventgrid/azure-eventgrid/samples/namespace/async_samples/sample_consume_process_events_async.py

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com