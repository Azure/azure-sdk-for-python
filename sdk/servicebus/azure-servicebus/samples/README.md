---
page_type: sample
languages:
  - python
products:
  - azure
  - azure-servicebus
urlFragment: servicebus-samples
---

# Azure Service Bus client library for Python Samples

These are code samples that show common scenario operations with the Azure Service Bus client library.
Both [sync version](./sync_sampes) and [async version](./async_samples) of samples are provided, async samples require Python 3.5 or later.

- [topic_send.py](./sync_samples/topic_send.py) ([async version](./async_samples/topic_send_async.py)) - Examples to send messages on a service bus topic:
    - From a connection string
    - Enabling Logging

## Prerequisites
- Python 2.7, 3.5 or later.
- **Microsoft Azure Subscription:**  To use Azure services, including Azure Service Bus, you'll need a subscription.
If you do not have an existing Azure account, you may sign up for a free trial or use your MSDN subscriber benefits when you [create an account](https://account.windowsazure.com/Home/Index).

## Setup

1. Install the Azure Service Bus client library for Python with [pip](https://pypi.org/project/pip/):
```bash
pip install azure-servicebus
```
2. Clone or download this sample repository.
3. Open the sample folder in Visual Studio Code or your IDE of choice.

## Running the samples

1. Open a terminal window and `cd` to the directory that the samples are saved in.
2. Set the environment variables specified in the sample file you wish to run.
3. Follow the usage described in the file, e.g. `python topic_send.py`.

        Note: If the sample in question uses pytest (look for @livetest marks) please run via pytest specifying the test name, and have the servicebus credentials present in environment variables
        as described in conftest.py.

## Next steps

Check out the [API reference documentation](https://docs.microsoft.com/en-us/python/api/azure-servicebus/azure.servicebus.receive_handler.sessionreceiver?view=azure-python) to learn more about
what you can do with the Azure Service Bus client library.
