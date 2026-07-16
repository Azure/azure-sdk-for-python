```py
namespace azure.ai.agentserver.invocations

    class azure.ai.agentserver.invocations.InvocationAgentServerHost(_WSHandlerMixin, AgentServerHost):
        property routes: list[BaseRoute]    # Read-only
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

        def ws_handler(self, fn: WSHandler) -> WSHandler: ...


```