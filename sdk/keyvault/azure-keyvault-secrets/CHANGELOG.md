# Release History

## 4.5.0b1 (2022-06-07)

### Bugs Fixed
- Port numbers are now preserved in the `vault_url` property of a `KeyVaultSecretIdentifier`
  ([#24446](https://github.com/Azure/azure-sdk-for-python/issues/24446))

## 4.4.0 (2022-03-28)

### Features Added
- Key Vault API version 7.3 is now the default
- Added support for multi-tenant authentication when using `azure-identity`
  1.8.0 or newer ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698))
- (From 4.4.0b3) Added `managed` property to SecretProperties

### Other Changes
- (From 4.4.0b3) Python 2.7 is no longer supported. Please use Python version 3.6 or later.
- Updated minimum `azure-core` version to 1.20.0
- (From 4.4.0b2) To support multi-tenant authentication, `get_token` calls during challenge
  authentication requests now pass in a `tenant_id` keyword argument
  ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698)). See
  https://aka.ms/azsdk/python/identity/tokencredential for more details on how to integrate
  this parameter if `get_token` is implemented by a custom credential.

## 4.4.0b3 (2022-02-08)

### Features Added
- Added `managed` property to SecretProperties

### Other Changes
- Python 2.7 is no longer supported. Please use Python version 3.6 or later.
- (From 4.4.0b2) To support multi-tenant authentication, `get_token` calls during challenge
  authentication requests now pass in a `tenant_id` keyword argument
  ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698))

## 4.4.0b2 (2021-11-11)

### Features Added
- Added support for multi-tenant authentication when using `azure-identity` 1.7.1 or newer
  ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698))

### Other Changes
- Updated minimum `azure-core` version to 1.15.0

## 4.4.0b1 (2021-09-09)

### Features Added
- Key Vault API version 7.3-preview is now the default

