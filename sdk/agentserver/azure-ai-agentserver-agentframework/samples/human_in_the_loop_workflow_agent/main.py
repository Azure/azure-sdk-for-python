# Copyright (c) Microsoft. All rights reserved.

import asyncio
import json
from dataclasses import dataclass
from typing import Any

from agent_framework import (  # noqa: E402
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    response_handler,
)
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
from workflow_as_agent_reflection_pattern import (  # noqa: E402
    ReviewRequest,
    ReviewResponse,
    Worker,
)

from azure.ai.agentserver.agentframework import from_agent_framework
from azure.ai.agentserver.agentframework.persistence import FileCheckpointRepository

load_dotenv()


@dataclass
class HumanReviewRequest:
    """A request message type for escalation to a human reviewer."""

    agent_request: ReviewRequest | None = None

    def convert_to_payload(self) -> str:
        request = self.agent_request
        payload: dict[str, Any] = {"agent_request": None}

        if request:
            payload["agent_request"] = {
                "request_id": request.request_id,
                "user_messages": [msg.to_dict() for msg in request.user_messages],
                "agent_messages": [msg.to_dict() for msg in request.agent_messages],
            }

        return json.dumps(payload, indent=2)


class ReviewerWithHumanInTheLoop(Executor):
    """Executor that always escalates reviews to a human manager."""

    def __init__(self, worker_id: str, reviewer_id: str | None = None) -> None:
        unique_id = reviewer_id or f"{worker_id}-reviewer"
        super().__init__(id=unique_id)
        self._worker_id = worker_id

    @handler
    async def review(self, request: ReviewRequest, ctx: WorkflowContext) -> None:
        print(f"Reviewer: Evaluating response for request {request.request_id[:8]}...")
        print("Reviewer: Escalating to human manager...")

        await ctx.request_info(
            request_data=HumanReviewRequest(agent_request=request),
            response_type=ReviewResponse,
        )

    @response_handler
    async def accept_human_review(
        self,
        original_request: HumanReviewRequest,
        response: ReviewResponse,
        ctx: WorkflowContext[ReviewResponse],
    ) -> None:
        print(f"Reviewer: Accepting human review for request {response.request_id[:8]}...")
        print(f"Reviewer: Human feedback: {response.feedback}")
        print(f"Reviewer: Human approved: {response.approved}")
        print("Reviewer: Forwarding human review back to worker...")
        await ctx.send_message(response, target_id=self._worker_id)


def create_builder() -> WorkflowBuilder:
    worker = Worker(
        id="sub-worker",
        chat_client=AzureOpenAIChatClient(credential=AzureCliCredential()),
    )
    reviewer = ReviewerWithHumanInTheLoop(worker_id="sub-worker")
    return WorkflowBuilder(start_executor=worker).add_edge(worker, reviewer).add_edge(reviewer, worker)


async def run_agent() -> None:
    builder = create_builder()
    await from_agent_framework(
        builder,
        checkpoint_repository=FileCheckpointRepository(storage_path="./checkpoints"),
    ).run_async()


if __name__ == "__main__":
    asyncio.run(run_agent())
