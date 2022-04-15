# Release History

## 1.4.0 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 1.3.0 (2021-11-10)

### Bugs Fixed
- Fix the issue that data was persisted according to an incorrect schema/in an incorrect format ([#20518](https://github.com/Azure/azure-sdk-for-python/issues/20518))

  `SecretReferenceConfigurationSetting` in 1.2.0 used "secret_uri" rather than "uri" as the schema keywords which 
  broken inter-operation of `SecretReferenceConfigurationSetting` between SDK and the portal. 
  
  Please:
  - Use 1.3.0+ for any `SecretReferenceConfigurationSetting` uses.
  - Call a get method for existing `SecretReferenceConfigurationSetting`s and set them back to correct the format.

## 1.2.0 (2021-07-06)
### Features Added
* Adds `FeatureFlagConfigurationSetting` and `SecretReferenceConfigurationSetting` models
* `AzureAppConfigurationClient` can now be used as a context manager.
* Adds `update_sync_token` to update sync tokens from Event Grid notifications.

## 1.2.0b2 (2021-06-08)

### Features
- Adds context manager functionality to the sync and async `AzureAppConfigurationClient`s.

### Fixes
- Fixes a deserialization bug for `FeatureFlagConfigurationSetting` and `SecretReferenceConfigurationSetting`.

## 1.2.0b1 (2021-04-06)

### Features

- Adds method `update_sync_token` to include sync tokens from EventGrid notifications.
- Added `SecretReferenceConfigurationSetting` type to represent a configuration setting that references a KeyVault Secret.
Added `FeatureFlagConfigurationSetting` type to represent a configuration setting that controls a feature flag.

## 1.1.1 (2020-10-05)

### Features

- Improve error message if Connection string secret has incorrect padding    #14140

## 1.1.0 (2020-09-08)

### Features

- Added match condition support for `set_read_only` method    #13276

## 1.0.1 (2020-08-10)

### Fixes

- Doc & Sample fixes

## 1.0.0 (2020-01-06)

### Features

- Add AAD auth support    #8924

### Breaking changes

- List_configuration_settings & list_revisions now take string key/label filter instead of keys/labels list   #9066

## 1.0.0b6 (2019-12-03)

### Features

- Add sync-token support    #8418

### Breaking changes

- Combine set_read_only & clear_read_only to be set_read_only(True/False)   #8453

## 1.0.0b5 (2019-10-30)

### Breaking changes

- etag and match_condition of delete_configuration_setting are now keyword argument only #8161

## 1.0.0b4 (2019-10-07)

- Add conditional operation support
- Add set_read_only and clear_read_only methods

## 1.0.0b3 (2019-09-09)

- New azure app configuration
