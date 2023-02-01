# Release History

## 1.0.0b4 (2022-11-24)

### Features Added

  - Added operation group CheckNameAvailabilityOperations
  - Model DevBoxDefinition has a new parameter hibernate_support
  - Model DevBoxDefinitionProperties has a new parameter hibernate_support
  - Model DevBoxDefinitionUpdate has a new parameter hibernate_support
  - Model DevBoxDefinitionUpdateProperties has a new parameter hibernate_support
  - Model DevCenter has a new parameter dev_center_uri
  - Model Project has a new parameter dev_center_uri
  - Model ProjectProperties has a new parameter dev_center_uri

### Breaking Changes

  - Renamed operation NetworkConnectionsOperations.run_health_checks to NetworkConnectionsOperations.begin_run_health_checks

## 1.0.0b3 (2022-11-08)

### Features Added

  - Model Catalog has a new parameter sync_state
  - Model CatalogProperties has a new parameter sync_state
  - Model OperationStatus has a new parameter operations
  - Model OperationStatus has a new parameter resource_id

### Breaking Changes

  - Client name is changed from `DevCenterClient` to `DevCenterMgmtClient`
  - Parameter status of model OperationStatus is now required

## 1.0.0b2 (2022-09-29)

### Features Added

  - Added operation group ProjectAllowedEnvironmentTypesOperations

## 1.0.0b1 (2022-08-15)

* Initial Release
