# Release History

## 1.2.0b2 (2025-03-24)

### Features Added

  - Model `ConnectedCluster` added property `kind`
  - Model `ConnectedCluster` added property `distribution_version`
  - Model `ConnectedCluster` added property `private_link_state`
  - Model `ConnectedCluster` added property `private_link_scope_resource_id`
  - Model `ConnectedCluster` added property `azure_hybrid_benefit`
  - Model `ConnectedCluster` added property `aad_profile`
  - Model `ConnectedCluster` added property `arc_agent_profile`
  - Model `ConnectedCluster` added property `security_profile`
  - Model `ConnectedCluster` added property `oidc_issuer_profile`
  - Model `ConnectedCluster` added property `gateway`
  - Model `ConnectedCluster` added property `arc_agentry_configurations`
  - Model `ConnectedCluster` added property `miscellaneous_properties`
  - Model `ConnectedClusterPatch` added property `distribution`
  - Model `ConnectedClusterPatch` added property `distribution_version`
  - Model `ConnectedClusterPatch` added property `azure_hybrid_benefit`
  - Enum `ConnectivityStatus` added member `AGENT_NOT_INSTALLED`
  - Model `HybridConnectionConfig` added property `relay_tid`
  - Model `HybridConnectionConfig` added property `relay_type`
  - Added model `AadProfile`
  - Added model `AgentError`
  - Added model `ArcAgentProfile`
  - Added model `ArcAgentryConfigurations`
  - Added enum `AutoUpgradeOptions`
  - Added enum `AzureHybridBenefit`
  - Added enum `ConnectedClusterKind`
  - Added model `Gateway`
  - Added model `OidcIssuerProfile`
  - Added enum `PrivateLinkState`
  - Added model `SecurityProfile`
  - Added model `SecurityProfileWorkloadIdentity`
  - Added model `SystemComponent`
  - Model `ConnectedClusterOperations` added method `begin_create_or_replace`

### Breaking Changes

  - Model `ConnectedClusterPatch` deleted or renamed its instance variable `properties`
  - Deleted or renamed method `ConnectedClusterOperations.begin_create`

## 1.2.0b1 (2022-11-09)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.1.0 (2021-10-20)

**Features**

  - Added operation ConnectedClusterOperations.list_cluster_user_credential

## 1.0.0 (2021-05-19)

**Features**

  - Model ConnectedCluster has a new parameter system_data

**Breaking changes**

  - Model ConnectedCluster no longer has parameter aad_profile
  - Removed operation ConnectedClusterOperations.list_cluster_user_credentials
  - Model ConnectedClusterPatch has a new signature

## 1.0.0b1 (2020-12-09)

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

## 0.1.0 (2020-05-18)

* Initial Release
