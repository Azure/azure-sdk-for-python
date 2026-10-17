# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Host a native A2A v1.0 hello-world agent in Foundry."""

from a2a.helpers import new_task_from_user_message, new_text_message, new_text_part
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill, TaskState

from azure.ai.agentserver.a2a import A2AAgentServerHost


class HelloWorldExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task
        if task is None:
            if context.message is None:
                raise ValueError("A2A request did not contain a message")
            task = new_task_from_user_message(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(
            event_queue=event_queue,
            task_id=task.id,
            context_id=task.context_id,
        )
        await updater.add_artifact(parts=[new_text_part(text="Hello from Foundry", media_type="text/plain")])
        await updater.update_status(
            state=TaskState.TASK_STATE_COMPLETED,
            message=new_text_message("Done"),
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        del context, event_queue
        raise NotImplementedError("Cancellation is not supported")


card = AgentCard(
    name="Hello World Agent",
    description="Returns a greeting",
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(),
    supported_interfaces=[
        AgentInterface(
            protocol_binding="JSONRPC",
            protocol_version="1.0",
            url="http://localhost:8088/invocations/a2a",
        )
    ],
    skills=[
        AgentSkill(
            id="hello_world",
            name="Hello world",
            description="Returns a greeting",
            input_modes=["text/plain"],
            output_modes=["text/plain"],
            tags=["hello"],
            examples=["Say hello"],
        )
    ],
)
handler = DefaultRequestHandler(
    agent_executor=HelloWorldExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=card,
)
host = A2AAgentServerHost(agent_card=card, request_handler=handler)

if __name__ == "__main__":
    host.run()
