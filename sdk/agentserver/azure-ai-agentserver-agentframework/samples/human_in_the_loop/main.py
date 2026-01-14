# Copyright (c) Microsoft. All rights reserved.

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from agent_framework import (  # noqa: E402
    Executor,
    InMemoryCheckpointStorage,
    WorkflowAgent,
    WorkflowBuilder,
    WorkflowContext,
    handler,
    response_handler,
)
from workflow_as_agent_reflection_pattern import (  # noqa: E402
    ReviewRequest,
    ReviewResponse,
    Worker,
)

from azure.ai.agentserver.agentframework import from_agent_framework

load_dotenv()

@dataclass
class HumanReviewRequest:
    """A request message type for escalation to a human reviewer."""

    agent_request: ReviewRequest | None = None

    def convert_to_payload(self) -> str:
        """Convert the HumanReviewRequest to a payload string."""
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
        # In this simplified example, we always escalate to a human manager.
        # See workflow_as_agent_reflection.py for an implementation
        # using an automated agent to make the review decision.
        print(f"Reviewer: Evaluating response for request {request.request_id[:8]}...")
        print("Reviewer: Escalating to human manager...")

        # Forward the request to a human manager by sending a HumanReviewRequest.
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
        # Accept the human review response and forward it back to the Worker.
        print(f"Reviewer: Accepting human review for request {response.request_id[:8]}...")
        print(f"Reviewer: Human feedback: {response.feedback}")
        print(f"Reviewer: Human approved: {response.approved}")
        print("Reviewer: Forwarding human review back to worker...")
        await ctx.send_message(response, target_id=self._worker_id)


def build_agent():
    # Build a workflow with bidirectional communication between Worker and Reviewer,
    # and escalation paths for human review.
    agent = (
        WorkflowBuilder()
        .register_executor(
            lambda: Worker(
                id="sub-worker",
                chat_client=AzureOpenAIChatClient(credential=AzureCliCredential()),
            ),
            name="worker",
        )
        .register_executor(
            lambda: ReviewerWithHumanInTheLoop(worker_id="sub-worker"),
            name="reviewer",
        )
        .add_edge("worker", "reviewer")  # Worker sends requests to Reviewer
        .add_edge("reviewer", "worker")  # Reviewer sends feedback to Worker
        .set_start_executor("worker")
        .build()
        .as_agent()  # Convert workflow into an agent interface
    )
    return agent


async def run_agent() -> None:
    """Run the workflow inside the agent server adapter."""
    agent = build_agent()
    await from_agent_framework(agent).run_async()

if __name__ == "__main__":
    asyncio.run(run_agent())