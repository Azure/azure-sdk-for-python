# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exercise the local A2A samples with the official native client.

Run ``python sample_client.py --help`` for sending and task lookup.
This client targets the local container routes, not the authenticated public
Foundry endpoint.
"""

import argparse
import asyncio

import httpx2 as httpx
from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import get_artifact_text, get_message_text, new_text_message
from a2a.types import GetTaskRequest, Role, SendMessageRequest, Task, TaskState


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", default="http://localhost:8088", help="Local server base URL, without /a2a.")
    parser.add_argument("--message", default="hello")
    parser.add_argument("--context-id", help="Reuse an opaque context ID from a previous response.")
    parser.add_argument("--get-task", metavar="TASK_ID", help="Retrieve a task instead of sending a message.")
    return parser.parse_args(argv)


def _print_task(task: Task) -> None:
    print(f"Task: {task.id}", flush=True)
    print(f"Context: {task.context_id}", flush=True)
    print(f"State: {TaskState.Name(task.status.state)}", flush=True)
    for artifact in task.artifacts:
        print(f"Artifact: {get_artifact_text(artifact, delimiter='')}", flush=True)


async def _run(args: argparse.Namespace) -> None:
    async with httpx.AsyncClient(headers={"A2A-Version": "1.0"}, timeout=60.0) as http_client:
        card = await A2ACardResolver(http_client, args.endpoint).get_agent_card(
            relative_card_path="a2a/.well-known/agent-card.json",
        )
        client = await create_client(card, ClientConfig(streaming=False, httpx_client=http_client))
        try:
            if args.get_task:
                _print_task(await client.get_task(GetTaskRequest(id=args.get_task)))
                return

            request = SendMessageRequest(
                message=new_text_message(
                    args.message,
                    role=Role.ROLE_USER,
                    context_id=args.context_id,
                )
            )
            completed = False
            async for response in client.send_message(request):
                if response.HasField("task"):
                    _print_task(response.task)
                    completed = response.task.status.state == TaskState.TASK_STATE_COMPLETED
                elif response.HasField("message"):
                    print(f"Message: {get_message_text(response.message)}", flush=True)
                    completed = True
            if not completed:
                raise RuntimeError("The greeting sample did not return a completed task or inline message")
        finally:
            await client.close()


if __name__ == "__main__":
    asyncio.run(_run(_parse_args()))
