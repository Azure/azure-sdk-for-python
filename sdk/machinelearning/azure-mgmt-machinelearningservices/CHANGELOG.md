# Release History

## 2.0.0b1 (2022-11-17)

### Features Added

  - Added operation PrivateEndpointConnectionsOperations.create_or_update
  - Added operation PrivateEndpointConnectionsOperations.delete
  - Added operation PrivateEndpointConnectionsOperations.list
  - Added operation PrivateLinkResourcesOperations.list
  - Added operation WorkspacesOperations.begin_diagnose
  - Added operation WorkspacesOperations.begin_prepare_notebook
  - Added operation WorkspacesOperations.list_notebook_access_token
  - Added operation WorkspacesOperations.list_notebook_keys
  - Added operation WorkspacesOperations.list_outbound_network_dependencies_endpoints
  - Added operation WorkspacesOperations.list_storage_account_keys
  - Added operation group BatchDeploymentsOperations
  - Added operation group BatchEndpointsOperations
  - Added operation group CodeContainersOperations
  - Added operation group CodeVersionsOperations
  - Added operation group ComponentContainersOperations
  - Added operation group ComponentVersionsOperations
  - Added operation group ComputeOperations
  - Added operation group DataContainersOperations
  - Added operation group DataVersionsOperations
  - Added operation group DatastoresOperations
  - Added operation group EnvironmentContainersOperations
  - Added operation group EnvironmentVersionsOperations
  - Added operation group JobsOperations
  - Added operation group ModelContainersOperations
  - Added operation group ModelVersionsOperations
  - Added operation group OnlineDeploymentsOperations
  - Added operation group OnlineEndpointsOperations
  - Added operation group SchedulesOperations
  - Model AKS has a new parameter disable_local_auth
  - Model AmlCompute has a new parameter disable_local_auth
  - Model AmlComputeProperties has a new parameter enable_node_public_ip
  - Model AmlComputeProperties has a new parameter isolated_network
  - Model AmlComputeProperties has a new parameter os_type
  - Model AmlComputeProperties has a new parameter property_bag
  - Model AmlComputeProperties has a new parameter virtual_machine_image
  - Model ClusterUpdateParameters has a new parameter properties
  - Model Compute has a new parameter disable_local_auth
  - Model ComputeInstance has a new parameter disable_local_auth
  - Model ComputeInstanceLastOperation has a new parameter operation_trigger
  - Model ComputeInstanceProperties has a new parameter compute_instance_authorization_type
  - Model ComputeInstanceProperties has a new parameter containers
  - Model ComputeInstanceProperties has a new parameter data_disks
  - Model ComputeInstanceProperties has a new parameter data_mounts
  - Model ComputeInstanceProperties has a new parameter enable_node_public_ip
  - Model ComputeInstanceProperties has a new parameter personal_compute_instance_settings
  - Model ComputeInstanceProperties has a new parameter schedules
  - Model ComputeInstanceProperties has a new parameter setup_scripts
  - Model ComputeInstanceProperties has a new parameter versions
  - Model ComputeResource has a new parameter system_data
  - Model DataFactory has a new parameter disable_local_auth
  - Model DataLakeAnalytics has a new parameter disable_local_auth
  - Model Databricks has a new parameter disable_local_auth
  - Model DatabricksProperties has a new parameter workspace_url
  - Model EncryptionProperty has a new parameter identity
  - Model ErrorDetail has a new parameter additional_info
  - Model ErrorDetail has a new parameter details
  - Model ErrorDetail has a new parameter target
  - Model ErrorResponse has a new parameter error
  - Model HDInsight has a new parameter disable_local_auth
  - Model PrivateEndpoint has a new parameter subnet_arm_id
  - Model PrivateEndpointConnection has a new parameter identity
  - Model PrivateEndpointConnection has a new parameter location
  - Model PrivateEndpointConnection has a new parameter sku
  - Model PrivateEndpointConnection has a new parameter system_data
  - Model PrivateEndpointConnection has a new parameter tags
  - Model PrivateLinkResource has a new parameter system_data
  - Model QuotaUpdateParameters has a new parameter location
  - Model Resource has a new parameter system_data
  - Model ResourceQuota has a new parameter aml_workspace_location
  - Model Sku has a new parameter capacity
  - Model Sku has a new parameter family
  - Model Sku has a new parameter size
  - Model SslConfiguration has a new parameter leaf_domain_label
  - Model SslConfiguration has a new parameter overwrite_existing_domain
  - Model Usage has a new parameter aml_workspace_location
  - Model VirtualMachine has a new parameter disable_local_auth
  - Model VirtualMachineSizeListResult has a new parameter value
  - Model Workspace has a new parameter ml_flow_tracking_uri
  - Model Workspace has a new parameter primary_user_assigned_identity
  - Model Workspace has a new parameter public_network_access
  - Model Workspace has a new parameter service_managed_resources_settings
  - Model Workspace has a new parameter storage_hns_enabled
  - Model Workspace has a new parameter system_data
  - Model Workspace has a new parameter tenant_id
  - Model Workspace has a new parameter v1_legacy_mode
  - Model WorkspaceUpdateParameters has a new parameter application_insights
  - Model WorkspaceUpdateParameters has a new parameter container_registry
  - Model WorkspaceUpdateParameters has a new parameter identity
  - Model WorkspaceUpdateParameters has a new parameter image_build_compute
  - Model WorkspaceUpdateParameters has a new parameter primary_user_assigned_identity
  - Model WorkspaceUpdateParameters has a new parameter public_network_access
  - Model WorkspaceUpdateParameters has a new parameter service_managed_resources_settings

