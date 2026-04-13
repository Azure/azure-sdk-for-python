# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import datetime
import time
from typing import Any, Dict, Generator, Optional

from copilot.generated.session_events import SessionEvent, SessionEventType

from azure.ai.agentserver.core.models import Response as OpenAIResponse
from azure.ai.agentserver.core.models.projects import (
    ItemContentOutputText,
    ResponseCompletedEvent,
    ResponseContentPartAddedEvent,
    ResponseContentPartDoneEvent,
    ResponseCreatedEvent,
    ResponseFailedEvent,
    ResponseInProgressEvent,
    ResponseOutputItemAddedEvent,
    ResponseOutputItemDoneEvent,
    ResponsesAssistantMessageItemResource,
    ResponseStreamEvent,
    ResponseTextDeltaEvent,
    ResponseTextDoneEvent,
)
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers — build model objects for nested RAPI event fields.
#
# Nested objects MUST be model instances (not plain dicts).  Dict-based
# nested objects cause SSE stream truncation on the ADC platform — the
# proxy drops events when as_dict() serializes differently for raw dicts
# vs typed models.  Keyword-arg construction + model objects matches the
# agent_framework adapter pattern which is proven to stream correctly.
# ---------------------------------------------------------------------------

def _make_message_item(
    item_id: str, text: str, *, status: str = "completed",
) -> ResponsesAssistantMessageItemResource:
    """Build an assistant message item model."""
    return ResponsesAssistantMessageItemResource(
        id=item_id, status=status,
        content=[ItemContentOutputText(text=text, annotations=[])],
    )


def _make_part(text: str = "") -> ItemContentOutputText:
    """Build an output_text content part model."""
    return ItemContentOutputText(text=text, annotations=[])


def _make_response(
    response_id: str,
    status: str,
    created_at: int,
    context: AgentRunContext,
    output: Optional[list] = None,
    usage: Optional[dict] = None,
    error: Optional[dict] = None,
) -> OpenAIResponse:
    """Build an OpenAI Response model."""
    resp_dict: Dict[str, Any] = {
        "object": "response",
        "id": response_id,
        "status": status,
        "created_at": created_at,
        "output": output or [],
    }
    agent_id = context.get_agent_id_object()
    if agent_id is not None:
        resp_dict["agent_id"] = agent_id
    conversation = context.get_conversation_object()
    if conversation is not None:
        resp_dict["conversation"] = conversation
    if usage is not None:
        resp_dict["usage"] = usage
    if error is not None:
        resp_dict["error"] = error
    return OpenAIResponse(resp_dict)


class CopilotResponseConverter:
    @staticmethod
    def to_response(text: str, context: AgentRunContext, *, extra_output: Optional[list] = None) -> OpenAIResponse:
        """Build a non-streaming OpenAI Response from the final assistant text.

        If *text* is empty, a fallback message is used so the response is
        never blank.  *extra_output* items (e.g. MCP consent requests) are
        appended to the response output list.
        """
        item_id = context.id_generator.generate_message_id()
        if not text.strip():
            text = "(No response text was produced by the agent.)"
        output: list = [
            ResponsesAssistantMessageItemResource(
                id=item_id,
                status="completed",
                content=[
                    ItemContentOutputText(text=text, annotations=[]),
                ],
            )
        ]
        if extra_output:
            output.extend(extra_output)
        return OpenAIResponse(
            id=context.response_id,
            created_at=datetime.datetime.now(),
            output=output,
        )


