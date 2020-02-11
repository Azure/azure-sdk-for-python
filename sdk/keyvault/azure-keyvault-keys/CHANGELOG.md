# Release History

## 4.0.1 (2020-02-11)
- `azure.keyvault.keys` defines `__version__`
- Challenge authentication policy preserves request options
([#8999](https://github.com/Azure/azure-sdk-for-python/pull/8999))
- Updated `msrest` requirement to >=0.6.0
- Challenge authentication policy requires TLS
([#9457](https://github.com/Azure/azure-sdk-for-python/pull/9457))
- Methods no longer raise the internal error `KeyVaultErrorException`
([#9690](https://github.com/Azure/azure-sdk-for-python/issues/9690))
- Fix `AttributeError` in async CryptographyClient when verifying signatures remotely
([#9734](https://github.com/Azure/azure-sdk-for-python/pull/9734))

## 2019-10-31 4.0.0
### Breaking changes:
- Removed `KeyClient.get_cryptography_client()` and `CryptographyClient.get_key()`
- Moved the optional parameters of several methods into kwargs (
[docs](https://azure.github.io/azure-sdk-for-python/ref/azure.keyvault.keys.html)
detail the new keyword arguments):
  - `create_key` now has positional parameters `name` and `key_type`
  - `create_ec_key` and `create_rsa_key` now have one positional parameter, `name`
  - `update_key_properties` now has two positional parameters, `name` and
     (optional) `version`
  - `import_key` now has positional parameters `name` and `key`
- `CryptographyClient` operations return class instances instead of tuples and renamed the following
properties
    - Renamed the `decrypted_bytes` property of `DecryptResult` to `plaintext`
    - Renamed the `unwrapped_bytes` property of `UnwrapResult` to `key`
    - Renamed the `result` property of `VerifyResult` to `is_valid`
- Renamed the `UnwrapKeyResult` and `WrapKeyResult` classes to `UnwrapResult` and `WrapResult`
- Renamed `list_keys` to `list_properties_of_keys`
- Renamed `list_key_versions` to `list_properties_of_key_versions`
- Renamed sync method `delete_key` to `begin_delete_key`
- The sync method `begin_delete_key` and async `delete_key` now return pollers that return a `DeletedKey`
- Renamed `Key` to `KeyVaultKey`
- `KeyVaultKey` properties `created`, `expires`, and `updated` renamed to `created_on`,
`expires_on`, and `updated_on`
- The `vault_endpoint` parameter of `KeyClient` has been renamed to `vault_url`
- The property `vault_endpoint` has been renamed to `vault_url` in all models

### New features:
- Now all `CryptographyClient` returns include `key_id` and `algorithm` properties


## 4.0.0b4 (2019-10-08)
- Enums `JsonWebKeyCurveName`, `JsonWebKeyOperation`, and `JsonWebKeyType` have
been renamed to `KeyCurveName`, `KeyOperation`, and `KeyType`, respectively.
- `Key` now has attribute `properties`, which holds certain properties of the
key, such as `version`. This changes the shape of the returned `Key` type,
as certain properties of `Key` (such as `version`) have to be accessed
through the `properties` property. See the updated [docs](https://azure.github.io/azure-sdk-for-python/ref/azure.keyvault.keys.html)
for details.
- `update_key` has been renamed to `update_key_properties`
- The `vault_url` parameter of `KeyClient` has been renamed to `vault_endpoint`
- The property `vault_url` has been renamed to `vault_endpoint` in all models

### Fixes and improvements:
- The `key` argument to `import_key` should be an instance of `azure.keyvault.keys.JsonWebKey`
([#7590](https://github.com/Azure/azure-sdk-for-python/pull/7590))


## 4.0.0b3 (2019-09-11)
### Breaking changes:
- `CryptographyClient` methods `wrap` and `unwrap` are renamed `wrap_key` and
`unwrap_key`, respectively.

### New features:
- `CryptographyClient` performs encrypt, verify and wrap operations locally
when its key's public material is available (i.e., when it has keys/get
permission).

## 4.0.0b2 (2019-08-06)
### Breaking changes:
- Removed `azure.core.Configuration` from the public API in preparation for a
revamped configuration API. Static `create_config` methods have been renamed
`_create_config`, and will be removed in a future release.
- Removed `wrap_key` and `unwrap_key` from `KeyClient`. These are now available
through `CryptographyClient`.
- This version of the library requires `azure-core` 1.0.0b2
  - If you later want to revert to a version requiring azure-core 1.0.0b1,
  of this or another Azure SDK library, you must explicitly install azure-core
  1.0.0b1 as well. For example:
  `pip install azure-core==1.0.0b1 azure-keyvault-keys==4.0.0b1`

### New features:
- Added `CryptographyClient`, a client for performing cryptographic operations
(encrypt/decrypt, wrap/unwrap, sign/verify) with a key.
- Distributed tracing framework OpenCensus is now supported
- Added support for HTTP challenge based authentication, allowing clients to
interact with vaults in sovereign clouds.

### Other changes:
- Async clients use [aiohttp](https://pypi.org/project/aiohttp/) for transport
by default. See
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md/#transport)
for more information about using other transports.

## 4.0.0b1 (2019-06-28)
Version 4.0.0b1 is the first preview of our efforts to create a user-friendly
and Pythonic client library for Azure Key Vault. For more information about
preview releases of other Azure SDK libraries, please visit
https://aka.ms/azure-sdk-preview1-python.

This library is not a direct replacement for `azure-keyvault`. Applications
using that library would require code changes to use `azure-keyvault-keys`.
This package's
[documentation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/README.md)
and
[samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/samples)
demonstrate the new API.

### Major changes from `azure-keyvault`
- Packages scoped by functionality
    - `azure-keyvault-keys` contains a client for key operations,
    `azure-keyvault-secrets` contains a client for secret operations
- Client instances are scoped to vaults (an instance interacts with one vault
only)
- Asynchronous API supported on Python 3.5.3+
    - the `azure.keyvault.keys.aio` namespace contains an async equivalent of
    the synchronous client in `azure.keyvault.keys`
- Authentication using `azure-identity` credentials
  - see this package's
  [documentation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/README.md)
  , and the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md)
  for more information

### `azure-keyvault` features not implemented in this release
- Certificate management APIs
- Cryptographic operations, e.g. sign, un/wrap_key, verify, en- and
decrypt
- National cloud support. This release supports public global cloud vaults,
    e.g. https://{vault-name}.vault.azure.net
