# Azure Service Bus client library for Python

Azure Service Bus is a high performance cloud-managed messaging service for providing real-time and fault-tolerant communication between distributed senders and receivers.

Service Bus provides multiple mechanisms for asynchronous highly reliable communication, such as structured first-in-first-out messaging, 
publish/subscribe capabilities, and the ability to easily scale as your needs grow.

Use the Service Bus client library for Python to communicate between applications and services and implement asynchronous messaging patterns.

* Create Service Bus namespaces, queues, topics, and subscriptions, and modify their settings
* Send and receive messages within your Service Bus channels.
* Utilize message locks, sessions, and dead letter functionality to implement complex messaging patterns.

  - [Package (PyPi)][pypi]
  - [API reference documentation][api_docs]
  - [Product documentation][product_docs]
  - [Source code](./)
  - [ChangeLog](./CHANGELOG.md)
  - [Samples](./samples)
  - [Versioned API References][versioned_api_ref]

## Getting started

### Install the package

Install the Azure Service Bus client library for Python with [pip][pip]:

```Bash
pip install azure-servicebus --pre
```

**Prerequisites**: 
To use this package, you must have:
* Azure subscription - [Create a free account][azure_sub]
* Azure Service Bus - [Namespace and management credentials][service_bus_namespace]
* Python 2.7, 3.4, 3.5, 3.6 or 3.7 - [Install Python][python]

If you need an azure service bus namespace and do not wish to use the portal, you can use the Azure [Cloud Shell][cloud_shell_bash] to create one with this Azure CLI command:

```Bash
az servicebus namespace create --resource-group <resource-group-name> --name <servicebus-namespace-name> --location <servicebus-namespace-location>
```

### Authenticate the client

Interaction with Service Bus starts with an instance of the `ServiceBusClient` class. You either need a **connection string with SAS key**, or a **namespace** and one of its **account keys** to instantiate the client object.

#### Get credentials