### Breaking Changes

  - Client name is changed from `AzureMachineLearningWorkspaces` to `MachineLearningServicesMgmtClient`
  - Model AmlComputeNodesInformation no longer has parameter compute_type
  - Model ClusterUpdateParameters no longer has parameter scale_settings
  - Model ErrorResponse no longer has parameter code
  - Model ErrorResponse no longer has parameter details
  - Model ErrorResponse no longer has parameter message
  - Model Resource no longer has parameter identity
  - Model Resource no longer has parameter location
  - Model Resource no longer has parameter sku
  - Model Resource no longer has parameter tags
  - Model VirtualMachineSizeListResult no longer has parameter aml_compute
  - Model Workspace no longer has parameter creation_time
  - Operation VirtualMachineSizesOperations.list no longer has parameter compute_type
  - Operation VirtualMachineSizesOperations.list no longer has parameter recommended
  - Operation WorkspacesOperations.list_by_resource_group has a new parameter skip
  - Operation WorkspacesOperations.list_by_resource_group no longer has parameter skiptoken
  - Operation WorkspacesOperations.list_by_subscription has a new parameter skip
  - Operation WorkspacesOperations.list_by_subscription no longer has parameter skiptoken
  - Parameter name of model Sku is now required
  - Removed operation PrivateEndpointConnectionsOperations.begin_delete
  - Removed operation PrivateEndpointConnectionsOperations.put
  - Removed operation PrivateLinkResourcesOperations.list_by_workspace
  - Removed operation group AzureMachineLearningWorkspacesOperationsMixin
  - Removed operation group MachineLearningComputeOperations
  - Removed operation group NotebooksOperations
  - Renamed operation WorkspacesOperations.resync_keys to WorkspacesOperations.begin_resync_keys
  - Renamed operation WorkspacesOperations.update to WorkspacesOperations.begin_update

## 1.0.0 (2020-12-21)

**Breaking changes**

  - Operation MachineLearningComputeOperations.begin_update has a new signature
  - Operation PrivateEndpointConnectionsOperations.put has a new signature
  - Operation QuotasOperations.update has a new signature
  - Operation PrivateEndpointConnectionsOperations.put has a new signature

## 1.0.0b1 (2020-10-31)

This is beta preview version.
For detailed changelog please refer to equivalent stable version 0.1.0 (https://pypi.org/project/azure-mgmt-machinelearningservices/0.1.0/)

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
  - For a complete set of supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.


## 0.1.0 (2019-06-27)

  - Initial Release
