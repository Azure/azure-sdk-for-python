# Release History

## 1.0.0 (2026-05-26)

### Features Added

  - Client `PolicyClient` added method `send_request`
  - Added model `ExtensionResource`

### Breaking Changes

  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Removed operation group `PolicyClient.data_policy_manifests` (`DataPolicyManifestsOperations`); this API is gated by `Versions.v2025_11_01` and is expected to return in a later API upgrade.
  - Removed related models `Alias`, `AliasPath`, `AliasPathAttributes`, `AliasPathMetadata`, `AliasPathTokenType`, `AliasPattern`, `AliasPatternType`, `AliasType`, `DataEffect`, `DataManifestCustomResourceFunctionDefinition`, `DataPolicyManifest`, and `ResourceTypeAliases`; these are tied to the gated `data_policy_manifests` API and are expected to return in a later API upgrade.
  - Methods `PolicyAssignmentsOperations.get`, `PolicyAssignmentsOperations.list`, `PolicyAssignmentsOperations.list_for_management_group`, `PolicyAssignmentsOperations.list_for_resource`, and `PolicyAssignmentsOperations.list_for_resource_group` changed parameter `expand` from `positional_or_keyword` to `keyword_only`.
  - Removed methods `PolicyAssignmentsOperations.create_by_id`, `PolicyAssignmentsOperations.delete_by_id`, `PolicyAssignmentsOperations.get_by_id`, and `PolicyAssignmentsOperations.update_by_id`; this remains visible because the SDK PR predates the mitigation in https://github.com/Azure/azure-rest-api-specs/pull/43501.
  - Methods `PolicySetDefinitionVersionsOperations.get`, `PolicySetDefinitionVersionsOperations.get_at_management_group`, `PolicySetDefinitionVersionsOperations.get_built_in`, `PolicySetDefinitionVersionsOperations.list`, `PolicySetDefinitionVersionsOperations.list_built_in`, and `PolicySetDefinitionVersionsOperations.list_by_management_group` changed parameter `expand` from `positional_or_keyword` to `keyword_only`.
  - Methods `PolicySetDefinitionsOperations.get`, `PolicySetDefinitionsOperations.get_at_management_group`, `PolicySetDefinitionsOperations.get_built_in`, `PolicySetDefinitionsOperations.list`, `PolicySetDefinitionsOperations.list_built_in`, and `PolicySetDefinitionsOperations.list_by_management_group` changed parameter `expand` from `positional_or_keyword` to `keyword_only`.

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
