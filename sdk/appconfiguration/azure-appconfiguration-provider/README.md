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

<!-- SNIPPET:connection_string_sample.create_provider_connection_string -->

```python
import os
from azure.appconfiguration.provider import load

connection_string = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

# Connecting to Azure App Configuration using connection string
config = load(connection_string=connection_string, **kwargs)
```

<!-- END SNIPPET -->

or with Entra ID:

<!-- SNIPPET:entra_id_sample.create_provider_entra_id -->

```python
import os
from azure.appconfiguration.provider import load
from azure.identity import DefaultAzureCredential

endpoint = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]
credential = DefaultAzureCredential()

# Connecting to Azure App Configuration using Entra ID
config = load(endpoint=endpoint, credential=credential, **kwargs)
```

<!-- END SNIPPET -->

these providers will by default load all configurations with `(No Label)` from your configuration store into a dictionary of key/values.

### Features

Currently the Azure App Configuration Provider enables:

* Connecting to an App Configuration Store using a connection string or Entra ID.
* Selecting multiple sets of configurations using `SettingSelector`.
* Filtering by tags using `tag_filters` on `SettingSelector`.
* Loading from snapshots using `snapshot_name` on `SettingSelector`.
* Loading Feature Flags
* Dynamic Refresh
* Geo-Replication support with replica discovery and load balancing.
* Trim prefixes off key names.
* Resolving Key Vault References, requires Entra ID.
* Secret Resolver, resolve Key Vault References locally without connecting to Key Vault.
* Periodic Key Vault secret refresh via `secret_refresh_interval`.
* Json Content Type
* Configuration mapper for transforming settings during load.
* Configurable startup timeout with retry.
* Async support via `azure.appconfiguration.provider.aio`.

## Examples

### Selecting configurations

You can refine or expand the configurations loaded from your store by using `SettingSelector`s. Setting selectors provide a way to pass a key filter and label filter into the provider.

<!-- SNIPPET:entra_id_sample.setting_selector_entra_id -->

```python
from azure.appconfiguration.provider import load, SettingSelector

# Connection to Azure App Configuration using SettingSelector
selects = [SettingSelector(key_filter="message*")]
config = load(
    endpoint=endpoint,
    credential=credential,
    selects=selects,
    feature_flag_enabled=True,
    feature_flag_selectors=None,
    **kwargs,
)
```

<!-- END SNIPPET -->

In this example, configuration settings with keys matching `message*` are loaded. Feature flags are also enabled, so the default feature flags (those with no label) will be loaded.

### Filtering by Tags

You can filter configuration settings by tags using the `tag_filters` parameter on `SettingSelector`. Tag filters must follow the format `"tagName=tagValue"`.

<!-- SNIPPET:entra_id_sample.tag_filters -->

```python
from azure.appconfiguration.provider import load, SettingSelector

# Filtering by tags
selects = [SettingSelector(key_filter="*", tag_filters=["env=prod"])]
config = load(endpoint=endpoint, credential=credential, selects=selects, **kwargs)
```

<!-- END SNIPPET -->

### Loading from Snapshots

You can load configuration settings from a snapshot by providing `snapshot_name` on `SettingSelector`. When `snapshot_name` is specified, all configuration settings from the snapshot are loaded. Note that `snapshot_name` cannot be used together with `key_filter`, `label_filter`, or `tag_filters`. In the examples below, `endpoint`, `credential`, and `snapshot_name` are assumed to be defined. See the [snapshot sample](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration-provider/samples/snapshot_sample.py) for complete setup.

<!-- SNIPPET:snapshot_sample.load_snapshot -->

```python
from azure.appconfiguration.provider import load, SettingSelector

# Step 2: Loading configuration settings from the snapshot
snapshot_selects = [SettingSelector(snapshot_name=snapshot_name)]
config = load(endpoint=endpoint, credential=credential, selects=snapshot_selects, **kwargs)
```

