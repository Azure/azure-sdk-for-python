# Release History

## 1.0.0 (2024-12-22)

### Features Added

  - Client `PlaywrightTestingMgmtClient` added method `send_request`
  - Client `PlaywrightTestingMgmtClient` added operation group `account_quotas`
  - Model `AccountProperties` added property `local_auth`
  - Model `AccountUpdateProperties` added property `local_auth`
  - Enum `FreeTrialState` added member `NOT_ELIGIBLE`
  - Enum `FreeTrialState` added member `NOT_REGISTERED`
  - Enum `ProvisioningState` added member `CREATING`
  - Enum `QuotaNames` added member `REPORTING`
  - Model `QuotaProperties` added property `offering_type`
  - Added model `AccountFreeTrialProperties`
  - Added model `AccountQuota`
  - Added model `AccountQuotaProperties`
  - Added enum `CheckNameAvailabilityReason`
  - Added model `CheckNameAvailabilityRequest`
  - Added model `CheckNameAvailabilityResponse`
  - Added enum `OfferingType`
  - Model `AccountsOperations` added method `check_name_availability`
  - Added model `AccountQuotasOperations`
  - Method `Account.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]], properties: Optional[_models.AccountProperties])`
  - Method `Account.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `Account.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]])`
  - Method `Account.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `AccountProperties.__init__` has a new overload `def __init__(self: None, regional_affinity: Optional[Union[str, _models.EnablementStatus]], scalable_execution: Optional[Union[str, _models.EnablementStatus]], reporting: Optional[Union[str, _models.EnablementStatus]], local_auth: Optional[Union[str, _models.EnablementStatus]])`
  - Method `AccountProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `AccountUpdate.__init__` has a new overload `def __init__(self: None, tags: Optional[Dict[str, str]], properties: Optional[_models.AccountUpdateProperties])`
  - Method `AccountUpdate.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `AccountUpdateProperties.__init__` has a new overload `def __init__(self: None, regional_affinity: Optional[Union[str, _models.EnablementStatus]], scalable_execution: Optional[Union[str, _models.EnablementStatus]], reporting: Optional[Union[str, _models.EnablementStatus]], local_auth: Optional[Union[str, _models.EnablementStatus]])`
  - Method `AccountUpdateProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `ErrorResponse.__init__` has a new overload `def __init__(self: None, error: Optional[_models.ErrorDetail])`
  - Method `ErrorResponse.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `Operation.__init__` has a new overload `def __init__(self: None, display: Optional[_models.OperationDisplay])`
  - Method `Operation.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `Quota.__init__` has a new overload `def __init__(self: None, properties: Optional[_models.QuotaProperties])`
  - Method `Quota.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `QuotaProperties.__init__` has a new overload `def __init__(self: None, free_trial: Optional[_models.FreeTrialProperties])`
  - Method `QuotaProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `SystemData.__init__` has a new overload `def __init__(self: None, created_by: Optional[str], created_by_type: Optional[Union[str, _models.CreatedByType]], created_at: Optional[datetime], last_modified_by: Optional[str], last_modified_by_type: Optional[Union[str, _models.CreatedByType]], last_modified_at: Optional[datetime])`
  - Method `SystemData.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `TrackedResource.__init__` has a new overload `def __init__(self: None, location: str, tags: Optional[Dict[str, str]])`
  - Method `TrackedResource.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `AccountQuota.__init__` has a new overload `def __init__(self: None, properties: Optional[_models.AccountQuotaProperties])`
  - Method `AccountQuota.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `AccountQuotaProperties.__init__` has a new overload `def __init__(self: None, free_trial: Optional[_models.AccountFreeTrialProperties])`
  - Method `AccountQuotaProperties.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `CheckNameAvailabilityRequest.__init__` has a new overload `def __init__(self: None, name: Optional[str], type: Optional[str])`
  - Method `CheckNameAvailabilityRequest.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `CheckNameAvailabilityResponse.__init__` has a new overload `def __init__(self: None, name_available: Optional[bool], reason: Optional[Union[str, _models.CheckNameAvailabilityReason]], message: Optional[str])`
  - Method `CheckNameAvailabilityResponse.__init__` has a new overload `def __init__(self: None, mapping: Mapping[str, Any])`
  - Method `AccountsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, account_name: str, resource: Account, content_type: str)`
  - Method `AccountsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, account_name: str, resource: IO[bytes], content_type: str)`
  - Method `AccountsOperations.begin_create_or_update` has a new overload `def begin_create_or_update(self: None, resource_group_name: str, account_name: str, resource: JSON, content_type: str)`
  - Method `AccountsOperations.update` has a new overload `def update(self: None, resource_group_name: str, account_name: str, properties: AccountUpdate, content_type: str)`
  - Method `AccountsOperations.update` has a new overload `def update(self: None, resource_group_name: str, account_name: str, properties: IO[bytes], content_type: str)`
  - Method `AccountsOperations.update` has a new overload `def update(self: None, resource_group_name: str, account_name: str, properties: JSON, content_type: str)`
  - Method `AccountsOperations.check_name_availability` has a new overload `def check_name_availability(self: None, body: CheckNameAvailabilityRequest, content_type: str)`
  - Method `AccountsOperations.check_name_availability` has a new overload `def check_name_availability(self: None, body: JSON, content_type: str)`
  - Method `AccountsOperations.check_name_availability` has a new overload `def check_name_availability(self: None, body: IO[bytes], content_type: str)`

