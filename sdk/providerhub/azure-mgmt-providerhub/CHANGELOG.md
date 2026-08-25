# Release History

## 2.0.0 (2026-08-25)

### Features Added

  - Client `ProviderHubMgmtClient` added operation group `manifests`
  - Model `ApplicationDataAuthorization` added property `exclude_application_id_from_manifest`
  - Model `CustomRolloutPropertiesSpecification` added property `manifest_checkin_specification`
  - Model `CustomRolloutPropertiesSpecification` added property `rollout_id`
  - Model `CustomRolloutPropertiesStatus` added property `completed_regions_info`
  - Model `CustomRolloutSpecification` added property `manifest_checkin_specification`
  - Model `CustomRolloutSpecification` added property `rollout_id`
  - Model `CustomRolloutStatus` added property `completed_regions_info`
  - Model `DefaultRolloutPropertiesSpecification` added property `manifest_checkin_specification`
  - Model `DefaultRolloutSpecification` added property `manifest_checkin_specification`
  - Enum `ExtensionCategory` added member `RESOURCE_BILLING_NOTIFICATION`
  - Model `LinkedAccessCheck` added property `options`
  - Model `LocalizedOperationDefinition` added property `properties`
  - Model `LocalizedOperationDefinitionDisplay` added property `qps_ploc`
  - Model `LocalizedOperationDisplayDefinition` added property `qps_ploc`
  - Enum `MarketplaceType` added member `PROVIDER_HUB`
  - Model `ProviderRegistrationProperties` added property `enable_preset_resource_types`
  - Model `ProviderRegistrationProperties` added property `obo_subscription_id`
  - Enum `ResourceDeletionPolicy` added member `CASCADE`
  - Enum `ResourceDeletionPolicy` added member `FORCE`
  - Enum `ResourceDeletionPolicy` added member `SOFT_DELETE`
  - Model `ResourceProviderManagement` added property `feature_management_owners`
  - Model `ResourceProviderManifest` added property `token_auth_configuration`
  - Model `ResourceProviderManifestManagement` added property `feature_management_owners`
  - Model `ResourceProviderManifestPropertiesManagement` added property `feature_management_owners`
  - Enum `ResourceProviderType` added member `DECOMMISSIONED`
  - Model `ResourceType` added property `resource_deletion_policies`
  - Model `ResourceTypeRegistrationProperties` added property `managed_resource_group_configuration`
  - Model `ResourceTypeRegistrationProperties` added property `private_endpoint_configuration`
  - Model `ResourceTypeRegistrationProperties` added property `resource_deletion_policies`
  - Model `ResourceTypeRegistrationProperties` added property `super_scale_enabled`
  - Model `ResourceTypeRegistrationProperties` added property `write_lock`
  - Model `ResourceTypeRegistrationPropertiesManagement` added property `feature_management_owners`
  - Model `ResourceTypeRegistrationPropertiesResourceManagementOptionsBatchProvisioningSupport` added property `action_configurations`
  - Model `ResourceTypeRegistrationPropertiesResourceManagementOptionsBatchProvisioningSupport` added property `batch_contract_version`
  - Model `ResourceTypeRegistrationPropertiesResourceManagementOptionsBatchProvisioningSupport` added property `max_batch_size`
  - Model `ResourceTypeRegistrationPropertiesResourceManagementOptionsBatchProvisioningSupport` added property `max_nested_batch_size`
  - Model `ResourceTypeRegistrationPropertiesResourceManagementOptionsBatchProvisioningSupport` added property `required_features`
  - Model `ThrottlingMetric` added property `bucket_size`
  - Added model `ActionConfiguration`
  - Added model `AppliedManifestInfo`
  - Added model `GroupConnectivityInformation`
  - Added enum `LinkedAccessCheckOptions`
  - Added model `LocalizedOperationDisplayDefinitionQpsPloc`
  - Added model `ManagedResourceGroupDenyAssignmentConfiguration`
  - Added enum `ManifestCheckinOption`
  - Added model `ManifestCheckinSpecification`
  - Added model `ManifestInfo`
  - Added model `ManifestInfoProperties`
  - Added model `PrivateEndpointConfiguration`
  - Added enum `RPaaSResourceDeletionPolicy`
  - Added model `ResourceDeletionPolicyAndProperties`
  - Added model `ResourceDeletionPolicyProperties`
  - Added model `ResourceTypeManagedResourceGroupConfiguration`
  - Added model `WriteLockConfiguration`
  - Added enum `WriteLockState`
  - Added operation group `ManifestsOperations`

### Breaking Changes

  - Deleted or renamed enum value `ResourceDeletionPolicy.CASCADE_DELETE_ALL`
  - Deleted or renamed enum value `ResourceDeletionPolicy.CASCADE_DELETE_PROXY_ONLY_CHILDREN`
  - Deleted or renamed model `ManifestResourceDeletionPolicy`
  - Method `Operations.list_by_provider_registration` changed return type from `List[OperationsDefinition]` to `OperationsPutContent`

## 1.0.0 (2026-07-29)

### Other Changes

  - First GA

## 1.0.0b1 (2026-07-08)

### Other Changes

  - Initial version