class CopilotStreamingResponseConverter:
    """Converts Copilot SDK session events into RAPI streaming response events.

    Uses dict-based construction for all SSE events to ensure correct
    serialization by the agentserver-core framework.  This matches the
    proven pattern from the hosted-agent-cli skills template.

    Event order per turn:
        ASSISTANT_TURN_START
        ASSISTANT_MESSAGE_DELTA xN   (streaming text chunks)
        ASSISTANT_USAGE              (token counts — arrives BEFORE message)
        ASSISTANT_MESSAGE            (authoritative full text — always emitted)
        ASSISTANT_TURN_END           (always emitted, even on error)
        SESSION_IDLE                 (session finished processing)

    In multi-turn (tool-calling) flows the turn sequence repeats.
    """

    def __init__(self, context: AgentRunContext):
        self.context = context
        self._sequence = -1
        self._created_at: int = int(time.time())
        self._accumulated_text: str = ""
        self._turn_count: int = 0
        self._item_id: str = context.id_generator.generate_message_id()
        self._usage: Optional[Dict[str, Any]] = None
        self._completed: bool = False
        self._failed: bool = False
        self._session_error: Optional[str] = None

    def _seq(self) -> int:
        self._sequence += 1
        return self._sequence

    def _resp(self, status: str, output=None, usage=None, error=None) -> OpenAIResponse:
        return _make_response(
            self.context.response_id, status, self._created_at,
            self.context, output=output, usage=usage, error=error,
        )

    def _resp_minimal(self, status: str) -> OpenAIResponse:
        """Minimal response model for envelope events — keeps initial SSE burst small.

        The ADC proxy has a limited initial read buffer.  Full response
        dicts (with agent_id, conversation, output, metadata) push the
        first 4 envelope events over the buffer limit, causing truncation.
        Use this for created/in_progress; use ``_resp`` for completed.
        """
        return OpenAIResponse({"id": self.context.response_id, "object": "response",
                                "status": status, "created_at": self._created_at})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def to_stream_events(
        self, events: list[SessionEvent], context: AgentRunContext,
    ) -> Generator[ResponseStreamEvent, None, None]:
        """Convert a collected batch of Copilot SessionEvents into RAPI stream events."""
        for event in events:
            yield from self._convert_event(event, context)

    # ------------------------------------------------------------------
    # Event conversion
    # ------------------------------------------------------------------

    def _convert_event(
        self, event: SessionEvent, context: AgentRunContext,
    ) -> Generator[ResponseStreamEvent, None, None]:
        """Yield zero or more RAPI ResponseStreamEvents for a single Copilot session event."""
        item_id = self._item_id

        match event:

            # -- Turn start --
            case SessionEvent(type=SessionEventType.ASSISTANT_TURN_START):
                self._item_id = context.id_generator.generate_message_id()
                item_id = self._item_id
                self._accumulated_text = ""
                is_first_turn = self._turn_count == 0
                self._turn_count += 1

                if is_first_turn:
                    yield ResponseCreatedEvent(
                        sequence_number=self._seq(),
                        response=self._resp_minimal("in_progress"),
                    )
                    yield ResponseInProgressEvent(
                        sequence_number=self._seq(),
                        response=self._resp_minimal("in_progress"),
                    )

                yield ResponseOutputItemAddedEvent(
                    sequence_number=self._seq(), output_index=0,
                    item=_make_message_item(item_id, "", status="in_progress"),
                )
                yield ResponseContentPartAddedEvent(
                    sequence_number=self._seq(), item_id=item_id,
                    output_index=0, content_index=0,
                    part=_make_part(""),
                )

            # -- Streaming text delta --
            case SessionEvent(type=SessionEventType.ASSISTANT_MESSAGE_DELTA, data=data) if data and data.content:
                self._accumulated_text += data.content
                yield ResponseTextDeltaEvent(
                    sequence_number=self._seq(), item_id=item_id,
                    output_index=0, content_index=0, delta=data.content,
                )

            # -- Token / model usage (arrives BEFORE ASSISTANT_MESSAGE) --
            case SessionEvent(type=SessionEventType.ASSISTANT_USAGE, data=data) if data:
                usage: Dict[str, Any] = {}
                if data.input_tokens is not None:
                    usage["input_tokens"] = int(data.input_tokens)
                if data.output_tokens is not None:
                    usage["output_tokens"] = int(data.output_tokens)
                total = (int(data.input_tokens or 0)) + (int(data.output_tokens or 0))
                if total:
                    usage["total_tokens"] = total
                if usage:
                    self._usage = usage

            # -- Full assistant message (authoritative, always emitted) --
            # Emit a synthetic delta if no streaming deltas arrived, then
            # emit all done-events immediately.
            case SessionEvent(type=SessionEventType.ASSISTANT_MESSAGE, data=data) if data and data.content:
                text = data.content

                if not self._accumulated_text:
                    self._accumulated_text = text
                    yield ResponseTextDeltaEvent(
                        sequence_number=self._seq(), item_id=item_id,
                        output_index=0, content_index=0, delta=text,
                    )

                final_item = _make_message_item(item_id, text)
                yield ResponseTextDoneEvent(
                    sequence_number=self._seq(), item_id=item_id,
                    output_index=0, content_index=0, text=text,
                )
                yield ResponseContentPartDoneEvent(
                    sequence_number=self._seq(), item_id=item_id,
                    output_index=0, content_index=0, part=_make_part(text),
                )
                yield ResponseOutputItemDoneEvent(
                    sequence_number=self._seq(), output_index=0,
                    item=final_item,
                )
                yield ResponseCompletedEvent(
                    sequence_number=self._seq(),
                    response=self._resp("completed", output=[final_item], usage=self._usage),
                )
                self._completed = True

            # -- Session error --
            case SessionEvent(type=SessionEventType.SESSION_ERROR, data=data):
                error_msg = ""
                if data:
                    error_msg = getattr(data, 'message', None) or getattr(data, 'content', None) or repr(data)
                self._session_error = error_msg
                logger.error(f"Copilot session error: {error_msg}")

                if not self._completed and not self._failed:
                    yield ResponseFailedEvent(
                        sequence_number=self._seq(),
                        response=self._resp("failed", error={"code": "server_error", "message": error_msg}),
                    )
                    self._failed = True

            # -- Turn end --
            case SessionEvent(type=SessionEventType.ASSISTANT_TURN_END):
                pass

            # -- Session idle (safety net) --
            case SessionEvent(type=SessionEventType.SESSION_IDLE):
                if not self._completed and not self._failed and self._turn_count > 0:
                    logger.warning("SESSION_IDLE without response.completed -- forcing completion")
                    text = self._accumulated_text
                    if not text.strip():
                        if self._session_error:
                            text = f"(Agent error: {self._session_error})"
                        else:
                            text = "(No response text was produced by the agent.)"
                    final_item = _make_message_item(item_id, text)
                    yield ResponseTextDeltaEvent(
                        sequence_number=self._seq(), item_id=item_id,
                        output_index=0, content_index=0, delta=text,
                    )
                    yield ResponseTextDoneEvent(
                        sequence_number=self._seq(), item_id=item_id,
                        output_index=0, content_index=0, text=text,
                    )
                    yield ResponseContentPartDoneEvent(
                        sequence_number=self._seq(), item_id=item_id,
                        output_index=0, content_index=0, part=_make_part(text),
                    )
                    yield ResponseOutputItemDoneEvent(
                        sequence_number=self._seq(), output_index=0,
                        item=final_item,
                    )
                    yield ResponseCompletedEvent(
                        sequence_number=self._seq(),
                        response=self._resp("completed", output=[final_item], usage=self._usage),
                    )
                    self._completed = True

            # -- MCP OAuth consent required --
            case SessionEvent(type=SessionEventType.MCP_OAUTH_REQUIRED, data=data) if data:
                consent_url = getattr(data, "url", "") or ""
                server_label = (
                    getattr(data, "server_name", "")
                    or getattr(data, "name", "")
                    or "unknown"
                )
                logger.info(f"MCP OAuth consent required: server={server_label} url={consent_url}")
                consent_item = {
                    "type": "oauth_consent_request",
                    "id": context.id_generator.generate_message_id(),
                    "consent_link": consent_url,
                    "server_label": server_label,
                }
                yield ResponseOutputItemAddedEvent(
                    sequence_number=self._seq(), output_index=1, item=consent_item,
                )
                yield ResponseOutputItemDoneEvent(
                    sequence_number=self._seq(), output_index=1, item=consent_item,
                )

            # -- Reasoning --
            case SessionEvent(type=SessionEventType.ASSISTANT_REASONING, data=data):
                if data and data.content:
                    logger.debug(f"Copilot reasoning: {data.content[:120]!r}")

            # -- All other events --
            case _:
                ename = event.type.name if event.type else "UNKNOWN"
                logger.debug(f"Unhandled Copilot event: {ename}")
