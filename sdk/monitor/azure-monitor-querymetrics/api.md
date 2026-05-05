```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.monitor.querymetrics

    class azure.monitor.querymetrics.Metric:
        display_description: str
        id: str
        name: str
        timeseries: List[TimeSeriesElement]
        type: str
        unit: str

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.monitor.querymetrics.MetricAggregationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "Average"
        COUNT = "Count"
        MAXIMUM = "Maximum"
        MINIMUM = "Minimum"
        NONE = "None"
        TOTAL = "Total"


    class azure.monitor.querymetrics.MetricValue:
        average: Optional[float]
        count: Optional[float]
        maximum: Optional[float]
        minimum: Optional[float]
        timestamp: datetime
        total: Optional[float]

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.monitor.querymetrics.MetricsClient(GeneratedClient): implements ContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                api_version: str = ..., 
                audience: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def query_resources(
                self, 
                *, 
                aggregations: Optional[Sequence[Union[MetricAggregationType, str]]] = ..., 
                filter: Optional[str] = ..., 
                granularity: Optional[timedelta] = ..., 
                max_results: Optional[int] = ..., 
                metric_names: Sequence[str], 
                metric_namespace: str, 
                order_by: Optional[str] = ..., 
                resource_ids: Sequence[str], 
                roll_up_by: Optional[str] = ..., 
                timespan: Optional[Union[timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]]] = ..., 
                **kwargs: Any
            ) -> List[MetricsQueryResult]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.monitor.querymetrics.MetricsQueryResult:
        cost: Optional[int]
        granularity: Optional[timedelta]
        metrics: List[Metric]
        namespace: Optional[str]
        resource_region: Optional[str]
        timespan: str

        def __init__(self, **kwargs: Any) -> None: ...


    class azure.monitor.querymetrics.TimeSeriesElement:
        data: List[MetricValue]
        metadata_values: Dict[str, str]

        def __init__(self, **kwargs: Any) -> None: ...


namespace azure.monitor.querymetrics.aio

    class azure.monitor.querymetrics.aio.MetricsClient(GeneratedClient): implements AsyncContextManager 

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: str = ..., 
                audience: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def query_resources(
                self, 
                *, 
                aggregations: Optional[Sequence[Union[MetricAggregationType, str]]] = ..., 
                filter: Optional[str] = ..., 
                granularity: Optional[timedelta] = ..., 
                max_results: Optional[int] = ..., 
                metric_names: Sequence[str], 
                metric_namespace: str, 
                order_by: Optional[str] = ..., 
                resource_ids: Sequence[str], 
                roll_up_by: Optional[str] = ..., 
                timespan: Optional[Union[timedelta, Tuple[datetime, timedelta], Tuple[datetime, datetime]]] = ..., 
                **kwargs: Any
            ) -> List[MetricsQueryResult]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


```