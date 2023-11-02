# Release History

## 1.1.0b1 (2023-10-23)

### Features Added

  - Added operation CatalogsOperations.begin_connect
  - Added operation CatalogsOperations.get_sync_error_details
  - Added operation group CatalogDevBoxDefinitionsOperations
  - Added operation group CustomizationTasksOperations
  - Added operation group EnvironmentDefinitionsOperations
  - Model AllowedEnvironmentType has a new parameter display_name
  - Model Catalog has a new parameter connection_state
  - Model Catalog has a new parameter last_connection_time
  - Model Catalog has a new parameter last_sync_stats
  - Model Catalog has a new parameter sync_type
  - Model CatalogProperties has a new parameter connection_state
  - Model CatalogProperties has a new parameter last_connection_time
  - Model CatalogProperties has a new parameter last_sync_stats
  - Model CatalogProperties has a new parameter sync_type
  - Model CatalogUpdate has a new parameter sync_type
  - Model CatalogUpdateProperties has a new parameter sync_type
  - Model DevBoxDefinition has a new parameter validation_status
  - Model DevBoxDefinitionProperties has a new parameter validation_status
  - Model DevCenter has a new parameter display_name
  - Model DevCenter has a new parameter encryption
  - Model DevCenterUpdate has a new parameter display_name
  - Model DevCenterUpdate has a new parameter encryption
  - Model EnvironmentType has a new parameter display_name
  - Model EnvironmentTypeUpdate has a new parameter display_name
  - Model Pool has a new parameter dev_box_count
  - Model Pool has a new parameter display_name
  - Model Pool has a new parameter managed_virtual_network_regions
  - Model Pool has a new parameter single_sign_on_status
  - Model Pool has a new parameter virtual_network_type
  - Model PoolProperties has a new parameter dev_box_count
  - Model PoolProperties has a new parameter display_name
  - Model PoolProperties has a new parameter managed_virtual_network_regions
  - Model PoolProperties has a new parameter single_sign_on_status
  - Model PoolProperties has a new parameter virtual_network_type
  - Model PoolUpdate has a new parameter display_name
  - Model PoolUpdate has a new parameter managed_virtual_network_regions
  - Model PoolUpdate has a new parameter single_sign_on_status
  - Model PoolUpdate has a new parameter virtual_network_type
  - Model PoolUpdateProperties has a new parameter display_name
  - Model PoolUpdateProperties has a new parameter managed_virtual_network_regions
  - Model PoolUpdateProperties has a new parameter single_sign_on_status
  - Model PoolUpdateProperties has a new parameter virtual_network_type
  - Model Project has a new parameter display_name
  - Model ProjectEnvironmentType has a new parameter display_name
  - Model ProjectEnvironmentType has a new parameter environment_count
  - Model ProjectEnvironmentTypeProperties has a new parameter display_name
  - Model ProjectEnvironmentTypeProperties has a new parameter environment_count
  - Model ProjectProperties has a new parameter display_name
  - Model ProjectUpdate has a new parameter display_name
  - Model ProjectUpdateProperties has a new parameter display_name
  - Model Usage has a new parameter id

## 1.0.0 (2023-05-20)

### Features Added

  - Added operation NetworkConnectionsOperations.list_outbound_network_dependencies_endpoints
  - Added operation PoolsOperations.begin_run_health_checks
  - Model Image has a new parameter hibernate_support
  - Model Pool has a new parameter health_status
  - Model Pool has a new parameter health_status_details
  - Model Pool has a new parameter stop_on_disconnect
  - Model PoolProperties has a new parameter health_status
  - Model PoolProperties has a new parameter health_status_details
  - Model PoolProperties has a new parameter stop_on_disconnect
  - Model PoolUpdate has a new parameter stop_on_disconnect
  - Model PoolUpdateProperties has a new parameter stop_on_disconnect
  - Model Project has a new parameter max_dev_boxes_per_user
  - Model ProjectProperties has a new parameter max_dev_boxes_per_user
  - Model ProjectUpdate has a new parameter max_dev_boxes_per_user
  - Model ProjectUpdateProperties has a new parameter max_dev_boxes_per_user

### Breaking Changes

  - Model ImageReference no longer has parameter offer
  - Model ImageReference no longer has parameter publisher
  - Model ImageReference no longer has parameter sku

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
