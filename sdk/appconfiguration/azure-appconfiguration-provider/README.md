# Azure App Configuration Python Provider

Azure App Configuration is a managed service that helps developers centralize their application configurations simply and securely. This provider adds additional functionality above the azure-sdk-for-python.

Using the provider enables loading sets of configurations from a Azure App Configuration store in a managed way.

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
config = AzureAppConfigurationProvider.load(connection_string="your-connection-string")
```

or with AAD:

```python
config = AzureAppConfigurationProvider.load(endpoint="your-endpoint", credential=DefaultAzureCredential())
```

these providers will by default load all configurations with `(No Label)` from your configuration store.

### Selecting configurations

You can refine or expand the configurations loaded from your store by using `SettingSelector`s. Setting selectors provide a way to pass a key filter and label filter into the provider.

```python
selects = {SettingSelector(key_filter="*", label_filter="\0"), SettingSelector(key_filter="*", label_filter="dev")}
config = AzureAppConfigurationProvider.load(
    endpoint=endpoint, credential=default_credential, selects=selects)
```
In this example all configuration with empty label and the dev label are loaded. Because the dev selector is listed last, any configurations from dev take priority over those with `(No Label)` when duplicates are found.

### Trimming Keys

You can trim the prefix off of keys by providing a list of trimmed key prefixes to the provider.

```python
trimmed_key_prefixes={"/application/"}
config = AzureAppConfigurationProvider.load(
    endpoint=endpoint, credential=default_credential, trimmed_key_prefixes=trimmed_key_prefixes)
```

### Resolving Key Vault References

Key Vault References can be resolved by providing credentials to your key vault to the provider using `AzureAppConfigurationKeyVaultOptions`.

#### With Credentials

You can provide `AzureAppConfigurationKeyVaultOptions` with a credential and all key vault references will be resolved with it. The provider will attempt to connect to any key vault referenced with the credential provided.

```python
key_vault_options = AzureAppConfigurationKeyVaultOptions(credential=default_credential)
config = AzureAppConfigurationProvider.load(endpoint=endpoint, credential=default_credential, key_vault_options=key_vault_options)
```
### With Clients

You can provide `AzureAppConfigurationKeyVaultOptions` with a list of `SecretClients`.

```python
key_vault_options = AzureAppConfigurationKeyVaultOptions(
    secret_clients={SecretClient(
        vault_url=key_vault_uri, credential=default_credential)})
config = AzureAppConfigurationProvider.load(endpoint=endpoint, credential=default_credential, key_vault_options=key_vault_options)
```

### Secret Resolver

If no Credentials or Clients are provided a secret resolver can be used. Secret resolver provides a way to return any value you want to a key vault reference.

```python
def secret_resolver(uri):
    return "From Secret Resolver"

key_vault_options = AzureAppConfigurationKeyVaultOptions(
    secret_resolver=secret_resolver)
config = AzureAppConfigurationProvider.load(
    endpoint=endpoint, credential=default_credential, key_vault_options=key_vault_options)
```