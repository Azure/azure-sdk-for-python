```py
namespace azure.ai.agentserver.invocations

    class azure.ai.agentserver.invocations.InvocationAgentServerHost(_WSHandlerMixin, AgentServerHost):
        property ws_ping_interval: float    # Read-only

        def __init__(
                self, 
                *, 
                openapi_spec: Optional[dict[str, Any]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def cancel_invocation_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def get_invocation_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

        def get_openapi_spec(self) -> Optional[dict[str, Any]]: ...

        def invoke_handler(self, fn: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]: ...

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

        def ws_handler(self, fn: WSHandler) -> WSHandler: ...


```