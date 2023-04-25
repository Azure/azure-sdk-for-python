# Azure App Configuration client library for Python

Azure App Configuration is a managed service that helps developers centralize their application configurations simply and securely.

Modern programs, especially programs running in a cloud, generally have many components that are distributed in nature. Spreading configuration settings across these components can lead to hard-to-troubleshoot errors during an application deployment. Use App Configuration to securely store all the settings for your application in one place.

Use the client library for App Configuration to create and manage application configuration settings.

[Source code](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration)
| [Package (Pypi)][package]
| [Package (Conda)](https://anaconda.org/microsoft/azure-appconfiguration/)
| [API reference documentation](https://learn.microsoft.com/python/api/azure-appconfiguration/azure.appconfiguration?view=azure-python)
| [Product documentation][appconfig_docs]

## _Disclaimer_

_Azure SDK Python packages support for Python 2.7 has ended 01 January 2022. For more information and questions, please refer to https://github.com/Azure/azure-sdk-for-python/issues/20691_
_Python 3.7 or later is required to use this package. For more details, please refer to [Azure SDK for Python version support policy](https://github.com/Azure/azure-sdk-for-python/wiki/Azure-SDKs-Python-version-support-policy)._

## Getting started

### Install the package

Install the Azure App Configuration client library for Python with pip:

```commandline
pip install azure-appconfiguration
```

### Prerequisites

* Python 3.7 or later is required to use this package.
* You need an [Azure subscription][azure_sub], and a [Configuration Store][configuration_store] to use this package.

To create a Configuration Store, you can use the Azure Portal or [Azure CLI][azure_cli].

After that, create the Configuration Store:

```Powershell
az appconfig create --name <config-store-name> --resource-group <resource-group-name> --location eastus
```

### Authenticate the client

In order to interact with the App Configuration service, you'll need to create an instance of the
[AzureAppConfigurationClient][configuration_client_class] class. To make this possible,
you can either use the connection string of the Configuration Store or use an AAD token.

#### Use connection string

##### Get credentials

Use the [Azure CLI][azure_cli] snippet below to get the connection string from the Configuration Store.

```Powershell
az appconfig credential list --name <config-store-name>
```

Alternatively, get the connection string from the Azure Portal.

##### Create client

Once you have the value of the connection string, you can create the AzureAppConfigurationClient:

<!-- SNIPPET:hello_world_sample.create_app_config_client -->

```python
import os
from azure.appconfiguration import AzureAppConfigurationClient
CONNECTION_STRING = os.environ['APPCONFIGURATION_CONNECTION_STRING']

# Create app config client
client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)
```

<!-- END SNIPPET -->

#### Use AAD token

Here we demonstrate using [DefaultAzureCredential][default_cred_ref]
to authenticate as a service principal. However, [AzureAppConfigurationClient][configuration_client_class]
accepts any [azure-identity][azure_identity] credential. See the
[azure-identity][azure_identity] documentation for more information about other
credentials.

##### Create a service principal (optional)
This [Azure CLI][azure_cli] snippet shows how to create a
new service principal. Before using it, replace "your-application-name" with
the appropriate name for your service principal.

Create a service principal:
```Bash
az ad sp create-for-rbac --name http://my-application --skip-assignment
```

> Output:
> ```json
> {
>     "appId": "generated app id",
>     "displayName": "my-application",
>     "name": "http://my-application",
>     "password": "random password",
>     "tenant": "tenant id"
> }
> ```

Use the output to set **AZURE_CLIENT_ID** ("appId" above), **AZURE_CLIENT_SECRET**
("password" above) and **AZURE_TENANT_ID** ("tenant" above) environment variables.
The following example shows a way to do this in Bash:
```Bash
export AZURE_CLIENT_ID="generated app id"
export AZURE_CLIENT_SECRET="random password"
export AZURE_TENANT_ID="tenant id"
```

Assign one of the applicable [App Configuration roles](https://docs.microsoft.com/azure/azure-app-configuration/rest-api-authorization-azure-ad) to the service principal.

##### Create a client
Once the **AZURE_CLIENT_ID**, **AZURE_CLIENT_SECRET** and
**AZURE_TENANT_ID** environment variables are set,
[DefaultAzureCredential][default_cred_ref] will be able to authenticate the
[AzureAppConfigurationClient][configuration_client_class].

Constructing the client also requires your configuration store's URL, which you can
get from the Azure CLI or the Azure Portal. In the Azure Portal, the URL can be found listed as the service "Endpoint"

```python
from azure.identity import DefaultAzureCredential
from azure.appconfiguration import AzureAppConfigurationClient

credential = DefaultAzureCredential()

client = AzureAppConfigurationClient(base_url="your_endpoint_url", credential=credential)
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
read_only : bool
tags : dict
etag : str
```

## Examples

The following sections provide several code snippets covering some of the most common Configuration Service tasks, including:

* [Create a Configuration Setting](#create-a-configuration-setting)
* [Get a Configuration Setting](#get-a-configuration-setting)
* [Delete a Configuration Setting](#delete-a-configuration-setting)
* [List Configuration Settings](#list-configuration-settings)
* [Async APIs](#async-apis)

### Create a Configuration Setting

Create a Configuration Setting to be stored in the Configuration Store.
There are two ways to store a Configuration Setting:

- add_configuration_setting creates a setting only if the setting does not already exist in the store.

<!-- SNIPPET:hello_world_advanced_sample.create_config_setting -->

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

<!-- END SNIPPET -->

- set_configuration_setting creates a setting if it doesn't exist or overrides an existing setting.

<!-- SNIPPET:hello_world_advanced_sample.set_config_setting -->

```python
added_config_setting.value = "new value"
added_config_setting.content_type = "new content type"
updated_config_setting = client.set_configuration_setting(config_setting)
```

<!-- END SNIPPET -->

### Get a Configuration Setting

Get a previously stored Configuration Setting.

<!-- SNIPPET:hello_world_sample.get_config_setting -->

```python
fetched_config_setting = client.get_configuration_setting(
    key="MyKey"
)
```

<!-- END SNIPPET -->

### Delete a Configuration Setting

Delete an existing Configuration Setting.

<!-- SNIPPET:hello_world_advanced_sample.delete_config_setting -->

```python
client.delete_configuration_setting(
    key="MyKey",
    label="MyLabel",
)
```

<!-- END SNIPPET -->

### List Configuration Settings

List all configuration settings filtered with label_filter and/or key_filter.

<!-- SNIPPET:hello_world_advanced_sample.list_config_setting -->

```python
config_settings = client.list_configuration_settings(label_filter="MyLabel")
for item in config_settings:
    print_configuration_setting(item)
```

<!-- END SNIPPET -->

### Async APIs

Async client is supported.
To use the async client library, import the AzureAppConfigurationClient from package azure.appconfiguration.aio instead of azure.appconfiguration

<!-- SNIPPET:hello_world_sample_async.create_app_config_client -->

```python
import os
from azure.appconfiguration.aio import AzureAppConfigurationClient
CONNECTION_STRING = os.environ['APPCONFIGURATION_CONNECTION_STRING']

# Create app config client
client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)
```

<!-- END SNIPPET -->

This async AzureAppConfigurationClient has the same method signatures as the sync ones except that they're async.
For instance, to retrieve a Configuration Setting asynchronously, async_client can be used:

<!-- SNIPPET:hello_world_sample_async.get_config_setting -->

```python
fetched_config_setting = await client.get_configuration_setting(
    key="MyKey"
)
```

<!-- END SNIPPET -->

To use list_configuration_settings, call it synchronously and iterate over the returned async iterator asynchronously

<!-- SNIPPET:hello_world_advanced_sample_async.list_config_setting -->

```python
config_settings = client.list_configuration_settings(label_filter="MyLabel")
async for item in config_settings:
    print_configuration_setting(item)
```

<!-- END SNIPPET -->

## Troubleshooting

See the [troubleshooting guide][troubleshooting_guide] for details on how to diagnose various failure scenarios.

## Next steps

### More sample code

Several App Configuration client library samples are available to you in this GitHub repository.  These include:
- [Hello world](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/hello_world_sample.py) / [Async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/hello_world_sample_async.py)
- [Hello world with labels](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/hello_world_advanced_sample.py) / [Async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/hello_world_advanced_sample_async.py)
- [Make a configuration setting readonly](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/read_only_sample.py) / [Async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/hello_world_sample_async.py)
- [Read revision history](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/list_revision_sample.py) / [Async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/list_revision_sample_async.py)
- [Get a setting if changed](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/conditional_operation_sample.py) / [Async version](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/conditional_operation_sample_async.py)

 For more details see the [samples README](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/samples/README.md).

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

<!-- LINKS -->
[appconfig_docs]: https://docs.microsoft.com/azure/azure-app-configuration/
[appconfig_rest]: https://github.com/Azure/AppConfiguration#rest-api-reference
[azure_cli]: https://docs.microsoft.com/cli/azure
[azure_sub]: https://azure.microsoft.com/free/
[configuration_client_class]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/azure/appconfiguration/_azure_appconfiguration_client.py
[package]: https://pypi.org/project/azure-appconfiguration/
[configuration_store]: https://azure.microsoft.com/services/app-configuration/
[default_cred_ref]: https://aka.ms/azsdk-python-identity-default-cred-ref
[azure_identity]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
[cla]: https://cla.microsoft.com
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
[coc_faq]: https://opensource.microsoft.com/codeofconduct/faq/
[coc_contact]: mailto:opencode@microsoft.com
[troubleshooting_guide]: https://aka.ms/azsdk/python/appconfiguration/troubleshoot
