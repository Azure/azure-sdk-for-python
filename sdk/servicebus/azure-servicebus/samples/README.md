---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-service-bus
urlFragment: servicebus-samples
---

# Azure Service Bus client library for Python Samples

> **NOTE**: This document outlines the samples for the latest version of the `azure-servicebus` package
> which has different APIs than the older version (0.50). Please visit [this link](https://github.com/Azure/azure-sdk-for-python/tree/servicebus_v0.50.3/sdk/servicebus/azure-servicebus/samples) for samples of version 0.50 of this library.

These are code samples that show common scenario operations with the Azure Service Bus client library.
Both [sync version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples) and [async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples) of samples are provided, async samples require Python 3.5 or later.

- [send_queue.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/send_queue.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/send_queue_async.py)) - Examples to send messages to a service bus queue:
    - From a connection string
    - Enabling Logging
- [send_topic.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/send_topic.py) ([async version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/send_topic_async.py)) - Examples to send messages to a service bus topic:
    - From a connection string
    - Enabling Logging
- [receive_queue.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/receive_queue.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/receive_queue_async.py)) - Examples to receive messages from a service bus queue:
    - Receive messages
- [receive_subscription.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/receive_subscription.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/receive_subscription_async.py)) - Examples to receive messages from a service bus subscription:
    - Receive messages
- [receive_peek.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/receive_peek.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/receive_peek_async.py)) - Examples to peek messages from a service bus queue:
    - Peek messages
- [receive_deferred_message_queue.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/receive_deferred_message_queue.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/receive_deferred_message_queue_async.py)) - Examples to defer received messages and receive deferred messages from a service bus queue:
    - Defer received messages
    - Receive deferred messages
- [receive_deadlettered_messages.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/receive_deadlettered_messages.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/receive_deadlettered_messages_async.py)) - Examples to receive dead-lettered messages from a service bus queue:
    - Receive dead-lettered messages
- [receive_iterator_queue.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/receive_iterator_queue.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/receive_iterator_queue_async.py)) - Examples to receive messages from a service bus queue by iterating over ServiceBusReceiver:
    - Receive messages by iterating over ServiceBusReceiver
- [session_pool_receive.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/session_pool_receive.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/session_pool_receive_async.py)) - Examples to receive messages from multiple available sessions in parallel with a thread pool:
    - Receive messages from multiple available sessions in parallel with a thread pool
    - Automatically renew the lock on the session through AutoLockRenewer
- [session_send_receive.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/session_send_receive.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/session_send_receive_async.py)) - Examples to send messages to and receive messages from a session-enabled service bus queue:
    - Send messages to a session-enabled queue
    - Receive messages from session-enabled queue
- [schedule_messages_and_cancellation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/schedule_messages_and_cancellation.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/schedule_messages_and_cancellation_async.py)) - Examples to schedule messages and cancel scheduled messages on a service bus queue:
    - Schedule a single message or multiple messages to a queue
    - Cancel scheduled messages from a queue
- [schedule_topic_messages_and_cancellation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/schedule_topic_messages_and_cancellation.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/schedule_topic_messages_and_cancellation_async.py)) - Examples to schedule messages and cancel scheduled messages on a service bus topic:
    - Schedule a single message or multiple messages to a topic
    - Cancel scheduled messages from a topic
- [client_identity_authentication.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/client_identity_authentication.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/client_identity_authentication_async.py)) - Examples to authenticate the client by Azure Activate Directory:
    - Authenticate and create the client utilizing the `azure.identity` library
- [authenticate_client_connstr.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/samples/sync_samples/authenticate_client_connstr.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/samples/async_samples/authenticate_client_connstr_async.py)) - Examples to authenticate the client by Connection String:
    - Authenticate and create the client utilizing the connection string available in the Azure portal or via Azure CLI.
- [proxy.py](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/samples/sync_samples/proxy.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/samples/async_samples/proxy_async.py)) - Examples to send message behind a proxy:
    - Send message behind a proxy
- [auto_lock_renew.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/auto_lock_renew.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/auto_lock_renew_async.py)) - Examples to show usage of AutoLockRenewer:
    - Automatically renew lock on message received from non-sessionful entity
    - Automatically renew lock on the session of sessionful entity
    - Configure a callback to be triggered on auto lock renew failures.
- [mgmt_queue.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/mgmt_queue.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/mgmt_queue_async.py)) - Examples to manage queue entities under a given servicebus namespace:
    - Create a queue
    - Delete a queue
    - Update a queue
    - List queues
    - Get queue properties
    - Get queue runtime information
- [mgmt_topic](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/mgmt_topic.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/mgmt_topic_async.py)) - Examples to manage topic entities under a given servicebus namespace:
    - Create a topic
    - Delete a topic
    - Update a topic
    - List topic
    - Get topic properties
    - Get topic runtime information
- [mgmt_subscription](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/mgmt_subscription.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/mgmt_subscription_async.py)) - Examples to manage subscription entities under a given servicebus namespace:
    - Create a subscription
    - Delete a subscription
    - Update a subscription
    - List subscription
    - Get subscription properties
    - Get subscription runtime information
- [mgmt_rule](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/mgmt_rule.py) ([async_version](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/async_samples/mgmt_rule_async.py)) - Examples to manage rule entities under a given servicebus subscription:
    - Create a rule
    - Delete a rule
    - Update a rule
    - List rule
    - Get rule properties
- [failure_and_recovery.py](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus/samples/sync_samples/failure_and_recovery.py) - A demonstration of potential failure modes from an end-to-end send receive flow, as well as possible recovery patterns.

## Prerequisites
- Python 2.7, 3.5 or later.
- **Microsoft Azure Subscription:**  To use Azure services, including Azure Service Bus, you'll need a subscription.
If you do not have an existing Azure account, you may sign up for a free trial or use your MSDN subscriber benefits when you [create an account](https://account.windowsazure.com/Home/Index).

## Setup

1. Install the Azure Service Bus client library for Python with [pip](https://pypi.org/project/pip/):
```bash
pip install azure-servicebus
```
To run samples that utilize the Azure Active Directory for authentication, please install the `azure-identity` library:
```bash
pip install azure-identity
```
2. Clone or download this sample repository.
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python send_queue.py`.

## Next steps

Check out the [API reference documentation](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-servicebus/latest/index.html) to learn more about
what you can do with the Azure Service Bus client library.
