# Release History

## 3.0.0 (2026-10-22)

### Features Added

  - Client `ProviderHubMgmtClient` added operation group `endpoint_registrations`
  - Model `AppliedManifestInfo` added property `root_provider_namespace`
  - Model `CheckinManifestParams` added property `checkin_comment`
  - Model `CheckinManifestParams` added property `swagger_uri`
  - Model `CustomRolloutPropertiesSpecification` added property `rollout_orchestration_metadata`
  - Model `CustomRolloutSpecification` added property `rollout_orchestration_metadata`
  - Enum `OptInHeaderType` added member `AUXILIARY_USER_CONTEXT`
  - Enum `OptInHeaderType` added member `USER_CONTEXT`
  - Model `ProviderRegistrationProperties` added property `lifecycle_info`
  - Model `ResourceProviderManagement` added property `feature_approval_claims`
  - Model `ResourceProviderManifestManagement` added property `feature_approval_claims`
  - Model `ResourceProviderManifestPropertiesManagement` added property `feature_approval_claims`
  - Model `ResourceTypeRegistrationProperties` added property `lifecycle_info`
  - Model `ResourceTypeRegistrationPropertiesManagement` added property `feature_approval_claims`
  - Model `SwaggerSpecification` added property `lifecycle_info`
  - Added model `EndpointRegistration`
  - Added model `EndpointRegistrationProperties`
  - Added enum `IsolationType`
  - Added enum `LifecycleStage`
  - Added enum `PartnerCategory`
  - Added model `ResourceProviderLifecycleInfo`
  - Added model `ResourceTypeLifecycleInfo`
  - Added model `RolloutOrchestrationMetadata`
  - Added model `SwaggerSpecificationLifecycleInfo`
  - Operation group `ResourceTypeRegistrationsOperations` added method `begin_create_or_update_nested_resource_type_first`
  - Operation group `ResourceTypeRegistrationsOperations` added method `begin_delete_nested_resource_type_first`
  - Operation group `ResourceTypeRegistrationsOperations` added method `get_nested_resource_type_first`
  - Added operation group `EndpointRegistrationsOperations`

### Breaking Changes

  - Deleted or renamed client operation group `ProviderHubMgmtClient.new_region_frontload_release`
  - Model `FanoutLinkedNotificationRule` deleted or renamed its instance variable `dsts_configuration`
  - Model `ProviderRegistrationProperties` deleted or renamed its instance variable `dsts_configuration`
  - Deleted or renamed enum value `ResourceAccessPolicy.ACIS_ACTION_ALLOWED`
  - Deleted or renamed enum value `ResourceAccessPolicy.ACIS_READ_ALLOWED`
  - Model `ResourceProviderManagement` deleted or renamed its instance variable `service_tree_infos`
  - Model `ResourceProviderManifestManagement` deleted or renamed its instance variable `service_tree_infos`
  - Model `ResourceProviderManifestProperties` deleted or renamed its instance variable `dsts_configuration`
  - Model `ResourceProviderManifestPropertiesManagement` deleted or renamed its instance variable `service_tree_infos`
  - Model `ResourceType` deleted or renamed its instance variable `service_tree_infos`
  - Model `ResourceTypeEndpoint` deleted or renamed its instance variable `dsts_configuration`
  - Model `ResourceTypeRegistrationProperties` deleted or renamed its instance variable `dsts_configuration`
  - Model `ResourceTypeRegistrationProperties` deleted or renamed its instance variable `service_tree_infos`
  - Model `ResourceTypeRegistrationPropertiesManagement` deleted or renamed its instance variable `service_tree_infos`
  - Deleted or renamed model `AvailableCheckInManifestEnvironment`
  - Deleted or renamed model `DstsConfiguration`
  - Deleted or renamed model `FanoutLinkedNotificationRuleDstsConfiguration`
  - Deleted or renamed model `FrontloadPayload`
  - Deleted or renamed model `FrontloadPayloadProperties`
  - Deleted or renamed model `FrontloadPayloadPropertiesOverrideEndpointLevelFields`
  - Deleted or renamed model `FrontloadPayloadPropertiesOverrideManifestLevelFields`
  - Deleted or renamed model `ManifestLevelPropertyBag`
  - Deleted or renamed model `Readiness`
  - Deleted or renamed model `ResourceProviderManifestPropertiesDstsConfiguration`
  - Deleted or renamed model `ResourceTypeEndpointBase`
  - Deleted or renamed model `ResourceTypeEndpointBaseDstsConfiguration`
  - Deleted or renamed model `ResourceTypeEndpointBaseFeaturesRule`
  - Deleted or renamed model `ResourceTypeEndpointDstsConfiguration`
  - Deleted or renamed model `ResourceTypeRegistrationPropertiesDstsConfiguration`
  - Deleted or renamed model `ServiceFeatureFlagAction`
  - Deleted or renamed model `ServiceTreeInfo`
  - Deleted or renamed model `NewRegionFrontloadReleaseOperations`

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
  - Added model `ResourceDeletionPolicyAndProperties`
  - Added model `ResourceDeletionPolicyProperties`
  - Added model `ResourceTypeManagedResourceGroupConfiguration`
  - Added model `WriteLockConfiguration`
  - Added enum `WriteLockState`
  - Added operation group `ManifestsOperations`

### Breaking Changes

  - Renamed enum `ResourceDeletionPolicy` to `RPaaSResourceDeletionPolicy`
  - Renamed enum `ManifestResourceDeletionPolicy` to `ResourceDeletionPolicy`
  - Method `Operations.list_by_provider_registration` changed return type from `List[OperationsDefinition]` to `OperationsPutContent`

## 1.0.0 (2026-07-29)

### Other Changes

  - First GA

## 1.0.0b1 (2026-07-08)

### Other Changes

  - Initial version
