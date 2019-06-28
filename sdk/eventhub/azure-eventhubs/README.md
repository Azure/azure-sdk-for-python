# Azure Event Hubs client library for Python

Azure Event Hubs is a big data streaming platform and event ingestion service. It can receive and process millions of events per second.

Use the Event Hubs client library for Python to:

- Publish events to the Event Hubs service through a producer.
- Read events from the Event Hubs service through a consumer.

On Python 3.5.3 and above, it also includes:

- An async producer and consumer that supports async/await methods.
- An Event Processor Host module that manages the distribution of partition readers.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/eventhub/azure-eventhubs) | [Package (PyPi)](https://pypi.org/project/azure-eventhub/) | [API reference documentation](https://docs.microsoft.com/python/api/azure-eventhub) | [Product documentation](https://docs.microsoft.com/en-ca/azure/event-hubs/)

# Getting started

## Install the package

Install the Azure Event Hubs client library for Python with pip:

```
$ pip install azure-eventhub
```

### Prerequisites

- An Azure subscription.
- Python 2.7, 3.5 or later.
- An existing Event Hubs namespace and event hub. You can create these entities by following the instructions in [this article](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-create)

## Authenticate the client

Interaction with Event Hubs starts with an instance of the EventHubClient class. You need the host name, SAS/AAD credential and event hub name to instantiate the client object.

### Get credentials

You can find credential information in [Azure Portal](https://portal.azure.com/).

### Create client

There are several ways to instantiate the EventHubClient object and the following code snippets demonstrate one way:

```python
import os
from azure.eventhub import EventHubClient

connection_str = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
    os.environ['EVENT_HUB_HOSTNAME'],
    os.environ['EVENT_HUB_SAS_POLICY'],
    os.environ['EVENT_HUB_SAS_KEY'],
    os.environ['EVENT_HUB_NAME'])
client = EventHubClient.from_connection_string(connection_str)
```

# Key concepts

- **Namespace:** An Event Hubs namespace provides a unique scoping container, referenced by its fully qualified domain name, in which you create one or more event hubs or Kafka topics.

- **Event publishers**: Any entity that sends data to an event hub is an event producer, or event publisher. Event publishers can publish events using HTTPS or AMQP 1.0 or Kafka 1.0 and later. Event publishers use a Shared Access Signature (SAS) token to identify themselves to an event hub, and can have a unique identity, or use a common SAS token.

- **Event consumers**: Any entity that reads event data from an event hub is an event consumer. All Event Hubs consumers connect via the AMQP 1.0 session and events are delivered through the session as they become available. The client does not need to poll for data availability.

- **SAS tokens**: Event Hubs uses Shared Access Signatures, which are available at the namespace and event hub level. A SAS token is generated from a SAS key and is an SHA hash of a URL, encoded in a specific format. Using the name of the key (policy) and the token, Event Hubs can regenerate the hash and thus authenticate the sender.

For more information about these concepts, see [Features and terminology in Azure Event Hubs](https://docs.microsoft.com/en-ca/azure/event-hubs/event-hubs-features).

# Examples

The following sections provide several code snippets covering some of the most common Event Hubs tasks, including:

- [Send event data](#send-event-data)
- [Receive event data](#receive-event-data)
- [Async send event data](#async-send-event-data)
- [Async receive event data](#async-receive-event-data)

## Send event data

Sends an event data and blocks until acknowledgement is received or operation times out.

```python
import os
from azure.eventhub import EventHubClient, EventData

connection_str = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
    os.environ['EVENT_HUB_HOSTNAME'],
    os.environ['EVENT_HUB_SAS_POLICY'],
    os.environ['EVENT_HUB_SAS_KEY'],
    os.environ['EVENT_HUB_NAME'])
client = EventHubClient.from_connection_string(connection_str)
sender = client.create_producer(partition_id="0")

try:
 	event_list = []
 	for i in range(10):
 		event_list.append(EventData(b"A single event"))

 	with sender:
 	    sender.send(event_list)
except:
	raise
finally:
    pass
```

## Receive event data

Receive events from the EventHub.

```python
import os
import logging
from azure.eventhub import EventHubClient, EventData, EventPosition

connection_str = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
    os.environ['EVENT_HUB_HOSTNAME'],
    os.environ['EVENT_HUB_SAS_POLICY'],
    os.environ['EVENT_HUB_SAS_KEY'],
    os.environ['EVENT_HUB_NAME'])
client = EventHubClient.from_connection_string(connection_str)
receiver = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition.new_events_only())

try:
    logger = logging.getLogger("azure.eventhub")
    with receiver:
        received = receiver.receive(max_batch_size=100, timeout=5)
        for event_data in received:
            logger.info("Message received:{}".format(event_data.body_as_str()))
except:
    raise
finally:
    pass
```

## Async send event data

Sends an event data and asynchronously.

```python
import os
from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventData

connection_str = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
    os.environ['EVENT_HUB_HOSTNAME'],
    os.environ['EVENT_HUB_SAS_POLICY'],
    os.environ['EVENT_HUB_SAS_KEY'],
    os.environ['EVENT_HUB_NAME'])
client = EventHubClient.from_connection_string(connection_str)
sender = client.create_producer(partition_id="0")

try:
 	event_list = []
 	for i in range(10):
 		event_list.append(EventData(b"A single event"))

	async with sender:
		await sender.send(event_list)
except:
	raise
finally:
    pass
```

## Async receive event data

Receive events asynchronously from the EventHub.

```python
import os
import logging
from azure.eventhub.aio import EventHubClient
from azure.eventhub import EventData, EventPosition

connection_str = "Endpoint=sb://{}/;SharedAccessKeyName={};SharedAccessKey={};EntityPath={}".format(
    os.environ['EVENT_HUB_HOSTNAME'],
    os.environ['EVENT_HUB_SAS_POLICY'],
    os.environ['EVENT_HUB_SAS_KEY'],
    os.environ['EVENT_HUB_NAME'])
client = EventHubClient.from_connection_string(connection_str)
receiver = client.create_consumer(consumer_group="$default", partition_id="0", event_position=EventPosition.new_events_only())

try:
    logger = logging.getLogger("azure.eventhub")
    async with receiver:
        received = await receiver.receive(max_batch_size=100, timeout=5)
        for event_data in received:
            logger.info("Message received:{}".format(event_data.body_as_str()))
except:
    raise
finally:
    pass
```

# Troubleshooting

## General

The Event Hubs APIs generate the following exceptions.

- **AuthenticationError:** Failed to authenticate because of wrong address, SAS policy/key pair, SAS token or azure identity.
- **ConnectError:** Failed to connect to the EventHubs. The AuthenticationError is a type of ConnectError.
- **ConnectionLostError:** Lose connection after a connection has been built.
- **EventDataError:** The EventData to be sent fails data validation. 
For instance, this error is raised if you try to send an EventData that is already sent.
- **EventDataSendError:** The Eventhubs service responds with an error when an EventData is sent.
- **EventHubError:** All other Eventhubs related errors. It is also the root error class of all the above mentioned errors.

# Next steps

## Examples

- ./examples/send.py - use sender to publish events
- ./examples/recv.py - use receiver to read events
- ./examples/send_async.py - async/await support of a sender
- ./examples/recv_async.py - async/await support of a receiver
- ./examples/eph.py - event processor host

## Documentation

Reference documentation is available at https://docs.microsoft.com/python/api/azure-eventhub.

## Logging

- Enable 'azure.eventhub' logger to collect traces from the library.
- Enable 'uamqp' logger to collect traces from the underlying uAMQP library.
- Enable AMQP frame level trace by setting `network_tracing=True` when creating the client.

## Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the [Issues](https://github.com/Azure/azure-sdk-for-python/issues) section of the project.

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.