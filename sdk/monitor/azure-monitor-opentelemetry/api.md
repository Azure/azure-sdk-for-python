```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.monitor.opentelemetry

    def azure.monitor.opentelemetry.configure_azure_monitor(
            *, 
            browser_sdk_loader_config: Optional[dict] = ..., 
            connection_string: Optional[str] = ..., 
            credential: Union[TokenCredential, None] = ..., 
            disable_offline_storage: Optional[bool] = ..., 
            enable_live_metrics: Optional[bool] = ..., 
            enable_performance_counters: Optional[bool] = ..., 
            enable_trace_based_sampling_for_logs: Optional[bool] = ..., 
            instrumentation_options: Optional[dict] = ..., 
            log_record_processors: Optional[list[LogRecordProcessor]] = ..., 
            logger_name: Optional[str] = ..., 
            metric_readers: Optional[list[MetricReader]] = ..., 
            resource: Optional[Resource] = ..., 
            span_processors: Optional[list[SpanProcessor]] = ..., 
            storage_directory: Optional[str] = ..., 
            views: Optional[list[View]] = ..., 
            **kwargs
        ) -> None: ...


```