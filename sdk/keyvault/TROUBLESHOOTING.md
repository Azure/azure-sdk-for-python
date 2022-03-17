# Troubleshooting guide for the Azure Key Vault SDKs

The Azure Key Vault SDKs for Python use a common HTTP pipeline and authentication to create, update, and delete secrets,
keys, and certificates in Key Vault and Managed HSM. This troubleshooting guide contains steps for diagnosing issues
common to these SDKs.

For package-specific troubleshooting guides, see any of the following:

* [Troubleshooting guide for the Azure Key Vault Administration SDK][kv_admin_troubleshooting]
* [Troubleshooting guide for the Azure Key Vault Certificates SDK][kv_certs_troubleshooting]
* [Troubleshooting guide for the Azure Key Vault Keys SDK][kv_keys_troubleshooting]
* [Troubleshooting guide for the Azure Key Vault Secrets SDK][kv_secrets_troubleshooting]

## Table of Contents

* [Authentication issues](#authentication-issues)
  * [HTTP 401 errors](#http-401-errors)
    * [Frequent HTTP 401 errors in logs](#frequent-http-401-errors-in-logs)
    * [AKV10032: Invalid issuer](#akv10032-invalid-issuer)
    * [Other authentication issues](#other-authentication-issues)
  * [HTTP 403 errors](#http-403-errors)
    * [Operation not permitted](#operation-not-permitted)
* [Other service errors](#other-service-errors)
  * [HTTP 429: Too many requests](#http-429-too-many-requests)

## Authentication issues

### HTTP 401 errors

HTTP 401 errors may indicate problems authenticating, but silent 401 errors are also an expected part of the Azure Key
Vault authentication flow.

#### Frequent HTTP 401 errors in logs

Most often, this is expected. Azure Key Vault issues a challenge for initial requests that force authentication. You may
see these errors most often during application startup, but may also see these periodically during the application's
lifetime when authentication tokens are near expiration.

If you are not seeing subsequent exceptions from the Key Vault SDKs, authentication challenges are likely the cause. If
you continuously see 401 errors without successful operations, there may be an issue with the authentication library
that's being used. We recommend using the Azure SDK's [azure-identity] library for authentication.

#### AKV10032: Invalid issuer

You may see an error similar to:

```text
AKV10032: Invalid issuer. Expected one of https://sts.windows.net/{tenant 1}/, found https://sts.windows.net/{tenant 2}/.
```

This is most often caused by being logged into a different tenant than the Key Vault authenticates.

See our [DefaultAzureCredential] documentation to see the order credentials are read. You may be logged into a different
tenant for one credential that gets read before another credential. For example, you might be logged into Visual Studio
under the wrong tenant even though you're logged into the Azure CLI under the correct tenant.

Automatic tenant discovery support has been added when referencing [azure-identity] version 1.8.0 or newer, and any of
the following Key Vault SDK package versions or newer:

Package | Minimum Version
--- | ---
`azure-keyvault-administration` | 4.1.0
`azure-keyvault-certificates` | 4.4.0
`azure-keyvault-keys` | 4.5.0
`azure-keyvault-secrets` | 4.4.0

Upgrading to these package versions should resolve any "Invalid Issuer" errors as long as the application or user is a
member of the resource's tenant.

#### Other authentication issues

If you are using the [azure-identity] package - which contains [DefaultAzureCredential] - to authenticate requests to
Azure Key Vault, please see the package's [troubleshooting guide][identity_troubleshooting].

### HTTP 403 errors

HTTP 403 errors indicate the user is not authorized to perform a specific operation in Key Vault or Managed HSM.

#### Operation not permitted

You may see an error similar to:

```text
Operation decrypt is not permitted on this key.
```

The message and inner `code` may vary, but the rest of the text will indicate which operation is not permitted.

This error indicates that the authenticated application or user does not have permissions to perform that operation,
though the cause may vary.

1. Check that the application or user has the appropriate permissions:
    * [Access policies][access_policies] (Key Vault)
    * [Role-Based Access Control (RBAC)][rbac] (Key Vault and Managed HSM)
2. If the appropriate permissions are assigned to your application or user, make sure you are authenticating as that
user.
    * If using the [DefaultAzureCredential], a different credential might've been used than one you expected.
    [Enable logging][identity_logging] and you will see which credential the [DefaultAzureCredential] used as shown
    below, and why previously-attempted credentials were rejected.

## Other service errors

To troubleshoot additional HTTP service errors not described below, see
[Azure Key Vault REST API Error Codes][kv_error_codes].

### HTTP 429: Too many requests

If you get an exception or see logs that describe HTTP 429, you may be making too many requests to Key Vault too
quickly.

Possible solutions include:

1. Use a single `CertificateClient`, `KeyClient`, or `SecretClient` in your application for a single Key Vault.
2. Use a single instance of [DefaultAzureCredential] or other credential you use to authenticate your clients for each
Key Vault or Managed HSM endpoint you need to access. It's safe to give the same credential to multiple clients.
3. Use Azure App Configuration for storing non-secrets and references to Key Vault secrets. Storing all app
configuration in Key Vault will increase the likelihood of requests being throttled as more application instances are
started. See the [azure-appconfiguration] package for more information.
4. If you are performing encryption or decryption operations, consider using wrap and unwrap operations for a symmetric
key -- this may also improve application throughput.

See the [Azure Key Vault throttling guide][throttling_guide] for more information.


[access_policies]: https://docs.microsoft.com/azure/key-vault/general/assign-access-policy
[azure-appconfiguration]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/appconfiguration/azure-appconfiguration/README.md
[azure-identity]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md

[DefaultAzureCredential]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md#defaultazurecredential

[identity_logging]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md#logging
[identity_troubleshooting]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/TROUBLESHOOTING.md

[kv_admin_troubleshooting]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-administration/TROUBLESHOOTING.md
[kv_certs_troubleshooting]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates/TROUBLESHOOTING.md
[kv_error_codes]: https://docs.microsoft.com/azure/key-vault/general/rest-error-codes
[kv_keys_troubleshooting]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-keys/TROUBLESHOOTING.md
[kv_secrets_troubleshooting]: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-secrets/TROUBLESHOOTING.md

[rbac]: https://docs.microsoft.com/azure/key-vault/general/rbac-guide

[throttling_guide]: https://docs.microsoft.com/azure/key-vault/general/overview-throttling
