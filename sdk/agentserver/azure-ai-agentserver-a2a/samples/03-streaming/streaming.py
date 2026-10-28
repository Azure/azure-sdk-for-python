# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Stream a greeting as incremental updates to one native A2A artifact.

From the samples directory, run ``python 03-streaming\\streaming.py``
and then ``python sample_client.py --stream`` in another terminal.

Local task storage is in memory; hosted default storage uses Foundry.
"""

import asyncio
import os
import uuid

os.environ.setdefault("OTEL_INSTRUMENTATION_A2A_SDK_ENABLED", "false")

from a2a.helpers import new_task_from_user_message, new_text_message, new_text_part
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill, TaskState
from a2a.utils.errors import TaskNotCancelableError

from azure.ai.agentserver.a2a import A2AAgentServerHost
from azure.ai.agentserver.core import AgentConfig


class StreamingGreetingExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task
        if task is None:
            if context.message is None:
                raise ValueError("A2A request did not contain a message")
            task = new_task_from_user_message(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue=event_queue, task_id=task.id, context_id=task.context_id)
        await updater.update_status(
            state=TaskState.TASK_STATE_WORKING,
            message=new_text_message("Generating a greeting"),
        )
        artifact_id = str(uuid.uuid4())
        chunks = ("Hello ", "from ", "streaming ", "A2A!")
        for index, text in enumerate(chunks):
            last_chunk = index == len(chunks) - 1
            await updater.add_artifact(
                artifact_id=artifact_id,
                name="greeting",
                parts=[new_text_part(text=text, media_type="text/plain")],
                append=index > 0,
                last_chunk=last_chunk,
            )
            if not last_chunk:
                await asyncio.sleep(0.2)

        await updater.update_status(
            state=TaskState.TASK_STATE_COMPLETED,
            message=new_text_message("Done"),
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        del context, event_queue
        raise TaskNotCancelableError(message="Cancellation is not supported by this greeting sample")


agent_url = os.environ.get("A2A_AGENT_URL", f"http://localhost:{AgentConfig.from_env().port}/a2a")
card = AgentCard(
    name="Streaming Greeting Agent",
    description="Streams a greeting as updates to one artifact",
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(streaming=True),
    supported_interfaces=[AgentInterface(protocol_binding="JSONRPC", protocol_version="1.0", url=agent_url)],
    skills=[
        AgentSkill(
            id="streaming_greeting",
            name="Streaming greeting",
            description="Returns an incremental greeting",
            input_modes=["text/plain"],
            output_modes=["text/plain"],
            tags=["hello", "streaming"],
            examples=["Say hello"],
        )
    ],
)
host = A2AAgentServerHost(agent_card=card, agent_executor=StreamingGreetingExecutor())

if __name__ == "__main__":
    host.run()
