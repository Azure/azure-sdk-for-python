# Release History

## 1.0.0 (2026-05-26)

### Features Added

  - Client `PolicyClient` added method `send_request`
  - Added model `ExtensionResource`

### Breaking Changes

  - Deleted or renamed client operation group `PolicyClient.data_policy_manifests`
  - Deleted or renamed model `Alias`
  - Deleted or renamed model `AliasPath`
  - Deleted or renamed model `AliasPathAttributes`
  - Deleted or renamed model `AliasPathMetadata`
  - Deleted or renamed model `AliasPathTokenType`
  - Deleted or renamed model `AliasPattern`
  - Deleted or renamed model `AliasPatternType`
  - Deleted or renamed model `AliasType`
  - Deleted or renamed model `DataEffect`
  - Deleted or renamed model `DataManifestCustomResourceFunctionDefinition`
  - Deleted or renamed model `DataPolicyManifest`
  - Deleted or renamed model `ResourceTypeAliases`
  - Method `PolicyAssignmentsOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicyAssignmentsOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicyAssignmentsOperations.list_for_management_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicyAssignmentsOperations.list_for_resource` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `PolicyAssignmentsOperations.list_for_resource_group` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Deleted or renamed method `PolicyAssignmentsOperations.create_by_id`
  - Deleted or renamed method `PolicyAssignmentsOperations.delete_by_id`
  - Deleted or renamed method `PolicyAssignmentsOperations.get_by_id`
  - Deleted or renamed method `PolicyAssignmentsOperations.update_by_id`
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
  - Deleted or renamed model `DataPolicyManifestsOperations`

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
