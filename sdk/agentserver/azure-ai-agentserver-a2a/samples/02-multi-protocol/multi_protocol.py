# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Host A2A v1.0 and Invocations on one Foundry agent server."""

import os

os.environ.setdefault("OTEL_INSTRUMENTATION_A2A_SDK_ENABLED", "false")

from a2a.helpers import new_task_from_user_message, new_text_message, new_text_part
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, TaskState
from starlette.requests import Request
from starlette.responses import JSONResponse

from azure.ai.agentserver.a2a import A2AAgentServerHost
from azure.ai.agentserver.invocations import InvocationAgentServerHost


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
        await updater.add_artifact(parts=[new_text_part(text="Hello over A2A", media_type="text/plain")])
        await updater.update_status(
            state=TaskState.TASK_STATE_COMPLETED,
            message=new_text_message("Done"),
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        del context, event_queue
        raise NotImplementedError("Cancellation is not supported")


class MultiProtocolHost(A2AAgentServerHost, InvocationAgentServerHost):
    pass


card = AgentCard(
    name="Multi-protocol Agent",
    description="Accepts A2A and Invocations requests",
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(),
    supported_interfaces=[
        AgentInterface(
            protocol_binding="JSONRPC",
            protocol_version="1.0",
            url="http://localhost:8088/a2a",
        )
    ],
    skills=[],
)
handler = DefaultRequestHandler(
    agent_executor=HelloWorldExecutor(),
    task_store=InMemoryTaskStore(),
    agent_card=card,
)
host = MultiProtocolHost(agent_card=card, request_handler=handler)


@host.invoke_handler
async def handle_invocation(_request: Request) -> JSONResponse:
    return JSONResponse({"message": "Hello over Invocations"})


if __name__ == "__main__":
    host.run()
