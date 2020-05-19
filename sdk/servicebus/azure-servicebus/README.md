# Microsoft Azure Service Bus SDK for Python

> **NOTE**: Starting with the GA release of version 7.0.0 (currently in preview), this package will be deprecated.
> Users can get a head-start on transitioning by installing or upgrading via `pip install azure-servicebus --pre` and reviewing our [migration guide](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/servicebus/azure-servicebus/migration_guide.md)

This is the Microsoft Azure Service Bus Client Library.
This package has been tested with Python 2.7, 3.4, 3.5, 3.6 and 3.7.

Microsoft Azure Service Bus supports a set of cloud-based, message-oriented middleware technologies including reliable message queuing and durable publish/subscribe messaging.

* [SDK source code](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/servicebus/azure-servicebus)
* [SDK reference documentation](https://docs.microsoft.com/python/api/overview/azure/servicebus/client?view=azure-python)
* [Service Bus documentation](https://docs.microsoft.com/azure/service-bus-messaging/)


## What's new in v0.50.2?

As of version 0.50.2 a new AMQP-based API is available for sending and receiving messages. This update involves **breaking changes**.
Please read [Migration from 0.21.1 to 0.50.2](#migration-from-0211-to-0502) to determine if upgrading is
right for you at this time.

The new AMQP-based API offers improved message passing reliability, performance and expanded feature support going forward.
The new API also offers support for asynchronous operations (based on asyncio) for sending, receiving and handling messages.

For documentation on the legacy HTTP-based operations please see [Using HTTP-based operations of the legacy API](https://docs.microsoft.com/python/api/overview/azure/servicebus?view=azure-python#using-http-based-operations-of-the-legacy-api).


## Prerequisites

* Azure subscription - [Create a free account](https://azure.microsoft.com/free/)
* Azure Service Bus [namespace and management credentials](https://docs.microsoft.com/azure/service-bus-messaging/service-bus-create-namespace-portal)


## Installation

```shell
pip install azure-servicebus
```

## Migration from 0.21.1 to 0.50.2

Major breaking changes were introduced in version 0.50.2.
The original HTTP-based API is still available in v0.50.2 - however it now exists under a new namesapce: `azure.servicebus.control_client`.

### Should I upgrade?

The new package (v0.50.2) offers no improvements in HTTP-based operations over v0.21.1. The HTTP-based API is identical except that it now
exists under a new namespace. For this reason if you only wish to use HTTP-based operations (`create_queue`, `delete_queue` etc) - there will be
no additional benefit in upgrading at this time.


### How do I migrate my code to the new version?

Code written against v0.21.0 can be ported to version 0.50.2 by simply changing the import namespace:

```python
# from azure.servicebus import ServiceBusService  <- This will now raise an ImportError
from azure.servicebus.control_client import ServiceBusService

key_name = 'RootManageSharedAccessKey' # SharedAccessKeyName from Azure portal
key_value = ''  # SharedAccessKey from Azure portal
sbs = ServiceBusService(service_namespace,
                        shared_access_key_name=key_name,
                        shared_access_key_value=key_value)
```


# Usage

For reference documentation and code snippets see [Service Bus](https://docs.microsoft.com/python/api/overview/azure/servicebus)
on docs.microsoft.com.


# Provide Feedback

If you encounter any bugs or have suggestions, please file an issue in the
[Issues](https://github.com/Azure/azure-sdk-for-python/issues)
section of the project.


![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fazure-servicebus%2FREADME.png)