Use the [Azure CLI][azure_cli] snippet below to populate an environment variable with the service bus connection string (you can also find these values in the [Azure portal][azure_portal]. The snippet is formatted for the Bash shell.

```Bash
RES_GROUP=<resource-group-name>
NAMESPACE_NAME=<servicebus-namespace-name>

export CONNECTION_STRING=$(az servicebus namespace authorization-rule keys list --resource-group $RES_GROUP --namespace-name $NAMESPACE_NAME --query RootManageSharedAccessKey --output tsv)
```

#### Create client

Once you've populated the `CONNECTION_STRING` environment variable, you can create the `ServiceBusClient`.

```Python
from azure.servicebus import ServiceBusClient

import os
connstr = os.environ['CONNECTION_STRING']

with ServiceBusClient.from_connection_string(connstr) as client:
    ...
```

Note: client can be initialized without a context manager, but must be manually closed via client.close() to not leak resources.

## Key concepts

Once you've initialized a `ServiceBusClient`, you can interact with the primary resource types within a Service Bus Namespace, of which multiple can exist and on which actual message transmission takes place, the namespace often serving as an application container:

* Queue: Allows for Sending and Receiving of messages, ordered first-in-first-out.  Often used for point-to-point communication.

* Topic: As opposed to Queues, Topics are better suited to publish/subscribe scenarios.  A topic can be sent to, but requires a subscription, of which there can be multiple in parallel, to consume from.

* Subscription: The mechanism to consume from a Topic.  Each subscription is independent, and receaves a copy of each message sent to the topic.  Rules and Filters can be used to tailor which messages are received by a specific subscription.

For more information about these resources, see [What is Azure Service Bus?][service_bus_overview].

## Examples

The following sections provide several code snippets covering some of the most common Service Bus tasks, including:

* [Create a queue](#create-a-queue)
* [Send a message to a queue](#send-to-a-queue)
* [Receive a message from a queue](#receive-from-a-queue)
* [Deadletter a message on receipt](#deadletter-a-message)

### Create a queue

After authenticating your `ServiceBusClient`, you can work with any resource in the namespace. The code snippet below creates a queue, continuing if one already exists with the same name within this Service Bus Namespace (generating a `409 Conflict` error).

```Python
queue_name = 'testQueue'
try:
    client.create_queue(queue_name)
except HTTPFailure as e:
    if e.status_code != 409:
        raise
```

> NOTE: For more information on error handling and troubleshooting, see the [Troubleshooting](#troubleshooting) section.

### Send to a queue

This example sends a message to a queue that is assumed to already exist per [creating a queue](#create-a-queue).

```Python
with client.get_queue_sender(queue_name):

    message = Message("Single message")
    queue_sender.send(message)
```

### Receive from a queue

To receive from a queue, you can either perform a one-off receive via "receiver.receive()" or receive persistently as follows:

```Python
with client.get_queue_receiver(queue_name) as receiver:
    for msg in receiver:
        print(str(msg))
        msg.complete()
```

### Deadletter a message

When receiving from a queue, you have multiple actions you can take on the messages you receive.  Where the prior example completes a message,
permanently removing it from the queue and marking as complete, this example demonstrates how to send the message to the dead letter queue:

```Python
with client.get_queue_receiver(queue_name) as receiver:
    for msg in receiver:
        print(str(msg))
        msg.dead_letter()
```

## Troubleshooting

### General

When you interact with Service Bus using the Python SDK, errors returned by the service correspond to the same HTTP status codes returned for REST API requests:

[HTTP Status Codes for Azure Service Bus Queues][queue_status_codes]
>NOTE: Status codes defined for each operation type, see the sidebar in the above link.

For example, if you try to create a queue using an ID (name) that already exists in your Service Bus namespace, a `409` error is returned, indicating the conflict. In the following snippet, the error is handled gracefully by catching the exception and displaying additional information about the error.

```Python
try:
    client.create_queue(queue_name)
except HTTPFailure as e:
    if e.status_code == 409:
        print("""Error creating queue.
HTTP status code 409: The ID (name) provided for the container is already in use.
The queue name must be unique within the namespace.""")
    else:
        raise
```

## Next steps

### More sample code

Several Service Bus Python SDK samples are available to you in the SDK's GitHub repository. These samples provide example code for additional scenarios commonly encountered while working with Service Bus:

* [`send_queue.py`][sample_send_queue] - Python code for sending to a service bus queue:
* [`receive_queue.py`][sample_receive_queue] - Python code for receiving from a service bus queue:

### Additional documentation

For more extensive documentation on the Service Bus service, see the [Service Bus DB documentation][service_bus_docs] on docs.microsoft.com.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

<!-- LINKS -->
[azure_cli]: https://docs.microsoft.com/cli/azure
[api_docs]: https://docs.microsoft.com/python/api/overview/azure/servicebus/client?view=azure-python
[product_docs]: https://docs.microsoft.com/azure/service-bus-messaging/
[azure_portal]: https://portal.azure.com
[azure_sub]: https://azure.microsoft.com/free/
[cloud_shell]: https://docs.microsoft.com/azure/cloud-shell/overview
[cloud_shell_bash]: https://shell.azure.com/bash
[pip]: https://pypi.org/project/pip/
[pypi]: https://pypi.org/project/azure-servicebus/
[python]: https://www.python.org/downloads/
[venv]: https://docs.python.org/3/library/venv.html
[virtualenv]: https://virtualenv.pypa.io
[versioned_api_ref]: https://azure.github.io/azure-sdk-for-python/ref/Service-Bus.html
[service_bus_namespace]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-create-namespace-portal
[service_bus_overview]: https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messaging-overview
[queue_status_codes]: https://docs.microsoft.com/en-us/rest/api/servicebus/create-queue#response-codes
[service_bus_docs]: https://docs.microsoft.com/en-us/azure/service-bus/
[sample_send_queue]: https://github.com/yunhaoling/azure-sdk-for-python/blob/servicebus-track2/sdk/servicebus/azure-servicebus/samples/sync_samples/send_queue.py
[sample_receive_queue]: https://github.com/yunhaoling/azure-sdk-for-python/blob/servicebus-track2/sdk/servicebus/azure-servicebus/samples/sync_samples/receive_queue.py