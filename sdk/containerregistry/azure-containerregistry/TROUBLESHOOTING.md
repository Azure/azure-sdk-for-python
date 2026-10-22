# Troubleshoot Azure Container Registry client library issues

This troubleshooting guide contains instructions to diagnose frequently encountered issues while using the Azure Container Registry client library for Python.

## General Troubleshooting

ACR client library will raise exceptions defined in [Azure Core][azure_core_exceptions].

### Enable client logging

This library uses the standard
[logging][python_logging] library for logging.

Basic information about HTTP sessions (URLs, headers, etc.) is logged at `INFO` level.

Detailed `DEBUG` level logging, including request/response bodies and **unredacted**
headers, can be enabled on the client or per-operation with the `logging_enable` keyword argument.

See full Python SDK logging documentation with examples [here][sdk_logging_docs].

### Optional Configuration

Optional keyword arguments can be passed in at the client and per-operation level.
The azure-core [reference documentation][azure_core_ref_docs]
describes available configurations for retries, logging, transport protocols, and more.

## Troubleshooting authentication errors

### HTTP 401 Errors

HTTP 401 errors indicate problems authenticating. Check the exception message or logs for more information.

#### Anonymous access issues

You may see error similar to the one below, it indicates an attempt to perform operation that requires authentication without credentials.

```
{"errors":[{"code":"UNAUTHORIZED","message":"authentication required, visit https://aka.ms/acr/authorization for
more information."}]}
```

Unauthorized access can only be enabled for read (pull) operations such as listing repositories, getting properties or tags. Refer to [Anonymous pull access] to learn about anonymous access limitation.

### HTTP 403 Errors

HTTP 403 errors indicate that user is not authorized to perform a specific operation in Azure Container Registry.

#### Insufficient permissions

If you see an error similar to the one below, it means that the provided credentials do not have permission to access the registry.

```
{"errors":[{"code":"DENIED","message":"retrieving permissions failed"}]}
```

To resolve:

1. Check that the application or user that is making the request has sufficient permissions. Check [Troubleshoot registry login] for possible solutions.
1. If the user or application is granted sufficient privileges to query the workspace, make sure you are authenticating as that user/application. If you are authenticating using [DefaultAzureCredential], check the logs to verify that the credential used is the one you expected. To enable logging, see the [Enable client logging] section above.

For more help on troubleshooting authentication errors, please see the Azure Identity client library [troubleshooting guide].

#### Network access issues

The below error indicates that public access to the Azure Container Registry is disabled or restricted. Refer to [Troubleshoot network issues with registry] for more information.

```
{"errors":[{"code":"DENIED","message":"client with IP '<your IP address>' is not allowed access. Refer https://aka.m
s/acr/firewall to grant access."}]}
```

<!-- LINKS -->
[azure_core_exceptions]: https://aka.ms/azsdk/python/core/docs#module-azure.core.exceptions
[python_logging]: https://docs.python.org/3/library/logging.html
[sdk_logging_docs]: https://learn.microsoft.com/azure/developer/python/azure-sdk-logging
[azure_core_ref_docs]: https://aka.ms/azsdk/python/core/docs
[anonymous pull access]: https://learn.microsoft.com/azure/container-registry/anonymous-pull-access
[troubleshoot registry login]: https://learn.microsoft.com/azure/container-registry/container-registry-troubleshoot-login
[defaultazurecredential]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/README.md#authenticate-with-defaultazurecredential
[enable client logging]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/containerregistry/azure-containerregistry/TROUBLESHOOTING.md#enable-client-logging
[troubleshooting guide]: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/TROUBLESHOOTING.md
[troubleshoot network issues with registry]: https://learn.microsoft.com/azure/container-registry/container-registry-troubleshoot-access
