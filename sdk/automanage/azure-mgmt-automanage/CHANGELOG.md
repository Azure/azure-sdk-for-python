# Release History

## 2.0.0b1 (2022-12-14)

### Features Added

  - Model BestPractice has a new parameter properties
  - Model Report has a new parameter properties
  - Model ServicePrincipal has a new parameter properties

### Breaking Changes

  - Model BestPractice no longer has parameter configuration
  - Model Report no longer has parameter configuration_profile
  - Model Report no longer has parameter duration
  - Model Report no longer has parameter end_time
  - Model Report no longer has parameter error
  - Model Report no longer has parameter last_modified_time
  - Model Report no longer has parameter report_format_version
  - Model Report no longer has parameter resources
  - Model Report no longer has parameter start_time
  - Model Report no longer has parameter status
  - Model Report no longer has parameter type_properties_type
  - Model ServicePrincipal no longer has parameter authorization_set
  - Model ServicePrincipal no longer has parameter service_principal_id

## 1.0.0 (2022-08-02)

**Features**

  - Added operation ConfigurationProfileAssignmentsOperations.create_or_update
  - Added operation ConfigurationProfileAssignmentsOperations.list_by_cluster_name
  - Added operation ConfigurationProfileAssignmentsOperations.list_by_machine_name
  - Added operation ConfigurationProfileAssignmentsOperations.list_by_virtual_machines
  - Added operation group BestPracticesOperations
  - Added operation group BestPracticesVersionsOperations
  - Added operation group ConfigurationProfileHCIAssignmentsOperations
  - Added operation group ConfigurationProfileHCRPAssignmentsOperations
  - Added operation group ConfigurationProfilesOperations
  - Added operation group ConfigurationProfilesVersionsOperations
  - Added operation group HCIReportsOperations
  - Added operation group HCRPReportsOperations
  - Added operation group ReportsOperations
  - Added operation group ServicePrincipalsOperations
  - Model ConfigurationProfileAssignment has a new parameter managed_by
  - Model ConfigurationProfileAssignment has a new parameter system_data
  - Model ConfigurationProfileAssignmentProperties has a new parameter status
  - Model Operation has a new parameter action_type
  - Model Operation has a new parameter origin

**Breaking changes**

  - Model ConfigurationProfileAssignmentProperties no longer has parameter account_id
  - Model ConfigurationProfileAssignmentProperties no longer has parameter compliance
  - Model ConfigurationProfileAssignmentProperties no longer has parameter configuration_profile_preference_id
  - Model ConfigurationProfileAssignmentProperties no longer has parameter provisioning_status
  - Model Operation no longer has parameter status_code
  - Removed operation ConfigurationProfileAssignmentsOperations.begin_create_or_update
  - Removed operation group AccountsOperations
  - Removed operation group ConfigurationProfilePreferencesOperations

## 1.0.0b2 (2021-04-21)

 - Fix dependency for package

## 1.0.0b1 (2020-09-10)

* Initial Release
