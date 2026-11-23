# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Host a native A2A v1.0 hello-world agent.

From the samples directory, run ``python 01-hello-world\\hello_world.py``
and then ``python sample_client.py`` in another terminal.

Local task storage is in memory; hosted default storage uses Foundry.
See the samples README for setup, state limitations, and hosted-agent guidance.
"""

import os

os.environ.setdefault("OTEL_INSTRUMENTATION_A2A_SDK_ENABLED", "false")

from a2a.helpers import new_task_from_user_message, new_text_message, new_text_part
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill, TaskState
from a2a.utils.errors import TaskNotCancelableError

from azure.ai.agentserver.a2a import A2AAgentServerHost
from azure.ai.agentserver.core import AgentConfig


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
        raise TaskNotCancelableError(message="Cancellation is not supported by this greeting sample")


agent_url = os.environ.get("A2A_AGENT_URL", f"http://localhost:{AgentConfig.from_env().port}/a2a")
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
            url=agent_url,
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
host = A2AAgentServerHost(agent_card=card, agent_executor=HelloWorldExecutor())

if __name__ == "__main__":
    host.run()
