# Release History

## 1.0.0b3 (2026-05-26)

### Features Added

  - Client `PolicyClient` added method `send_request`
  - Client `PolicyClient` added operation group `policy_enrollments`
  - Client `PolicyClient` added operation group `policy_exemptions`
  - Client `PolicyClient` added operation group `variables`
  - Client `PolicyClient` added operation group `variable_values`
  - Model `DataPolicyManifest` added property `system_data`
  - Model `ExternalEvaluationEndpointInvocationResult` added property `endpoint_kind`
  - Model `ExternalEvaluationEndpointInvocationResult` added property `policy_action`
  - Model `ExternalEvaluationEndpointInvocationResult` added property `policy_evaluation_details`
  - Model `ExternalEvaluationEndpointInvocationResult` added property `additional_info`
  - Model `PolicyTokenResponse` added property `request_details`
  - Enum `SelectorKind` added member `GROUP_PRINCIPAL_ID`
  - Enum `SelectorKind` added member `USER_PRINCIPAL_ID`
  - Added enum `AssignmentScopeValidation`
  - Added model `DataManifestResourceFunctionsDefinition`
  - Added enum `ExemptionCategory`
  - Added model `ExtensionResource`
  - Added enum `PolicyAction`
  - Added model `PolicyEnrollment`
  - Added model `PolicyEnrollmentProperties`
  - Added model `PolicyEnrollmentUpdate`
  - Added model `PolicyEnrollmentUpdateProperties`
  - Added model `PolicyExemption`
  - Added model `PolicyExemptionProperties`
  - Added model `PolicyExemptionUpdate`
  - Added model `PolicyExemptionUpdateProperties`
  - Added model `PolicyTokenEvaluatedRequestDetails`
  - Added model `PolicyVariableColumn`
  - Added model `PolicyVariableProperties`
  - Added model `PolicyVariableValueColumnValue`
  - Added model `PolicyVariableValueProperties`
  - Added model `SelfServeExemptionSettings`
  - Added model `Variable`
  - Added model `VariableValue`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `PolicyLogInfo` deleted property `policy_set_definition_display_name`/`policy_set_definition_category`/`policy_definition_display_name`/`policy_definition_group_names`/`policy_assignment_display_name`/`resource_location`/`ancestors`/`compliance_reason_code`/`policy_exemption_ids` to match actual service behavior
  - Method `PolicyAssignmentsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicyAssignmentsOperations.get_by_id` deleted or renamed its parameter `expand` of kind `positional_or_keyword`
  - Method `PolicyAssignmentsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicyAssignmentsOperations.list_for_management_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicyAssignmentsOperations.list_for_resource` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicyAssignmentsOperations.list_for_resource_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicySetDefinitionVersionsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicySetDefinitionVersionsOperations.get_at_management_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicySetDefinitionVersionsOperations.get_built_in` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicySetDefinitionVersionsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicySetDefinitionVersionsOperations.list_built_in` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicySetDefinitionVersionsOperations.list_by_management_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicySetDefinitionsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicySetDefinitionsOperations.get_at_management_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicySetDefinitionsOperations.get_built_in` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicySetDefinitionsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicySetDefinitionsOperations.list_built_in` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicySetDefinitionsOperations.list_by_management_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`

## 1.0.0b2 (2026-02-28)

### Features Added

  - Client `PolicyClient` added operation group `policy_tokens`
  - Enum `EnforcementMode` added member `ENROLL`
  - Model `ErrorResponse` added property `error`
  - Enum `OverrideKind` added member `DEFINITION_VERSION`
  - Model `PolicyAssignment` added property `assignment_type`
  - Model `PolicyAssignment` added property `instance_id`
  - Model `PolicyDefinition` added property `external_evaluation_enforcement_settings`
  - Model `PolicyDefinitionVersion` added property `external_evaluation_enforcement_settings`
  - Added enum `AssignmentType`
  - Added model `ErrorDetail`
  - Added enum `ExternalEndpointResult`
  - Added model `ExternalEvaluationEndpointInvocationResult`
  - Added model `ExternalEvaluationEndpointSettings`
  - Added model `ExternalEvaluationEnforcementSettings`
  - Added model `PolicyLogInfo`
  - Added model `PolicyTokenOperation`
  - Added model `PolicyTokenRequest`
  - Added model `PolicyTokenResponse`
  - Added enum `PolicyTokenResult`
  - Added model `ProxyResource`
  - Added model `Resource`

### Breaking Changes

  - Deleted client operation group `PolicyClient.policy_exemptions`
  - Deleted client operation group `PolicyClient.variables`
  - Deleted client operation group `PolicyClient.variable_values`
  - Model `ErrorResponse` deleted its instance variable `code`
  - Model `ErrorResponse` deleted its instance variable `message`
  - Model `ErrorResponse` deleted its instance variable `target`
  - Model `ErrorResponse` deleted its instance variable `details`
  - Model `ErrorResponse` deleted its instance variable `additional_info`
  - Property `value` of model `PolicyAssignmentListResult` is required
  - Property `value` of model `PolicyDefinitionListResult` is required
  - Property `value` of model `PolicyDefinitionVersionListResult` is required
  - Property `value` of model `PolicySetDefinitionListResult` is required
  - Property `value` of model `PolicySetDefinitionVersionListResult` is required
  - Deleted model `AssignmentScopeValidation`
  - Deleted model `ExemptionCategory`
  - Deleted model `PolicyExemption`
  - Deleted model `PolicyExemptionUpdate`
  - Deleted model `PolicyVariableColumn`
  - Deleted model `PolicyVariableValueColumnValue`
  - Deleted model `Variable`
  - Deleted model `VariableValue`

## 1.0.0b1 (2026-02-04)

### Other Changes

  - Initial version
