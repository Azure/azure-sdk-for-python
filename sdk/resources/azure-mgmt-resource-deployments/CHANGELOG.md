# Release History

## 1.0.0b2 (2026-05-21)

### Features Added

  - Client `DeploymentsMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `DeploymentsMgmtClient` added method `send_request`
  - Model `DeploymentExtended` added property `system_data`
  - Added model `CloudError`
  - Added enum `CreatedByType`
  - Added model `ExtensionResource`
  - Added model `Resource`
  - Added model `SystemData`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `WhatIfOperationResult` moved instance variable `changes`, `potential_changes` and `diagnostics` under property `properties` whose type is `WhatIfOperationProperties`
  - Deleted or renamed model `DeploymentExtendedFilter`
  - Deleted or renamed model `ResourceProviderOperationDisplayProperties`
  - Deleted or renamed model `SubResource`

## 1.0.0b1 (2025-06-20)

### Other Changes

  - Initial version
