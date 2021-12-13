# Release History

## 1.0.0b3 (2021-12-13)

**Features**

  - Model ConfigurationProfileAssignmentProperties has a new parameter profile_overrides
  - Model ConfigurationProfileAssignmentProperties has a new parameter status
  - Model ConfigurationProfileAssignment has a new parameter system_data
  - Model Operation has a new parameter action_type
  - Model Operation has a new parameter origin
  - Added operation ConfigurationProfileAssignmentsOperations.create_or_update
  - Added operation group BestPracticesOperations
  - Added operation group BestPracticesVersionsOperations
  - Added operation group ConfigurationProfilesVersionsOperations
  - Added operation group ReportsOperations
  - Added operation group ConfigurationProfilesOperations

**Breaking changes**

  - Model ConfigurationProfileAssignmentProperties no longer has parameter account_id
  - Model ConfigurationProfileAssignmentProperties no longer has parameter provisioning_status
  - Model ConfigurationProfileAssignmentProperties no longer has parameter configuration_profile_preference_id
  - Model ConfigurationProfileAssignmentProperties no longer has parameter compliance
  - Model Operation no longer has parameter status_code
  - Removed operation ConfigurationProfileAssignmentsOperations.begin_create_or_update
  - Removed operation group AccountsOperations
  - Removed operation group ConfigurationProfilePreferencesOperations

## 1.0.0b2 (2021-04-21)

 - Fix dependency for package

## 1.0.0b1 (2020-09-10)

* Initial Release
