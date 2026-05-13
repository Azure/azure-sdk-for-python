```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.10.20


namespace azure.ai.agentserver.core

    def azure.ai.agentserver.core.build_server_version(sdk_name: str, version: str) -> str: ...


    def azure.ai.agentserver.core.configure_observability(
            *, 
            connection_string: Optional[str] = ..., 
            log_level: Optional[str] = ...
        ) -> None: ...


    def azure.ai.agentserver.core.create_error_response(
            code: str, 
            message: str, 
            *, 
            details: Optional[list[dict[str, Any]]] = ..., 
            error_type: Optional[str] = ..., 
            headers: Optional[dict[str, str]] = ..., 
            status_code: int
        ) -> JSONResponse: ...


    def azure.ai.agentserver.core.detach_context(token: Any) -> None: ...


    def azure.ai.agentserver.core.end_span(span: Any, exc: Optional[BaseException] = None) -> None: ...


    def azure.ai.agentserver.core.flush_spans(timeout_millis: int = 5000) -> None: ...


    def azure.ai.agentserver.core.record_error(span: Any, exc: BaseException) -> None: ...


    def azure.ai.agentserver.core.set_current_span(span: Any) -> Any: ...


    async def azure.ai.agentserver.core.trace_stream:async(iterator: AsyncIterable[_Content], span: Any) -> AsyncIterator[_Content]: ...


    class azure.ai.agentserver.core.AgentConfig:

        def __init__(
                self, 
                *, 
                agent_id: str, 
                agent_name: str, 
                agent_version: str, 
                appinsights_connection_string: str, 
                is_hosted: bool, 
                otlp_endpoint: str, 
                port: int, 
                project_endpoint: str, 
                project_id: str, 
                session_id: str, 
                sse_keepalive_interval: int
            ) -> None: ...

        @classmethod
        def from_env(cls) -> Self: ...


    class azure.ai.agentserver.core.AgentServerHost(Starlette):
        property routes: list[BaseRoute]    # Read-only

        async def __call__(
                self, 
                scope: Scope, 
                receive: Receive, 
                send: Send
            ) -> None: ...

        def __init__(
                self, 
                *, 
                access_log: Optional[Logger] = _SENTINEL_ACCESS_LOG, 
                access_log_format: Optional[str] = ..., 
                applicationinsights_connection_string: Optional[str] = ..., 
                configure_observability: Optional[Callable[, None]] = _tracing.configure_observability, 
                graceful_shutdown_timeout: Optional[int] = ..., 
                log_level: Optional[str] = ..., 
                routes: Optional[list[Route]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def add_exception_handler(
                self, 
                exc_class_or_status_code: int | type[Exception], 
                handler: ExceptionHandler
            ) -> None: ...

        def add_middleware(
                self, 
                middleware_class: _MiddlewareFactory[P], 
                *args: args, 
                **kwargs: kwargs
            ) -> None: ...

        def add_route(
                self, 
                path: str, 
                route: Callable[[Request], Awaitable[Response] | Response], 
                methods: list[str] | None = None, 
                name: str | None = None, 
                include_in_schema: bool = True
            ) -> None: ...

        def build_middleware_stack(self) -> ASGIApp: ...

        def host(
                self, 
                host: str, 
                app: ASGIApp, 
                name: str | None = None
            ) -> None: ...

        def mount(
                self, 
                path: str, 
                app: ASGIApp, 
                name: str | None = None
            ) -> None: ...

        def register_server_version(self, version_segment: str) -> None: ...

        @contextlib.contextmanager
        def request_span(
                self, 
                headers: Any, 
                request_id: str, 
                operation: str, 
                *, 
                end_on_exit: bool = True, 
                operation_name: Optional[str] = ..., 
                session_id: str = ""
            ) -> Any: ...

        def run(
                self, 
                host: str = "0.0.0.0", 
                port: Optional[int] = None
            ) -> None: ...

        async def run_async(
                self, 
                host: str = "0.0.0.0", 
                port: Optional[int] = None
            ) -> None: ...

        def shutdown_handler(self, fn: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]: ...

        @staticmethod
        async def sse_keepalive_stream(iterator: AsyncIterable[_Content], interval: int) -> AsyncIterator[_Content]: ...

        def url_path_for(
                self, 
                name: str, 
                /, 
                **path_params: Any
            ) -> URLPath: ...


    class azure.ai.agentserver.core.InboundRequestLoggingMiddleware:

        async def __call__(
                self, 
                scope: Scope, 
                receive: Receive, 
                send: Send
            ) -> None: ...

        def __init__(self, app: ASGIApp) -> None: ...


    class azure.ai.agentserver.core.RequestIdMiddleware:

        async def __call__(
                self, 
                scope: Scope, 
                receive: Receive, 
                send: Send
            ) -> None: ...

        def __init__(self, app: ASGIApp) -> None: ...


```