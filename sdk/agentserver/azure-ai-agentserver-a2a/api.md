```py
namespace azure.ai.agentserver.a2a

    @experimental
    class azure.ai.agentserver.a2a.A2AAgentServerHost(AgentServerHost):
        property agent_card: AgentCard    # Read-only
        property request_handler: RequestHandler    # Read-only
        property routes: list[BaseRoute]    # Read-only

        def __init__(
                self,
                *,
                agent_card: AgentCard,
                agent_executor: Optional[AgentExecutor] = ...,
                card_modifier: Optional[Callable[[AgentCard], Awaitable[AgentCard]]] = ...,
                context_builder: Optional[ServerCallContextBuilder] = ...,
                request_handler: Optional[RequestHandler] = ...,
                task_store: Optional[TaskStore] = ...,
                **kwargs: Any
            ) -> None: ...


    @experimental
    class azure.ai.agentserver.a2a.FoundryTaskStore(TaskStore): implements AsyncContextManager

        def __init__(
                self,
                name: str,
                *,
                credential: AsyncTokenCredential | None = ...,
                endpoint: FoundryStorageEndpoint | str | None = ...,
                item_ttl_seconds: int = DEFAULT_ITEM_TTL_SECONDS
            ) -> None: ...

        async def aclose(self) -> None: ...

        async def delete(
                self,
                task_id: str,
                context: ServerCallContext
            ) -> None: ...

        async def get(
                self,
                task_id: str,
                context: ServerCallContext
            ) -> Task | None: ...

        async def list(
                self,
                params: ListTasksRequest,
                context: ServerCallContext
            ) -> ListTasksResponse: ...

        async def save(
                self,
                task: Task,
                context: ServerCallContext
            ) -> None: ...


```