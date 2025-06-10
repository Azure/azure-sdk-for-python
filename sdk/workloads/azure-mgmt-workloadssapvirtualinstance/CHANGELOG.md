# Release History

## 1.0.0 (2025-04-30)

### Features Added

  - Added operation SAPApplicationServerInstancesOperations.begin_start
  - Added operation SAPApplicationServerInstancesOperations.begin_stop
  - Added operation SAPDatabaseInstancesOperations.begin_start
  - Added operation SAPDatabaseInstancesOperations.begin_stop
  - Added operation SAPVirtualInstancesOperations.get_availability_zone_details
  - Added operation SAPVirtualInstancesOperations.get_disk_configurations
  - Added operation SAPVirtualInstancesOperations.get_sap_supported_sku
  - Added operation SAPVirtualInstancesOperations.get_sizing_recommendations
  - Added operation group SAPCentralServerInstancesOperations
  - Model OperationStatusResult has a new parameter resource_id

### Breaking Changes

  - Operation SAPApplicationServerInstancesOperations.begin_create has a new required parameter resource
  - Operation SAPApplicationServerInstancesOperations.begin_create no longer has parameter body
  - Operation SAPApplicationServerInstancesOperations.update has a new required parameter properties
  - Operation SAPApplicationServerInstancesOperations.update no longer has parameter body
  - Operation SAPDatabaseInstancesOperations.begin_create has a new required parameter resource
  - Operation SAPDatabaseInstancesOperations.begin_create no longer has parameter body
  - Operation SAPDatabaseInstancesOperations.update has a new required parameter properties
  - Operation SAPDatabaseInstancesOperations.update no longer has parameter body
  - Operation SAPVirtualInstancesOperations.begin_create has a new required parameter resource
  - Operation SAPVirtualInstancesOperations.begin_create no longer has parameter body
  - Operation SAPVirtualInstancesOperations.begin_update has a new required parameter properties
  - Operation SAPVirtualInstancesOperations.begin_update no longer has parameter body
  - Removed operation SAPApplicationServerInstancesOperations.begin_start_instance
  - Removed operation SAPApplicationServerInstancesOperations.begin_stop_instance
  - Removed operation SAPDatabaseInstancesOperations.begin_start_instance
  - Removed operation SAPDatabaseInstancesOperations.begin_stop_instance
  - Removed operation group SAPCentralInstancesOperations
  - Removed operation group WorkloadsSapVirtualInstanceMgmtClientOperationsMixin

## 1.0.0b1 (2024-03-21)

* Initial Release
