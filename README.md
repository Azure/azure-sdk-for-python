# Microsoft Azure SDK for Python

This project provides a set of Python packages that make it easy to access
the Microsoft Azure storage and queue services. For documentation on how
to host Python applications on Microsoft Azure, please see the
[Microsoft Azure](http://www.windowsazure.com/en-us/develop/python/)
Python Developer Center.

The SDK supports Python 2.7, 3.3, 3.4.

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
* Service Management
    * storage accounts: create, update, delete, list, regenerate keys
    * affinity groups: create, update, delete, list, get properties
    * locations: list
    * hosted services: create, update, delete, list, get properties
    * deployment: create, get, delete, swap, change configuration, update status, upgrade, rollback
    * role instance: reboot, reimage
    * discover addresses and ports for the endpoints of other role instances in your service
    * get configuration settings and access local resources
    * get role instance information for current role and other role instances
    * query and set the status of the current role

# Getting Started
## Download Source Code

To get the source code of the SDK via **git** just type:

    git clone https://github.com/Azure/azure-sdk-for-python.git
    cd ./azure-sdk-for-python

## Download Package

Alternatively, to get the source code via the Python Package Index (PyPI), type

    %SystemDrive%\Python27\Scripts\pip.exe install azure

You can use these packages against the cloud Microsoft Azure Services, or against
the local Storage Emulator (with the exception of Service Bus features).

1. To use the cloud services, you need to first create an account with Microsoft Azure. To use the storage services, you need to set the AZURE_STORAGE_ACCOUNT and the AZURE_STORAGE_ACCESS_KEY environment variables to the storage account name and primary access key you obtain from the Azure Portal. To use Service Bus, you need to set the AZURE_SERVICEBUS_NAMESPACE and the AZURE_SERVICEBUS_ACCESS_KEY environment variables to the service bus namespace and the default key you obtain from the Azure Portal.
2. To use the Storage Emulator, make sure the latest version of the Microsoft Azure SDK is installed on the machine, and set the EMULATED environment variable to any value ("true", "1", etc.)

# Usage
## Table Storage

To ensure a table exists, call **create\_table**:

```Python
from azure.storage import TableService
ts = TableService(account_name, account_key)
ts.create_table('tasktable')
```

A new entity can be added by calling **insert\_entity**:

```Python
from datetime import datetime
ts = TableService(account_name, account_key)
ts.create_table('tasktable')
ts.insert_entity(
     'tasktable',
     {
        'PartitionKey' : 'tasksSeattle',
        'RowKey': '1',
        'Description': 'Take out the trash',
        'DueDate': datetime(2011, 12, 14, 12) 
    }
)
```

The method **get\_entity** can then be used to fetch the entity that was just inserted:

```Python
ts = TableService(account_name, account_key)
entity = ts.get_entity('tasktable', 'tasksSeattle', '1')
```

## Blob Storage

The **create\_container** method can be used to create a 
container in which to store a blob:

```Python
from azure.storage import BlobService
blob_service = BlobService(account_name, account_key)
blob_service.create_container('images')
```

To upload a file 'uploads/image.png' from disk to a blob named 'image.png', the method **put\_block\_blob\_from\_path** can be used:

```Python
from azure.storage import BlobService
blob_service = BlobService(account_name, account_key)
blob_service.put_block_blob_from_path('images', 'image.png', 'uploads/image.png')
```

To upload an already opened file to a blob named 'image.png', the method **put\_block\_blob\_from\_file** can be used instead:

```Python
with open('uploads/image.png') as file:
  blob_service.put_block_blob_from_file('images', 'image.png', file)
```

To upload unicode text, use **put\_block\_blob\_from\_text** which will do the conversion to bytes using the specified encoding.

To upload bytes, use **put\_block\_blob\_from\_bytes**.

To download a blob named 'image.png' to a file on disk 'downloads/image.png', where the 'downloads' folder already exists, the **get\_blob\_to\_path** method can be used:

```Python
from azure.storage import BlobService
blob_service = BlobService(account_name, account_key)
blob = blob_service.get_blob_to_path('images', 'image.png', 'downloads/image.png')
```

To download to an already opened file, use **get\_blob\_to\_file**.

To download to an array of bytes, use **get\_blob\_to\_bytes**.

To download to unicode text, use **get\_blob\_to\_text**.


## Storage Queues

The **create\_queue** method can be used to ensure a queue exists:

```Python
from azure.storage import QueueService
queue_service = QueueService(account_name, account_key)
queue_service.create_queue('taskqueue')
```

The **put\_message** method can then be called to insert the message into the queue:

```Python
from azure.storage import QueueService
queue_service = QueueService(account_name, account_key)
queue_service.put_message('taskqueue', 'Hello world!')
```

It is then possible to call the **get\_messages** method, process the message and then call **delete\_message** with the message id and receipt. This two-step process ensures messages don't get lost when they are removed from the queue.

```Python
from azure.storage import QueueService
queue_service = QueueService(account_name, account_key)
messages = queue_service.get_messages('taskqueue')
queue_service.delete_message('taskqueue', messages[0].message_id, messages[0].pop_receipt)
```

## ServiceBus Queues

ServiceBus Queues are an alternative to Storage Queues that might be useful in scenarios where more advanced messaging features are needed (larger message sizes, message ordering, single-operaiton destructive reads, scheduled delivery) using push-style delivery (using long polling).

The **create\_queue** method can be used to ensure a queue exists:

```Python
from azure.servicebus import ServiceBusService
sbs = ServiceBusService(service_namespace, account_key, 'owner')
sbs.create_queue('taskqueue')
```

The **send\_queue\_message** method can then be called to insert the message into the queue:

```Python
from azure.servicebus import ServiceBusService, Message
sbs = ServiceBusService(service_namespace, account_key, 'owner')
msg = Message('Hello World!')
sbs.send_queue_message('taskqueue', msg)
```

It is then possible to call the **receive\_queue\_message** method to dequeue the message.

```Python
from azure.servicebus import ServiceBusService
sbs = ServiceBusService(service_namespace, account_key, 'owner')
msg = sbs.receive_queue_message('taskqueue')
```

## ServiceBus Topics

ServiceBus topics are an abstraction on top of ServiceBus Queues that make pub/sub scenarios easy to implement.

The **create\_topic** method can be used to create a server-side topic:

```Python
from azure.servicebus import ServiceBusService
sbs = ServiceBusService(service_namespace, account_key, 'owner')
sbs.create_topic('taskdiscussion')
```

The **send\_topic\_message** method can be used to send a message to a topic:

```Python
from azure.servicebus import ServiceBusService, Message
sbs = ServiceBusService(service_namespace, account_key, 'owner')
msg = Message('Hello World!')
sbs.send_topic_message('taskdiscussion', msg)
```

A client can then create a subscription and start consuming messages by calling the **create\_subscription** method followed by the **receive\_subscription\_message** method. Please note that any messages sent before the subscription is created will not be received.

```Python
from azure.servicebus import ServiceBusService, Message
sbs = ServiceBusService(service_namespace, account_key, 'owner')
sbs.create_subscription('taskdiscussion', 'client1')
msg = Message('Hello World!')
sbs.send_topic_message('taskdiscussion', msg)
msg = sbs.receive_subscription_message('taskdiscussion', 'client1')
```


## Service Management

### Set-up certificates

You  need to create two certificates, one for the server (a .cer file) and one for the client (a .pem file). To create the .pem file using [OpenSSL](http://www.openssl.org), execute this: 

  openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mycert.pem -out mycert.pem

To create the .cer certificate, execute this: 

  openssl x509 -inform pem -in mycert.pem -outform der -out mycert.cer

After you have created the certificate, you will need to upload the .cer file to Microsoft Azure via the "Upload" action of the "Settings" tab of the [management portal](http://manage.windows.com).

To initialize the management service, pass in your subscription id and the path to the .pem file.

```Python
from azure.servicemanagement import ServiceManagementService
subscription_id = '00000000-0000-0000-0000-000000000000'
cert_file = 'mycert.pem'
sms = ServiceManagementService(subscription_id, cert_file)
```

### List Available Locations

```Python
locations = sms.list_locations()
for location in locations:
    print(location.name)
```

### Create a Storage Service

To create a storage service, you need a name for the service (between 3 and 24 lowercase characters and unique within Microsoft Azure), a label (up to 100 characters, automatically encoded to base-64), and either a location or an affinity group.

```Python
name = "mystorageservice"
desc = name
label = name
location = 'West US'

result = sms.create_storage_account(name, desc, label, location=location)
```
  
  
### Create a Cloud Service

A cloud service is also known as a hosted service (from earlier versions of Microsoft Azure).  The **create_hosted_service** method allows you to create a new hosted service by providing a hosted service name (which must be unique in Microsoft Azure), a label (automatically encoded to base-64), and the location *or* the affinity group for your service. 

```Python
name = "myhostedservice"
desc = name
label = name
location = 'West US'

result = sms.create_hosted_service(name, label, desc, location=location)
```

### Create a Deployment

To make a new deployment to Azure you must store the package file in a Microsoft Azure Blob Storage account under the same subscription as the hosted service to which the package is being uploaded. You can create a deployment package with the [Microsoft Azure PowerShell cmdlets](https://www.windowsazure.com/en-us/develop/php/how-to-guides/powershell-cmdlets/), or with the [cspack commandline tool](http://msdn.microsoft.com/en-us/library/wingg432988.aspx).

```Python
service_name = "myhostedservice"
deployment_name = "v1"
slot = 'Production'
package_url = "URL_for_.cspkg_file"
configuration = base64.b64encode(open(file_path, 'rb').read('path_to_.cscfg_file'))
label = service_name

result = sms.create_deployment(service_name,
                     slot,
                     deployment_name,
                     package_url,
                     label,
                     configuration)

operation = sms.get_operation_status(result.request_id)
print('Operation status: ' + operation.status)
```


** For more examples please see the [Microsoft Azure Python Developer Center](http://www.windowsazure.com/en-us/develop/python) **

# Need Help?

Be sure to check out the Microsoft Azure [Developer Forums on Stack Overflow](http://go.microsoft.com/fwlink/?LinkId=234489) if you have trouble with the provided code.

# Contribute Code or Provide Feedback

If you would like to become an active contributor to this project please follow the instructions provided in [Microsoft Azure Projects Contribution Guidelines](http://windowsazure.github.com/guidelines.html).

If you encounter any bugs with the library please file an issue in the [Issues](https://github.com/WindowsAzure/azure-sdk-for-python/issues) section of the project.

# Learn More
[Microsoft Azure Python Developer Center](http://www.windowsazure.com/en-us/develop/python/)
