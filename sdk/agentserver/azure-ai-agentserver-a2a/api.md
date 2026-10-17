```py
namespace azure.ai.agentserver.a2a

    class azure.ai.agentserver.a2a.A2AAgentServerHost(AgentServerHost):
        property agent_card: AgentCard    # Read-only
        property request_handler: RequestHandler    # Read-only
        property routes: list[BaseRoute]    # Read-only

        def __init__(
                self,
                *,
                agent_card: AgentCard,
                card_modifier: Optional[Callable[[AgentCard], Awaitable[AgentCard]]] = ...,
                context_builder: Optional[ServerCallContextBuilder] = ...,
                request_handler: RequestHandler,
                **kwargs: Any
            ) -> None: ...


```