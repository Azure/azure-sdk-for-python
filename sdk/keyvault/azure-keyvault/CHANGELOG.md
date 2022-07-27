# Release History

## 4.2.0 (2022-03-29)
**Disclaimer**

This package and the `azure.keyvault` namespace does not contain code anymore. This package now installs three sub-packages instead:

* [azure-keyvault-certificates](https://pypi.org/project/azure-keyvault-certificates/)
* [azure-keyvault-keys](https://pypi.org/project/azure-keyvault-keys/)
* [azure-keyvault-secrets](https://pypi.org/project/azure-keyvault-secrets/)

All code needs to be adapted to use the new namespaces. See individual package readmes for details.

## Other Changes
- Python 2.7 is no longer supported. Please use Python version 3.6 or later.

## 4.1.0 (2020-04-10)
**Disclaimer**

This package and the `azure.keyvault` namespace does not contain code anymore. This package now installs three sub-packages instead:

* [azure-keyvault-certificates](https://pypi.org/project/azure-keyvault-certificates/)
* [azure-keyvault-keys](https://pypi.org/project/azure-keyvault-keys/)
* [azure-keyvault-secrets](https://pypi.org/project/azure-keyvault-secrets/)

All code needs to be adapted to use the new namespaces. See individual package readmes for details.

 
## 4.0.0 (2019-10-31)

**Disclaimer**

This package and the `azure.keyvault` namespace does not contain code anymore. This package now installs three sub-packages instead:

* azure-keyvault-keys
* azure-keyvault-secrets

Certificates scenarios are in preview with the additional package `azure-keyvault-certificates`.

All code needs to be adapted to use the new namespaces. See individual package readme for details.

## 1.1.0 (2018-08-07)

* Adding support for multi-api and API profiles

## 1.0.0 (2018-06-27)

* Moving azure-keyvault to stable API version 7.0
* Adding support for EC certificate create and import
* Renaming curve SECP256K1 and algorithm ECDSA256 to P-256K and ES256K respectively

## 1.0.0b1 (2018-04-10)

* Upgraded to autorest 3.0 generated code

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes.

- Model signatures now use only keyword-argument syntax. All positional arguments must be re-written as keyword-arguments.
  To keep auto-completion in most cases, models are now generated for Python 2 and Python 3. Python 3 uses the "*" syntax for keyword-only arguments.
- Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to improve the behavior when unrecognized enum values are encountered.
  While this is not a breaking change, the distinctions are important, and are documented here:
  https://docs.python.org/3/library/enum.html#others
  At a glance:

  - "is" should not be used at all.
  - "format" will return the string value, where "%s" string formatting will return `NameOfEnum.stringvalue`. Format syntax should be preferred.

- New Long Running Operation:

  - Return type changes from `msrestazure.azure_operation.AzureOperationPoller` to `msrest.polling.LROPoller`. External API is the same.
  - Return type is now **always** a `msrest.polling.LROPoller`, regardless of the optional parameters used.
  - The behavior has changed when using `raw=True`. Instead of returning the initial call result as `ClientRawResponse`,
    without polling, now this returns an LROPoller. After polling, the final resource will be returned as a `ClientRawResponse`.
  - New `polling` parameter. The default behavior is `Polling=True` which will poll using ARM algorithm. When `Polling=False`,
    the response of the initial call will be returned without polling.
  - `polling` parameter accepts instances of subclasses of `msrest.polling.PollingMethod`.
  - `add_done_callback` will no longer raise if called after polling is finished, but will instead execute the callback right away.


## 1.0.0a2 (2018-03-28)

* Upgrading to API version 7.0-preview
* Adding elliptic curve key support
* Adding managed storage account key backup, restore and soft delete support
* Breaking update to managed storage account SasDefinition creation
* Adding certificate backup and restore support
* Adding certificate transparency

## 1.0.0a1 (2018-01-25)

* Added message encryption support for message encryption enabled vaults

## 0.3.7 (2017-09-22)

* Workaround for Azure Stack ADFS authentication issue https://github.com/Azure/azure-cli/issues/4448

## 0.3.6 (2017-08-16)

* Updated KeyVaultClient to accept both KeyVaultAuthentication and azure.common.credentials instances for authentication

## 0.3.5 (2017-06-23)

* Fix: https://github.com/Azure/azure-sdk-for-python/issues/1159
* KeyVaultId refactoring
  - adding object specific id classes to make usage more uniform with other key vault SDKs
  - added storage account id and storage sas definition id parsing and formatting

## 0.3.4 (2017-06-07)

* Adding Preview Features
  - Managed Storage Account keys for managing storage credentials and provisioning SAS tokens
  - Key Vault "Soft Delete" allowing for recovery of deleted keys, secrets and certificates
  - Secret Backup and Restore for secret recovery and migration

## 0.3.3 (2017-05-10)

* Reverting to 0.3.0, since behavior of 0.3.2 is not satisfying either.

## 0.3.2 (2017-05-09)

* Fix critical regression on 0.3.1 (#1157)
* Now the client respects 'REQUESTS_CA_BUNDLE' and 'CURL_CA_BUNDLE'

## 0.3.1 (2017-05-09)

* Support for REQUESTS_CA_BUNDLE (#1154)

## 0.3.0 (2017-05-08)

* Moving KeyVaultClient class to the azure.keyvault namespace
* Moving model classes to the azure.keyvault.models namespace
* Deprecating 'generated' namespaces azure.keyvault.generated and azure.keyvault.generated.models
* Exposed KeyVaultId class through azure.keyvault namespace
* Moving identifier parsing methods to static methods on KeyVaultId class
* Removing convenience overridden methods from KeyVaultClient
  - update_key(self, key_identifier, ...
  - get_key(self, key_identifier, ...
  - encrypt(self, key_identifier, ...
  - decrypt(self, key_identifier, ...
  - sign(self, key_identifier, ...
  - verify(self, key_identifier, ...
  - wrap_key(self, key_identifier, ...
  - unwrap_key(self, key_identifier, ...
  - update_secret(self, secret_identifier, ...
  - get_secret(self, secret_identifier, ...
  - get_certificate(self, certificate_identifier, ...

## 0.2.0 (2017-04-09)

**Bugfixes**

- Fix possible deserialization error, but updating from list<enumtype> to list<str> when applicable

**Notes**

- This wheel package is now built with the azure wheel extension

## 0.1.0 (2016-12-29)

* Initial Release
