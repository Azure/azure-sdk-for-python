```py
namespace azure.ai.agentserver.invocations

    class azure.ai.agentserver.invocations.InvocationAgentServerHost(_WSHandlerMixin, AgentServerHost):
        property routes: list[BaseRoute]    # Read-only
        property ws_ping_interval: float    # Read-only

        async def __call__(
                self, 
                scope: Scope, 
                receive: Receive, 
                send: Send
            ) -> None: ...

        def __init__(
                self, 
                *, 
                openapi_spec: Optional[dict[str, Any]] = ..., 
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

        def cancel_invocation_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def get_invocation_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def get_openapi_spec(self) -> Optional[dict[str, Any]]: ...

        def host(
                self, 
                host: str, 
                app: ASGIApp, 
                name: str | None = None
            ) -> None: ...

        def invoke_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def mount(
                self, 
                path: str, 
                app: ASGIApp, 
                name: str | None = None
            ) -> None: ...

        def register_server_version(self, version_segment: str) -> None: ...

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

        def ws_handler(self, fn: WSHandler) -> WSHandler: ...


```