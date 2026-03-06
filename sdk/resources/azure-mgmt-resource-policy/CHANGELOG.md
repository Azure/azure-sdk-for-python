# Release History

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
