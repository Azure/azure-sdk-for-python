# Azure Service Bus client library for Python

Azure Service Bus is a high performance cloud-managed messaging service for providing real-time and fault-tolerant communication between distributed senders and receivers.

Service Bus provides multiple mechanisms for asynchronous highly reliable communication, such as structured first-in-first-out messaging, 
publish/subscribe capabilities, and the ability to easily scale as your needs grow.

Use the Service Bus client library for Python to communicate between applications and services and implement asynchronous messaging patterns.

* Create Service Bus namespaces, queues, topics, and subscriptions, and modify their settings.
* Send and receive messages within your Service Bus channels.
* Utilize message locks, sessions, and dead letter functionality to implement complex messaging patterns.

[Source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/) | [Package (PyPi)][pypi] | [API reference documentation][api_docs] | [Product documentation][product_docs] | [Samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples) | [Changelog](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/CHANGELOG.md)

**NOTE**: If you are using version 0.50 or lower and want to migrate to the latest version
of this package please look at our [migration guide to move from Service Bus V0.50 to Service Bus V7][migration_guide].

## Getting started

### Install the package

Install the Azure Service Bus client library for Python with [pip][pip]:

```Bash
pip install azure-servicebus
```

### Prerequisites: 
To use this package, you must have:
* Azure subscription - [Create a free account][azure_sub]
* Azure Service Bus - [Namespace and management credentials][service_bus_namespace]
* Python 2.7, 3.5 or later - [Install Python][python]


If you need an Azure service bus namespace, you can create it via the [Azure Portal][azure_namespace_creation].
If you do not wish to use the graphical portal UI, you can use the Azure CLI via [Cloud Shell][cloud_shell_bash], or Azure CLI run locally, to create one with this Azure CLI command:

```Bash
az servicebus namespace create --resource-group <resource-group-name> --name <servicebus-namespace-name> --location <servicebus-namespace-location>
```

### Authenticate the client

Interaction with Service Bus starts with an instance of the `ServiceBusClient` class. You either need a **connection string with SAS key**, or a **namespace** and one of its **account keys** to instantiate the client object.
Please find the samples linked below for demonstration as to how to authenticate via either approach.

#### [Create client from connection string][sample_authenticate_client_connstr]

- To obtain the required credentials, one can use the [Azure CLI][azure_cli] snippet (Formatted for Bash Shell) at the top of the linked sample to populate an environment variable with the service bus connection string (you can also find these values in the [Azure Portal][azure_portal] by following the step-by-step guide to [Get a service bus connection string][get_servicebus_conn_str]).

#### [Create client using the azure-identity library][sample_authenticate_client_aad]:

