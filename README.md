# Windows Azure SDK for Python

This project provides a set of Python packages that make it easy to access
the Windows Azure storage and queue services. For documentation on how
to host Python applications on Windows Azure, please see the
[Windows Azure](http://www.windowsazure.com/en-us/develop/python/)
Python Developer Center.

# Features

* Tables
    * create and delete tables
    * create, query, insert, update, merge, and delete entities
* Blobs
    * create, list, and delete containers, work with container metadata and permissions, list blobs in container
    * create block and page blobs (from a stream, a file, or a string), work with blob blocks and pages, delete blobs
    * work with blob properties, metadata, leases, snapshot a blob
* Storage Queues
    * create, list, and delete queues, and work with queue metadata
    * create, get, peek, update, delete messages
* Service Bus
    * Queues: create, list and delete queues; create, list, and delete subscriptions; send, receive, unlock and delete messages
    * Topics: create, list, and delete topics; create, list, and delete rules

# Getting Started
## Download Source Code

To get the source code of the SDK via **git** just type:

    git clone https://github.com/WindowsAzure/azure-sdk-for-python.git
    cd ./azure-sdk-for-python

## Download Package

Alternatively, to get the source code via the Python Package Index (PyPI), type

    %SystemDrive%\Python27\Scripts\pip.exe install pyazure

You can use these packages against the cloud Windows Azure Services, or against
the local Storage Emulator (with the exception of Service Bus features).

1. To use the cloud services, you need to first create an account with Windows Azure. To use the storage services, you need to set the AZURE_STORAGE_ACCOUNT and the AZURE_STORAGE_ACCESS_KEY environment variables to the storage account name and primary access key you obtain from the Azure Portal. To use Service Bus, you need to set the AZURE_SERVICEBUS_NAMESPACE and the AZURE_SERVICEBUS_ACCESS_KEY environment variables to the service bus namespace and the default key you obtain from the Azure Portal.
2. To use the Storage Emulator, make sure the latest version of the Windows Azure SDK is installed on the machine, and set the EMULATED environment variable to any value ("true", "1", etc.)

# Usage
## Table Storage

To ensure a table exists, call **create_table**:

```Python
from azure.storage import TableService
ts = TableService(account_name, account_key)
table = ts.create_table('tasktable')
```

A new entity can be added by calling **insert_entity**:

```Python
ts = TableService(account_name, account_key)
table = ts.create_table('tasktable')
table.insert_entity(
     'tasktable',
     {
        'PartitionKey' : 'tasksSeattle',
        'RowKey': '1',
        'Description': 'Take out the trash',
        'DueDate': datetime(2011, 12, 14, 12) 
    }
)
```

The method **get_entity** can then be used to fetch the entity that was just inserted:

```Python
ts = TableService(account_name, account_key)
entity = ts.get_entity('tasktable', 'tasksSeattle', '1')
```

## Blob Storage

The **create_container** method can be used to create a 
container in which to store a blob:

```Python
from azure.storage import BlobService
blob_service = BlobService()
container = blob_service.create_container('taskcontainer')
```

To upload a file (assuming it is called task1-upload.txt, it contains the exact text "hello world" (no quotation marks), and it is placed in the same folder as the script below), the method **put_blob** can be used:

```Python
from azure.storage import BlobService
blob_service = BlobService(account_name, account_key)
blob_service.put_blob('taskcontainer', 'task1', 
blobService = azure.createBlobService()
blobService.put_blob('taskcontainer', 'task1', file('task1-upload.txt').read())

```

To download the blob and write it to the file system, the **get_blob** method can be used:

```Python
from azure.storage import BlobService
blob_service = BlobService(account_name, account_key)
blob = blob_service.get_blob('taskcontainer', 'task1')
```

## Storage Queues

The **create_queue** method can be used to ensure a queue exists:

```Python
from azure.storage import QueueService
queue_service = QueueService(account_name, account_key)
queue = queue_service.create_queue('taskqueue')
```

The **put_message** method can then be called to insert the message into the queue:

```Python
from azure.storage import QueueService
queue_service = QueueService(account_name, account_key)
queue_service.put_message('taskqueue', 'Hello world!')
```

It is then possible to call the **get___messages** method, process the message and then call **delete_message** on the messages ID. This two-step process ensures messages don't get lost when they are removed from the queue.

```Python
from azure.storage import QueueService
queue_service = QueueService(account_name, account_key)
messages = queue_service.get_messages('taskqueue')
queue_service.delete_message('taskqueue', messages[0].message_id)
```

## ServiceBus Queues

ServiceBus Queues are an alternative to Storage Queues that might be useful in scenarios where more advanced messaging features are needed (larger message sizes, message ordering, single-operaiton destructive reads, scheduled delivery) using push-style delivery (using long polling).

The **create_queue** method can be used to ensure a queue exists:

```Python
from azure.servicebus import ServiceBusService
sbs = ServiceBusService(service_namespace, account_key)
queue = sbs.create_queue('taskqueue');
```

The **send__queue__message** method can then be called to insert the message into the queue:

```Python
from azure.servicebus import ServiceBusService
sbs = ServiceBusService(service_namespace, account_key)
sbs.send_queue_message('taskqueue', 'Hello World!')
```

It is then possible to call the **read__delete___queue__message** method to dequeue the message.

```Python
from azure.servicebus import ServiceBusService
sbs = ServiceBusService(service_namespace, account_key)
msg = sbs.read_delete_queue_message('taskqueue')
```

## ServiceBus Topics

ServiceBus topics are an abstraction on top of ServiceBus Queues that make pub/sub scenarios easy to implement.

The **create_topic** method can be used to create a server-side topic:

```Python
from azure.servicebus import ServiceBusService
sbs = ServiceBusService(service_namespace, account_key)
topic = sbs.create_topic('taskdiscussion')
```

The **send__topic__message** method can be used to send a message to a topic:

```Python
from azure.servicebus import ServiceBusService
sbs = ServiceBusService(service_namespace, account_key)
sbs.send_topic_message('taskdiscussion', 'Hello world!')
```

A client can then create a subscription and start consuming messages by calling the **create__subscription** method followed by the **receive__subscription__message** method. Please note that any messages sent before the subscription is created will not be received.

```Python
from azure.servicebus import ServiceBusService
sbs = ServiceBusService(service_namespace, account_key)
sbs.create_subscription('taskdiscussion', 'client1')
msg = sbs.receive_subscription_message('taskdiscussion', 'client1')
```

** For more examples please see the [Windows Azure Python Developer Center](http://www.windowsazure.com/en-us/develop/python) **

# Need Help?

Be sure to check out the Windows Azure [Developer Forums on Stack Overflow](http://go.microsoft.com/fwlink/?LinkId=234489) if you have trouble with the provided code.

# Contribute Code or Provide Feedback

If you would like to become an active contributor to this project please follow the instructions provided in [Windows Azure Projects Contribution Guidelines](http://windowsazure.github.com/guidelines.html).

If you encounter any bugs with the library please file an issue in the [Issues](https://github.com/WindowsAzure/azure-sdk-for-python/issues) section of the project.

# Learn More
[Windows Azure Python Developer Center](http://www.windowsazure.com/en-us/develop/python/)
