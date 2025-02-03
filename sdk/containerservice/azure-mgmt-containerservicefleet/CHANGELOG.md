# Release History

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
