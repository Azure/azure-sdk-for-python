# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Persist native A2A Tasks using Core's generic state store.

Run this example, send a message with sample_client.py, stop the server, and
restart it with the same AGENTSERVER_STATE_ROOT. GetTask still returns the saved
completed Task. Local storage is file-backed; hosted storage uses Foundry.
This persists task snapshots, not unfinished executor execution.
"""

import os

os.environ.setdefault("OTEL_INSTRUMENTATION_A2A_SDK_ENABLED", "false")

from a2a.helpers import get_message_text, new_task_from_user_message, new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill, Part, TaskState
from a2a.utils.errors import TaskNotCancelableError

from azure.ai.agentserver.a2a import A2AAgentServerHost, FoundryTaskStore
from azure.ai.agentserver.core import AgentConfig


class PersistentEchoExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        if context.message is None:
            raise ValueError("A2A request did not contain a message")
        task = context.current_task
        if task is None:
            task = new_task_from_user_message(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue=event_queue, task_id=task.id, context_id=task.context_id)
        await updater.add_artifact(
            parts=[Part(text=f"Persisted: {get_message_text(context.message)}", media_type="text/plain")]
        )
        await updater.update_status(
            state=TaskState.TASK_STATE_COMPLETED,
            message=new_text_message("Saved in the state store"),
        )

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        del context, event_queue
        raise TaskNotCancelableError(message="Cancellation is not supported by this persistence sample")


config = AgentConfig.from_env()
agent_url = os.environ.get("A2A_AGENT_URL", f"http://localhost:{config.port}/a2a")
card = AgentCard(
    name="State Store Agent",
    description="Persists native A2A Tasks across server restarts",
    version="1.0.0",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    capabilities=AgentCapabilities(),
    supported_interfaces=[AgentInterface(protocol_binding="JSONRPC", protocol_version="1.0", url=agent_url)],
    skills=[
        AgentSkill(
            id="persistent_echo",
            name="Persistent echo",
            description="Saves an echo artifact that can be retrieved after restart",
            tags=["state-store"],
            input_modes=["text/plain"],
            output_modes=["text/plain"],
        )
    ],
)
task_store = None if config.is_hosted else FoundryTaskStore("a2a-state-store-demo")
host = A2AAgentServerHost(
    agent_card=card,
    agent_executor=PersistentEchoExecutor(),
    task_store=task_store,
)


@host.shutdown_handler
async def close_storage() -> None:
    if task_store is not None:
        await task_store.aclose()


if __name__ == "__main__":
    host.run()
