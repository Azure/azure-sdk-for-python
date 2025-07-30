# Release History

## 4.0.0b1 (2025-07-30)

### Features Added

  - Client `ContainerServiceFleetMgmtClient` added method `send_request`
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
  - Model `AutoUpgradeProfilesOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `AutoUpgradeProfilesOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `AutoUpgradeProfilesOperations` added parameter `etag` in method `begin_delete`
  - Model `AutoUpgradeProfilesOperations` added parameter `match_condition` in method `begin_delete`
  - Model `FleetMembersOperations` added parameter `etag` in method `begin_create`
  - Model `FleetMembersOperations` added parameter `match_condition` in method `begin_create`
  - Model `FleetMembersOperations` added parameter `etag` in method `begin_delete`
  - Model `FleetMembersOperations` added parameter `match_condition` in method `begin_delete`
  - Model `FleetMembersOperations` added parameter `etag` in method `begin_update`
  - Model `FleetMembersOperations` added parameter `match_condition` in method `begin_update`
  - Model `FleetUpdateStrategiesOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `FleetUpdateStrategiesOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `FleetUpdateStrategiesOperations` added parameter `etag` in method `begin_delete`
  - Model `FleetUpdateStrategiesOperations` added parameter `match_condition` in method `begin_delete`
  - Model `FleetsOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `FleetsOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `FleetsOperations` added parameter `etag` in method `begin_delete`
  - Model `FleetsOperations` added parameter `match_condition` in method `begin_delete`
  - Model `FleetsOperations` added parameter `etag` in method `begin_update`
  - Model `FleetsOperations` added parameter `match_condition` in method `begin_update`
  - Model `UpdateRunsOperations` added parameter `etag` in method `begin_create_or_update`
  - Model `UpdateRunsOperations` added parameter `match_condition` in method `begin_create_or_update`
  - Model `UpdateRunsOperations` added parameter `etag` in method `begin_delete`
  - Model `UpdateRunsOperations` added parameter `match_condition` in method `begin_delete`
  - Model `UpdateRunsOperations` added parameter `etag` in method `begin_skip`
  - Model `UpdateRunsOperations` added parameter `match_condition` in method `begin_skip`
  - Model `UpdateRunsOperations` added parameter `etag` in method `begin_start`
  - Model `UpdateRunsOperations` added parameter `match_condition` in method `begin_start`
  - Model `UpdateRunsOperations` added parameter `etag` in method `begin_stop`
  - Model `UpdateRunsOperations` added parameter `match_condition` in method `begin_stop`
  - Added model `GatesOperations`

### Breaking Changes

  - Model `FleetMemberUpdate` deleted or renamed its instance variable `group`
  - Method `AutoUpgradeProfilesOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `AutoUpgradeProfilesOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `AutoUpgradeProfilesOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `FleetMembersOperations.begin_create` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `FleetMembersOperations.begin_create` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `FleetMembersOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `FleetMembersOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `FleetUpdateStrategiesOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `FleetUpdateStrategiesOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `FleetUpdateStrategiesOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `FleetsOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `FleetsOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `FleetsOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `FleetsOperations.begin_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `UpdateRunsOperations.begin_create_or_update` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `UpdateRunsOperations.begin_create_or_update` deleted or renamed its parameter `if_none_match` of kind `positional_or_keyword`
  - Method `UpdateRunsOperations.begin_delete` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `UpdateRunsOperations.begin_skip` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `UpdateRunsOperations.begin_start` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `UpdateRunsOperations.begin_stop` deleted or renamed its parameter `if_match` of kind `positional_or_keyword`
  - Method `FleetUpdateStrategiesOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'fleet_name', 'update_strategy_name', 'resource', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'fleet_name', 'update_strategy_name', 'resource', 'etag', 'match_condition', 'kwargs']`
  - Method `FleetsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'fleet_name', 'resource', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'fleet_name', 'resource', 'etag', 'match_condition', 'kwargs']`
  - Method `AutoUpgradeProfilesOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'fleet_name', 'auto_upgrade_profile_name', 'resource', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'fleet_name', 'auto_upgrade_profile_name', 'resource', 'etag', 'match_condition', 'kwargs']`
  - Method `UpdateRunsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'fleet_name', 'update_run_name', 'resource', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'fleet_name', 'update_run_name', 'resource', 'etag', 'match_condition', 'kwargs']`
  - Method `FleetMembersOperations.begin_create` re-ordered its parameters from `['self', 'resource_group_name', 'fleet_name', 'fleet_member_name', 'resource', 'if_match', 'if_none_match', 'kwargs']` to `['self', 'resource_group_name', 'fleet_name', 'fleet_member_name', 'resource', 'etag', 'match_condition', 'kwargs']`

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
