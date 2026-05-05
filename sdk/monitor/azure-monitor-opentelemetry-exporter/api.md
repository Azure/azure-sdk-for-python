```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.monitor.opentelemetry.exporter

    class azure.monitor.opentelemetry.exporter.ApplicationInsightsSampler(Sampler):

        def __init__(self, sampling_ratio: float = 1.0): ...

        def get_description(self) -> str: ...

        def should_sample(
                self, 
                parent_context: Optional[Context], 
                trace_id: int, 
                name: str, 
                kind: Optional[SpanKind] = None, 
                attributes: Attributes = None, 
                links: Optional[Sequence[Link]] = None, 
                trace_state: Optional[TraceState] = None
            ) -> SamplingResult: ...


    class azure.monitor.opentelemetry.exporter.AzureMonitorLogExporter(BaseExporter, LogRecordExporter):

        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                connection_string: Optional[str] = ..., 
                credential: Optional[ManagedIdentityCredential/ClientSecretCredential] = ..., 
                disable_offline_storage: Optional[bool] = ..., 
                storage_directory: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                *, 
                api_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> AzureMonitorLogExporter: ...

        def export(
                self, 
                batch: Sequence[ReadableLogRecord], 
                **kwargs: Any
            ) -> LogRecordExportResult: ...

        def shutdown(self) -> None: ...


    class azure.monitor.opentelemetry.exporter.AzureMonitorMetricExporter(BaseExporter, MetricExporter):

        def __init__(self, **kwargs: Any) -> None: ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                *, 
                api_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> AzureMonitorMetricExporter: ...

        def export(
                self, 
                metrics_data: OTMetricsData, 
                timeout_millis: float = 10000, 
                **kwargs: Any
            ) -> MetricExportResult: ...

        def force_flush(self, timeout_millis: float = 10000) -> bool: ...

        def shutdown(
                self, 
                timeout_millis: float = 30000, 
                **kwargs: Any
            ) -> None: ...


    class azure.monitor.opentelemetry.exporter.AzureMonitorTraceExporter(BaseExporter, SpanExporter):

        def __init__(self, **kwargs: Any): ...

        @classmethod
        def from_connection_string(
                cls, 
                conn_str: str, 
                *, 
                api_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> AzureMonitorTraceExporter: ...

        def export(
                self, 
                spans: Sequence[ReadableSpan], 
                **_kwargs: Any
            ) -> SpanExportResult: ...

        def shutdown(self) -> None: ...


    class azure.monitor.opentelemetry.exporter.RateLimitedSampler(Sampler):

        def __init__(self, target_spans_per_second_limit: float): ...

        def get_description(self) -> str: ...

        def should_sample(
                self, 
                parent_context: Optional[Context], 
                trace_id: int, 
                name: str, 
                kind: Optional[SpanKind] = None, 
                attributes: Attributes = None, 
                links: Optional[Sequence[Link]] = None, 
                trace_state: Optional[TraceState] = None
            ) -> SamplingResult: ...


namespace azure.monitor.opentelemetry.exporter.statsbeat

    def azure.monitor.opentelemetry.exporter.statsbeat.collect_statsbeat_metrics(exporter: BaseExporter) -> None: ...


    def azure.monitor.opentelemetry.exporter.statsbeat.shutdown_statsbeat_metrics() -> bool: ...


    class azure.monitor.opentelemetry.exporter.statsbeat.StatsbeatConfig:

        def __eq__(self, other: object) -> bool: ...

        def __hash__(self) -> int: ...

        def __init__(
                self, 
                endpoint: str, 
                region: str, 
                instrumentation_key: str, 
                disable_offline_storage: bool = False, 
                credential: Optional[Any] = None, 
                distro_version: Optional[str] = None, 
                connection_string: Optional[str] = None
            ) -> None: ...

        @classmethod
        def from_config(
                cls, 
                base_config: StatsbeatConfig, 
                config_dict: Dict[str, str]
            ) -> Optional[StatsbeatConfig]: ...

        @classmethod
        def from_exporter(cls, exporter: Any) -> Optional[StatsbeatConfig]: ...


    class azure.monitor.opentelemetry.exporter.statsbeat.StatsbeatManager(metaclass=Singleton):

        def __init__(self) -> None: ...

        def get_current_config(self) -> Optional[StatsbeatConfig]: ...

        def initialize(self, config: StatsbeatConfig) -> bool: ...

        def is_initialized(self) -> bool: ...

        def shutdown(self) -> bool: ...


namespace azure.monitor.opentelemetry.exporter.statsbeat.customer

    def azure.monitor.opentelemetry.exporter.statsbeat.customer.collect_customer_sdkstats(exporter: BaseExporter) -> None: ...


    def azure.monitor.opentelemetry.exporter.statsbeat.customer.get_customer_stats_manager() -> CustomerSdkStatsManager: ...


    def azure.monitor.opentelemetry.exporter.statsbeat.customer.shutdown_customer_sdkstats_metrics() -> None: ...


```