### Other Changes
- Updated type hints to fix mypy errors
  ([#19158](https://github.com/Azure/azure-sdk-for-python/issues/19158))

## 4.3.0 (2021-06-22)
This is the last version to support Python 3.5. The next version will require Python 2.7 or 3.6+.
### Fixed
- Correct typing for async paging methods

### Changed
- Key Vault API version 7.2 is now the default
- Updated minimum `msrest` version to 0.6.21

### Added
- Added class `KeyVaultSecretIdentifier` that parses out a full ID returned by Key Vault,
  so users can easily access the secret's `name`, `vault_url`, and `version`.

## 4.2.0 (2020-08-11)
### Fixed
- Values of `x-ms-keyvault-region` and `x-ms-keyvault-service-version` headers
  are no longer redacted in logging output

### Changed
- Key Vault API version 7.1 is now the default
- Updated minimum `azure-core` version to 1.7.0

### Added
- At construction, clients accept a `CustomHookPolicy` through the optional
  keyword argument `custom_hook_policy`
- All client requests include a unique ID in the header `x-ms-client-request-id`
- Dependency on `azure-common` for multiapi support

## 4.2.0b1 (2020-03-10)
- Support for Key Vault API version 7.1-preview
([#10124](https://github.com/Azure/azure-sdk-for-python/pull/10124))
  - Added `recoverable_days` to `CertificateProperties`
  - Added `ApiVersion` enum identifying Key Vault versions supported by this package

## 4.1.0 (2020-03-10)
- `SecretClient` instances have a `close` method which closes opened sockets.
Used as a context manager, a `SecretClient` closes opened sockets on exit.
([#9906](https://github.com/Azure/azure-sdk-for-python/pull/9906))
- Pollers no longer sleep after operation completion
([#9991](https://github.com/Azure/azure-sdk-for-python/pull/9991))

## 4.0.1 (2020-02-11)
- `azure.keyvault.secrets` defines `__version__`
- Challenge authentication policy preserves request options
([#8999](https://github.com/Azure/azure-sdk-for-python/pull/8999))
- Updated `msrest` requirement to >=0.6.0
- Challenge authentication policy requires TLS
([#9457](https://github.com/Azure/azure-sdk-for-python/pull/9457))
- Methods no longer raise the internal error `KeyVaultErrorException`
([#9690](https://github.com/Azure/azure-sdk-for-python/issues/9690))

## 4.0.0 (2019-10-31)
### Breaking changes:
- Moved optional parameters of two methods into kwargs (
[docs](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-keyvault-secrets/4.0.0/azure.keyvault.secrets.html)
detail the new keyword arguments):
  - `set_secret` now has positional parameters `name` and `value`
  - `update_secret_properties` now has positional parameters `name` and
    (optional) `version`
- Renamed `list_secrets` to `list_properties_of_secrets`
- Renamed `list_secret_versions` to `list_properties_of_secret_versions`
- Renamed sync method `delete_secret` to `begin_delete_secret`
- The sync method `begin_delete_secret` and async `delete_secret` now return pollers that return a `DeletedSecret`
- Renamed `Secret` to `KeyVaultSecret`
- `KeyVaultSecret`  properties `created`, `expires`, and `updated` renamed to `created_on`,
`expires_on`, and `updated_on`
- The `vault_endpoint` parameter of `SecretClient` has been renamed to `vault_url`
- The property `vault_endpoint` has been renamed to `vault_url` in all models


## 4.0.0b4 (2019-10-08)
### Breaking changes:
- `Secret` now has attribute `properties`, which holds certain properties of the
secret, such as `version`. This changes the shape of the returned `Secret` type,
as certain properties of `Secret` (such as `version`) have to be accessed
through the `properties` property.

- `update_secret` has been renamed to `update_secret_properties`
- The `vault_url` parameter of `SecretClient` has been renamed to `vault_endpoint`
- The property `vault_url` has been renamed to `vault_endpoint` in all models

### Fixes and improvements
- `list_secrets` and `list_secret_versions` return the correct type

## 4.0.0b3 (2019-09-11)
This release includes only internal changes.

## 4.0.0b2 (2019-08-06)
### Breaking changes:
- Removed `azure.core.Configuration` from the public API in preparation for a
revamped configuration API. Static `create_config` methods have been renamed
`_create_config`, and will be removed in a future release.
- This version of the library requires `azure-core` 1.0.0b2
  - If you later want to revert to a version requiring azure-core 1.0.0b1,
  of this or another Azure SDK library, you must explicitly install azure-core
  1.0.0b1 as well. For example:
  `pip install azure-core==1.0.0b1 azure-keyvault-secrets==4.0.0b1`

### New features:
- Distributed tracing framework OpenCensus is now supported
- Added support for HTTP challenge based authentication, allowing clients to
interact with vaults in sovereign clouds.

## 4.0.0b1 (2019-06-28)
Version 4.0.0b1 is the first preview of our efforts to create a user-friendly
and Pythonic client library for Azure Key Vault. For more information about
preview releases of other Azure SDK libraries, please visit
https://aka.ms/azure-sdk-preview1-python.

This library is not a direct replacement for `azure-keyvault`. Applications
using that library would require code changes to use `azure-keyvault-secrets`.
This package's
[documentation](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets/README.md)
and
[samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets/samples)
demonstrate the new API.

### Major changes from `azure-keyvault`
- Packages scoped by functionality
    - `azure-keyvault-secrets` contains a client for secret operations,
    `azure-keyvault-keys` contains a client for key operations
- Client instances are scoped to vaults (an instance interacts with one vault
only)
- Asynchronous API supported on Python 3.5.3+
    - the `azure.keyvault.secrets.aio` namespace contains an async equivalent of
    the synchronous client in `azure.keyvault.secrets`
- Authentication using `azure-identity` credentials
  - see this package's
  [documentation](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets/README.md)
  , and the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md)
  for more information

### `azure-keyvault` features not implemented in this library
- Certificate management APIs
- National cloud support. This release supports public global cloud vaults,
    e.g. https://{vault-name}.vault.azure.net