- This constructor takes the fully qualified namespace of your Service Bus instance and a credential that implements the
[TokenCredential][token_credential_interface]
protocol. There are implementations of the `TokenCredential` protocol available in the
[azure-identity package][pypi_azure_identity]. The fully qualified namespace is of the format `<yournamespace.servicebus.windows.net>`.
- To use the credential types provided by `azure-identity`, please install the package:
```pip install azure-identity```
- Additionally, to use the async API supported on Python 3.5+, you must first install an async transport, such as [`aiohttp`](https://pypi.org/project/aiohttp/):
```pip install aiohttp```
- When using Azure Active Directory, your principal must be assigned a role which allows access to Service Bus, such as the
Azure Service Bus Data Owner role. For more information about using Azure Active Directory authorization with Service Bus,
please refer to [the associated documentation][servicebus_aad_authentication].

>**Note:** client can be initialized without a context manager, but must be manually closed via client.close() to not leak resources.

## Key concepts

Once you've initialized a `ServiceBusClient`, you can interact with the primary resource types within a Service Bus Namespace, of which multiple can exist and on which actual message transmission takes place, the namespace often serving as an application container:

* [Queue][queue_concept]: Allows for Sending and Receiving of message.  Often used for point-to-point communication.

* [Topic][topic_concept]: As opposed to Queues, Topics are better suited to publish/subscribe scenarios.  A topic can be sent to, but requires a subscription, of which there can be multiple in parallel, to consume from.

* [Subscription][subscription_concept]: The mechanism to consume from a Topic.  Each subscription is independent, and receives a copy of each message sent to the topic.  Rules and Filters can be used to tailor which messages are received by a specific subscription.

For more information about these resources, see [What is Azure Service Bus?][service_bus_overview].

To interact with these resources, one should be familiar with the following SDK concepts:

* [ServiceBusClient][client_reference]: This is the object a user should first initialize to connect to a Service Bus Namespace.  To interact with a queue, topic, or subscription, one would spawn a sender or receiver off of this client.

* [ServiceBusSender][sender_reference]: To send messages to a Queue or Topic, one would use the corresponding `get_queue_sender` or `get_topic_sender` method off of a `ServiceBusClient` instance as seen [here](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/send_queue.py).

* [ServiceBusReceiver][receiver_reference]: To receive messages from a Queue or Subscription, one would use the corresponding `get_queue_receiver` or `get_subscription_receiver` method off of a `ServiceBusClient` instance as seen [here](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/receive_queue.py).

* [ServiceBusMessage][message_reference]: When sending, this is the type you will construct to contain your payload.  When receiving, this is where you will access the payload.

## Examples

The following sections provide several code snippets covering some of the most common Service Bus tasks, including:

* [Send messages to a queue](#send-messages-to-a-queue "Send messages to a queue")
* [Receive messages from a queue](#receive-messages-from-a-queue "Receive messages from a queue")
* [Send and receive a message from a session enabled queue](#send-and-receive-a-message-from-a-session-enabled-queue "Send and receive a message from a session enabled queue")
* [Working with topics and subscriptions](#working-with-topics-and-subscriptions "Working with topics and subscriptions")
* [Settle a message after receipt](#settle-a-message-after-receipt "Settle a message after receipt")
* [Automatically renew Message or Session locks](#automatically-renew-message-or-session-locks "Automatically renew Message or Session locks")

To perform management tasks such as creating and deleting queues/topics/subscriptions, please utilize the azure-mgmt-servicebus library, available [here][servicebus_management_repository].

Please find further examples in the [samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples) directory demonstrating common Service Bus scenarios such as sending, receiving, session management and message handling.

### Send messages to a queue 
> **NOTE:** see reference documentation [here][send_reference].

This example sends single message and array of messages to a queue that is assumed to already exist, created via the Azure portal or az commands.

```Python
from azure.servicebus import ServiceBusClient, ServiceBusMessage

import os
connstr = os.environ['SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_queue_sender(queue_name) as sender:
        # Sending a single message
        single_message = ServiceBusMessage("Single message")
        sender.send_messages(single_message)

        # Sending a list of messages
        messages = [ServiceBusMessage("First message"), ServiceBusMessage("Second message")]
        sender.send_messages(messages)
```

> **NOTE:** A message may be scheduled for delayed delivery using the `ServiceBusSender.schedule_messages()` method, or by specifying `ServiceBusMessage.scheduled_enqueue_time_utc` before calling `ServiceBusSender.send_messages()`

> For more detail on scheduling and schedule cancellation please see a sample [here](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/schedule_messages_and_cancellation.py).

### Receive messages from a queue

To receive from a queue, you can either perform an ad-hoc receive via `receiver.receive_messages()` or receive persistently through the receiver itself.

#### [Receive messages from a queue through iterating over ServiceBusReceiver][streaming_receive_reference]

```Python
from azure.servicebus import ServiceBusClient

import os
connstr = os.environ['SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

with ServiceBusClient.from_connection_string(connstr) as client:
    # max_wait_time specifies how long the receiver should wait with no incoming messages before stopping receipt.  
    # Default is None; to receive forever.
    with client.get_queue_receiver(queue_name, max_wait_time=30) as receiver:
        for msg in receiver:  # ServiceBusReceiver instance is a generator.
            print(str(msg))
            # If it is desired to halt receiving early, one can break out of the loop here safely.
```

> **NOTE:** Any message received with `receive_mode=PEEK_LOCK` (this is the default, with the alternative RECEIVE_AND_DELETE removing the message from the queue immediately on receipt)
> has a lock that must be renewed via `receiver.renew_message_lock` before it expires if processing would take longer than the lock duration.
> See [AutoLockRenewer](#automatically-renew-message-or-session-locks "Automatically renew Message or Session locks") for a helper to perform this in the background automatically.
> Lock duration is set in Azure on the queue or topic itself.

#### [Receive messages from a queue through ServiceBusReceiver.receive_messages()][receive_reference]

> **NOTE:** `ServiceBusReceiver.receive_messages()` receives a single or constrained list of messages through an ad-hoc method call, as opposed to receiving perpetually from the generator. It always returns a list.

```Python
from azure.servicebus import ServiceBusClient

import os
connstr = os.environ['SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_queue_receiver(queue_name) as receiver:
        received_message_array = receiver.receive_messages(max_wait_time=10)  # try to receive a single message within 10 seconds
        if received_message_array:
            print(str(received_message_array[0]))

    with client.get_queue_receiver(queue_name) as receiver:
        received_message_array = receiver.receive_messages(max_message_count=5, max_wait_time=10)  # try to receive maximum 5 messages in a batch within 10 seconds
        for message in received_message_array:
            print(str(message))
```

In this example, max_message_count declares the maximum number of messages to attempt receiving before hitting a max_wait_time as specified in seconds.

> **NOTE:** It should also be noted that `ServiceBusReceiver.peek_messages()` is subtly different than receiving, as it does not lock the messages being peeked, and thus they cannot be settled.


### Send and receive a message from a session enabled queue
> **NOTE:** see reference documentation for session [send][session_send_reference] and [receive][session_receive_reference].

Sessions provide first-in-first-out and single-receiver semantics on top of a queue or subscription.  While the actual receive syntax is the same, initialization differs slightly.

```Python
from azure.servicebus import ServiceBusClient, ServiceBusMessage

import os
connstr = os.environ['SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']
session_id = os.environ['SERVICE_BUS_SESSION_ID']

with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_queue_sender(queue_name) as sender:
        sender.send_messages(ServiceBusMessage("Session Enabled Message", session_id=session_id))

    # If session_id is null here, will receive from the first available session.
    with client.get_queue_receiver(queue_name, session_id=session_id) as receiver:
        for msg in receiver:
            print(str(msg))
```

> **NOTE**: Messages received from a session do not need their locks renewed like a non-session receiver; instead the lock management occurs at the
> session level with a session lock that may be renewed with `receiver.session.renew_lock()`


### Working with [topics][topic_reference] and [subscriptions][subscription_reference]
> **NOTE:** see reference documentation for [topics][topic_reference] and [subscriptions][subscription_reference].

Topics and subscriptions give an alternative to queues for sending and receiving messages.  See documents [here][topic_concept] for more overarching detail,
and of how these differ from queues.

```Python
from azure.servicebus import ServiceBusClient, ServiceBusMessage

import os
connstr = os.environ['SERVICE_BUS_CONNECTION_STR']
topic_name = os.environ['SERVICE_BUS_TOPIC_NAME']
subscription_name = os.environ['SERVICE_BUS_SUBSCRIPTION_NAME']

with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_topic_sender(topic_name) as sender:
        sender.send_messages(ServiceBusMessage("Data"))

    # If session_id is null here, will receive from the first available session.
    with client.get_subscription_receiver(topic_name, subscription_name) as receiver:
        for msg in receiver:
            print(str(msg))
```

### Settle a message after receipt

When receiving from a queue, you have multiple actions you can take on the messages you receive.

> **NOTE**: You can only settle `ServiceBusReceivedMessage` objects which are received in `ServiceBusReceiveMode.PEEK_LOCK` mode (this is the default).
> `ServiceBusReceiveMode.RECEIVE_AND_DELETE` mode removes the message from the queue on receipt.  `ServiceBusReceivedMessage` messages
> returned from `peek_messages()` cannot be settled, as the message lock is not taken like it is in the aforementioned receive methods.

If the message has a lock as mentioned above, settlement will fail if the message lock has expired.  
If processing would take longer than the lock duration, it must be maintained via `receiver.renew_message_lock` before it expires.
Lock duration is set in Azure on the queue or topic itself.
See [AutoLockRenewer](#automatically-renew-message-or-session-locks "Automatically renew Message or Session locks") for a helper to perform this in the background automatically.

#### [Complete][complete_reference]

Declares the message processing to be successfully completed, removing the message from the queue.

```Python
from azure.servicebus import ServiceBusClient

import os
connstr = os.environ['SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_queue_receiver(queue_name) as receiver:
        for msg in receiver:
            print(str(msg))
            receiver.complete_message(msg)
```

#### [Abandon][abandon_reference]

Abandon processing of the message for the time being, returning the message immediately back to the queue to be picked up by another (or the same) receiver.

```Python
from azure.servicebus import ServiceBusClient

import os
connstr = os.environ['SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_queue_receiver(queue_name) as receiver:
        for msg in receiver:
            print(str(msg))
            receiver.abandon_message(msg)
```

#### [DeadLetter][deadletter_reference]

Transfer the message from the primary queue into a special "dead-letter sub-queue" where it can be accessed using the `ServiceBusClient.get_<queue|subscription>_receiver` function with parameter `sub_queue=ServiceBusSubQueue.DEAD_LETTER` and consumed from like any other receiver. (see sample [here](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/receive_deadlettered_messages.py))

```Python
from azure.servicebus import ServiceBusClient

import os
connstr = os.environ['SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_queue_receiver(queue_name) as receiver:
        for msg in receiver:
            print(str(msg))
            receiver.dead_letter_message(msg)
```

#### [Defer][defer_reference]

Defer is subtly different from the prior settlement methods.  It prevents the message from being directly received from the queue
by setting it aside such that it must be received by sequence number in a call to `ServiceBusReceiver.receive_deferred_messages` (see sample [here](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/receive_deferred_message_queue.py))

```Python
from azure.servicebus import ServiceBusClient

import os
connstr = os.environ['SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_queue_receiver(queue_name) as receiver:
        for msg in receiver:
            print(str(msg))
            receiver.defer_message(msg)
```

### Automatically renew Message or Session locks
> **NOTE:** see reference documentation for [auto-lock-renewal][autolockrenew_reference].

`AutoLockRenewer` is a simple method for ensuring your message or session remains locked even over long periods of time, if calling `receiver.renew_message_lock`/`receiver.session.renew_lock` is impractical or undesired.
Internally, it is not much more than shorthand for creating a concurrent watchdog to do lock renewal if the object is nearing expiry.
It should be used as follows:

* Message lock automatic renewing

```python
from azure.servicebus import ServiceBusClient, AutoLockRenewer

import os
connstr = os.environ['SERVICE_BUS_CONNECTION_STR']
queue_name = os.environ['SERVICE_BUS_QUEUE_NAME']

# Can also be called via "with AutoLockRenewer() as renewer" to automate closing.
renewer = AutoLockRenewer()
with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_queue_receiver(queue_name) as receiver:
        for msg in receiver.receive_messages():
            renewer.register(receiver, msg, max_lock_renewal_duration=60)
            # Do your application logic here
            receiver.complete_message(msg)
renewer.close()
```

* Session lock automatic renewing

```python
from azure.servicebus import ServiceBusClient, AutoLockRenewer

import os
connstr = os.environ['SERVICE_BUS_CONNECTION_STR']
session_queue_name = os.environ['SERVICE_BUS_SESSION_QUEUE_NAME']
session_id = os.environ['SERVICE_BUS_SESSION_ID']

# Can also be called via "with AutoLockRenewer() as renewer" to automate closing.
renewer = AutoLockRenewer()
with ServiceBusClient.from_connection_string(connstr) as client:
    with client.get_queue_receiver(session_queue_name, session_id=session_id) as receiver:
        renewer.register(receiver, receiver.session, max_lock_renewal_duration=300) # Duration for how long to maintain the lock for, in seconds.

        for msg in receiver.receive_messages():
            # Do your application logic here
            receiver.complete_message(msg)
renewer.close()
```

If for any reason auto-renewal has been interrupted or failed, this can be observed via the `auto_renew_error` property on the object being renewed, or by having passed a callback to the `on_lock_renew_failure` parameter on renewer initialization.
It would also manifest when trying to take action (such as completing a message) on the specified object.

## Troubleshooting

### Logging

- Enable `azure.servicebus` logger to collect traces from the library.
- Enable `uamqp` logger to collect traces from the underlying uAMQP library.
- Enable AMQP frame level trace by setting `logging_enable=True` when creating the client.

### Timeouts

There are various timeouts a user should be aware of within the library.
- 10 minute service side link closure:  A link, once opened, will be closed after 10 minutes idle to protect the service against resource leakage.  This should largely
be transparent to a user, but if you notice a reconnect occurring after such a duration, this is why.  Performing any operations, including management operations, on the
link will extend this timeout.
- max_wait_time: Provided on creation of a receiver or when calling `receive_messages()`, the time after which receiving messages will halt after no traffic.  This applies both to the imperative `receive_messages()` function as well as the length
a generator-style receive will run for before exiting if there are no messages.  Passing None (default) will wait forever, up until the 10 minute threshold if no other action is taken.

> **NOTE:** If processing of a message or session is sufficiently long as to cause timeouts, as an alternative to calling `receiver.renew_message_lock`/`receiver.session.renew_lock` manually, one can
> leverage the `AutoLockRenewer` functionality detailed [above](#automatically-renew-message-or-session-locks "Automatically renew Message or Session locks").

### Common Exceptions

The Service Bus APIs generate the following exceptions in azure.servicebus.exceptions:

- **ServiceBusConnectionError:** An error occurred in the connection to the service.
This may have been caused by a transient network issue or service problem. It is recommended to retry.
- **ServiceBusAuthorizationError:** An error occurred when authorizing the connection to the service.
This may have been caused by the credentials not having the right permission to perform the operation.
It is recommended to check the permission of the credentials.
- **ServiceBusAuthenticationError:** An error occurred when authenticate the connection to the service.
This may have been caused by the credentials being incorrect. It is recommended to check the credentials.
- **OperationTimeoutError:** This indicates that the service did not respond to an operation within the expected amount of time.
This may have been caused by a transient network issue or service problem. The service may or may not have successfully completed the request; the status is not known.
It is recommended to attempt to verify the current state and retry if necessary.
- **MessageSizeExceededError:** This indicate that the message content is larger than the service bus frame size.
This could happen when too many service bus messages are sent in a batch or the content passed into
the body of a `Message` is too large. It is recommended to reduce the count of messages being sent in a batch or the size of content being passed into a single `ServiceBusMessage`. 
- **MessageAlreadySettled:** This indicates failure to settle the message.
This could happen when trying to settle an already-settled message.
- **MessageLockLostError:** The lock on the message has expired and it has been released back to the queue.
It will need to be received again in order to settle it.
You should be aware of the lock duration of a message and keep renewing the lock before expiration in case of long processing time.
`AutoLockRenewer` could help on keeping the lock of the message automatically renewed.
- **SessionLockLostError:** The lock on the session has expired.
All unsettled messages that have been received can no longer be settled.
It is recommended to reconnect to the session if receive messages again if necessary.
You should be aware of the lock duration of a session and keep renewing the lock before expiration in case of long processing time.
`AutoLockRenewer` could help on keeping the lock of the session automatically renewed.
- **MessageNotFoundError:** Attempt to receive a message with a particular sequence number. This message isn't found.
Make sure the message hasn't been received already. Check the deadletter queue to see if the message has been deadlettered.
- **MessagingEntityNotFoundError:** Entity associated with the operation doesn't exist or it has been deleted.
Please make sure the entity exists.
- **MessagingEntityDisabledError:** Request for a runtime operation on a disabled entity. Please Activate the entity.
- **ServiceBusQuotaExceededError:** The messaging entity has reached its maximum allowable size, or the maximum number of connections to a namespace has been exceeded.
Create space in the entity by receiving messages from the entity or its subqueues.
- **ServiceBusServerBusyError:** Service isn't able to process the request at this time. Client can wait for a period of time, then retry the operation.
- **ServiceBusCommunicationError:** Client isn't able to establish a connection to Service Bus.
Make sure the supplied host name is correct and the host is reachable.
If your code runs in an environment with a firewall/proxy, ensure that the traffic to the Service Bus domain/IP address and ports isn't blocked.
- **SessionCannotBeLockedError:** Attempt to connect to a session with a specific session ID, but the session is currently locked by another client.
Make sure the session is unlocked by other clients.
- **AutoLockRenewFailed:** An attempt to renew a lock on a message or session in the background has failed.
This could happen when the receiver used by `AutoLockRenerer` is closed or the lock of the renewable has expired.
It is recommended to re-register the renewable message or session by receiving the message or connect to the sessionful entity again.
- **AutoLockRenewTimeout:** The time allocated to renew the message or session lock has elapsed. You could re-register the object that wants be auto lock renewed or extend the timeout in advance.
- **ServiceBusError:** All other Service Bus related errors. It is the root error class of all the errors described above.

Please view the [exceptions reference docs][exception_reference] for detailed descriptions of our common Exception types.

## Next steps

### More sample code

Please find further examples in the [samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples) directory demonstrating common Service Bus scenarios such as sending, receiving, session management and message handling.

### Additional documentation

For more extensive documentation on the Service Bus service, see the [Service Bus documentation][service_bus_docs] on docs.microsoft.com.

### Management capabilities and documentation

For users seeking to perform management operations against ServiceBus (Creating a queue/topic/etc, altering filter rules, enumerating entities)
please see the [azure-mgmt-servicebus documentation][service_bus_mgmt_docs] for API documentation.  Terse usage examples can be found
[here](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-mgmt-servicebus/tests) as well.

### Building uAMQP wheel from source

`azure-servicebus` depends on the [uAMQP](https://pypi.org/project/uamqp/) for the AMQP protocol implementation.
uAMQP wheels are provided for most major operating systems and will be installed automatically when installing `azure-servicebus`.

If you're running on a platform for which uAMQP wheels are not provided, please follow
 the [uAMQP Installation](https://github.com/Azure/azure-uamqp-python#installation) guidance to install from source.

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
[api_docs]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/index.html
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
[service_bus_mgmt_docs]: https://docs.microsoft.com/python/api/overview/azure/servicebus/management?view=azure-python
[queue_concept]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-messaging-overview#queues
[topic_concept]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-messaging-overview#topics
[subscription_concept]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-queues-topics-subscriptions#topics-and-subscriptions
[azure_namespace_creation]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-create-namespace-portal
[servicebus_management_repository]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-mgmt-servicebus
[get_servicebus_conn_str]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-create-namespace-portal#get-the-connection-string
[servicebus_aad_authentication]: https://docs.microsoft.com/azure/service-bus-messaging/service-bus-authentication-and-authorization
[token_credential_interface]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core/azure/core/credentials.py
[pypi_azure_identity]: https://pypi.org/project/azure-identity/
[message_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html#azure.servicebus.ServiceBusMessage
[receiver_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html#azure.servicebus.ServiceBusReceiver
[sender_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html#azure.servicebus.ServiceBusSender
[client_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html#azure.servicebus.ServiceBusClient
[send_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html?highlight=send_messages#azure.servicebus.ServiceBusSender.send_messages
[receive_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html?highlight=receive_messages#azure.servicebus.ServiceBusReceiver.receive_messages
[streaming_receive_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html?highlight=next#azure.servicebus.ServiceBusReceiver.next
[session_receive_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html?highlight=session_id#azure.servicebus.ServiceBusSessionReceiver.receive_messages
[session_send_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html?highlight=session_id#azure.servicebus.ServiceBusMessage.session_id
[complete_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html?highlight=complete_message#azure.servicebus.ServiceBusReceiver.complete_message
[abandon_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html?highlight=abandon_message#azure.servicebus.ServiceBusReceiver.abandon_message
[defer_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html?highlight=defer_message#azure.servicebus.ServiceBusReceiver.defer_message
[deadletter_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html?highlight=dead_letter_message#azure.servicebus.ServiceBusReceiver.dead_letter_message
[autolockrenew_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html#azure.servicebus.AutoLockRenewer
[exception_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html#module-azure.servicebus.exceptions
[subscription_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.aio.html?highlight=subscription#azure.servicebus.aio.ServiceBusClient.get_subscription_receiver
[topic_reference]: https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/azure.servicebus.html?highlight=topic#azure.servicebus.ServiceBusClient.get_topic_sender
[sample_authenticate_client_connstr]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/samples/sync_samples/authenticate_client_connstr.py
[sample_authenticate_client_aad]: https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/samples/sync_samples/client_identity_authentication.py
[migration_guide]: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/migration_guide.md
