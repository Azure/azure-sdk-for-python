```py
namespace azure.mgmt.alertprocessingrules

    class azure.mgmt.alertprocessingrules.AlertProcessingRulesMgmtClient: implements ContextManager 
        alert_processing_rules: AlertProcessingRulesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.alertprocessingrules.aio

    class azure.mgmt.alertprocessingrules.aio.AlertProcessingRulesMgmtClient: implements AsyncContextManager 
        alert_processing_rules: AlertProcessingRulesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.alertprocessingrules.aio.operations

    class azure.mgmt.alertprocessingrules.aio.operations.AlertProcessingRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule: AlertProcessingRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule: AlertProcessingRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_by_name(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AlertProcessingRule]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AlertProcessingRule]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule_patch: PatchObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule_patch: PatchObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...


namespace azure.mgmt.alertprocessingrules.models

    class azure.mgmt.alertprocessingrules.models.Action(_Model):
        action_type: str

        @overload
        def __init__(
                self, 
                *, 
                action_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_ACTION_GROUPS = "AddActionGroups"
        REMOVE_ALL_ACTION_GROUPS = "RemoveAllActionGroups"


    class azure.mgmt.alertprocessingrules.models.AddActionGroups(Action, discriminator='AddActionGroups'):
        action_group_ids: list[str]
        action_type: Literal[ActionType.ADD_ACTION_GROUPS]

        @overload
        def __init__(
                self, 
                *, 
                action_group_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.AlertProcessingRule(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[AlertProcessingRuleProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AlertProcessingRuleProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.AlertProcessingRuleProperties(_Model):
        actions: list[Action]
        conditions: Optional[list[Condition]]
        description: Optional[str]
        enabled: Optional[bool]
        schedule: Optional[Schedule]
        scopes: list[str]

        @overload
        def __init__(
                self, 
                *, 
                actions: list[Action], 
                conditions: Optional[list[Condition]] = ..., 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                schedule: Optional[Schedule] = ..., 
                scopes: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.Condition(_Model):
        field: Optional[Union[str, Field]]
        operator: Optional[Union[str, Operator]]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                field: Optional[Union[str, Field]] = ..., 
                operator: Optional[Union[str, Operator]] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.alertprocessingrules.models.DailyRecurrence(Recurrence, discriminator='Daily'):
        end_time: str
        recurrence_type: Literal[RecurrenceType.DAILY]
        start_time: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                start_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.DaysOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.alertprocessingrules.models.ErrorResponse(_Model):
        error: Optional[ErrorResponseBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.ErrorResponseBody(_Model):
        code: Optional[str]
        details: Optional[list[ErrorResponseBody]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[ErrorResponseBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.Field(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALERT_CONTEXT = "AlertContext"
        ALERT_RULE_ID = "AlertRuleId"
        ALERT_RULE_NAME = "AlertRuleName"
        DESCRIPTION = "Description"
        MONITOR_CONDITION = "MonitorCondition"
        MONITOR_SERVICE = "MonitorService"
        SEVERITY = "Severity"
        SIGNAL_TYPE = "SignalType"
        TARGET_RESOURCE = "TargetResource"
        TARGET_RESOURCE_GROUP = "TargetResourceGroup"
        TARGET_RESOURCE_TYPE = "TargetResourceType"


    class azure.mgmt.alertprocessingrules.models.MonthlyRecurrence(Recurrence, discriminator='Monthly'):
        days_of_month: list[int]
        end_time: str
        recurrence_type: Literal[RecurrenceType.MONTHLY]
        start_time: str

        @overload
        def __init__(
                self, 
                *, 
                days_of_month: list[int], 
                end_time: Optional[str] = ..., 
                start_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.Operator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINS = "Contains"
        DOES_NOT_CONTAIN = "DoesNotContain"
        EQUALS = "Equals"
        NOT_EQUALS = "NotEquals"


    class azure.mgmt.alertprocessingrules.models.PatchObject(_Model):
        properties: Optional[PatchProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.alertprocessingrules.models.PatchProperties(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.Recurrence(_Model):
        end_time: Optional[str]
        recurrence_type: str
        start_time: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[str] = ..., 
                recurrence_type: str, 
                start_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.RecurrenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        MONTHLY = "Monthly"
        WEEKLY = "Weekly"


    class azure.mgmt.alertprocessingrules.models.RemoveAllActionGroups(Action, discriminator='RemoveAllActionGroups'):
        action_type: Literal[ActionType.REMOVE_ALL_ACTION_GROUPS]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.alertprocessingrules.models.Schedule(_Model):
        effective_from: Optional[str]
        effective_until: Optional[str]
        recurrences: Optional[list[Recurrence]]
        time_zone: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                effective_from: Optional[str] = ..., 
                effective_until: Optional[str] = ..., 
                recurrences: Optional[list[Recurrence]] = ..., 
                time_zone: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.SystemData(_Model):
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, CreatedByType]]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, CreatedByType]]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.alertprocessingrules.models.WeeklyRecurrence(Recurrence, discriminator='Weekly'):
        days_of_week: list[Union[str, DaysOfWeek]]
        end_time: str
        recurrence_type: Literal[RecurrenceType.WEEKLY]
        start_time: str

        @overload
        def __init__(
                self, 
                *, 
                days_of_week: list[Union[str, DaysOfWeek]], 
                end_time: Optional[str] = ..., 
                start_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.alertprocessingrules.operations

    class azure.mgmt.alertprocessingrules.operations.AlertProcessingRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule: AlertProcessingRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule: AlertProcessingRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_by_name(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AlertProcessingRule]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AlertProcessingRule]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule_patch: PatchObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule_patch: PatchObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                alert_processing_rule_name: str, 
                alert_processing_rule_patch: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertProcessingRule: ...


namespace azure.mgmt.alertprocessingrules.types

    class azure.mgmt.alertprocessingrules.types.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_ACTION_GROUPS = "AddActionGroups"
        REMOVE_ALL_ACTION_GROUPS = "RemoveAllActionGroups"


    class azure.mgmt.alertprocessingrules.types.AddActionGroups(TypedDict, total=False):
        key "actionGroupIds": Required[list[str]]
        key "actionType": Required[Literal[ActionType.ADD_ACTION_GROUPS]]
        action_group_ids: list[str]
        action_type: Literal[ActionType.ADD_ACTION_GROUPS]


    class azure.mgmt.alertprocessingrules.types.AlertProcessingRule(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AlertProcessingRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: AlertProcessingRuleProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.alertprocessingrules.types.AlertProcessingRuleProperties(TypedDict, total=False):
        key "actions": Required[list[Action]]
        key "description": str
        key "enabled": bool
        key "schedule": ForwardRef('Schedule', module='types')
        key "scopes": Required[list[str]]
        actions: list[Action]
        conditions: list[Condition]
        description: str
        enabled: bool
        schedule: Schedule
        scopes: list[str]


    class azure.mgmt.alertprocessingrules.types.Condition(TypedDict, total=False):
        key "field": Union[str, Field]
        key "operator": Union[str, Operator]
        field: Union[str, Field]
        operator: Union[str, Operator]
        values: list[str]
        values_property: list[str]


    class azure.mgmt.alertprocessingrules.types.DailyRecurrence(TypedDict, total=False):
        key "endTime": str
        key "recurrenceType": Required[Literal[RecurrenceType.DAILY]]
        key "startTime": str
        end_time: str
        recurrence_type: Literal[RecurrenceType.DAILY]
        start_time: str


    class azure.mgmt.alertprocessingrules.types.MonthlyRecurrence(TypedDict, total=False):
        key "daysOfMonth": Required[list[int]]
        key "endTime": str
        key "recurrenceType": Required[Literal[RecurrenceType.MONTHLY]]
        key "startTime": str
        days_of_month: list[int]
        end_time: str
        recurrence_type: Literal[RecurrenceType.MONTHLY]
        start_time: str


    class azure.mgmt.alertprocessingrules.types.PatchObject(TypedDict, total=False):
        key "properties": ForwardRef('PatchProperties', module='types')
        properties: PatchProperties
        tags: dict[str, str]


    class azure.mgmt.alertprocessingrules.types.PatchProperties(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.alertprocessingrules.types.RecurrenceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"
        MONTHLY = "Monthly"
        WEEKLY = "Weekly"


    class azure.mgmt.alertprocessingrules.types.RemoveAllActionGroups(TypedDict, total=False):
        key "actionType": Required[Literal[ActionType.REMOVE_ALL_ACTION_GROUPS]]
        action_type: Literal[ActionType.REMOVE_ALL_ACTION_GROUPS]


    class azure.mgmt.alertprocessingrules.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.alertprocessingrules.types.Schedule(TypedDict, total=False):
        key "effectiveFrom": str
        key "effectiveUntil": str
        key "timeZone": str
        effective_from: str
        effective_until: str
        recurrences: list[Recurrence]
        time_zone: str


    class azure.mgmt.alertprocessingrules.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.alertprocessingrules.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.alertprocessingrules.types.WeeklyRecurrence(TypedDict, total=False):
        key "daysOfWeek": Required[list[Union[str, DaysOfWeek]]]
        key "endTime": str
        key "recurrenceType": Required[Literal[RecurrenceType.WEEKLY]]
        key "startTime": str
        days_of_week: list[Union[str, DaysOfWeek]]
        end_time: str
        recurrence_type: Literal[RecurrenceType.WEEKLY]
        start_time: str


```