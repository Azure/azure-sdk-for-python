# Troubleshoot Azure App Configuration client library issues

This troubleshooting guide contains instructions to diagnose frequently encountered issues while using the Azure App Configuration client library for Python.

## Table of contents

* [General troubleshooting](#general-troubleshooting)
  * [Enable client logging](#enable-client-logging)
* [Troubleshooting authentication issues](#troubleshooting-authentication-issues)
  * [ClientAuthenticationError](#clientauthenticationerror)
  * [CredentialUnavailableError](#credentialunavailableerror)
  * [Permission issues](#permission-issues)
* [Get additional help](#get-additional-help)

## General Troubleshooting

Azure App Configuration client library will raise exceptions defined in [Azure Core](https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions).

### Enable client logging

This library uses the standard [logging](https://docs.python.org/3/library/logging.html) library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted** headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

See full Python SDK logging documentation with examples [here](https://docs.microsoft.com/azure/developer/python/azure-sdk-logging).

## Troubleshooting authentication issues

In addition to connection strings, Azure App Configuration supports [role-based access control](https://learn.microsoft.com/azure/role-based-access-control/overview) (RBAC) using Azure Active Directory authentication. For more details on getting started, see the [README](https://learn.microsoft.com/python/api/overview/azure/appconfiguration-readme?view=azure-python) of Azure App Configuration library. For details on the credential types supported in `azure.identity`, see the [Azure Identity documentation](https://learn.microsoft.com/python/api/overview/azure/identity-readme?view=azure-python).

If authentication or authorization fails, you will likely encounter one of these errors:

### ClientAuthenticationError

Errors arising from authentication can be raised on any service client method that makes a request to the service. This is because the token is requested from the credential on the first call to the service and on any subsequent requests to the service that need to refresh the token.

To distinguish these failures from failures in the service client, Azure Identity raises the `ClientAuthenticationError` with details describing the source of the error in the error message. Depending on the application, these errors may or may not be recoverable.

```python
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import DefaultAzureCredential
from azure.appconfiguration import AzureAppConfigurationClient

# Create a secret client using the DefaultAzureCredential
client = AzureAppConfigurationClient("<my_endpoint_string>", DefaultAzureCredential())
try:
    client.get_configuration_setting("key")
except ClientAuthenticationError as ex:
    print(f"Authentication failed. {ex.message}")
```

### CredentialUnavailableError

The `CredentialUnavailableError` is a special error type derived from `ClientAuthenticationError`. This error type is used to indicate that the credential can't authenticate in the current environment, due to lack of required configuration or setup. This error is also used as a signal to chained credential types, such as `DefaultAzureCredential` and `ChainedTokenCredential`, that the chained credential should continue to try other credential types later in the chain.

### Permission issues

Calls to service clients resulting in `HttpResponseError` with a `StatusCode` of 401 or 403 often indicate the caller doesn't have sufficient permissions for the specified API. Check the service documentation to determine which RBAC roles are needed for the specific request, and ensure the authenticated user or service principal have been granted the appropriate roles on the resource.

## Get additional help

Additional information on ways to reach out for support can be found in the [SUPPORT.md](https://github.com/Azure/azure-sdk-for-python/blob/main/SUPPORT.md) at the root of the repo.
