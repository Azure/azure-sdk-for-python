# Copyright (c) Microsoft. All rights reserved.

import json
from dataclasses import dataclass
from uuid import uuid4

from agent_framework import (
    AgentResponseUpdate,
    Content,
    Executor,
    Message,
    SupportsChatGetResponse,
    WorkflowContext,
    WorkflowEvent,
    handler,
)


@dataclass
class ReviewRequest:
    """Structured request passed from Worker to Reviewer for evaluation."""

    request_id: str
    user_messages: list[Message]
    agent_messages: list[Message]


@dataclass
class ReviewResponse:
    """Structured response from Reviewer back to Worker."""

    request_id: str
    feedback: str
    approved: bool

    @staticmethod
    def convert_from_payload(payload: str) -> "ReviewResponse":
        data = json.loads(payload)
        return ReviewResponse(
            request_id=data["request_id"],
            feedback=data["feedback"],
            approved=data["approved"],
        )


PendingReviewState = tuple[ReviewRequest, list[Message]]


class Worker(Executor):
    """Executor that generates responses and incorporates feedback when necessary."""

    def __init__(self, id: str, chat_client: SupportsChatGetResponse) -> None:
        super().__init__(id=id)
        self._chat_client = chat_client
        self._pending_requests: dict[str, PendingReviewState] = {}

    @handler
    async def handle_user_messages(self, user_messages: list[Message], ctx: WorkflowContext[ReviewRequest]) -> None:
        print("Worker: Received user messages, generating response...")

        messages = [Message(role="system", contents=[Content.from_text("You are a helpful assistant.")])]
        messages.extend(user_messages)

        print("Worker: Calling LLM to generate response...")
        response = await self._chat_client.get_response(messages=messages)
        print(f"Worker: Response generated: {response.messages[-1].text}")

        messages.extend(response.messages)

        request = ReviewRequest(request_id=str(uuid4()), user_messages=user_messages, agent_messages=response.messages)
        print(f"Worker: Sending response for review (ID: {request.request_id[:8]})")
        await ctx.send_message(request)

        self._pending_requests[request.request_id] = (request, messages)

    @handler
    async def handle_review_response(self, review: ReviewResponse, ctx: WorkflowContext[ReviewRequest]) -> None:
        print(f"Worker: Received review for request {review.request_id[:8]} - Approved: {review.approved}")

        if review.request_id not in self._pending_requests:
            raise ValueError(f"Unknown request ID in review: {review.request_id}")

        request, messages = self._pending_requests.pop(review.request_id)

        if review.approved:
            print("Worker: Response approved. Emitting to external consumer...")
            contents: list[Content] = []
            for message in request.agent_messages:
                contents.extend(message.contents)

            await ctx.add_event(
                WorkflowEvent(
                    "output",
                    data=AgentResponseUpdate(contents=contents, role="assistant"),
                )
            )
            return

        print(f"Worker: Response not approved. Feedback: {review.feedback}")
        print("Worker: Regenerating response with feedback...")

        messages.append(Message(role="system", contents=[Content.from_text(review.feedback)]))
        messages.append(
            Message(
                role="system",
                contents=[Content.from_text("Please incorporate the feedback and regenerate the response.")],
            )
        )
        messages.extend(request.user_messages)

        response = await self._chat_client.get_response(messages=messages)
        print(f"Worker: New response generated: {response.messages[-1].text}")

        messages.extend(response.messages)

        new_request = ReviewRequest(
            request_id=review.request_id,
            user_messages=request.user_messages,
            agent_messages=response.messages,
        )
        await ctx.send_message(new_request)

        self._pending_requests[new_request.request_id] = (new_request, messages)

    async def on_checkpoint_save(self) -> dict:
        return {"pending_requests": self._pending_requests}

    async def on_checkpoint_restore(self, data: dict) -> None:
        self._pending_requests = data.get("pending_requests", {})
