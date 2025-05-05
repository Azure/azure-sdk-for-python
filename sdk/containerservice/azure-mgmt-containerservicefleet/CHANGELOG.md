# Release History

## 3.1.0 (2025-04-10)

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