<!-- END SNIPPET -->

You can also mix snapshot selectors with regular selectors. Later selectors take precedence when there are duplicate keys.

<!-- SNIPPET:snapshot_sample.load_snapshot_mixed -->

```python
# Step 3: Combine snapshot with regular selectors (later selectors take precedence)
mixed_selects = [
    SettingSelector(snapshot_name=snapshot_name),  # Load all settings from snapshot
    SettingSelector(key_filter="override.*", label_filter="prod"),  # Also load specific override settings
]
config_mixed = load(endpoint=endpoint, credential=credential, selects=mixed_selects, **kwargs)
```

<!-- END SNIPPET -->

## Dynamic Refresh

The provider can be configured to refresh configurations from the store on a set interval. This is done by providing a `refresh_on` to the provider, which is a list of key(s) that will be watched for changes, and when they do change a refresh can happen. `refresh_interval` is the period of time in seconds between refreshes. `on_refresh_success` is a callback that will be called only if a change is detected and no error happens. `on_refresh_error` is a callback that will be called when a refresh fails.

<!-- SNIPPET:refresh_sample.refresh_provider -->

```python
import os
from azure.appconfiguration.provider import load, WatchKey

connection_string = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

config = load(
    connection_string=connection_string,
    refresh_on=[WatchKey("Sentinel")],
    refresh_interval=60,
    **kwargs,
)
```

<!-- END SNIPPET -->

In this example, the sentinel key will be checked for changes no sooner than every 60 seconds. In order to check for changes, the provider's `refresh` method needs to be called.

<!-- SNIPPET:refresh_sample.refresh_call -->

```python
config.refresh()
```

<!-- END SNIPPET -->

Once the provider is refreshed, the configurations can be accessed as normal. And if any changes have been made it will be updated with the latest values. If the `refresh_interval` hasn't passed since the last refresh check, the provider will not check for changes.

