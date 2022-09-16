# Release History

## 1.1.0 (2022-03-31)

**Features**

  - Added operation group WorkspacePrivateEndpointConnectionsOperations
  - Added operation group WorkspacePrivateLinkResourcesOperations
  - Model DicomService has a new parameter identity
  - Model DicomService has a new parameter private_endpoint_connections
  - Model DicomService has a new parameter public_network_access
  - Model DicomServicePatchResource has a new parameter identity
  - Model FhirService has a new parameter event_state
  - Model FhirService has a new parameter private_endpoint_connections
  - Model FhirService has a new parameter public_network_access
  - Model FhirService has a new parameter resource_version_policy_configuration
  - Model FhirServiceAcrConfiguration has a new parameter oci_artifacts
  - Model OperationDetail has a new parameter properties
  - Model OperationResultsDescription has a new parameter end_time
  - Model ServiceAcrConfigurationInfo has a new parameter oci_artifacts
  - Model ServiceManagedIdentityIdentity has a new parameter principal_id
  - Model ServiceManagedIdentityIdentity has a new parameter tenant_id
  - Model ServiceManagedIdentityIdentity has a new parameter user_assigned_identities
  - Model WorkspaceProperties has a new parameter private_endpoint_connections
  - Model WorkspaceProperties has a new parameter public_network_access

**Breaking changes**

  - Parameter type of model ServiceManagedIdentityIdentity is now required

## 1.1.0b1 (2021-08-26)

**Features**

  - Added operation group IotConnectorFhirDestinationOperations
  - Added operation group WorkspacesOperations
  - Added operation group FhirDestinationsOperations
  - Added operation group DicomServicesOperations
  - Added operation group FhirServicesOperations
  - Added operation group IotConnectorsOperations

## 1.0.0 (2021-04-12)

**Features**

  - Model ServicesDescription has a new parameter system_data
  - Model ServicesProperties has a new parameter acr_configuration

## 1.0.0b1 (2020-12-04)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 0.2.0 (2020-11-02)

**Features**

  - Model ServiceCosmosDbConfigurationInfo has a new parameter key_vault_key_uri
  - Model ServicesPatchDescription has a new parameter public_network_access
  - Model ServicesDescription has a new parameter identity
  - Model ServicesProperties has a new parameter public_network_access
  - Model ServicesProperties has a new parameter export_configuration
  - Model ServicesProperties has a new parameter private_endpoint_connections
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations

**Breaking changes**

  - Operation ServicesOperations.update has a new signature
  - Model Resource no longer has parameter kind
  - Model Resource no longer has parameter tags
  - Model Resource no longer has parameter etag
  - Model Resource no longer has parameter location

## 0.1.0 (2019-08-03)

  - Initial Release
