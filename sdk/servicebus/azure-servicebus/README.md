# Azure Service Bus client library for Python

Azure Service Bus is a high performance cloud-managed messaging service for providing real-time and fault-tolerant communication between distributed senders and receivers.

Service Bus provides multiple mechanisms for asynchronous highly reliable communication, such as structured first-in-first-out messaging, 
publish/subscribe capabilities, and the ability to easily scale as your needs grow.

Use the Service Bus client library for Python to communicate between applications and services and implement asynchronous messaging patterns.

* Create Service Bus namespaces, queues, topics, and subscriptions, and modify their settings
* Send and receive messages within your Service Bus channels.
* Utilize message locks, sessions, and dead letter functionality to implement complex messaging patterns.

[Source code](./) | [Package (PyPi)][pypi] | [API reference documentation][api_docs] | [Product documentation][product_docs] | [Samples](./samples) | [Changelog](./CHANGELOG.md)

## Getting started

### Install the package

Install the Azure Service Bus client library for Python with [pip][pip]:

```Bash
pip install azure-servicebus --pre
```

### Prerequisites: 
To use this package, you must have:
* Azure subscription - [Create a free account][azure_sub]
* Azure Service Bus - [Namespace and management credentials][service_bus_namespace]
* Python 2.7, 3.5, 3.6, 3.7 or 3.8 - [Install Python][python]


If you need an Azure service bus namespace, you can create it via the [Azure Portal][azure_namespace_creation].
If you do not wish to use the graphical portal UI, you can use the Azure CLI via [Cloud Shell][cloud_shell_bash], or Azure CLI run locally, to create one with this Azure CLI command:

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

export SERVICE_BUS_CONN_STR=$(az servicebus namespace authorization-rule keys list --resource-group $RES_GROUP --namespace-name $NAMESPACE_NAME --query RootManageSharedAccessKey --output tsv)
```

#### Create client

Once you've populated the `SERVICE_BUS_CONN_STR` environment variable, you can create the `ServiceBusClient`.

```Python
from azure.servicebus import ServiceBusClient

import os
connstr = os.environ['SERVICE_BUS_CONN_STR']

with ServiceBusClient.from_connection_string(connstr) as client:
    ...
```

Note: client can be initialized without a context manager, but must be manually closed via client.close() to not leak resources.

## Key concepts

Once you've initialized a `ServiceBusClient`, you can interact with the primary resource types within a Service Bus Namespace, of which multiple can exist and on which actual message transmission takes place, the namespace often serving as an application container:

* [Queue][queue_concept]: Allows for Sending and Receiving of messages, ordered first-in-first-out.  Often used for point-to-point communication.

* [Topic][topic_concept]: As opposed to Queues, Topics are better suited to publish/subscribe scenarios.  A topic can be sent to, but requires a subscription, of which there can be multiple in parallel, to consume from.

* [Subscription][subscription_concept]: The mechanism to consume from a Topic.  Each subscription is independent, and receaves a copy of each message sent to the topic.  Rules and Filters can be used to tailor which messages are received by a specific subscription.

For more information about these resources, see [What is Azure Service Bus?][service_bus_overview].

To interact with these resources, one should be familiar with the following SDK concepts:

* [ServiceBusClient](./azure/servicebus/_servicebus_client.py): This is the object a user should first initialize to connect to a Service Bus Namespace.  To interact with a queue topic or subscription, one would spawn a sender or receiver off of this client.

* [Sender](./azure/servicebus/_servicebus_sender.py): To send messages to a Queue or Topic, one would use the corrosponding `get_queue_sender` or `get_topic_sender` method off of a `ServiceBusClient` instance as seen [here](./samples/sync_samples/send_queue.py)

* [Receiver](./azure/servicebus/_servicebus_receiver.py): To receive messages from a Queue or Subscription, one would use the corrosponding `get_queue_receiver` or `get_subscription_receiver` method off of a `ServiceBusClient` instance as seen [here](./samples/sync_samples/receive_queue.py)

* [Message](./azure/servicebus/_common/message.py): When sending, this is the type you will construct to contain your payload.  When receiving, this is where you will access the payload and control how the message is "settled" (completed, dead-lettered, etc)

## Examples

The following sections provide several code snippets covering some of the most common Service Bus tasks, including:

* [Send a message to a queue](#send-to-a-queue)
* [Receive a message from a queue](#receive-from-a-queue)
* [Defer a message on receipt](#defer-a-message)


### Send to a queue

This example sends a message to a queue that is assumed to already exist, created via the Azure portal or az commands.

```Python
from azure.servicebus import ServiceBusClient

import os
connstr = os.environ['SERVICE_BUS_CONN_STR']

with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_queue_sender(queue_name):

        message = Message("Single message")
        queue_sender.send(message)
```

### Receive from a queue

To receive from a queue, you can either perform a one-off receive via "receiver.receive()" or receive persistently as follows:

```Python
from azure.servicebus import ServiceBusClient

import os
connstr = os.environ['SERVICE_BUS_CONN_STR']

with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_queue_receiver(queue_name) as receiver:
        for msg in receiver:
            print(str(msg))
            msg.complete()
```

### Defer a message

When receiving from a queue, you have multiple actions you can take on the messages you receive.  Where the prior example completes a message,
permanently removing it from the queue and marking as complete, this example demonstrates how to defer the message, sending it back to the queue
such that it must now be received via sequence number:

```Python
from azure.servicebus import ServiceBusClient

import os
connstr = os.environ['SERVICE_BUS_CONN_STR']

with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_queue_receiver(queue_name) as receiver:
        for msg in receiver:
            print(str(msg))
            msg.defer()
```

## Troubleshooting

### Logging

- Enable `azure.servicebus` logger to collect traces from the library.
- Enable `uamqp` logger to collect traces from the underlying uAMQP library.
- Enable AMQP frame level trace by setting `logging_enable=True` when creating the client.

## Next steps

### More sample code

Please find further examples in the [samples](./samples) directory demonstrating common Service Bus scenarios such as sending, receiving, and message handling.

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
[service_bus_namespace]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-create-namespace-portal
[service_bus_overview]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-messaging-overview
[queue_status_codes]: https://docs.microsoft.com/rest/api/servicebus/create-queue#response-codes
[service_bus_docs]: https://docs.microsoft.com/azure/service-bus/
[queue_concept]: https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messaging-overview#queues
[topic_concept]: https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-messaging-overview#topics
[subscription_concept]: https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-queues-topics-subscriptions#topics-and-subscriptions
[azure_namespace_creation]: https://docs.microsoft.com/en-us/azure/service-bus-messaging/service-bus-create-namespace-portal
