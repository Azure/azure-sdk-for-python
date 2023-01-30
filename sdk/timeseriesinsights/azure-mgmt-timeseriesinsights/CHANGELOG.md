# Release History

## 2.0.0b1 (2022-10-28)

### Features Added

  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations
  - Model AzureEventSourceProperties has a new parameter local_timestamp
  - Model AzureEventSourceProperties has a new parameter time
  - Model AzureEventSourceProperties has a new parameter type
  - Model EventHubEventSourceCommonProperties has a new parameter local_timestamp
  - Model EventHubEventSourceCommonProperties has a new parameter time
  - Model EventHubEventSourceCommonProperties has a new parameter type
  - Model EventHubEventSourceCreateOrUpdateParameters has a new parameter local_timestamp_properties_local_timestamp
  - Model EventHubEventSourceCreateOrUpdateParameters has a new parameter time
  - Model EventHubEventSourceCreateOrUpdateParameters has a new parameter type
  - Model EventHubEventSourceCreationProperties has a new parameter local_timestamp
  - Model EventHubEventSourceCreationProperties has a new parameter time
  - Model EventHubEventSourceCreationProperties has a new parameter type
  - Model EventHubEventSourceResource has a new parameter local_timestamp
  - Model EventHubEventSourceResource has a new parameter time
  - Model EventHubEventSourceResource has a new parameter type_properties_ingress_start_at_type
  - Model EventHubEventSourceResourceProperties has a new parameter local_timestamp
  - Model EventHubEventSourceResourceProperties has a new parameter time
  - Model EventHubEventSourceResourceProperties has a new parameter type
  - Model EventSourceCommonProperties has a new parameter local_timestamp
  - Model EventSourceCommonProperties has a new parameter time
  - Model EventSourceCommonProperties has a new parameter type
  - Model Gen2EnvironmentCreateOrUpdateParameters has a new parameter private_endpoint_connections
  - Model Gen2EnvironmentCreateOrUpdateParameters has a new parameter public_network_access
  - Model Gen2EnvironmentResource has a new parameter private_endpoint_connections
  - Model Gen2EnvironmentResource has a new parameter public_network_access
  - Model Gen2EnvironmentResourceProperties has a new parameter private_endpoint_connections
  - Model Gen2EnvironmentResourceProperties has a new parameter public_network_access
  - Model IoTHubEventSourceCommonProperties has a new parameter local_timestamp
  - Model IoTHubEventSourceCommonProperties has a new parameter time
  - Model IoTHubEventSourceCommonProperties has a new parameter type
  - Model IoTHubEventSourceCreateOrUpdateParameters has a new parameter local_timestamp_properties_local_timestamp
  - Model IoTHubEventSourceCreateOrUpdateParameters has a new parameter time
  - Model IoTHubEventSourceCreateOrUpdateParameters has a new parameter type
  - Model IoTHubEventSourceCreationProperties has a new parameter local_timestamp
  - Model IoTHubEventSourceCreationProperties has a new parameter time
  - Model IoTHubEventSourceCreationProperties has a new parameter type
  - Model IoTHubEventSourceResource has a new parameter local_timestamp
  - Model IoTHubEventSourceResource has a new parameter time
  - Model IoTHubEventSourceResource has a new parameter type_properties_ingress_start_at_type
  - Model IoTHubEventSourceResourceProperties has a new parameter local_timestamp
  - Model IoTHubEventSourceResourceProperties has a new parameter time
  - Model IoTHubEventSourceResourceProperties has a new parameter type
  - Model Operation has a new parameter origin
  - Model Operation has a new parameter service_specification

### Breaking Changes

  - Model EventHubEventSourceMutableProperties no longer has parameter local_timestamp
  - Model EventHubEventSourceUpdateParameters no longer has parameter local_timestamp
  - Model EventSourceMutableProperties no longer has parameter local_timestamp
  - Model IoTHubEventSourceMutableProperties no longer has parameter local_timestamp
  - Model IoTHubEventSourceUpdateParameters no longer has parameter local_timestamp
  - Parameter kind of model EnvironmentUpdateParameters is now required
  - Parameter kind of model EventHubEventSourceUpdateParameters is now required
  - Parameter kind of model EventSourceUpdateParameters is now required
  - Parameter kind of model Gen1EnvironmentUpdateParameters is now required
  - Parameter kind of model Gen2EnvironmentUpdateParameters is now required
  - Parameter kind of model IoTHubEventSourceUpdateParameters is now required

## 1.0.0 (2021-03-26)

**Features**

  - Model EventHubEventSourceUpdateParameters has a new parameter kind
  - Model IoTHubEventSourceUpdateParameters has a new parameter kind
  - Model Gen1EnvironmentUpdateParameters has a new parameter kind
  - Model EventSourceUpdateParameters has a new parameter kind
  - Model Gen2EnvironmentUpdateParameters has a new parameter kind
  - Model EnvironmentUpdateParameters has a new parameter kind

**Breaking changes**

  - Operation AccessPoliciesOperations.update has a new signature
  - Operation EventSourcesOperations.update has a new signature
  - Operation EnvironmentsOperations.begin_update has a new signature
  - Operation ReferenceDataSetsOperations.update has a new signature
  - Operation AccessPoliciesOperations.update has a new signature

## 1.0.0b1 (2020-12-14)

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

## 0.2.0 (2020-02-18)
+++++++++++++++++++++

**Features**

- Model EnvironmentStatus has a new parameter warm_storage

**Breaking changes**

- Operation EnvironmentsOperations.update has a new signature
- Model EnvironmentResource has a new signature
- Model EnvironmentUpdateParameters has a new signature
- Model EnvironmentCreateOrUpdateParameters has a new signature

## 0.1.0 (2020-01-15)

  - Initial Release
