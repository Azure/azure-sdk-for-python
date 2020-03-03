# Microsoft Azure Service Bus SDK for Python

This is the Microsoft Azure Service Bus Client Library.
This package has been tested with Python 2.7, 3.4, 3.5, 3.6 and 3.7.

Microsoft Azure Service Bus supports a set of cloud-based, message-oriented middleware technologies including reliable message queuing and durable publish/subscribe messaging.

* [SDK source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus)
* [SDK reference documentation](https://docs.microsoft.com/python/api/overview/azure/servicebus/client?view=azure-python)
* [Service Bus documentation](https://docs.microsoft.com/azure/service-bus-messaging/)


## What's new in v1.0.0b1?

As of version v1.0.0b1 a new AMQP-based API is available for sending and receiving messages. This update involves **breaking changes**.
Please read [Migration from 0.50.2 to 1.0.0b1](#migration-from-0502-to-100b1) to determine if upgrading is
right for you at this time.

The new API offers a simplified interface aligned with the current generation of ServiceBus SDKs across our language offerings,
with expanded feature support going forward.  This initial preview focuses on core queue sending and receiving functionality,
and will set the skeleton for the full feature set to be rolled out in concurrent previews.

For documentation on the legacy HTTP-based operations please see [Using HTTP-based operations of the legacy API](https://docs.microsoft.com/python/api/overview/azure/servicebus?view=azure-python#using-http-based-operations-of-the-legacy-api).


## Prerequisites

* Azure subscription - [Create a free account](https://azure.microsoft.com/free/)
* Azure Service Bus [namespace and management credentials](https://docs.microsoft.com/azure/service-bus-messaging/service-bus-create-namespace-portal)


## Installation

```shell
pip install azure-servicebus --pre
```

## Migration from 0.50.2 to 1.0.0b1

Major breaking changes were introduced in version 1.0.0b1.
If the existing stable API is needed (v0.50.2) as opposed to this preview release, it can be installed or reverted to via 
```shell
pip install azure-servicebus --upgrade
```
The original HTTP-based API is still available in v1.0.0b1 - however it now exists under a new namesapce: `azure.servicebus.control_client`.

### Should I upgrade?

The primary motivation for upgrading at this point is to gain early exposure to the service bus 1.0 release to provide feedback or improvements.

While we expect the SDK surface area to not change significantly as we progress through preview releases, this cannot be guaranteed.

The new package (v1.0.0b1) offers no improvements in HTTP-based operations over v0.50.2. The HTTP-based API is identical except that it now
exists under a new namespace. For this reason if you only wish to use HTTP-based operations (`create_queue`, `delete_queue` etc) - there will be
no additional benefit in upgrading at this time.


### How do I migrate my code to the new version?

This initial preview release focuses on Queue support.  Full featureset will be rolled out in future previews.
Code written against v0.50.2 can be ported to version 1.0.0b1 as follows:

#### v0.50.2 Sender
```python
from azure.servicebus import ServiceBusClient

CONNECTION_STR = '' # connection string from Azure portal.
QUEUE_NAME = '' # queue name, also from the Azure portal, within the service bus corrosponding to the connection string above.

client = ServiceBusClient.from_connection_string(CONNECTION_STR)
queue_client = client.get_queue(QUEUE_NAME)
message1 = Message("Hello World!")
queue_client.send(message1)
```

#### V1.0.0b1 Sender
```python
from azure.servicebus import ServiceBusSenderClient, Message

CONNECTION_STR = '' # connection string from Azure portal.
QUEUE_NAME = '' # queue name, also from the Azure portal, within the service bus corrosponding to the connection string above.

sender_client = ServiceBusSenderClient.from_connection_string(
    conn_str=CONNECTION_STR,
    queue_name=QUEUE_NAME
)

message = Message("Single message")

with sender_client:
    sender_client.send(message)
```

#### v0.50.2 Receiver
```python
from azure.servicebus import ServiceBusClient

CONNECTION_STR = '' # connection string from Azure portal.
QUEUE_NAME = '' # queue name, also from the Azure portal, within the service bus corrosponding to the connection string above.

client = ServiceBusClient.from_connection_string(CONNECTION_STR)
queue_client = client.get_queue(QUEUE_NAME)
with queue_client.get_receiver(idle_timeout=3) as queue_receiver:
    for message in queue_receiver:
        print(str(message))
        message.complete()
```

#### V1.0.0b1 Receiver
```python
from azure.servicebus import ServiceBusSenderClient, Message

CONNECTION_STR = '' # connection string from Azure portal.
QUEUE_NAME = '' # queue name, also from the Azure portal, within the service bus corrosponding to the connection string above.

receiver_client = ServiceBusReceiverClient.from_connection_string(
    conn_str=CONNECTION_STR,
    queue_name=QUEUE_NAME
)

with receiver_client:
    for msg in receiver_client.receive():
        print(str(msg))
        msg.complete()
```

For code utilizing the `azure.servicebus.control_client` namespace in v0.50.2, no changes will be necessary.

# Usage

For reference documentation and code snippets see [Service Bus](https://docs.microsoft.com/python/api/overview/azure/servicebus)
on docs.microsoft.com.


# Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the
[Issues](https://github.com/Azure/azure-sdk-for-python/issues)
section of the project.


![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fazure-servicebus%2FREADME.png)