For additional info check out [Dynamic Refresh](https://learn.microsoft.com/azure/azure-app-configuration/enable-dynamic-configuration-python) on MS Learn.

### Trimming Keys

You can trim the prefix off of keys by providing a list of trimmed key prefixes to the provider. For example, if you have the key(s) like `/application/message` in your configuration store, you could trim `/application/` from them.

<!-- SNIPPET:entra_id_sample.trim_prefixes_entra_id -->

```python
from azure.appconfiguration.provider import load

# Connecting to Azure App Configuration using Entra ID and trim key prefixes
trimmed = ["test."]
config = load(endpoint=endpoint, credential=credential, trim_prefixes=trimmed, **kwargs)
```

<!-- END SNIPPET -->

### Resolving Key Vault References

Key Vault References can be resolved by providing credentials to your key vault to the provider.

#### With Credentials

You can provide a `keyvault_credential` and all key vault references will be resolved with it. The provider will attempt to connect to any key vault referenced with the credential provided.

<!-- SNIPPET:key_vault_reference_sample.key_vault_reference -->

```python
from azure.appconfiguration.provider import load, SettingSelector

# Connection to Azure App Configuration using Entra ID and Resolving Key Vault References
selects = [SettingSelector(key_filter="*", label_filter="prod")]

config = load(endpoint=endpoint, credential=credential, keyvault_credential=credential, selects=selects, **kwargs)
```

<!-- END SNIPPET -->

#### With Client Configs

You can provide `keyvault_client_configs` with a mapping of Key Vault URIs to client configurations. This is useful when different Key Vaults require different credentials.

<!-- SNIPPET:key_vault_reference_customized_clients_sample.key_vault_reference_customized_clients -->

```python
from azure.appconfiguration.provider import load, SettingSelector

# Connection to Azure App Configuration using Entra ID with Provided Client
client_configs = {key_vault_uri: {"credential": credential}}
selects = [SettingSelector(key_filter="*", label_filter="prod")]
config = load(
    endpoint=endpoint,
    credential=credential,
    keyvault_client_configs=client_configs,
    selects=selects,
    **kwargs,
)
```

<!-- END SNIPPET -->

#### Secret Resolver

If no credentials or client configs are provided, a `secret_resolver` can be used. Secret resolver provides a way to return any value you want for a key vault reference.

<!-- SNIPPET:key_vault_reference_sample.key_vault_reference_secret_resolver -->

```python
from azure.appconfiguration.provider import load


def secret_resolver(uri):
    return "From Secret Resolver"


config = load(endpoint=endpoint, credential=credential, secret_resolver=secret_resolver, **kwargs)
```

<!-- END SNIPPET -->

### Secret Refresh Interval

When using Key Vault references, the provider can periodically refresh resolved secrets. If you set the `secret_refresh_interval` parameter, secrets are refreshed at that interval (minimum 1 second).

<!-- SNIPPET:key_vault_reference_sample.key_vault_reference_secret_refresh_interval -->

```python
from azure.appconfiguration.provider import load

# Refresh Key Vault secrets every 120 seconds
config = load(
    endpoint=endpoint,
    credential=credential,
    keyvault_credential=credential,
    secret_refresh_interval=120,
    **kwargs,
)
```

<!-- END SNIPPET -->

## Geo Replication

The Azure App Configuration Provider library will automatically discover the provided configuration store's replicas and use the replicas if any issue arises. From more information see [Geo-Replication](https://learn.microsoft.com/azure/azure-app-configuration/howto-geo-replication).

Replica discovery is enabled by default. If you want to disable it, you can set `replica_discovery_enabled` to `False`.

<!-- SNIPPET:entra_id_sample.geo_replication_disable_discovery -->

```python
from azure.appconfiguration.provider import load

# Disabling replica discovery
config = load(endpoint=endpoint, credential=credential, replica_discovery_enabled=False, **kwargs)
```

<!-- END SNIPPET -->

You can also enable load balancing to distribute requests across replicas by setting `load_balancing_enabled` to `True`.

<!-- SNIPPET:entra_id_sample.geo_replication_load_balancing -->

```python
from azure.appconfiguration.provider import load

# Enabling load balancing across replicas
config = load(endpoint=endpoint, credential=credential, load_balancing_enabled=True, **kwargs)
```

<!-- END SNIPPET -->

## Loading Feature Flags

Feature Flags can be loaded from config stores using the provider. Feature flags are loaded as a list of feature flag objects stored in the provider under `feature_management`, then `feature_flags`.

<!-- SNIPPET:entra_id_sample.feature_flag_loading -->

```python
from azure.appconfiguration.provider import load

config = load(endpoint=endpoint, credential=credential, feature_flag_enabled=True, **kwargs)
feature_flags = config["feature_management"]["feature_flags"]
alpha = next(flag for flag in feature_flags if flag["id"] == "Alpha")
print(alpha["enabled"])
```

<!-- END SNIPPET -->

By default all feature flags with no label are loaded when `feature_flag_enabled` is set to `True`. If you want to load feature flags with a specific label you can use `SettingSelector` to filter the feature flags.

<!-- SNIPPET:entra_id_sample.feature_flag_selector -->

```python
from azure.appconfiguration.provider import load, SettingSelector

config = load(
    endpoint=endpoint,
    credential=credential,
    feature_flag_enabled=True,
    feature_flag_selectors=[SettingSelector(key_filter="*", label_filter="dev")],
    **kwargs,
)
feature_flags = config["feature_management"]["feature_flags"]
alpha = next(flag for flag in feature_flags if flag["id"] == "Alpha")
print(alpha["enabled"])
```

<!-- END SNIPPET -->

To enable refresh for feature flags you need to enable refresh. This will allow the provider to refresh feature flags the same way it refreshes configurations. Unlike configurations, all loaded feature flags are monitored for changes and will cause a refresh. Refresh of configuration settings and feature flags are independent of each other. Both are trigged by the `refresh` method, but a feature flag changing will not cause a refresh of configurations and vice versa. Also, if refresh for configuration settings is not enabled, feature flags can still be enabled for refresh.

<!-- SNIPPET:refresh_sample_feature_flags.refresh_feature_flags -->

```python
import os
from azure.appconfiguration.provider import load, WatchKey

connection_string = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

config = load(
    connection_string=connection_string,
    refresh_on=[WatchKey("message")],
    refresh_on_feature_flags=True,
    refresh_interval=60,
    feature_flag_enabled=True,
    feature_flag_refresh_enabled=True,
    **kwargs,
)
```

<!-- END SNIPPET -->

## JSON Content Type

Configuration settings with a JSON content type (e.g., `application/json`) are automatically deserialized into their corresponding Python objects when loaded by the provider.

<!-- SNIPPET:entra_id_sample.json_content_type -->

```python
from azure.appconfiguration.provider import load

# Settings with JSON content type are automatically deserialized
config = load(endpoint=endpoint, credential=credential, **kwargs)
app_config = config["app/config"]  # Returns a dict if the value is JSON
print(app_config["timeout"])
```

<!-- END SNIPPET -->

## Configuration Mapper

You can provide a `configuration_mapper` callback to transform configuration settings before they are added to the provider.

<!-- SNIPPET:entra_id_sample.configuration_mapper -->

```python
from azure.appconfiguration.provider import load


def my_mapper(setting):
    # Transform the setting as needed
    setting.value = setting.value.strip()


config = load(endpoint=endpoint, credential=credential, configuration_mapper=my_mapper, **kwargs)
```

<!-- END SNIPPET -->

## Startup Timeout

The provider supports configurable startup timeout with automatic retry. By default, the provider allows 100 seconds for the initial load from Azure App Configuration. You can customize this with the `startup_timeout` parameter.

<!-- SNIPPET:entra_id_sample.startup_timeout -->

```python
from azure.appconfiguration.provider import load

config = load(endpoint=endpoint, credential=credential, startup_timeout=200, **kwargs)
```

<!-- END SNIPPET -->

## Async Support

The provider includes full async support via the `azure.appconfiguration.provider.aio` module.

<!-- SNIPPET:async_entra_id_sample.create_provider_entra_id_async -->

```python
from azure.appconfiguration.provider.aio import load

# Connecting to Azure App Configuration using Entra ID
config = await load(endpoint=endpoint, credential=credential, **kwargs)
print(config["message"])

await credential.close()
await config.close()
```

<!-- END SNIPPET -->

## Key concepts

The `AzureAppConfigurationProvider` is the main object returned by `load()`. It implements the `Mapping` interface, so it can be used like a read-only dictionary. Call `refresh()` (or `await refresh()` for async) to pull the latest values from the store.

Key types used:

* `SettingSelector` — Filters which configuration settings to load by key, label, tags, or snapshot name.
* `WatchKey` — Identifies a sentinel key (and optional label) used to trigger configuration refresh.
* `AzureAppConfigurationKeyVaultOptions` — Groups Key Vault credential, per-vault client configs, and secret resolver options.

## Troubleshooting

### Logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging. Information about configuration loading, refresh, and Key Vault resolution is logged at the `DEBUG` level.

### Common Issues

* **Key Vault references not resolving** — Ensure you have provided credentials via `key_vault_options` or `keyvault_credential`. Key Vault resolution requires Entra ID authentication.
* **Configuration not refreshing** — Make sure you are calling `config.refresh()` periodically (e.g., before each request in a web app). The provider does not auto-refresh in the background.
* **Startup failures** — If the store is unreachable during startup, the provider will retry until `startup_timeout` (default 100 seconds) is exceeded. Increase this value if your store is expected to have high latency.

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
