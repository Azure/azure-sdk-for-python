# Release History

## 4.6.0b2 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 4.6.0b1 (2022-06-07)

### Bugs Fixed
- If a key's ID contains a port number, this port will now be preserved in the vault URL of a
  `CryptographyClient` instance created from this key
  ([#24446](https://github.com/Azure/azure-sdk-for-python/issues/24446))
  - Port numbers are now preserved in the `vault_url` property of a `KeyVaultKeyIdentifier`

## 4.5.1 (2022-04-18)

### Bugs Fixed
- Fixed error that could occur when fetching a key rotation policy that has no defined
  `lifetime_actions`.

## 4.5.0 (2022-03-28)

### Features Added
- Key Vault API version 7.3 is now the default
- Added support for multi-tenant authentication when using `azure-identity`
  1.8.0 or newer ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698))
- (From 4.5.0b1) `KeyClient` has a `get_random_bytes` method for getting a requested number of
  random bytes from a managed HSM
- (From 4.5.0b2) Added support for secure key release from a Managed HSM
  ([#19588](https://github.com/Azure/azure-sdk-for-python/issues/19588))
  - Added `release_key` method to `KeyClient` for releasing the private component of a key
  - Added `exportable` and `release_policy` keyword-only arguments to key creation and import
    methods
  - Added `KeyExportEncryptionAlgorithm` enum for specifying an encryption algorithm to be used
    in key release
- (From 4.5.0b4) Added `KeyClient.get_cryptography_client`, which provides a simple way to
  create a `CryptographyClient` for a key, given its name and optionally a version
  ([#20621](https://github.com/Azure/azure-sdk-for-python/issues/20621))
- (From 4.5.0b4) Added support for automated and on-demand key rotation in Azure Key Vault
  ([#19840](https://github.com/Azure/azure-sdk-for-python/issues/19840))
  - Added `KeyClient.rotate_key` to rotate a key on-demand
  - Added `KeyClient.update_key_rotation_policy` to update a key's automated rotation policy
- (From 4.5.0b6) Added `immutable` keyword-only argument and property to `KeyReleasePolicy` to
  support immutable release policies. Once a release policy is marked as immutable, it can no
  longer be modified.

### Breaking Changes
> These changes do not impact the API of stable versions such as 4.4.0.
> Only code written against a beta version such as 4.5.0b1 may be affected.
- `KeyClient.update_key_rotation_policy` accepts a required `policy` argument
  ([#22981](https://github.com/Azure/azure-sdk-for-python/issues/22981))
- The optional `version` parameter in `KeyClient.release_key` is now a keyword-only argument
  ([#22981](https://github.com/Azure/azure-sdk-for-python/issues/22981))
- Renamed the `name` parameter in `KeyClient.get_key_rotation_policy` and
  `KeyClient.update_key_rotation_policy` to `key_name`
  ([#22981](https://github.com/Azure/azure-sdk-for-python/issues/22981))
- Enum values in `azure-keyvault-keys` are now uniformly lower-cased
  ([#22981](https://github.com/Azure/azure-sdk-for-python/issues/22981))

### Bugs Fixed
- `KeyType` now ignores casing during declaration, which resolves a scenario where Key Vault
  keys created with non-standard casing could not be fetched with the SDK
  ([#22797](https://github.com/Azure/azure-sdk-for-python/issues/22797))

### Other Changes
- (From 4.5.0b6) Python 2.7 is no longer supported. Please use Python version 3.6 or later.
- (From 4.5.0b6) Updated minimum `azure-core` version to 1.20.0
- (From 4.5.0b3) Updated type hints to fix mypy errors
  ([#19158](https://github.com/Azure/azure-sdk-for-python/issues/19158))
- (From 4.5.0b4) `CryptographyClient` no longer requires a key version when providing a key ID to its constructor
  (though providing a version is still recommended)
- (From 4.5.0b5) To support multi-tenant authentication, `get_token` calls during challenge
  authentication requests now pass in a `tenant_id` keyword argument
  ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698)). See
  https://aka.ms/azsdk/python/identity/tokencredential for more details on how to integrate
  this parameter if `get_token` is implemented by a custom credential.
- (From 4.5.0b6) Updated type hints for `KeyProperties` model's `managed`, `exportable`, and
  `release_policy` properties ([#22368](https://github.com/Azure/azure-sdk-for-python/pull/22368))

## 4.5.0b6 (2022-02-08)

### Features Added
- Added `immutable` keyword-only argument and property to `KeyReleasePolicy` to support immutable
  release policies. Once a release policy is marked as immutable, it can no longer be modified.

### Breaking Changes
> These changes do not impact the API of stable versions such as 4.4.0.
> Only code written against a beta version such as 4.5.0b1 may be affected.
- Renamed the required argument `data` in `KeyReleasePolicy`'s constructor to
  `encoded_policy`

### Other Changes
- Python 2.7 is no longer supported. Please use Python version 3.6 or later.
- Updated minimum `azure-core` version to 1.20.0
- Updated type hints for `KeyProperties` model's `managed`, `exportable`, and `release_policy`
  properties ([#22368](https://github.com/Azure/azure-sdk-for-python/pull/22368))
- (From 4.5.0b5) To support multi-tenant authentication, `get_token` calls during challenge
  authentication requests now pass in a `tenant_id` keyword argument
  ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698))

## 4.5.0b5 (2021-11-11)

### Features Added
- Added support for multi-tenant authentication when using `azure-identity` 1.7.1 or newer
  ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698))

### Breaking Changes
> These changes do not impact the API of stable versions such as 4.4.0.
> Only code written against a beta version such as 4.5.0b1 may be affected.
- `KeyClient.get_random_bytes` now returns bytes instead of RandomBytes. The RandomBytes class
  has been removed
- Renamed the `version` keyword-only argument in `KeyClient.get_cryptography_client` to
  `key_version`
- Renamed `KeyReleasePolicy.data` to `KeyReleasePolicy.encoded_policy`
- Renamed the `target` parameter in `KeyClient.release_key` to `target_attestation_token`

### Other Changes
- Updated minimum `azure-core` version to 1.15.0

## 4.5.0b4 (2021-10-07)

### Features Added
- Added `KeyClient.get_cryptography_client`, which provides a simple way to create a
  `CryptographyClient` for a key, given its name and optionally a version
  ([#20621](https://github.com/Azure/azure-sdk-for-python/issues/20621))
- Added support for automated and on-demand key rotation in Azure Key Vault
  ([#19840](https://github.com/Azure/azure-sdk-for-python/issues/19840))
  - Added `KeyClient.rotate_key` to rotate a key on-demand
  - Added `KeyClient.update_key_rotation_policy` to update a key's automated rotation policy

### Other Changes
- `CryptographyClient` no longer requires a key version when providing a key ID to its constructor
  (though providing a version is still recommended)

## 4.5.0b3 (2021-09-09)

### Other Changes
- Updated type hints to fix mypy errors
  ([#19158](https://github.com/Azure/azure-sdk-for-python/issues/19158))

## 4.5.0b2 (2021-08-10)

### Features Added
- Added support for secure key release from a Managed HSM
  ([#19588](https://github.com/Azure/azure-sdk-for-python/issues/19588))
  - Added `release_key` method to `KeyClient` for releasing the private component of a key
  - Added `exportable` and `release_policy` keyword-only arguments to key creation and import
    methods
  - Added `KeyExportEncryptionAlgorithm` enum for specifying an encryption algorithm to be used
    in key release

### Breaking Changes
> These changes do not impact the API of stable versions such as 4.4.0.
> Only code written against a beta version such as 4.5.0b1 may be affected.
- `KeyClient.get_random_bytes` now returns a `RandomBytes` model with bytes in a `value`
  property, rather than returning the bytes directly
  ([#19895](https://github.com/Azure/azure-sdk-for-python/issues/19895))

## 4.5.0b1 (2021-07-08)
Beginning with this release, this library requires Python 2.7 or 3.6+.

### Features Added
- Key Vault API version 7.3-preview is now the default
- `KeyClient` has a `get_random_bytes` method for getting a requested number of random
  bytes from a managed HSM

## 4.4.0 (2021-06-22)
This is the last version to support Python 3.5. The next version will require Python 2.7 or 3.6+.
### Changed
- Key Vault API version 7.2 is now the default
- (From 4.4.0b1) Updated minimum `msrest` version to 0.6.21

### Added
- `KeyClient` has a `create_oct_key` method for creating symmetric keys
- `KeyClient`'s `create_key` and `create_rsa_key` methods now accept a `public_exponent`
  keyword-only argument ([#18016](https://github.com/Azure/azure-sdk-for-python/issues/18016))
- (From 4.4.0b1) Added support for Key Vault API version 7.2
  ([#16566](https://github.com/Azure/azure-sdk-for-python/pull/16566))
  - Added `oct_hsm` to `KeyType`
  - Added 128-, 192-, and 256-bit AES-GCM, AES-CBC, and AES-CBCPAD encryption
    algorithms to `EncryptionAlgorithm`
  - Added 128- and 192-bit AES-KW key wrapping algorithms to `KeyWrapAlgorithm`
  - `CryptographyClient`'s `encrypt` method accepts `iv` and
    `additional_authenticated_data` keyword arguments
  - `CryptographyClient`'s `decrypt` method accepts `iv`,
    `additional_authenticated_data`, and `authentication_tag` keyword arguments
  - Added `iv`, `aad`, and `tag` properties to `EncryptResult`
- (From 4.4.0b3) `CryptographyClient` will perform all operations locally if initialized with
  the `.from_jwk` factory method
  ([#16565](https://github.com/Azure/azure-sdk-for-python/pull/16565))
- (From 4.4.0b3) Added requirement for `six`>=1.12.0
- (From 4.4.0b4) `CryptographyClient` can perform AES-CBCPAD encryption and decryption locally
  ([#17762](https://github.com/Azure/azure-sdk-for-python/pull/17762))

### Breaking Changes
> These changes do not impact the API of stable versions such as 4.3.1.
> Only code written against a beta version such as 4.4.0b1 may be affected.
- `parse_key_vault_key_id` and `KeyVaultResourceId` have been replaced by a
  `KeyVaultKeyIdentifier` class, which can be initialized with a key ID

## 4.4.0b4 (2021-04-06)
### Added
- `CryptographyClient` can perform AES-CBCPAD encryption and decryption locally
  ([#17762](https://github.com/Azure/azure-sdk-for-python/pull/17762))

## 4.4.0b3 (2021-03-11)
### Added
- `CryptographyClient` will perform all operations locally if initialized with
  the `.from_jwk` factory method
  ([#16565](https://github.com/Azure/azure-sdk-for-python/pull/16565))
- Added requirement for six>=1.12.0

## 4.4.0b2 (2021-02-10)
### Fixed
- API versions older than 7.2-preview no longer raise `ImportError` when
  performing async operations ([#16680](https://github.com/Azure/azure-sdk-for-python/pull/16680))

## 4.4.0b1 (2021-02-10)
### Changed
- Key Vault API version 7.2-preview is now the default
- Updated msrest requirement to >=0.6.21

### Added
- Support for Key Vault API version 7.2-preview
  ([#16566](https://github.com/Azure/azure-sdk-for-python/pull/16566))
  - Added `oct_hsm` to `KeyType`
  - Added 128-, 192-, and 256-bit AES-GCM, AES-CBC, and AES-CBCPAD encryption
    algorithms to `EncryptionAlgorithm`
  - Added 128- and 192-bit AES-KW key wrapping algorithms to `KeyWrapAlgorithm`
  - `CryptographyClient`'s `encrypt` method accepts `iv` and
    `additional_authenticated_data` keyword arguments
  - `CryptographyClient`'s `decrypt` method accepts `iv`,
    `additional_authenticated_data`, and `authentication_tag` keyword arguments
  - Added `iv`, `aad`, and `tag` properties to `EncryptResult`
- Added method `parse_key_vault_key_id` that parses out a full ID returned by
Key Vault, so users can easily access the key's `name`, `vault_url`, and `version`.

## 4.3.1 (2020-12-03)
### Fixed
- `CryptographyClient` operations no longer raise `AttributeError` when
  the client was constructed with a key ID
  ([#15608](https://github.com/Azure/azure-sdk-for-python/issues/15608))

## 4.3.0 (2020-10-06)
### Changed
- `CryptographyClient` can perform decrypt and sign operations locally
  ([#9754](https://github.com/Azure/azure-sdk-for-python/issues/9754))

### Fixed
- Correct typing for async paging methods

## 4.2.0 (2020-08-11)
### Fixed
- Values of `x-ms-keyvault-region` and `x-ms-keyvault-service-version` headers
  are no longer redacted in logging output
- `CryptographyClient` will no longer perform encrypt or wrap operations when
  its key has expired or is not yet valid

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
  - Added `import_key` to `KeyOperation`
  - Added `recoverable_days` to `CertificateProperties`
  - Added `ApiVersion` enum identifying Key Vault versions supported by this package

## 4.1.0 (2020-03-10)
- `KeyClient` instances have a `close` method which closes opened sockets. Used
as a context manager, a `KeyClient` closes opened sockets on exit.
([#9906](https://github.com/Azure/azure-sdk-for-python/pull/9906))
- Pollers no longer sleep after operation completion
([#9991](https://github.com/Azure/azure-sdk-for-python/pull/9991))

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

## 4.0.0 (2019-10-31)
### Breaking changes:
- Removed `KeyClient.get_cryptography_client()` and `CryptographyClient.get_key()`
- Moved the optional parameters of several methods into kwargs (
[docs](https://azuresdkdocs.blob.core.windows.net/$web/python/azure-keyvault-keys/4.0.0/index.html)
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
through the `properties` property.

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
[azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md/#transport)
for more information about using other transports.

## 4.0.0b1 (2019-06-28)
Version 4.0.0b1 is the first preview of our efforts to create a user-friendly
and Pythonic client library for Azure Key Vault. For more information about
preview releases of other Azure SDK libraries, please visit
https://aka.ms/azure-sdk-preview1-python.

This library is not a direct replacement for `azure-keyvault`. Applications
using that library would require code changes to use `azure-keyvault-keys`.
This package's
[documentation](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/README.md)
and
[samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/samples)
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
  [documentation](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/README.md)
  , and the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md)
  for more information

### `azure-keyvault` features not implemented in this release
- Certificate management APIs
- Cryptographic operations, e.g. sign, un/wrap_key, verify, en- and
decrypt
- National cloud support. This release supports public global cloud vaults,
    e.g. https://{vault-name}.vault.azure.net
