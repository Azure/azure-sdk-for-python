```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.monitorslis

    class azure.mgmt.monitorslis.MonitorSlisMgmtClient: implements ContextManager 
        slis: SlisOperations

        def __init__(
                self, 
                credential: TokenCredential, 
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


namespace azure.mgmt.monitorslis.aio

    class azure.mgmt.monitorslis.aio.MonitorSlisMgmtClient: implements AsyncContextManager 
        slis: SlisOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
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


namespace azure.mgmt.monitorslis.aio.operations

    class azure.mgmt.monitorslis.aio.operations.SlisOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                service_group_name: str, 
                sli_name: str, 
                resource: Sli, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Sli: ...

        @overload
        async def create_or_update(
                self, 
                service_group_name: str, 
                sli_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Sli: ...

        @overload
        async def create_or_update(
                self, 
                service_group_name: str, 
                sli_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Sli: ...

        @distributed_trace_async
        async def delete(
                self, 
                service_group_name: str, 
                sli_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                service_group_name: str, 
                sli_name: str, 
                **kwargs: Any
            ) -> Sli: ...

        @distributed_trace
        def list_by_parent(
                self, 
                service_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Sli]: ...


namespace azure.mgmt.monitorslis.models

    class azure.mgmt.monitorslis.models.AmwAccount(_Model):
        identity: str
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                identity: str, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.Baseline(_Model):
        evaluation_calculation_type: Union[str, EvaluationCalculationType]
        evaluation_period_days: int
        value: float

        @overload
        def __init__(
                self, 
                *, 
                evaluation_calculation_type: Union[str, EvaluationCalculationType], 
                evaluation_period_days: int, 
                value: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.BaselineProperties(_Model):
        baseline: Baseline

        @overload
        def __init__(
                self, 
                *, 
                baseline: Baseline
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.Category(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABILITY = "Availability"
        LATENCY = "Latency"


    class azure.mgmt.monitorslis.models.Condition(_Model):
        dimension_name: Optional[str]
        operator: Union[str, ConditionOperator]
        sampling_type: Optional[Union[str, SamplingType]]
        scalar_function: Optional[Union[str, ScalarFunction]]
        value: str

        @overload
        def __init__(
                self, 
                *, 
                dimension_name: Optional[str] = ..., 
                operator: Union[str, ConditionOperator], 
                sampling_type: Optional[Union[str, SamplingType]] = ..., 
                scalar_function: Optional[Union[str, ScalarFunction]] = ..., 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.ConditionOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINS = "contains"
        EQUAL = "=="
        GREATER_THAN = ">"
        GREATER_THAN_OR_EQUAL = ">="
        IN = "@in"
        LESS_THAN = "<"
        LESS_THAN_OR_EQUAL = "<="
        NOT_CONTAINS = "!contains"
        NOT_EQUAL = "!="
        NOT_IN = "!in"
        NOT_STARTS_WITH = "!startswith"
        STARTS_WITH = "startswith"


    class azure.mgmt.monitorslis.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.monitorslis.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.monitorslis.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.monitorslis.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.EvaluationCalculationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CALENDAR_DAYS = "CalendarDays"
        ROLLING_DAYS = "RollingDays"


    class azure.mgmt.monitorslis.models.EvaluationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REQUEST_BASED = "RequestBased"
        WINDOW_BASED = "WindowBased"


    class azure.mgmt.monitorslis.models.ExecutionState(_Model):
        message: Optional[str]
        state: str

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                state: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.monitorslis.models.Metric(_Model):
        metric_name: str
        metric_namespace: str

        @overload
        def __init__(
                self, 
                *, 
                metric_name: str, 
                metric_namespace: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.monitorslis.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.monitorslis.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.monitorslis.models.SamplingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVG = "avg"
        MAX = "max"
        MIN = "min"
        SUM = "sum"


    class azure.mgmt.monitorslis.models.ScalarFunction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVG = "avg"
        MAX = "max"
        MIN = "min"
        SUM = "sum"


    class azure.mgmt.monitorslis.models.Signal(_Model):
        signal_formula: str
        signal_sources: list[SignalSource]

        @overload
        def __init__(
                self, 
                *, 
                signal_formula: str, 
                signal_sources: list[SignalSource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.SignalSource(_Model):
        filters: list[Condition]
        metric_name: str
        metric_namespace: str
        signal_source_id: str
        source_amw_account_managed_identity: str
        source_amw_account_resource_id: str
        spatial_aggregation: SpatialAggregation
        temporal_aggregation: TemporalAggregation

        @overload
        def __init__(
                self, 
                *, 
                filters: list[Condition], 
                metric_name: str, 
                metric_namespace: str, 
                signal_source_id: str, 
                source_amw_account_managed_identity: str, 
                source_amw_account_resource_id: str, 
                spatial_aggregation: SpatialAggregation, 
                temporal_aggregation: TemporalAggregation
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.Sli(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        name: str
        properties: Optional[SliResource]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[SliResource] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.SliProperties(_Model):
        good_signals: Optional[Signal]
        signals: Optional[Signal]
        total_signals: Optional[Signal]
        window_uptime_criteria: Optional[WindowUptimeCriteria]

        @overload
        def __init__(
                self, 
                *, 
                good_signals: Optional[Signal] = ..., 
                signals: Optional[Signal] = ..., 
                total_signals: Optional[Signal] = ..., 
                window_uptime_criteria: Optional[WindowUptimeCriteria] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.SliResource(_Model):
        baseline_properties: BaselineProperties
        category: Union[str, Category]
        description: str
        destination_amw_accounts: list[AmwAccount]
        destination_metrics: Optional[list[Metric]]
        enable_alert: bool
        evaluation_type: Union[str, EvaluationType]
        execution_state: Optional[ExecutionState]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        sli_properties: SliProperties
        streaming_rule_id: Optional[str]
        streaming_rule_last_updated_timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                baseline_properties: BaselineProperties, 
                category: Union[str, Category], 
                description: str, 
                destination_amw_accounts: list[AmwAccount], 
                enable_alert: bool, 
                evaluation_type: Union[str, EvaluationType], 
                sli_properties: SliProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.SpatialAggregation(_Model):
        dimensions: list[str]
        type: Union[str, SpatialAggregationType]

        @overload
        def __init__(
                self, 
                *, 
                dimensions: list[str], 
                type: Union[str, SpatialAggregationType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.SpatialAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        MAX = "Max"
        MIN = "Min"
        SUM = "Sum"


    class azure.mgmt.monitorslis.models.SystemData(_Model):
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


    class azure.mgmt.monitorslis.models.TemporalAggregation(_Model):
        type: Union[str, TemporalAggregationType]
        window_size_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, TemporalAggregationType], 
                window_size_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.TemporalAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        DELTA = "Delta"
        INCREASE = "Increase"
        I_DELTA = "IDelta"
        I_RATE = "IRate"
        MAX = "Max"
        MIN = "Min"
        RATE = "Rate"
        SUM = "Sum"


    class azure.mgmt.monitorslis.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.monitorslis.models.WindowUptimeCriteria(_Model):
        comparator: Union[str, WindowUptimeCriteriaComparator]
        target: float

        @overload
        def __init__(
                self, 
                *, 
                comparator: Union[str, WindowUptimeCriteriaComparator], 
                target: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.monitorslis.models.WindowUptimeCriteriaComparator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GREATER_THAN = ">"
        GREATER_THAN_OR_EQUAL = ">="
        LESS_THAN = "<"
        LESS_THAN_OR_EQUAL = "<="


namespace azure.mgmt.monitorslis.operations

    class azure.mgmt.monitorslis.operations.SlisOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                service_group_name: str, 
                sli_name: str, 
                resource: Sli, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Sli: ...

        @overload
        def create_or_update(
                self, 
                service_group_name: str, 
                sli_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Sli: ...

        @overload
        def create_or_update(
                self, 
                service_group_name: str, 
                sli_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Sli: ...

        @distributed_trace
        def delete(
                self, 
                service_group_name: str, 
                sli_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                service_group_name: str, 
                sli_name: str, 
                **kwargs: Any
            ) -> Sli: ...

        @distributed_trace
        def list_by_parent(
                self, 
                service_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Sli]: ...


```