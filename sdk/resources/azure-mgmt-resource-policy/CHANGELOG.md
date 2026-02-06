# Release History

## 1.0.0 (2026-02-06)

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
  - Added model `PolicyTokensOperations`

### Breaking Changes

  - Deleted or renamed client operation group `PolicyClient.policy_exemptions`
  - Deleted or renamed client operation group `PolicyClient.variables`
  - Deleted or renamed client operation group `PolicyClient.variable_values`
  - Model `ErrorResponse` deleted or renamed its instance variable `code`
  - Model `ErrorResponse` deleted or renamed its instance variable `message`
  - Model `ErrorResponse` deleted or renamed its instance variable `target`
  - Model `ErrorResponse` deleted or renamed its instance variable `details`
  - Model `ErrorResponse` deleted or renamed its instance variable `additional_info`
  - Method `PolicyAssignmentListResult.__init__` removed default value `None` from its parameter `value`
  - Method `PolicyDefinitionListResult.__init__` removed default value `None` from its parameter `value`
  - Method `PolicyDefinitionVersionListResult.__init__` removed default value `None` from its parameter `value`
  - Method `PolicySetDefinitionListResult.__init__` removed default value `None` from its parameter `value`
  - Method `PolicySetDefinitionVersionListResult.__init__` removed default value `None` from its parameter `value`
  - Deleted or renamed model `AssignmentScopeValidation`
  - Deleted or renamed model `ExemptionCategory`
  - Deleted or renamed model `PolicyExemption`
  - Deleted or renamed model `PolicyExemptionUpdate`
  - Deleted or renamed model `PolicyVariableColumn`
  - Deleted or renamed model `PolicyVariableValueColumnValue`
  - Deleted or renamed model `Variable`
  - Deleted or renamed model `VariableValue`
  - Deleted or renamed model `PolicyExemptionsOperations`
  - Deleted or renamed model `VariableValuesOperations`
  - Deleted or renamed model `VariablesOperations`

## 1.0.0b1 (2026-02-04)

### Other Changes

  - Initial version