# Azure Event Grid client library for Python

Azure Event Grid is a fully-managed intelligent event routing service that allows for uniform event consumption using a publish-subscribe model.

[Source code][python-eg-src] | [Package (PyPI)][python-eg-pypi] | [API reference documentation][python-eg-ref-docs]| [Product documentation][python-eg-product-docs] | [Samples][python-eg-samples]| [Changelog][python-eg-changelog]

## Getting started

### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and an Event Grid Topic resource to use this package.

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
You can find the endpoint and the hostname on the Azure portal.

#### Create the client with AzureKeyCredential

To use an API key as the `credential` parameter,
pass the key as a string into an instance of [AzureKeyCredential][azure-key-credential].

```python
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient

endpoint = "https://<name>.<region>.eventgrid.azure.net"
credential = AzureKeyCredential("<api_key>")
eg_publisher_client = EventGridPublisherClient(endpoint, credential)
```

## Key concepts

Information about the key concepts on Event Grid, see [Concepts in Azure Event Grid][publisher-service-doc]

### EventGridPublisherClient
`EventGridPublisherClient` provides operations to send event data to topic hostname specified during client initialization.
CloudEvents and EventGridEvents can be sent either as a single event or a list of respective typed objects or their equivalent dict representations. To send a custom schema, a dict representation can be used. Please have a look at the [samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventgrid/azure-eventgrid/samples) for detailed examples.

## Examples

The following sections provide several code snippets covering some of the most common Event Grid tasks, including:

* [Send an Event Grid Event](#send-an-event-grid-event)
* [Send a Cloud Event](#send-a-cloud-event)

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
from azure.eventgrid import EventGridPublisherClient, CloudEvent

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

* Publish EventGrid Events to a topic: [sample_publish_eg_events_to_a_topic.py][python-eg-sample-egevent]
* Publish EventGrid Events to a domain: [sample_publish_eg_events_to_a_domain.py][python-eg-sample-egevent-to-domain]
* Publish a Cloud Event: [sample_publish_events_using_cloud_events_1.0_schema.py][python-eg-sample-send-cloudevent]

More samples can be found [here][python-eg-samples].

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
[python-eg-samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventgrid/azure-eventgrid/samples
[python-eg-changelog]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventgrid/azure-eventgrid/CHANGELOG.md
[pip]: https://pypi.org/project/pip/

[azure_portal_create_EG_resource]: https://ms.portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.EventGrid%2Ftopics
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[azure_subscription]: https://azure.microsoft.com/free/

[python-eg-sample-egevent]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_eg_events_to_a_topic.py
[python-eg-sample-egevent-to-domain]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_eg_events_to_a_domain.py
[python-eg-sample-send-cloudevent]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/sync_samples/sample_publish_events_using_cloud_events_1.0_schema.py
[publisher-service-doc]: https://docs.microsoft.com/azure/event-grid/concepts

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
