```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.onlineexperimentation

    class azure.onlineexperimentation.OnlineExperimentationClient(OnlineExperimentationClientOperationsMixin): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @overload
        def create_or_update_metric(
                self, 
                experiment_metric_id: str, 
                resource: ExperimentMetric, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExperimentMetric: ...

        @overload
        def create_or_update_metric(
                self, 
                experiment_metric_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExperimentMetric: ...

        @overload
        def create_or_update_metric(
                self, 
                experiment_metric_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExperimentMetric: ...

        @distributed_trace
        def delete_metric(
                self, 
                experiment_metric_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_metric(
                self, 
                experiment_metric_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExperimentMetric: ...

        @distributed_trace
        def list_metrics(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ExperimentMetric]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @overload
        def validate_metric(
                self, 
                body: ExperimentMetric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExperimentMetricValidationResult: ...

        @overload
        def validate_metric(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExperimentMetricValidationResult: ...

        @overload
        def validate_metric(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExperimentMetricValidationResult: ...


namespace azure.onlineexperimentation.aio

    class azure.onlineexperimentation.aio.OnlineExperimentationClient(OnlineExperimentationClientOperationsMixin): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @overload
        async def create_or_update_metric(
                self, 
                experiment_metric_id: str, 
                resource: ExperimentMetric, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExperimentMetric: ...

        @overload
        async def create_or_update_metric(
                self, 
                experiment_metric_id: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExperimentMetric: ...

        @overload
        async def create_or_update_metric(
                self, 
                experiment_metric_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExperimentMetric: ...

        @distributed_trace_async
        async def delete_metric(
                self, 
                experiment_metric_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_metric(
                self, 
                experiment_metric_id: str, 
                *, 
                etag: Optional[str] = ..., 
                if_modified_since: Optional[datetime] = ..., 
                if_unmodified_since: Optional[datetime] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> ExperimentMetric: ...

        @distributed_trace
        def list_metrics(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ExperimentMetric]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @overload
        async def validate_metric(
                self, 
                body: ExperimentMetric, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExperimentMetricValidationResult: ...

        @overload
        async def validate_metric(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExperimentMetricValidationResult: ...

        @overload
        async def validate_metric(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ExperimentMetricValidationResult: ...


namespace azure.onlineexperimentation.models

    class azure.onlineexperimentation.models.AggregatedValue(_Model):
        event_name: str
        event_property: str
        filter: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                event_name: str, 
                event_property: str, 
                filter: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.onlineexperimentation.models.AverageMetricDefinition(ExperimentMetricDefinition, discriminator='Average'):
        type: Literal[ExperimentMetricType.AVERAGE]
        value: AggregatedValue

        @overload
        def __init__(
                self, 
                *, 
                value: AggregatedValue
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.onlineexperimentation.models.DesiredDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DECREASE = "Decrease"
        INCREASE = "Increase"
        NEUTRAL = "Neutral"


    class azure.onlineexperimentation.models.DiagnosticCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED_SCHEMA_VALIDATION = "FailedSchemaValidation"
        INVALID_EVENT_CONDITION = "InvalidEventCondition"
        INVALID_EXPERIMENT_METRIC_DEFINITION = "InvalidExperimentMetricDefinition"
        UNSUPPORTED_EVENT_CONDITION = "UnsupportedEventCondition"


    class azure.onlineexperimentation.models.DiagnosticDetail(_Model):
        code: Union[str, DiagnosticCode]
        message: str


    class azure.onlineexperimentation.models.EventCountMetricDefinition(ExperimentMetricDefinition, discriminator='EventCount'):
        event: ObservedEvent
        type: Literal[ExperimentMetricType.EVENT_COUNT]

        @overload
        def __init__(
                self, 
                *, 
                event: ObservedEvent
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.onlineexperimentation.models.EventRateMetricDefinition(ExperimentMetricDefinition, discriminator='EventRate'):
        event: ObservedEvent
        rate_condition: str
        type: Literal[ExperimentMetricType.EVENT_RATE]

        @overload
        def __init__(
                self, 
                *, 
                event: ObservedEvent, 
                rate_condition: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.onlineexperimentation.models.ExperimentMetric(_Model):
        categories: List[str]
        definition: ExperimentMetricDefinition
        description: str
        desired_direction: Union[str, DesiredDirection]
        display_name: str
        etag: str
        id: str
        last_modified_at: datetime
        lifecycle: Union[str, LifecycleStage]

        @overload
        def __init__(
                self, 
                *, 
                categories: List[str], 
                definition: ExperimentMetricDefinition, 
                description: str, 
                desired_direction: Union[str, DesiredDirection], 
                display_name: str, 
                lifecycle: Union[str, LifecycleStage]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.onlineexperimentation.models.ExperimentMetricDefinition(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.onlineexperimentation.models.ExperimentMetricType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        EVENT_COUNT = "EventCount"
        EVENT_RATE = "EventRate"
        PERCENTILE = "Percentile"
        SUM = "Sum"
        USER_COUNT = "UserCount"
        USER_RATE = "UserRate"


    class azure.onlineexperimentation.models.ExperimentMetricValidationResult(_Model):
        diagnostics: List[DiagnosticDetail]
        is_valid: bool

        @overload
        def __init__(
                self, 
                *, 
                is_valid: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.onlineexperimentation.models.LifecycleStage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"


    class azure.onlineexperimentation.models.ObservedEvent(_Model):
        event_name: str
        filter: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                event_name: str, 
                filter: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.onlineexperimentation.models.PercentileMetricDefinition(ExperimentMetricDefinition, discriminator='Percentile'):
        percentile: float
        type: Literal[ExperimentMetricType.PERCENTILE]
        value: AggregatedValue

        @overload
        def __init__(
                self, 
                *, 
                percentile: float, 
                value: AggregatedValue
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.onlineexperimentation.models.SumMetricDefinition(ExperimentMetricDefinition, discriminator='Sum'):
        type: Literal[ExperimentMetricType.SUM]
        value: AggregatedValue

        @overload
        def __init__(
                self, 
                *, 
                value: AggregatedValue
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.onlineexperimentation.models.UserCountMetricDefinition(ExperimentMetricDefinition, discriminator='UserCount'):
        event: ObservedEvent
        type: Literal[ExperimentMetricType.USER_COUNT]

        @overload
        def __init__(
                self, 
                *, 
                event: ObservedEvent
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.onlineexperimentation.models.UserRateMetricDefinition(ExperimentMetricDefinition, discriminator='UserRate'):
        end_event: ObservedEvent
        start_event: ObservedEvent
        type: Literal[ExperimentMetricType.USER_RATE]

        @overload
        def __init__(
                self, 
                *, 
                end_event: ObservedEvent, 
                start_event: ObservedEvent
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


```