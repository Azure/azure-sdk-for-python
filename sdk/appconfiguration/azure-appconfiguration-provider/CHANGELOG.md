# Release History

## 1.2.0 (2024-05-24)

### Features Added

* Enable loading of feature flags with `feature_flag_enabled`
* Select Feature Flags to load with `feature_flag_selectors`
* Enable/Disable Feature Flag Refresh with `feature_flag_refresh_enabled`

### Bugs Fixed

* Fixes issue where loading configurations were slower due to returning a copy of the configurations.

## 1.1.0 (2024-01-29)

### Features Added

* New API for Azure App Configuration Provider, `refresh`, which can be used to refresh the configuration from the Azure App Configuration service. `refresh` by default can check every 30 seconds for changes to specified sentinel keys. If a change is detected then all configurations are reloaded. Sentinel keys can be set by passing a list of `SentinelKey`'s to `refresh_on`.
* Added new options `on_refresh_success` and `on_refresh_failure` callbacks to the load method. These callbacks are called when the refresh method successfully refreshes the configuration or fails to refresh the configuration.

### Bugs Fixed

* Verifies that the `refresh_interval` is at least 1 second.

## 1.1.0b3 (2023-12-19)

### Features Added

- Added on_refresh_success callback to load method. This callback is called when the refresh method successfully refreshes the configuration.
- Added minimum up time. This is the minimum amount of time the provider will try to be up before throwing an error. This is to prevent quick restart loops.

### Bugs Fixed

- Fixes issue where the refresh timer only reset after a change was found.

### Other Changes

- Renamed the type `SentinelKey` to be `WatchKey`.

## 1.1.0b2 (2023-09-29)

### Features Added

* Added support for `keyvault_credential`, `keyvault_client_configs`, and `secret_resolver` as `kwargs` instead of using `AzureAppConfigurationKeyVaultOptions`.

### Bugs Fixed

* Fixes issue where `user_agent` was required to be set.
* Fixes issue where correlation context info is wrong on refresh.

## 1.1.0b1 (2023-09-13)

### Features Added

* New API for Azure App Configuration Provider, `refresh`, which can be used to refresh the configuration from the Azure App Configuration service. `refresh` by default can check every 30 seconds for changes to specified sentinel keys. If a change is detected then all configurations are reloaded. Sentinel keys can be set by passing  a list of `SentinelKey`'s to `refresh_on`.
* Added support for customer provided user agent prefix.

### Other Changes

* Updated to use AZURE_APP_CONFIGURATION_TRACING_DISABLED environment variable to disable tracing.
* Changed the maximum number of retries to 2 from the default of 3 retries.
* Changed the maximum back off time between retries to 1 minute from the default of 2 minutes.
* Bumped minimum dependency on `azure-core` to `>=1.25.0`

## 1.0.0 (2023-03-09)

### Breaking Changes
* Renamed `load_provider` to `load`
* Added `AzureAppConfigurationKeyVaultOptions` to take in a `client_configs` a Mapping of endpoints to client kwargs instead of taking in the whole client.
* Removed `AzureAppConfigurationKeyVaultOptions` `secret_clients`, `client_configs` should be used instead.
* Made key_filter and label_filter kwargs for Setting Selector
* Renamed `trimmed_key_prefixes` to `trim_prefixes`

### Other Changes
* Made EMPTY_LABEL a constant. i.e. "\0"

## 1.0.0b2 (2023-02-15)

### Features Added
* Added Async Support
* Added missing methods for Mapping API
* Made load method properties unordered.

### Breaking Changes
* Changes how load works. Moves if from AzureAppConfigurationProvider.load to load_provider.
* Removed custom Key Vault Error
* Removed unneeded __repr__ and copy methods.
* All Feature Flags are added to there own key and have there prefix removed

### Bugs Fixed
* Fixed Issue where Key Vault Clients couldn't be set in some situations

### Other Changes
* Updated method docs
* Fixed load doc that used `selector` instead of `selects`.
* Fixed CLI link in Readme.

## 1.0.0b1 (2022-10-13)

New Azure App Configuration Provider

Provides additional support above the Azure App Configuration SDK. Enables:
* Connecting to an Azure App Configuration store
* Selecting multiple keys using Setting Selector
* Resolve Key Vault References when supplied AzureAppConfigurationKeyVaultOptions

The Azure App Configuration Provider once loaded returns a dictionary of key/value pairs to use in configuration.

```python
endpoint = "https://<your-store>.azconfig.io"
default_credential = DefaultAzureCredential()
config = AzureAppConfigurationProvider.load(
    endpoint=endpoint, credential=default_credential)
print(config["message"])
```
