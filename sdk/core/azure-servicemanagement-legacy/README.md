# Microsoft Azure SDK for Python

This is the Microsoft Azure Service Management Legacy Client Library.

All packages in this bundle have been tested with Python 2.7, 3.3, 3.4 and 3.5.

For the newer Azure Resource Management (ARM) libraries, see [azure-mgmt](https://pypi.python.org/pypi/azure-mgmt).

For a more complete set of Azure libraries, see the [azure sdk python release](https://aka.ms/azsdk/python/all).


# Compatibility

**IMPORTANT**: If you have an earlier version of the azure package
(version < 1.0), you should uninstall it before installing this package.

You can check the version using pip:

```shell
pip freeze
```

If you see azure==0.11.0 (or any version below 1.0), uninstall it first:

```shell
pip uninstall azure
```

# Features

-  Cloud Service management (Virtual Machines, VM Images, OS Images)
-  Storage accounts management
-  Scheduler management
-  Service Bus management
-  Affinity Group management
-  Management certificate management
-  Web Apps (Website) management


# Installation

## Download Package

To install via the Python Package Index (PyPI), type:

```shell
pip install azure-servicemanagement-legacy
```


## Download Source Code

To get the source code of the SDK via **git** type:

```shell
git clone https://github.com/Azure/azure-sdk-for-python.git
cd azure-sdk-for-python
cd azure-servicemanagement-legacy
python setup.py install
```


# Usage

## Authentication

### Set-up certificates

You will need two certificates, one for the server (a .cer file) and one for
the client (a .pem file).

### Using the Azure .PublishSettings certificate

You can download your Azure publish settings file and use the certificate that
is embedded in that file to create the client certificate. The server
certificate already exists, so you won't need to upload one.

To do this, download your [publish settings](https://go.microsoft.com/fwlink/?LinkID=301775)
then use this code to create the .pem file.

```python
from azure.servicemanagement import get_certificate_from_publish_settings

subscription_id = get_certificate_from_publish_settings(
    publish_settings_path='MyAccount.PublishSettings',
    path_to_write_certificate='mycert.pem',
    subscription_id='00000000-0000-0000-0000-000000000000',
)
```

The subscription id parameter is optional. If there are more than one
subscription in the publish settings, the first one will be used.

### Creating and uploading new certificate with OpenSSL

To create the .pem file using [OpenSSL](https://www.openssl.org), execute this:

```shell
openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout mycert.pem -out mycert.pem
```
To create the .cer certificate, execute this:

```shell
openssl x509 -inform pem -in mycert.pem -outform der -out mycert.cer
```

After you have created the certificate, you will need to upload the .cer
file to Microsoft Azure via the "Upload" action of the "Settings" tab of
the [management portal](https://manage.windowsazure.com).


## ServiceManagementService

### Initialization

To initialize the management service, pass in your subscription id and
the path to the .pem file.

```python
from azure.servicemanagement import ServiceManagementService
subscription_id = '00000000-0000-0000-0000-000000000000'
cert_file = 'mycert.pem'
sms = ServiceManagementService(subscription_id, cert_file)
```

### List Available Locations

```python
locations = sms.list_locations()
for location in locations:
    print(location.name)
```

### Create a Storage Service

To create a storage service, you need a name for the service (between 3
and 24 lowercase characters and unique within Microsoft Azure), a label
(up to 100 characters, automatically encoded to base-64), and either a
location or an affinity group.

```python
name = "mystorageservice"
desc = name
label = name
location = 'West US'

result = sms.create_storage_account(name, desc, label, location=location)
sms.wait_for_operation_status(result.request_id, timeout=30)
```

### Create a Cloud Service

A cloud service is also known as a hosted service (from earlier versions
of Microsoft Azure). The **create\_hosted\_service** method allows you
to create a new hosted service by providing a hosted service name (which
must be unique in Microsoft Azure), a label (automatically encoded to
base-64), and the location *or* the affinity group for your service.

```python
name = "myhostedservice"
desc = name
label = name
location = 'West US'

result = sms.create_hosted_service(name, label, desc, location=location)
sms.wait_for_operation_status(result.request_id, timeout=30)
```

### Create a Virtual Machine

To create a virtual machine, you first need to create a cloud service.
Then create the virtual machine deployment using the
create_virtual_machine_deployment method.

```python
from azure.servicemanagement import LinuxConfigurationSet, OSVirtualHardDisk

name = "myhostedservice"

# Name of an os image as returned by list_os_images
image_name = 'OpenLogic__OpenLogic-CentOS-62-20120531-en-us-30GB.vhd'

# Destination storage account container/blob where the VM disk
# will be created
media_link = 'url_to_target_storage_blob_for_vm_hd'

# Linux VM configuration, you can use WindowsConfigurationSet
# for a Windows VM instead
linux_config = LinuxConfigurationSet(
    'myhostname',
    'myuser',
    'mypassword',
    disable_ssh_password_authentication=True,
)

os_hd = OSVirtualHardDisk(image_name, media_link)

result = sms.create_virtual_machine_deployment(
    service_name=name,
    deployment_name=name,
    deployment_slot='production',
    label=name,
    role_name=name,
    system_config=linux_config,
    os_virtual_hard_disk=os_hd,
    role_size='Small',
)
sms.wait_for_operation_status(result.request_id, timeout=600)
```


# Need Help?

Be sure to check out the Microsoft Azure [Developer Forums on Stack
Overflow](https://go.microsoft.com/fwlink/?LinkId=234489) if you have
trouble with the provided code.


# Contribute Code or Provide Feedback

If you would like to become an active contributor to this project please
follow the instructions provided in [Microsoft Azure Projects
Contribution
Guidelines](https://azure.github.io/guidelines.html).

If you encounter any bugs with the library please file an issue in the
[Issues](https://github.com/Azure/azure-sdk-for-python/issues)
section of the project.


# Learn More

[Microsoft Azure Python Developer
Center](https://azure.microsoft.com/develop/python/)


![Impressions](https://azure-sdk-impressions.azurewebsites.net/api/impressions/azure-sdk-for-python%2Fazure-servicemanagement-legacy%2FREADME.png)
