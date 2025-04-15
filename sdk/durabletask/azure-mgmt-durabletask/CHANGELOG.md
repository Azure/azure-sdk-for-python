# Release History

## 1.0.0b2 (2025-04-15)

### Features Added

  - Client `DurableTaskMgmtClient` added operation group `retention_policies`
  - Added enum `PurgeableOrchestrationState`
  - Added model `RetentionPolicy`
  - Added model `RetentionPolicyDetails`
  - Added model `RetentionPolicyProperties`
  - Added model `RetentionPoliciesOperations`
  - Method `RetentionPolicy.__init__` has a new overload `def __init__(self: None, properties: Optional[_models.RetentionPolicyProperties])`
  - Method `RetentionPolicy.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `RetentionPolicyDetails.__init__` has a new overload `def __init__(self: None, retention_period_in_days: int, orchestration_state: Optional[Union[str, _models.PurgeableOrchestrationState]])`
  - Method `RetentionPolicyDetails.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `RetentionPolicyProperties.__init__` has a new overload `def __init__(self: None, retention_policies: Optional[List[_models.RetentionPolicyDetails]])`
  - Method `RetentionPolicyProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `RetentionPoliciesOperations.begin_create_or_replace` has a new overload `def begin_create_or_replace(self: None, resource_group_name: str, scheduler_name: str, resource: RetentionPolicy, content_type: str)`
  - Method `RetentionPoliciesOperations.begin_create_or_replace` has a new overload `def begin_create_or_replace(self: None, resource_group_name: str, scheduler_name: str, resource: JSON, content_type: str)`
  - Method `RetentionPoliciesOperations.begin_create_or_replace` has a new overload `def begin_create_or_replace(self: None, resource_group_name: str, scheduler_name: str, resource: IO[bytes], content_type: str)`
  - Method `RetentionPoliciesOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, scheduler_name: str, properties: RetentionPolicy, content_type: str)`
  - Method `RetentionPoliciesOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, scheduler_name: str, properties: JSON, content_type: str)`
  - Method `RetentionPoliciesOperations.begin_update` has a new overload `def begin_update(self: None, resource_group_name: str, scheduler_name: str, properties: IO[bytes], content_type: str)`

## 1.0.0b1 (2025-03-25)

### Other Changes

  - Initial version
