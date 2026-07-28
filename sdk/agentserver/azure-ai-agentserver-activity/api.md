```py
namespace azure.ai.agentserver.activity

    def azure.ai.agentserver.activity.get_hosted_agent_env(*, digital_worker: bool = False) -> dict[str, str]: ...


    class azure.ai.agentserver.activity.ActivityAgentServerHost(AgentServerHost):
        property adapter: Optional[HttpAdapterBase]    # Read-only
        property agent_app: AgentApplication    # Read-only
        property connection_config: Optional[Mapping[str, str]]    # Read-only
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
                adapter: Optional[HttpAdapterBase] = ..., 
                agent_app: Optional[AgentApplication] = ..., 
                authorization: Optional[Authorization] = ..., 
                connection_config: Optional[Mapping[str, str]] = ..., 
                connection_manager: Optional[MsalConnectionManager] = ..., 
                digital_worker: bool = False, 
                request_handler: Optional[Callable[[Request], Awaitable[Response]]] = ..., 
                storage: Optional[Storage] = ..., 
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


```