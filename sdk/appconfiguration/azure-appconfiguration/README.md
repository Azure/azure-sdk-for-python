# Azure App Configuration client library for Python
Azure App Configuration is a managed service that helps developers centralize their application configurations simply and securely.

Modern programs, especially programs running in a cloud, generally have many components that are distributed in nature. Spreading configuration settings across these components can lead to hard-to-troubleshoot errors during an application deployment. Use App Configuration to securely store all the settings for your application in one place.

Use the client library for App Configuration to create and manage application configuration settings.

[Source code]() | [Package (Pypi)][package] | [API reference documentation]() | [Product documentation][azconfig_docs]

## Getting started

### Supported Python version
Python 2.7 and 3.5+
### Install the package

Install the Azure App Configuration client library for Python with pip:

```commandline
pip install azure-appconfiguration
```

**Prerequisites**: You must have an [Azure subscription][azure_sub], and a [Configuration Store][configuration_store] to use this package.

To create a Configuration Store, you can use the Azure Portal or [Azure CLI][azure_cli].

After that, create the Configuration Store:


```Powershell
az appconfig create --name <config-store-name> --resource-group <resource-group-name> --location eastus
```

### Authenticate the client

In order to interact with the App Configuration service, you'll need to create an instance of the [AzureAppConfigurationClient][configuration_client_class] class. To make this possible, you'll need the connection string of the Configuration Store.

#### Get credentials
Use the [Azure CLI][azure_cli] snippet below to get the connection string from the Configuration Store.
```Powershell
az appconfig credential list --name <config-store-name>
```

Alternatively, get the connection string from the Azure Portal.

#### Create client

Once you have the value of the connection string, you can create the ConfigurationClient:

```python
    from azure.appconfiguration import AzureAppConfigurationClient

    connection_str = "<connection_string>"
    client = AzureAppConfigurationClient.from_connection_string(connection_str)
```

## Key concepts

### Configuration Setting
A Configuration Setting is the fundamental resource within a Configuration Store. In its simplest form it is a key and a value. However, there are additional properties such as the modifiable content type and tags fields that allow the value to be interpreted or associated in different ways.

The Label property of a Configuration Setting provides a way to separate Configuration Settings into different dimensions. These dimensions are user defined and can take any form. Some common examples of dimensions to use for a label include regions, semantic versions, or environments. Many applications have a required set of configuration keys that have varying values as the application exists across different dimensions.
For example, MaxRequests may be 100 in "NorthAmerica", and 200 in "WestEurope". By creating a Configuration Setting named MaxRequests with a label of "NorthAmerica" and another, only with a different value, in the "WestEurope" label, an application can seamlessly retrieve Configuration Settings as it runs in these two dimensions.

Properties of a Configuration Setting:

```python
    key : str
    label : str
    content_type : str
    value : str
    last_modified : str
    locked : bool
    tags : dict
    etag : str
```

## Examples
The following sections provide several code snippets covering some of the most common Configuration Service tasks, including:
- [Azure App Configuration client library for Python](#azure-app-configuration-client-library-for-python)
  - [Getting started](#getting-started)
    - [Supported Python version](#supported-python-version)
    - [Install the package](#install-the-package)
    - [Authenticate the client](#authenticate-the-client)
      - [Get credentials](#get-credentials)
      - [Create client](#create-client)
  - [Key concepts](#key-concepts)
    - [Configuration Setting](#configuration-setting)
  - [Examples](#examples)
    - [Create a Configuration Setting](#create-a-configuration-setting)
    - [Retrieve a Configuration Setting](#retrieve-a-configuration-setting)
    - [Update a Configuration Setting](#update-a-configuration-setting)
    - [Delete a Configuration Setting](#delete-a-configuration-setting)
    - [Query Configuration Settings](#query-configuration-settings)
  - [Async Client](#async-client)
  - [Troubleshooting](#troubleshooting)
    - [Logging](#logging)
### Create a Configuration Setting
Create a Configuration Setting to be stored in the Configuration Store.
There are two ways to store a Configuration Setting:
- add_configuration_setting creates a setting only if the setting does not already exist in the store.
```python
config_setting = ConfigurationSetting(
    key="MyKey",
    label="MyLabel",
    value="my value",
    content_type="my content type",
    tags={"my tag": "my tag value"}
)
added_config_setting = client.add_configuration_setting(config_setting)
```
- set_configuration_setting creates a setting if it doesn't exist or overrides an existing setting.
```python
config_setting = ConfigurationSetting(
    key="MyKey",
    label="MyLabel",
    value="my set value",
    content_type="my set content type",
    tags={"my set tag": "my set tag value"}
)
returned_config_setting = client.set_configuration_setting(config_setting)
```

### Retrieve a Configuration Setting
Retrieve a previously stored Configuration Setting.

```python
fetched_config_setting = client.get_configuration_setting(
    key="MyKey", label="MyLabel"
)
```

### Update a Configuration Setting
Use set_configuration_setting if you want to update a whole Configuration Setting object to the store.

Use update_configuration_setting if you want to only update some attributes and leave other attributes as what they're

```python
#  key and label are the identifier of the setting. Only value will be updated.
updated_kv = client.update_configuration_setting(
    key="MyKey",
    label="MyLabel",
    value="my updated value"
)
```

### Delete a Configuration Setting
Delete an existing Configuration Setting by calling delete_configuration_setting

```python
deleted_config_setting = client.delete_configuration_setting(
    key="MyKey", label="MyLabel"
)
```

### Query Configuration Settings
```python

filtered_listed = client.list_configuration_settings(
    labels=["*Labe*"], keys=["*Ke*"]
)
for item in filtered_listed:
    pass  # do something

```

## Async Client
Async client is supported for python 3.5+. 
To use the async client library, import the AzureAppConfigurationClient from package azure.appconfiguration.aio instead of azure.appconfiguration
```python
from azure.appconfiguration.aio import AzureAppConfigurationClient

connection_str = "<connection_string>"
async_client = AzureAppConfigurationClient.from_connection_string(connection_str)
```
This async AzureAppConfigurationClient has the same method signatures as the sync ones except that they're async.
For instance, to retrieve a Configuration Setting asynchronously, async_client can be used:
```python
fetched_config_setting = await async_client.get_configuration_setting(
    key="MyKey", label="MyLabel"
)
```

To use list_configuration_settings, call it synchronously and iterate over the returned async iterator asynchronously 
```python

filtered_listed = async_client.list_configuration_settings(
    labels=["*Labe*"], keys=["*Ke*"]
)
async for item in filtered_listed:
    pass  # do something

```

## Troubleshooting

### Logging

This SDK uses Python standard logging library.
You can configure logging print out debugging information to the stdout or anywhere you want.

```python
import logging

logging.basicConfig(level=logging.DEBUG)
````

Http request and response details are printed to stdout with this logging config.


<!-- LINKS -->
[appconfig_docs]: https://docs.microsoft.com/en-us/azure/azure-app-configuration/
[appconfig_rest]: https://github.com/Azure/AppConfiguration#rest-api-reference
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_sub]: https://azure.microsoft.com/free/
[configuration_client_class]: ./azure/configuration/azure_configuration_client.py
[package]: https://pypi.org/project/azure-app-configuration/