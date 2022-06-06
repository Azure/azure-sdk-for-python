# Release History

## 4.4.1 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed
- Port numbers are now preserved in the `vault_url` property of a `KeyVaultCertificateIdentifier`
  ([#24446](https://github.com/Azure/azure-sdk-for-python/issues/24446))

### Other Changes

## 4.4.0 (2022-03-28)

### Features Added
- Key Vault API version 7.3 is now the default
- Added support for multi-tenant authentication when using `azure-identity`
  1.8.0 or newer ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698))

### Bugs Fixed
- `KeyType` now ignores casing during declaration, which resolves a scenario where Key Vault
  keys created with non-standard casing could not be fetched with the SDK
  ([#22797](https://github.com/Azure/azure-sdk-for-python/issues/22797))

### Other Changes
- (From 4.4.0b3) Python 2.7 is no longer supported. Please use Python version 3.6 or later.
- Updated minimum `azure-core` version to 1.20.0
- (From 4.4.0b2) To support multi-tenant authentication, `get_token` calls during challenge
  authentication requests now pass in a `tenant_id` keyword argument
  ([#20698](https://github.com/Azure/azure-sdk-for-python/issues/20698)). See
  https://aka.ms/azsdk/python/identity/tokencredential for more details on how to integrate
  this parameter if `get_token` is implemented by a custom credential.

## 4.4.0b3 (2022-02-08)

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
### Changed
- Key Vault API version 7.2 is now the default
- Updated minimum `msrest` version to 0.6.21
- The `issuer_name` parameter for `CertificatePolicy` is now optional

### Added
- Added class `KeyVaultCertificateIdentifier` that parses out a full ID returned by Key Vault,
  so users can easily access the certificate's `name`, `vault_url`, and `version`.


## 4.2.1 (2020-09-08)
### Fixed
- Correct typing for paging methods
- Fixed incompatibility issues with API version 2016-10-01


## 4.2.0 (2020-08-11)
### Fixed
- Fixed an `AttributeError` during `get_certificate_version`
- `import_certificate` no longer raises `AttributeError` when the `policy`
  keyword argument isn't passed
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
- `CertificateClient` instances have a `close` method which closes opened
sockets. Used as a context manager, a `CertificateClient` closes opened sockets
on exit. ([#9906](https://github.com/Azure/azure-sdk-for-python/pull/9906))
- Pollers no longer sleep after operation completion
([#9991](https://github.com/Azure/azure-sdk-for-python/pull/9991))

## 4.0.1 (2020-02-11)
- `azure.keyvault.certificates` defines `__version__`
- Updated `msrest` requirement to >=0.6.0
- Challenge authentication policy requires TLS
([#9457](https://github.com/Azure/azure-sdk-for-python/pull/9457))
- Methods no longer raise the internal error `KeyVaultErrorException`
([#9690](https://github.com/Azure/azure-sdk-for-python/issues/9690))

## 4.0.0 (2020-01-08)
- First GA release

## 4.0.0b7 (2019-12-17)
- Challenge authentication policy preserves request options
([#8999](https://github.com/Azure/azure-sdk-for-python/pull/8999))
- Added `vault_url` property to `CertificateOperation`
- Removed `id`, `expires_on`, `not_before`, and `recover_level` properties from `CertificatePolicy`
- Removed `vault_url` property from `CertificateIssuer`
- Removed `vault_url` property from `IssuerProperties`


## 4.0.0b6 (2019-12-04)
- Updated `msrest` requirement to >=0.6.0
- Renamed `get_policy` to `get_certificate_policy`
- Renamed `update_policy` to `update_certificate_policy`
- Renamed `create_contacts` to `set_contacts`
- Renamed parameter `admin_details` of `create_issuer` and `update_issuer` to `admin_contacts`
- Renamed all `name` parameters to include the name of the object whose name we are referring to.
For example, the `name` parameter of `get_certificate` is now `certificate_name`
- Renamed `AdministratorDetails` to `AdministratorContact`
- Renamed the `ekus` property of `CertificatePolicy` to `enhanced_key_usage`
- Renamed the `curve` property of `CertificatePolicy` to `key_curve_name`
- Renamed the `san_upns` property of `CertificatePolicy` to `san_user_principal_names`
- Made the `subject_name` property of `CertificatePolicy` a kwarg and renamed it to `subject`
- Renamed the `deleted_date` property of `DeletedCertificate` to `deleted_on`
- Removed the `issuer_properties` property from `CertificateIssuer` and added the `provider` property
directly onto `CertificateIssuer`
- Renamed property `admin_details` of `CertificateIssuer` to `admin_contacts`
- Renamed the `thumbprint` property of `CertificateProperties` to `x509_thumbprint`
- Added `WellKnownIssuerNames` enum class that holds popular issuer names
- Renamed `SecretContentType` enum class to `CertificateContentType`


## 4.0.0b5 (2019-11-01)
- Removed redundant method `get_pending_certificate_signing_request()`. A pending CSR can be retrieved via `get_certificate_operation()`.
- Renamed the sync method `create_certificate` to `begin_create_certificate`
- Renamed `restore_certificate` to `restore_certificate_backup`
- Renamed `get_certificate` to `get_certificate_version`
- Renamed `get_certificate_with_policy` to `get_certificate`
- Renamed `list_certificates` to `list_properties_of_certificates`
- Renamed `list_properties_of_issuers` to `list_properties_of_issuers`
- Renamed `list_certificate_versions` to `list_properties_of_certificate_versions`
- `create_certificate` now has policy as a required parameter
- All optional positional parameters besides `version` have been moved to kwargs
- Renamed sync method `delete_certificate` to `begin_delete_certificate`
- Renamed sync method `recover_certificate` to `begin_recover_deleted_certificate`
- Renamed async method `recover_certificate` to `recover_deleted_certificate`
- The sync method `begin_delete_certificate` and async `delete_certificate` now return pollers that return a `DeletedCertificate`
- The sync method `begin_recover_deleted_certificate` and async `recover_deleted_certificate` now return pollers that return a `KeyVaultCertificate`

- Renamed enum `ActionType` to `CertificatePolicyAction`
- Renamed `Certificate` to `KeyVaultCertificate`
- Renamed `Contact` to `CertificateContact`
- Renamed `Issuer` to `CertificateIssuer`
- Renamed `CertificateError` to `CertificateOperationError`
- Renamed `expires` property of `CertificateProperties` and `CertificatePolicy` to `expires_on`
- Renamed `created` property of `CertificateProperties`, `CertificatePolicy`, and `CertificateIssuer` to `created_on`
- Renamed `updated` property of `CertificateProperties`, `CertificatePolicy`, and `CertificateIssuer` to `updated_on`
- The `vault_endpoint` parameter of `CertificateClient` has been renamed to `vault_url`
- The property `vault_endpoint` has been renamed to `vault_url` in all models
- `CertificatePolicy` now has a public class method `get_default` allowing users to get the default `CertificatePolicy`
- Logging can now be enabled properly on the client level

## 4.0.0b4 (2019-10-08)
- Enums `JsonWebKeyCurveName` and `JsonWebKeyType` have been renamed to `KeyCurveName` and `KeyType`, respectively.
- Both async and sync versions of `create_certificate` now return pollers that return the created `Certificate` if creation is successful,
and a `CertificateOperation` if not.
- `Certificate` now has attribute `properties`, which holds certain properties of the
certificate, such as `version`. This changes the shape of the `Certificate` type,
as certain properties of `Certificate` (such as `version`) have to be accessed
through the `properties` property.

- `update_certificate` has been renamed to `update_certificate_properties`
- The `vault_url` parameter of `CertificateClient` has been renamed to `vault_endpoint`
- The property `vault_url` has been renamed to `vault_endpoint` in all models

## 4.0.0b3 (2019-09-11)
Version 4.0.0b3 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Key Vault's certificates.

 This library is not a direct replacement for `azure-keyvault`. Applications
using that library would require code changes to use `azure-keyvault-certificates`.
This package's
[documentation](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates/README.md)
and
[samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates/samples)
demonstrate the new API.

### Breaking changes from `azure-keyvault`:
- Packages scoped by functionality
    - `azure-keyvault-certificates` contains a client for certificate operations
- Client instances are scoped to vaults (an instance interacts with one vault
only)
- Authentication using `azure-identity` credentials
  - see this package's
  [documentation](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/README.md)
  , and the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md)
  for more information

### New Features:
- Distributed tracing framework OpenCensus is now supported
- Asynchronous API supported on Python 3.5.3+
    - the `azure.keyvault.certificates.aio` namespace contains an async equivalent of
    the synchronous client in `azure.keyvault.certificates`
    - Async clients use [aiohttp](https://pypi.org/project/aiohttp/) for transport
    by default. See [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/README.md/#transport)
    for more information about using other transports.
