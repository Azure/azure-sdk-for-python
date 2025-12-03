# Release History

## 4.0.0b2 (2025-12-03)

### Features Added

  - Model `ContainerServiceFleetMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `ContainerServiceFleetMgmtClient` added operation group `fleet_managed_namespaces`
  - Added enum `AdoptionPolicy`
  - Added model `Affinity`
  - Added model `ClusterAffinity`
  - Added model `ClusterResourcePlacementSpec`
  - Added model `ClusterSelector`
  - Added model `ClusterSelectorTerm`
  - Added enum `DeletePolicy`
  - Added model `FleetManagedNamespace`
  - Added model `FleetManagedNamespacePatch`
  - Added model `FleetManagedNamespaceProperties`
  - Added enum `FleetManagedNamespaceProvisioningState`
  - Added model `FleetManagedNamespaceStatus`
  - Added model `LabelSelector`
  - Added enum `LabelSelectorOperator`
  - Added model `LabelSelectorRequirement`
  - Added model `ManagedNamespaceProperties`
  - Added model `NetworkPolicy`
  - Added model `PlacementPolicy`
  - Added model `PlacementProfile`
  - Added enum `PlacementType`
  - Added enum `PolicyRule`
  - Added model `PropagationPolicy`
  - Added enum `PropagationType`
  - Added model `PropertySelector`
  - Added enum `PropertySelectorOperator`
  - Added model `PropertySelectorRequirement`
  - Added model `ResourceQuota`
  - Added enum `TaintEffect`
  - Added model `Toleration`
  - Added enum `TolerationOperator`
  - Added model `FleetManagedNamespacesOperations`

## 4.0.0b1 (2025-08-04)

### Features Added

  - Client `ContainerServiceFleetMgmtClient` added operation group `gates`
  - Model `UpdateGroup` added property `before_gates`
  - Model `UpdateGroup` added property `after_gates`
  - Model `UpdateGroupStatus` added property `before_gates`
  - Model `UpdateGroupStatus` added property `after_gates`
  - Model `UpdateStage` added property `before_gates`
  - Model `UpdateStage` added property `after_gates`
  - Model `UpdateStageStatus` added property `before_gates`
  - Model `UpdateStageStatus` added property `after_gates`
  - Enum `UpdateState` added member `PENDING`
  - Enum `UpgradeChannel` added member `TARGET_KUBERNETES_VERSION`
  - Added model `FleetMemberUpdateProperties`
  - Added model `Gate`
  - Added model `GateConfiguration`
  - Added model `GatePatch`
  - Added model `GatePatchProperties`
  - Added model `GateProperties`
  - Added enum `GateProvisioningState`
  - Added enum `GateState`
  - Added model `GateTarget`
  - Added enum `GateType`
  - Added enum `Timing`
  - Added model `UpdateRunGateStatus`
  - Added model `UpdateRunGateTargetProperties`
  - Added operation group `GatesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. And please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for mgration.
  - Model `FleetMemberUpdate` deleted or renamed its instance variable `group`
  - Method `AutoUpgradeProfilesOperations.begin_create_or_update` renamed positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `AutoUpgradeProfilesOperations.begin_delete` renamed positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `FleetMembersOperations.begin_create` renamed positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `FleetMembersOperations.begin_delete` renamed positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `FleetMembersOperations.begin_update` renamed positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `FleetUpdateStrategiesOperations.begin_create_or_update` renamed positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `FleetUpdateStrategiesOperations.begin_delete` renamed positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `FleetsOperations.begin_create_or_update` renamed positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `FleetsOperations.begin_delete` renamed positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `FleetsOperations.begin_update` renamed positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `UpdateRunsOperations.begin_create_or_update` renamed positional_or_keyword parameters `if_match`/`if_none_match` to keyword_only parameters `etag`/`match_condition`
  - Method `UpdateRunsOperations.begin_delete` renamed positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `UpdateRunsOperations.begin_skip` renamed positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `UpdateRunsOperations.begin_start` renamed positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`
  - Method `UpdateRunsOperations.begin_stop` renamed positional_or_keyword parameter `if_match` to keyword_only parameters `etag`/`match_condition`

## 3.1.0 (2025-05-08)

### Features Added

  - Client `ContainerServiceFleetMgmtClient` added operation group `auto_upgrade_profiles`
  - Client `ContainerServiceFleetMgmtClient` added operation group `auto_upgrade_profile_operations`
  - Model `APIServerAccessProfile` added property `enable_vnet_integration`
  - Model `APIServerAccessProfile` added property `subnet_id`
  - Model `Fleet` added property `status`
  - Model `FleetMember` added property `status`
  - Model `NodeImageSelection` added property `custom_node_image_versions`
  - Enum `NodeImageSelectionType` added member `CUSTOM`
  - Model `UpdateRun` added property `auto_upgrade_profile_id`
  - Added enum `AutoUpgradeLastTriggerStatus`
  - Added model `AutoUpgradeNodeImageSelection`
  - Added enum `AutoUpgradeNodeImageSelectionType`
  - Added model `AutoUpgradeProfile`
  - Added model `AutoUpgradeProfileListResult`
  - Added enum `AutoUpgradeProfileProvisioningState`
  - Added model `AutoUpgradeProfileStatus`
  - Added model `FleetMemberStatus`
  - Added model `FleetStatus`
  - Added model `GenerateResponse`
  - Added enum `UpgradeChannel`
  - Added operation group `AutoUpgradeProfileOperationsOperations`
  - Added operation group `AutoUpgradeProfilesOperations`

## 3.0.0 (2024-10-31)

### Breaking Changes

- This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.

## 2.1.0 (2024-10-21)

### Features Added

  - Added operation group AutoUpgradeProfilesOperations
  - Model NodeImageSelection has a new parameter custom_node_image_versions

## 2.0.0 (2024-05-20)

### Breaking Changes

  - Model APIServerAccessProfile no longer has parameter enable_vnet_integration
  - Model APIServerAccessProfile no longer has parameter subnet_id

## 1.1.0 (2024-04-03)

### Features Added

  - Added operation UpdateRunsOperations.begin_skip
  - Model Fleet has a new parameter hub_profile

## 1.0.0 (2023-10-27)

### Breaking Changes

  - Model Fleet no longer has parameter hub_profile

## 1.0.0b3 (2023-10-23)

### Features Added

  - Added operation group FleetUpdateStrategiesOperations
  - Model AgentProfile has a new parameter vm_size
  - Model FleetHubProfile has a new parameter portal_fqdn
  - Model UpdateRun has a new parameter update_strategy_id

## 1.0.0b2 (2023-09-12)

### Features Added

  - Model Fleet has a new parameter identity
  - Model FleetHubProfile has a new parameter agent_profile
  - Model FleetHubProfile has a new parameter api_server_access_profile
  - Model FleetPatch has a new parameter identity
  - Model ManagedClusterUpdate has a new parameter node_image_selection
  - Model MemberUpdateStatus has a new parameter message
  - Model UpdateRunStatus has a new parameter node_image_selection

### Breaking Changes

  - Renamed operation FleetMembersOperations.update to FleetMembersOperations.begin_update
  - Renamed operation FleetsOperations.update to FleetsOperations.begin_update

## 1.0.0b1 (2023-06-16)

* Initial Release
