# Release History

## 1.0.0b2 (2026-05-21)

### Features Added

  - Client `DeploymentsMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `DeploymentsMgmtClient` added method `send_request`
  - Model `DeploymentExtended` added property `system_data`
  - Model `WhatIfOperationResult` added property `properties`
  - Added model `CloudError`
  - Added enum `CreatedByType`
  - Added model `ExtensionResource`
  - Added model `Resource`
  - Added model `SystemData`
  - Added model `WhatIfOperationProperties`

### Breaking Changes

  - Model `WhatIfOperationResult` deleted or renamed its instance variable `changes`
  - Model `WhatIfOperationResult` deleted or renamed its instance variable `potential_changes`
  - Model `WhatIfOperationResult` deleted or renamed its instance variable `diagnostics`
  - Deleted or renamed model `DeploymentExtendedFilter`
  - Deleted or renamed model `ResourceProviderOperationDisplayProperties`
  - Deleted or renamed model `SubResource`

## 1.0.0b1 (2025-06-20)

### Other Changes

  - Initial version
