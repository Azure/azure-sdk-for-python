# Release History

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
through the `properties` property. See the updated [docs](https://azure.github.io/azure-sdk-for-python/ref/azure.keyvault.certificates.html)
for details.
- `update_certificate` has been renamed to `update_certificate_properties`
- The `vault_url` parameter of `CertificateClient` has been renamed to `vault_endpoint`
- The property `vault_url` has been renamed to `vault_endpoint` in all models

## 4.0.0b3 (2019-09-11)
Version 4.0.0b3 is the first preview of our efforts to create a user-friendly and Pythonic client library for Azure Key Vault's certificates.

 This library is not a direct replacement for `azure-keyvault`. Applications
using that library would require code changes to use `azure-keyvault-certificates`.
This package's
[documentation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates/README.md)
and
[samples](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-certificates/samples)
demonstrate the new API.

### Breaking changes from `azure-keyvault`:
- Packages scoped by functionality
    - `azure-keyvault-certificates` contains a client for certificate operations
- Client instances are scoped to vaults (an instance interacts with one vault
only)
- Authentication using `azure-identity` credentials
  - see this package's
  [documentation](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys/README.md)
  , and the
  [Azure Identity documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/identity/azure-identity/README.md)
  for more information

### New Features:
- Distributed tracing framework OpenCensus is now supported
- Asynchronous API supported on Python 3.5.3+
    - the `azure.keyvault.certificates.aio` namespace contains an async equivalent of
    the synchronous client in `azure.keyvault.certificates`
    - Async clients use [aiohttp](https://pypi.org/project/aiohttp/) for transport
    by default. See [azure-core documentation](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/README.md/#transport)
    for more information about using other transports.
