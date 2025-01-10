# Release History

## 1.0.0 (2025-01-20)

### Features Added

  - Model `OperationErrorDetails` added property `timestamp`
  - Model `OperationErrorDetails` added property `azure_operation_name`
  - Model `ResourceOperationDetails` added property `timezone`
  - Model `Schedule` added property `deadline`
  - Model `Schedule` added property `timezone`
  - Method `Operation.__init__` has a new overload `def __init__(self: None, display: Optional[_models.OperationDisplay])`
  - Method `OperationErrorDetails.__init__` has a new overload `def __init__(self: None, error_code: str, error_details: str, timestamp: Optional[datetime], time_stamp: Optional[datetime], azure_operation_name: Optional[str], crp_operation_id: Optional[str])`
  - Method `ResourceOperationDetails.__init__` has a new overload `def __init__(self: None, operation_id: str, resource_id: Optional[str], op_type: Optional[Union[str, _models.ResourceOperationType]], subscription_id: Optional[str], deadline: Optional[datetime], deadline_type: Optional[Union[str, _models.DeadlineType]], state: Optional[Union[str, _models.OperationState]], timezone: Optional[str], time_zone: Optional[str], resource_operation_error: Optional[_models.ResourceOperationError], completed_at: Optional[datetime], retry_policy: Optional[_models.RetryPolicy])`
  - Method `Schedule.__init__` has a new overload `def __init__(self: None, deadline_type: Union[str, _models.DeadlineType], deadline: Optional[datetime], dead_line: Optional[datetime], timezone: Optional[str], time_zone: Optional[str])`

## 1.0.0b1 (2024-09-26)

### Other Changes

  - Initial version
