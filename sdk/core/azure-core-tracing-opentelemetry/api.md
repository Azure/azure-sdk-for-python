```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.core.tracing.ext.opentelemetry_span

    class azure.core.tracing.ext.opentelemetry_span.OpenTelemetrySchema:

        @classmethod
        def get_attribute_mappings(cls, version: OpenTelemetrySchemaVersion) -> Dict[str, str]: ...

        @classmethod
        def get_latest_version(cls) -> OpenTelemetrySchemaVersion: ...

        @classmethod
        def get_schema_url(cls, version: OpenTelemetrySchemaVersion) -> str: ...


    class azure.core.tracing.ext.opentelemetry_span.OpenTelemetrySpan(HttpSpanMixin): implements ContextManager 
        property kind: Optional[SpanKind]
        property span_instance: Span    # Read-only

        def __init__(
                self, 
                span: Optional[Span] = None, 
                name: Optional[str] = "span", 
                *, 
                context: Dict[str, str] = ..., 
                kind: Optional[SpanKind] = ..., 
                links: Optional[List[CoreLink]] = ..., 
                schema_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        @classmethod
        def change_context(cls, span: Union[Span, OpenTelemetrySpan]) -> ContextManager: ...

        @classmethod
        def get_current_span(cls) -> Span: ...

        @classmethod
        def get_current_tracer(cls) -> Tracer: ...

        @classmethod
        def link(
                cls, 
                traceparent: str, 
                attributes: Optional[Attributes] = None
            ) -> None: ...

        @classmethod
        def link_from_headers(
                cls, 
                headers: Dict[str, str], 
                attributes: Optional[Attributes] = None
            ) -> None: ...

        @classmethod
        def set_current_span(cls, span: Span) -> None: ...

        @classmethod
        def set_current_tracer(cls, tracer: Tracer) -> None: ...

        @classmethod
        def with_current_context(cls, func: Callable) -> Callable: ...

        def add_attribute(
                self, 
                key: str, 
                value: Union[str, int]
            ) -> None: ...

        def finish(self) -> None: ...

        def get_trace_parent(self) -> str: ...

        def span(
                self, 
                name: str = "span", 
                *, 
                kind: Optional[SpanKind] = ..., 
                links: Optional[List[CoreLink]] = ..., 
                **kwargs: Any
            ) -> OpenTelemetrySpan: ...

        def start(self) -> None: ...

        def to_header(self) -> Dict[str, str]: ...


```