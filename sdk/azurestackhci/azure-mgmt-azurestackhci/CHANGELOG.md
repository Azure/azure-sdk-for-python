# Release History

## 8.0.0b2 (2022-12-15)

### Features Added

  - Added operation ClustersOperations.delete
  - Added operation group GalleryimagesOperations
  - Added operation group GuestAgentOperations
  - Added operation group GuestAgentsOperations
  - Added operation group HybridIdentityMetadataOperations
  - Added operation group MachineExtensionsOperations
  - Added operation group MarketplacegalleryimagesOperations
  - Added operation group NetworkinterfacesOperations
  - Added operation group StoragecontainersOperations
  - Added operation group VirtualharddisksOperations
  - Added operation group VirtualmachinesOperations
  - Added operation group VirtualnetworksOperations
  - Model ArcSetting has a new parameter created_at
  - Model ArcSetting has a new parameter created_by
  - Model ArcSetting has a new parameter created_by_type
  - Model ArcSetting has a new parameter last_modified_at
  - Model ArcSetting has a new parameter last_modified_by
  - Model ArcSetting has a new parameter last_modified_by_type
  - Model Cluster has a new parameter created_at
  - Model Cluster has a new parameter created_by
  - Model Cluster has a new parameter created_by_type
  - Model Cluster has a new parameter last_modified_at
  - Model Cluster has a new parameter last_modified_by
  - Model Cluster has a new parameter last_modified_by_type
  - Model Extension has a new parameter created_at
  - Model Extension has a new parameter created_by
  - Model Extension has a new parameter created_by_type
  - Model Extension has a new parameter last_modified_at
  - Model Extension has a new parameter last_modified_by
  - Model Extension has a new parameter last_modified_by_type

### Breaking Changes

  - Model ArcSetting no longer has parameter arc_application_client_id
  - Model ArcSetting no longer has parameter arc_application_object_id
  - Model ArcSetting no longer has parameter arc_application_tenant_id
  - Model ArcSetting no longer has parameter arc_service_principal_object_id
  - Model ArcSetting no longer has parameter connectivity_properties
  - Model ArcSetting no longer has parameter system_data
  - Model Cluster no longer has parameter aad_application_object_id
  - Model Cluster no longer has parameter aad_service_principal_object_id
  - Model Cluster no longer has parameter principal_id
  - Model Cluster no longer has parameter service_endpoint
  - Model Cluster no longer has parameter software_assurance_properties
  - Model Cluster no longer has parameter system_data
  - Model Cluster no longer has parameter tenant_id
  - Model Cluster no longer has parameter type_identity_type
  - Model Cluster no longer has parameter user_assigned_identities
  - Model ClusterNode no longer has parameter node_type
  - Model ClusterNode no longer has parameter os_display_version
  - Model ClusterPatch no longer has parameter principal_id
  - Model ClusterPatch no longer has parameter tenant_id
  - Model ClusterPatch no longer has parameter type
  - Model ClusterPatch no longer has parameter user_assigned_identities
  - Model Extension no longer has parameter system_data
  - Model ProxyResource no longer has parameter system_data
  - Model Resource no longer has parameter system_data
  - Model TrackedResource no longer has parameter system_data
  - Removed operation ArcSettingsOperations.begin_create_identity
  - Removed operation ArcSettingsOperations.generate_password
  - Removed operation ArcSettingsOperations.update
  - Removed operation ClustersOperations.begin_create_identity
  - Removed operation ClustersOperations.begin_delete
  - Removed operation ClustersOperations.begin_extend_software_assurance_benefit
  - Removed operation ClustersOperations.begin_upload_certificate
  - Removed operation group OffersOperations
  - Removed operation group PublishersOperations
  - Removed operation group SkusOperations
  - Removed operation group UpdateRunsOperations
  - Removed operation group UpdateSummariesOperations
  - Removed operation group UpdatesOperations

## 8.0.0b1 (2022-11-25)

