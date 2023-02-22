# Release History

## 8.0.0 (2023-02-15)

### Features Added

  - Added operation group HybridComputeManagementClientOperationsMixin
  - Model HybridComputePrivateLinkScopeProperties has a new parameter private_endpoint_connections
  - Model MachineExtensionProperties has a new parameter enable_automatic_upgrade
  - Model MachineProperties has a new parameter agent_configuration
  - Model MachineProperties has a new parameter cloud_metadata
  - Model MachineProperties has a new parameter mssql_discovered
  - Model MachineProperties has a new parameter os_type
  - Model MachineProperties has a new parameter service_statuses
  - Model MachineUpdateProperties has a new parameter cloud_metadata
  - Model MachineUpdateProperties has a new parameter os_profile
  - Model OSProfile has a new parameter linux_configuration
  - Model OSProfile has a new parameter windows_configuration
  - Model OperationValue has a new parameter is_data_action
  - Model PrivateEndpointConnectionProperties has a new parameter group_ids

## 8.0.0b1 (2022-11-18)

### Features Added

  - Added operation group ExtensionMetadataOperations
  - Added operation group HybridComputeManagementClientOperationsMixin
  - Model HybridComputePrivateLinkScopeProperties has a new parameter private_endpoint_connections
  - Model Machine has a new parameter ad_fqdn
  - Model Machine has a new parameter agent_configuration
  - Model Machine has a new parameter agent_version
  - Model Machine has a new parameter client_public_key
  - Model Machine has a new parameter cloud_metadata
  - Model Machine has a new parameter detected_properties
  - Model Machine has a new parameter display_name
  - Model Machine has a new parameter dns_fqdn
  - Model Machine has a new parameter domain_name
  - Model Machine has a new parameter error_details
  - Model Machine has a new parameter last_status_change
  - Model Machine has a new parameter location_data
  - Model Machine has a new parameter machine_fqdn
  - Model Machine has a new parameter mssql_discovered
  - Model Machine has a new parameter os_name
  - Model Machine has a new parameter os_profile
  - Model Machine has a new parameter os_sku
  - Model Machine has a new parameter os_type
  - Model Machine has a new parameter os_version
  - Model Machine has a new parameter parent_cluster_resource_id
  - Model Machine has a new parameter private_link_scope_resource_id
  - Model Machine has a new parameter provisioning_state
  - Model Machine has a new parameter resources
  - Model Machine has a new parameter service_statuses
  - Model Machine has a new parameter status
  - Model Machine has a new parameter vm_id
  - Model Machine has a new parameter vm_uuid
  - Model MachineExtension has a new parameter auto_upgrade_minor_version
  - Model MachineExtension has a new parameter enable_automatic_upgrade
  - Model MachineExtension has a new parameter force_update_tag
  - Model MachineExtension has a new parameter instance_view
  - Model MachineExtension has a new parameter protected_settings
  - Model MachineExtension has a new parameter provisioning_state
  - Model MachineExtension has a new parameter publisher
  - Model MachineExtension has a new parameter settings
  - Model MachineExtension has a new parameter type_handler_version
  - Model MachineExtension has a new parameter type_properties_type
  - Model MachineExtensionUpdate has a new parameter auto_upgrade_minor_version
  - Model MachineExtensionUpdate has a new parameter enable_automatic_upgrade
  - Model MachineExtensionUpdate has a new parameter force_update_tag
  - Model MachineExtensionUpdate has a new parameter protected_settings
  - Model MachineExtensionUpdate has a new parameter publisher
  - Model MachineExtensionUpdate has a new parameter settings
  - Model MachineExtensionUpdate has a new parameter type
  - Model MachineExtensionUpdate has a new parameter type_handler_version
  - Model MachineUpdate has a new parameter cloud_metadata
  - Model MachineUpdate has a new parameter location_data
  - Model MachineUpdate has a new parameter os_profile
  - Model MachineUpdate has a new parameter parent_cluster_resource_id
  - Model MachineUpdate has a new parameter private_link_scope_resource_id
  - Model OSProfile has a new parameter linux_configuration
  - Model OSProfile has a new parameter windows_configuration
  - Model OperationValue has a new parameter is_data_action
  - Model PrivateEndpointConnectionProperties has a new parameter group_ids
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

### Breaking Changes

  - Model Machine no longer has parameter properties
  - Model MachineExtension no longer has parameter properties
  - Model MachineExtensionUpdate no longer has parameter properties
  - Model MachineUpdate no longer has parameter properties

## 7.0.0 (2021-04-15)

**Features**

  - Model MachineUpdateProperties has a new parameter private_link_scope_resource_id
  - Model MachineUpdateProperties has a new parameter parent_cluster_resource_id
  - Model MachineProperties has a new parameter private_link_scope_resource_id
  - Model MachineProperties has a new parameter parent_cluster_resource_id
  - Model MachineProperties has a new parameter detected_properties
  - Added operation group PrivateLinkResourcesOperations
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkScopesOperations

**Breaking changes**

  - Operation MachinesOperations.delete has a new signature
  - Operation MachinesOperations.get has a new signature
  - Model ErrorDetail has a new signature
  - Model OperationValue has a new signature
  - Model Machine has a new signature
  - Model MachineExtension has a new signature
  - Model MachineExtensionInstanceViewStatus has a new signature
  - Model MachineUpdate has a new signature
  - Model MachineExtensionUpdate has a new signature

## 7.0.0b1 (2020-12-07)

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

## 2.0.0 (2020-09-08)

**Features**

  - Model Machine has a new parameter ad_fqdn
  - Model Machine has a new parameter os_sku
  - Model Machine has a new parameter domain_name
  - Model Machine has a new parameter dns_fqdn
  - Model Machine has a new parameter vm_uuid
  - Model MachineProperties has a new parameter ad_fqdn
  - Model MachineProperties has a new parameter os_sku
  - Model MachineProperties has a new parameter domain_name
  - Model MachineProperties has a new parameter dns_fqdn
  - Model MachineProperties has a new parameter vm_uuid

**Breaking changes**

  - Model ErrorResponse has a new signature
  - Model MachineExtensionInstanceViewStatus has a new signature

## 1.0.0 (2020-08-19)

**Features**

  - Model Machine has a new parameter identity
  - Model Machine has a new parameter location_data
  - Model MachineUpdate has a new parameter location_data
  - Added operation group MachineExtensionsOperations

**Breaking changes**

  - Model MachineExtension no longer has parameter tenant_id
  - Model MachineExtension no longer has parameter principal_id
  - Model MachineExtension no longer has parameter type1
  - Model Machine no longer has parameter tenant_id
  - Model Machine no longer has parameter physical_location
  - Model Machine no longer has parameter principal_id
  - Model Machine no longer has parameter type1
  - Model MachineUpdate no longer has parameter physical_location
  - Model Resource no longer has parameter tenant_id
  - Model Resource no longer has parameter principal_id
  - Model Resource no longer has parameter location
  - Model Resource no longer has parameter type1
  - Model Resource no longer has parameter tags
  - Model ErrorResponse has a new signature

## 0.1.1 (2019-10-30)

  - Update project description and title

## 0.1.0 (2019-10-29)

**Breaking changes**

  - Removed MachineExtensionsOperations

## 0.1.0rc1 (2019-10-23)

  - Initial Release