### Breaking Changes

  - Model `Account` deleted or renamed its instance variable `additional_properties`
  - Model `AccountProperties` deleted or renamed its instance variable `additional_properties`
  - Model `AccountUpdate` deleted or renamed its instance variable `additional_properties`
  - Model `AccountUpdateProperties` deleted or renamed its instance variable `additional_properties`
  - Model `ErrorAdditionalInfo` deleted or renamed its instance variable `additional_properties`
  - Model `ErrorDetail` deleted or renamed its instance variable `additional_properties`
  - Model `ErrorResponse` deleted or renamed its instance variable `additional_properties`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `created_at`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `expiry_at`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `allocated_value`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `used_value`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `percentage_used`
  - Model `FreeTrialProperties` deleted or renamed its instance variable `additional_properties`
  - Model `Operation` deleted or renamed its instance variable `additional_properties`
  - Model `OperationDisplay` deleted or renamed its instance variable `additional_properties`
  - Model `ProxyResource` deleted or renamed its instance variable `additional_properties`
  - Model `Quota` deleted or renamed its instance variable `additional_properties`
  - Model `QuotaProperties` deleted or renamed its instance variable `additional_properties`
  - Model `Resource` deleted or renamed its instance variable `additional_properties`
  - Model `SystemData` deleted or renamed its instance variable `additional_properties`
  - Model `TrackedResource` deleted or renamed its instance variable `additional_properties`
  - Method `AccountsOperations.begin_create_or_update` inserted a `positional_or_keyword` parameter `account_name`
  - Method `AccountsOperations.begin_create_or_update` deleted or renamed its parameter `name` of kind `positional_or_keyword`
  - Method `AccountsOperations.begin_delete` inserted a `positional_or_keyword` parameter `account_name`
  - Method `AccountsOperations.begin_delete` deleted or renamed its parameter `name` of kind `positional_or_keyword`
  - Method `AccountsOperations.get` inserted a `positional_or_keyword` parameter `account_name`
  - Method `AccountsOperations.get` deleted or renamed its parameter `name` of kind `positional_or_keyword`
  - Method `AccountsOperations.update` inserted a `positional_or_keyword` parameter `account_name`
  - Method `AccountsOperations.update` deleted or renamed its parameter `name` of kind `positional_or_keyword`
  - Method `QuotasOperations.get` inserted a `positional_or_keyword` parameter `quota_name`
  - Method `QuotasOperations.get` deleted or renamed its parameter `name` of kind `positional_or_keyword`
  - Method `QuotasOperations.get` re-ordered its parameters from `['self', 'location', 'name', 'kwargs']` to `['self', 'location', 'quota_name', 'kwargs']`
  - Method `AccountsOperations.begin_create_or_update` re-ordered its parameters from `['self', 'resource_group_name', 'name', 'resource', 'kwargs']` to `['self', 'resource_group_name', 'account_name', 'resource', 'kwargs']`
  - Method `AccountsOperations.begin_delete` re-ordered its parameters from `['self', 'resource_group_name', 'name', 'kwargs']` to `['self', 'resource_group_name', 'account_name', 'kwargs']`
  - Method `AccountsOperations.update` re-ordered its parameters from `['self', 'resource_group_name', 'name', 'properties', 'kwargs']` to `['self', 'resource_group_name', 'account_name', 'properties', 'kwargs']`
  - Method `AccountsOperations.get` re-ordered its parameters from `['self', 'resource_group_name', 'name', 'kwargs']` to `['self', 'resource_group_name', 'account_name', 'kwargs']`

## 1.0.0b2 (2024-03-04)

### Features Added

  - Model Account has a new parameter properties
  - Model AccountUpdate has a new parameter properties
  - Model Quota has a new parameter properties

### Breaking Changes

  - Model Account no longer has parameter dashboard_uri
  - Model Account no longer has parameter provisioning_state
  - Model Account no longer has parameter regional_affinity
  - Model Account no longer has parameter reporting
  - Model Account no longer has parameter scalable_execution
  - Model AccountUpdate no longer has parameter regional_affinity
  - Model AccountUpdate no longer has parameter reporting
  - Model AccountUpdate no longer has parameter scalable_execution
  - Model Quota no longer has parameter free_trial
  - Model Quota no longer has parameter provisioning_state

## 1.0.0b1 (2023-09-27)

* Initial Release