### Features Added

  - Added operation ClustersOperations.begin_extend_software_assurance_benefit
  - Added operation group OffersOperations
  - Added operation group PublishersOperations
  - Added operation group SkusOperations
  - Added operation group UpdateRunsOperations
  - Added operation group UpdateSummariesOperations
  - Added operation group UpdatesOperations
  - Model ArcSetting has a new parameter system_data
  - Model Cluster has a new parameter principal_id
  - Model Cluster has a new parameter software_assurance_properties
  - Model Cluster has a new parameter system_data
  - Model Cluster has a new parameter tenant_id
  - Model Cluster has a new parameter type_identity_type
  - Model Cluster has a new parameter user_assigned_identities
  - Model ClusterNode has a new parameter node_type
  - Model ClusterNode has a new parameter os_display_version
  - Model ClusterPatch has a new parameter principal_id
  - Model ClusterPatch has a new parameter tenant_id
  - Model ClusterPatch has a new parameter type
  - Model ClusterPatch has a new parameter user_assigned_identities
  - Model Extension has a new parameter system_data
  - Model ProxyResource has a new parameter system_data
  - Model Resource has a new parameter system_data
  - Model TrackedResource has a new parameter system_data

### Breaking Changes

  - Model ArcSetting no longer has parameter created_at
  - Model ArcSetting no longer has parameter created_by
  - Model ArcSetting no longer has parameter created_by_type
  - Model ArcSetting no longer has parameter last_modified_at
  - Model ArcSetting no longer has parameter last_modified_by
  - Model ArcSetting no longer has parameter last_modified_by_type
  - Model Cluster no longer has parameter created_at
  - Model Cluster no longer has parameter created_by
  - Model Cluster no longer has parameter created_by_type
  - Model Cluster no longer has parameter last_modified_at
  - Model Cluster no longer has parameter last_modified_by
  - Model Cluster no longer has parameter last_modified_by_type
  - Model Extension no longer has parameter created_at
  - Model Extension no longer has parameter created_by
  - Model Extension no longer has parameter created_by_type
  - Model Extension no longer has parameter last_modified_at
  - Model Extension no longer has parameter last_modified_by
  - Model Extension no longer has parameter last_modified_by_type

## 7.0.0 (2022-05-26)

**Features**

  - Added operation ArcSettingsOperations.begin_create_identity
  - Added operation ArcSettingsOperations.generate_password
  - Added operation ArcSettingsOperations.update
  - Added operation ClustersOperations.begin_create_identity
  - Added operation ClustersOperations.begin_delete
  - Added operation ClustersOperations.begin_upload_certificate
  - Model ArcSetting has a new parameter arc_application_client_id
  - Model ArcSetting has a new parameter arc_application_object_id
  - Model ArcSetting has a new parameter arc_application_tenant_id
  - Model ArcSetting has a new parameter arc_service_principal_object_id
  - Model ArcSetting has a new parameter connectivity_properties
  - Model Cluster has a new parameter aad_application_object_id
  - Model Cluster has a new parameter aad_service_principal_object_id
  - Model Cluster has a new parameter service_endpoint

**Breaking changes**

  - Removed operation ClustersOperations.delete

## 6.1.0 (2022-04-08)

**Features**

  - Model Cluster has a new parameter desired_properties
  - Model ClusterNode has a new parameter windows_server_subscription
  - Model ClusterPatch has a new parameter aad_client_id
  - Model ClusterPatch has a new parameter aad_tenant_id
  - Model ClusterPatch has a new parameter desired_properties
  - Model ClusterReportedProperties has a new parameter diagnostic_level
  - Model ClusterReportedProperties has a new parameter imds_attestation

## 6.1.0b1 (2021-06-29)

**Features**

  - Model Cluster has a new parameter cloud_management_endpoint
  - Added operation group ArcSettingsOperations
  - Added operation group ExtensionsOperations

## 6.0.0 (2021-05-20)

- GA release

## 6.0.0b1 (2020-12-08)

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

## 1.0.0 (2020-10-14)

**Features**

  - Model Cluster has a new parameter last_billing_timestamp
  - Model Cluster has a new parameter registration_timestamp
  - Model Cluster has a new parameter last_sync_timestamp
  - Added operation ClustersOperations.list_by_subscription

**Breaking changes**

  - Removed operation ClustersOperations.list

## 1.0.0rc (2020-07-22)

* Initial Release
