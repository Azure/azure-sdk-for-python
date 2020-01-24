# Release History

## 4.1.0b1 (Unreleased)
- Challenge authentication policy preserves request options
([#8999](https://github.com/Azure/azure-sdk-for-python/pull/8999))
- Updated `msrest` requirement to >=0.6.0
- Challenge authentication policy requires TLS
([#9457](https://github.com/Azure/azure-sdk-for-python/pull/9457))

## 4.0.0 (2019-10-31)
### Breaking changes:
- Moved optional parameters of two methods into kwargs (
[docs](https://azure.github.io/azure-sdk-for-python/ref/azure.keyvault.secrets.html)
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
through the `properties` property. See the updated [docs](https://azure.github.io/azure-sdk-for-python/ref/azure.keyvault.secrets.html)
for details.
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
[documentation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets/README.md)
and
[samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets/samples)
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
  [documentation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-secrets/README.md)
  , and the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md)
  for more information

### `azure-keyvault` features not implemented in this library
- Certificate management APIs
- National cloud support. This release supports public global cloud vaults,
    e.g. https://{vault-name}.vault.azure.net
