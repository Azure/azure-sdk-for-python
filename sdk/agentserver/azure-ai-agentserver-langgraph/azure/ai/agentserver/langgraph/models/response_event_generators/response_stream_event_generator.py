# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=unused-argument
# mypy: ignore-errors
import time
from typing import List

from langchain_core import messages as langgraph_messages

from azure.ai.agentserver.core.models import projects as project_models
from .response_event_generator import (
    ResponseEventGenerator,
    StreamEventState,
)
from .response_output_item_event_generator import ResponseOutputItemEventGenerator
from ..._context import LanggraphRunContext


class ResponseStreamEventGenerator(ResponseEventGenerator):
    """
    :meta private:
    Top-level response stream event generator.

    Manages the lifecycle of a full Response API streaming response,
    emitting ``response.created``, ``response.in_progress``, and
    ``response.completed`` events. Delegates per-message processing to
    :class:`ResponseOutputItemEventGenerator`.
    """

    def __init__(self, logger, parent, *, hitl_helper=None) -> None:
        """
        :param logger: Logger instance for diagnostics.
        :param parent: Parent generator (unused at top level, pass ``None``).
        :param hitl_helper: Optional human-in-the-loop helper for interrupt handling.
        :type hitl_helper: HumanInTheLoopHelper | None
        """
        super().__init__(logger, parent)
        self.hitl_helper = hitl_helper
        self.aggregated_contents: List[project_models.ItemResource] = []

    def on_start(
        self, context: LanggraphRunContext, stream_state: StreamEventState
    ) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """Emit ``response.created`` and ``response.in_progress`` events.

        :param context: The agent run context.
        :type context: LanggraphRunContext
        :param stream_state: Mutable stream sequencing state.
        :type stream_state: StreamEventState
        :return: Tuple of ``(started, events)``.
        :rtype: tuple[bool, list[project_models.ResponseStreamEvent]]
        """
        if self.started:
            return True, []
        agent_id = context.agent_run.get_agent_id_object()
        conversation = context.agent_run.get_conversation_object()
        # response create event
        response_dict = {
            "object": "response",
            "agent_id": agent_id,
            "conversation": conversation,
            "id": context.agent_run.response_id,
            "status": "in_progress",
            "created_at": int(time.time()),
            "output": self.aggregated_contents
        }
        created_event = project_models.ResponseCreatedEvent(
            response=project_models.Response(response_dict),
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1

        # response in progress
        response_dict = {
            "object": "response",
            "agent_id": agent_id,
            "conversation": conversation,
            "id": context.agent_run.response_id,
            "status": "in_progress",
            "created_at": int(time.time()),
            "output": self.aggregated_contents
        }
        in_progress_event = project_models.ResponseInProgressEvent(
            response=project_models.Response(response_dict),
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1
        self.started = True
        return True, [created_event, in_progress_event]

    def should_complete(self, event: langgraph_messages.AnyMessage) -> bool:
        """Return ``True`` when the event signals response completion.

        :param event: The message event to evaluate.
        :type event: AnyMessage
        :return: ``True`` if ``event`` is ``None``.
        :rtype: bool
        """
        if event is None:
            return True
        return False

    def try_process_message(
        self, message: langgraph_messages.AnyMessage, context: LanggraphRunContext, stream_state: StreamEventState
    ) -> tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]:
        """Route the incoming message to the appropriate child processor.

        On first call, emits start events. For non-``None`` messages, creates a
        :class:`ResponseOutputItemEventGenerator` child. For ``None``, emits the
        completion event.

        :param message: The incoming LangGraph message, or ``None`` to signal end-of-stream.
        :type message: AnyMessage
        :param context: The agent run context.
        :type context: LanggraphRunContext
        :param stream_state: Mutable stream sequencing state.
        :type stream_state: StreamEventState
        :return: Tuple of ``(is_processed, next_processor, events)``.
        :rtype: tuple[bool, ResponseEventGenerator, list[project_models.ResponseStreamEvent]]
        """
        is_processed = False
        next_processor = self
        events = []

        if not self.started:
            self.started, start_events = self.on_start(context, stream_state)
            events.extend(start_events)

        if message:
            # create a child processor
            next_processor = ResponseOutputItemEventGenerator(
                self.logger, self, len(self.aggregated_contents), message.id, hitl_helper=self.hitl_helper
            )
            return is_processed, next_processor, events

        if self.should_end(message):
            # received a None message, indicating end of the stream
            done_events = self.on_end(message, context, stream_state)
            events.extend(done_events)
            is_processed = True
            next_processor = None

        return is_processed, next_processor, events

    def should_end(self, event: langgraph_messages.AnyMessage) -> bool:
        """Return ``True`` when the stream has ended.

        :param event: The message event to evaluate.
        :type event: AnyMessage
        :return: ``True`` if ``event`` is ``None``.
        :rtype: bool
        """
        if event is None:
            return True
        return False

    def on_end(self, message: langgraph_messages.AnyMessage, context: LanggraphRunContext,
               stream_state: StreamEventState) -> List[project_models.ResponseStreamEvent]:
        """Emit the ``response.completed`` event and propagate content to the parent.

        :param message: The terminating message (may be ``None``).
        :type message: AnyMessage
        :param context: The agent run context.
        :type context: LanggraphRunContext
        :param stream_state: Mutable stream sequencing state.
        :type stream_state: StreamEventState
        :return: List containing the ``ResponseCompletedEvent``.
        :rtype: list[project_models.ResponseStreamEvent]
        """
        agent_id = context.agent_run.get_agent_id_object()
        conversation = context.agent_run.get_conversation_object()
        response_dict = {
            "object": "response",
            "agent_id": agent_id,
            "conversation": conversation,
            "id": context.agent_run.response_id,
            "status": "completed",
            "created_at": int(time.time()),
            "output": self.aggregated_contents,
        }
        done_event = project_models.ResponseCompletedEvent(
            response=project_models.Response(response_dict),
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1
        if self.parent:
            self.parent.aggregate_content(self.aggregated_contents)
        return [done_event]

    def aggregate_content(self, content) -> None:
        """Accumulate a completed child item resource.

        :param content: A single :class:`ItemResource` or a list of them from a child processor.
        :type content: project_models.ItemResource | list[project_models.ItemResource]
        :raises ValueError: If ``content`` is neither a list nor an :class:`ItemResource`.
        """
        if isinstance(content, list):
            for c in content:
                self.aggregate_content(c)
            return
        if isinstance(content, project_models.ItemResource):
            self.aggregated_contents.append(content)
        else:
            raise ValueError(f"Invalid content type: {type(content)}, expected: {project_models.ItemResource}")
