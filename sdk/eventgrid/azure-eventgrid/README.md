# Azure EventGrid client library for Python

Azure Event Grid is a fully-managed intelligent event routing service that allows for uniform event consumption using a publish-subscribe model.

[Source code][python-eg-src] | [Package (PyPI)][python-eg-pypi] | [API reference documentation][python-eg-ref-docs]| [Product documentation][python-eg-product-docs] | [Samples][python-eg-samples]

## Getting started

### Prerequisites
* Python 2.7, or 3.5 or later is required to use this package.
* You must have an [Azure subscription][azure_subscription] and an EventGrid Topic resource to use this package.

### Install the package
Install the Azure EventGrid client library for Python with [pip][pip]:

```bash
pip install azure-eventgrid
```

#### Create an EventGrid Topic
You can create the resource using [Azure Portal][azure_portal_create_EG_resource]

### Authenticate the client
In order to interact with the Eventgrid service, you will need to create an instance of a client. 
A **topic_hostname** and **credential** are necessary to instantiate the client object.

#### Looking up the endpoint
You can find the endpoint and the hostname on the Azure portal.

#### Create the client with AzureKeyCredential

To use an API key as the `credential` parameter,
pass the key as a string into an instance of [AzureKeyCredential][azure-key-credential].

```python
from azure.core.credentials import AzureKeyCredential
from azure.eventgrid import EventGridPublisherClient

topic_hostname = "https://<name>.<region>.eventgrid.azure.net/api/events"
credential = AzureKeyCredential("<api_key>")
eg_publisher_client = EventGridPublisherClient(topic_hostname, credential)
```

## Key concepts

### EventGridPublisherClient
`EventGridPublisherClient` provides operations to send event data to topic hostname specified during client initialization.
Either a list or a single instance of CloudEvent/EventGridEvent/CustomEvent can be sent.

### EventGridConsumer
`EventGridConsumer` is used to desrialize an event received.

## Troubleshooting

### General
Eventgrid client library will raise exceptions defined in [Azure Core][azure_core_exceptions].

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

The following section provides several code snippets illustrating common patterns used in the EventGrid Python API.

### More sample code

These code samples show common champion scenario operations with the Azure Eventgrid client library.

* Publish Custom Events to a topic: [cs1_publish_custom_events_to_a_topic.py][python-eg-sample-customevent]
* Publish Custom events to a domain topic: [cs2_publish_custom_events_to_a_domain_topic.py][python-eg-sample-customevent-to-domain]
* Deserialize a System Event: [cs3_consume_system_events.py][python-eg-sample-consume-systemevent]
* Deserialize a Custom Event: [cs4_consume_custom_events.py][python-eg-sample-consume-customevent]
* Deserialize a Cloud Event: [cs5_consume_events_using_cloud_events_1.0_schema.py][python-eg-sample-consume-cloudevent]
* Publish a Cloud Event: [cs6_publish_events_using_cloud_events_1.0_schema.py][python-eg-sample-send-cloudevent]

More samples can be found [here][python-eg-samples].

### Additional documentation

For more extensive documentation on Azure EventGrid, see the [Eventgrid documentation][python-eg-product-docs] on docs.microsoft.com.

## Contributing
This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [cla.microsoft.com][cla].

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct][code_of_conduct]. For more information see the [Code of Conduct FAQ][coc_faq] or contact [opencode@microsoft.com][coc_contact] with any additional questions or comments.

<!-- LINKS -->

[python-eg-src]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/
[python-eg-pypi]: https://pypi.org/project/azure-eventgrid
[python-eg-product-docs]: https://docs.microsoft.com/en-us/azure/event-grid/overview
[python-eg-ref-docs]: https://aka.ms/azsdk/python/eventgrid/docs
[python-eg-samples]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventgrid/azure-eventgrid/samples

[azure_portal_create_EG_resource]: https://ms.portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/Microsoft.EventGrid%2Ftopics
[azure-key-credential]: https://aka.ms/azsdk/python/core/azurekeycredential
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs

[python-eg-sample-customevent]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/champion_scenarios/cs1_publish_custom_events_to_a_topic.py
[python-eg-sample-customevent-to-domain]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/champion_scenarios/cs2_publish_custom_events_to_a_domain_topic.py
[python-eg-sample-consume-systemevent]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/champion_scenarios/cs3_consume_system_events.py
[python-eg-sample-consume-customevent]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/champion_scenarios/cs4_consume_custom_events.py
[python-eg-sample-send-cloudevent]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/champion_scenarios/cs5_publish_events_using_cloud_events_1.0_schema.py
[python-eg-sample-consume-cloudevent]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/eventgrid/azure-eventgrid/samples/champion_scenarios/cs6_consume_events_using_cloud_events_1.0_schema.py

[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
