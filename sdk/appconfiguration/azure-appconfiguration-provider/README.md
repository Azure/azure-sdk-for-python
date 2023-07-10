# Azure App Configuration Python Provider client library for Python

Azure App Configuration is a managed service that helps developers centralize their application configurations simply and securely. This provider adds additional functionality above the azure-sdk-for-python.

Using the provider enables loading sets of configurations from an Azure App Configuration store in a managed way.

## Getting started

### Get credentials

Use the [Azure CLI][azure_cli] snippet below to get the connection string from the Configuration Store.

```Powershell
az appconfig credential list --name <config-store-name>
```

Alternatively, get the connection string from the Azure Portal.

### Creating a provider

You can create a client with a connection string:

```python
from azure.appconfiguration.provider import load

config = load(connection_string="your-connection-string")
```

or with AAD:

```python
from azure.appconfiguration.provider import load

config = load(endpoint="your-endpoint", credential=DefaultAzureCredential())
```

these providers will by default load all configurations with `(No Label)` from your configuration store into a dictionary of key/values.

### Features

Currently the Azure App Configuration Provider enables:

* Connecting to an App Configuration Store using a connection string or Azure Active Directory.
* Selecting multiple sets of configurations using `SettingSelector`.
* Trim prefixes off key names.
* Resolving Key Vault References, requires AAD.
* Secret Resolver, resolve Key Vault References locally without connecting to Key Vault.
* Json Content Type

#### Future Features

List of features we are going to add to the Python Provider in the future.

* Geo-Replication support
* Feature Management
* Dynamic Refresh
* Configuration Placeholders

## Examples

### Selecting configurations

You can refine or expand the configurations loaded from your store by using `SettingSelector`s. Setting selectors provide a way to pass a key filter and label filter into the provider.

```python
from azure.appconfiguration.provider import load, SettingSelector
from azure.identity import DefaultAzureCredential

selects = {SettingSelector(key_filter="*", label_filter="\0"), SettingSelector(key_filter="*", label_filter="dev")}
config = load(endpoint=endpoint, credential=DefaultAzureCredential(), selects=selects)
```

In this example all configuration with empty label and the dev label are loaded. Because the dev selector is listed last, any configurations from dev take priority over those with `(No Label)` when duplicates are found.

### Trimming Keys

You can trim the prefix off of keys by providing a list of trimmed key prefixes to the provider. For example, if you have the key(s) like `/application/message` in your configuration store, you could trim `/application/` from them.

```python
from azure.appconfiguration.provider import load
from azure.identity import DefaultAzureCredential

trim_prefixes={"/application/"}
config = load(endpoint=endpoint, credential=DefaultAzureCredential(), trim_prefixes=trim_prefixes)
print(config["message"])
```

### Resolving Key Vault References

Key Vault References can be resolved by providing credentials to your key vault to the provider using `AzureAppConfigurationKeyVaultOptions`.

#### With Credentials

You can provide `AzureAppConfigurationKeyVaultOptions` with a credential and all key vault references will be resolved with it. The provider will attempt to connect to any key vault referenced with the credential provided.

```python
from azure.appconfiguration.provider import load, AzureAppConfigurationKeyVaultOptions
from azure.identity import DefaultAzureCredential

key_vault_options = AzureAppConfigurationKeyVaultOptions(credential=DefaultAzureCredential())
config = load(endpoint=endpoint, credential=DefaultAzureCredential(), key_vault_options=key_vault_options)
```

### With Clients

You can provide `AzureAppConfigurationKeyVaultOptions` with a list of `SecretClients`.

```python
from azure.appconfiguration.provider import load, AzureAppConfigurationKeyVaultOptions
from azure.identity import DefaultAzureCredential

key_vault_options = AzureAppConfigurationKeyVaultOptions(
    client_configs={key_vault_uri: {'credential': credential}})
config = load(endpoint=endpoint, credential=DefaultAzureCredential(), key_vault_options=key_vault_options)
```

### Secret Resolver

If no Credentials or Clients are provided a secret resolver can be used. Secret resolver provides a way to return any value you want to a key vault reference.

```python
from azure.appconfiguration.provider import load, AzureAppConfigurationKeyVaultOptions
from azure.identity import DefaultAzureCredential

def secret_resolver(uri):
    return "From Secret Resolver"

key_vault_options = AzureAppConfigurationKeyVaultOptions(
    secret_resolver=secret_resolver)
config = load(endpoint=endpoint, credential=DefaultAzureCredential(), key_vault_options=key_vault_options)
```

## Key concepts

## Troubleshooting

## Next steps

Check out our Django and Flask examples to see how to use the provider in a web application.

### [Django](https://github.com/Azure/AppConfiguration/tree/main/examples/Python/python-django-webapp-sample)

### [Flask](https://github.com/Azure/AppConfiguration/tree/main/examples/Python/python-flask-webapp-sample)

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit <https://cla.microsoft.com>.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact <opencode@microsoft.com> with any
additional questions or comments.

[azure_cli]: https://learn.microsoft.com/cli/azure/appconfig
[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
