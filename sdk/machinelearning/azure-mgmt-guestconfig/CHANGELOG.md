# Release History

## 1.0.0b3 (2026-07-07)

### Features Added

  - Client `GuestConfigurationClient` added parameter `cloud_setting` in method `__init__`
  - Client `GuestConfigurationClient` added method `send_request`
  - Client `GuestConfigurationClient` added operation group `guest_configuration_connected_vmwarev_sphere_assignments`
  - Client `GuestConfigurationClient` added operation group `guest_configuration_connected_vmwarev_sphere_assignments_reports`
  - Model `GuestConfigurationAssignmentReportList` added property `next_link`
  - Model `GuestConfigurationNavigation` added property `content_managed_identity`
  - Model `Operation` moved instance variable `status_code` under property `properties` whose type is `OperationProperties`
  - Operation group `GuestConfigurationAssignmentsVMSSOperations` added method `create_or_update`
  - Added operation group `GuestConfigurationConnectedVMwarevSphereAssignmentsOperations`
  - Added operation group `GuestConfigurationConnectedVMwarevSphereAssignmentsReportsOperations`

### Other Changes

  - Deleted model `GuestConfigurationAssignmentList`/`OperationList`/`Resource` which actually were not used by SDK users

## 1.0.0b2 (2022-11-04)

### Features Added

  - Added operation GuestConfigurationAssignmentsOperations.rg_list
  - Added operation GuestConfigurationAssignmentsOperations.subscription_list
  - Added operation group GuestConfigurationAssignmentReportsVMSSOperations
  - Added operation group GuestConfigurationAssignmentsVMSSOperations
  - Model GuestConfigurationAssignment has a new parameter system_data
  - Model GuestConfigurationAssignmentProperties has a new parameter parameter_hash
  - Model GuestConfigurationAssignmentProperties has a new parameter resource_type
  - Model GuestConfigurationAssignmentProperties has a new parameter vmss_vm_list
  - Model GuestConfigurationAssignmentReportProperties has a new parameter vmss_resource_id
  - Model GuestConfigurationNavigation has a new parameter assignment_source
  - Model GuestConfigurationNavigation has a new parameter configuration_protected_parameter
  - Model GuestConfigurationNavigation has a new parameter content_type

## 1.0.0b1 (2021-07-13)

* Initial Release

