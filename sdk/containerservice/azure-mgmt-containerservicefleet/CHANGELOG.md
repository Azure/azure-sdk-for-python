# Release History

## 3.0.0 (2024-10-31)

### Breaking Changes

  - Deleted or renamed client operation group `ContainerServiceFleetMgmtClient.auto_upgrade_profiles`
  - Model `APIServerAccessProfile` deleted or renamed its instance variable `enable_vnet_integration`
  - Model `APIServerAccessProfile` deleted or renamed its instance variable `subnet_id`
  - Model `NodeImageSelection` deleted or renamed its instance variable `custom_node_image_versions`
  - Deleted or renamed enum value `NodeImageSelectionType.CUSTOM`
  - Deleted or renamed model `AutoUpgradeNodeImageSelection`
  - Deleted or renamed model `AutoUpgradeNodeImageSelectionType`
  - Deleted or renamed model `AutoUpgradeProfile`
  - Deleted or renamed model `AutoUpgradeProfileProvisioningState`
  - Deleted or renamed model `UpgradeChannel`
  - Deleted or renamed model `AutoUpgradeProfilesOperations`

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
