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

These are code samples that show common scenario operations with the Azure Service Bus client library.
Both [sync version](./sync_samples) and [async version](./async_samples) of samples are provided, async samples require Python 3.5 or later.

- [send_queue.py](./sync_samples/send_queue.py) ([async version](./async_samples/send_queue_async.py)) - Examples to send messages to a service bus queue:
    - From a connection string
    - Enabling Logging
- [receive_queue.py](./sync_samples/receive_queue.py) ([async_version](./async_samples/receive_queue_async.py)) - Examples to receive messages from a service bus queue:
    - Receive messages
- [receive_peek.py](./sync_samples/receive_peek.py) ([async_version](./async_samples/receive_peek_async.py)) - Examples to peek messages from a service bus queue:
    - Peek messages
- [receive_deferred_message_queue.py](./sync_samples/receive_deferred_message_queue.py) ([async_version](./async_samples/receive_deferred_message_queue_async.py)) - Examples to defer received messages and receive deferred messages from a service bus queue:
    - Defer received messages
    - Receive deferred messages
- [receive_iterator_queue.py](./sync_samples/receive_iterator_queue.py) ([async_version](./async_samples/receive_iterator_queue_async.py)) - Examples to receive messages from a service bus queue by iterating over ServiceBusReceiver:
    - Receive messages by iterating over ServiceBusReceiver
- [session_send_receive.py](./sync_samples/session_send_receive.py) ([async_version](./async_samples/session_send_receive_async.py)) - Examples to send messages to and received messages from a session-enabled service bus queue:
    - Send messages to a session-enabled queue
    - Received messages from session-enabled queue
- [client_identity_authentication.py](./sync_samples/client_identity_authentication.py) ([async_version](./async_samples/client_identity_authentication_async.py)) - Examples to authenticate the client by Azure Activate Directory
    - Authenticate and create the client utilizing the `azure.identity` library


## Prerequisites
- Python 2.7, 3.5 or later.
- **Microsoft Azure Subscription:**  To use Azure services, including Azure Service Bus, you'll need a subscription.
If you do not have an existing Azure account, you may sign up for a free trial or use your MSDN subscriber benefits when you [create an account](https://account.windowsazure.com/Home/Index).

## Setup

1. Install the Azure Service Bus client library for Python with [pip](https://pypi.org/project/pip/):
```bash
pip install --pre azure-servicebus
```
2. Clone or download this sample repository.
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python send_queue.py`.

## Next steps

Check out the [API reference documentation](https://docs.microsoft.com/en-us/python/api/azure-servicebus/azure.servicebus.receive_handler.sessionreceiver?view=azure-python) to learn more about
what you can do with the Azure Service Bus client library.
