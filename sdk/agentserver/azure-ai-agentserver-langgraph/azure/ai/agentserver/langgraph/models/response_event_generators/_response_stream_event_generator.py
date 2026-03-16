# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import time
from typing import Any, List, Optional, Union

from langchain_core import messages as langgraph_messages

from azure.ai.agentserver.core.models import _projects as project_models
from ._response_event_generator import (
    ResponseEventGenerator,
    ResponseGeneratorEvents,
    ResponseGeneratorMessage,
    ResponseGeneratorResult,
    StreamEventState,
)
from ._response_output_item_event_generator import ResponseOutputItemEventGenerator
from ..._context import LanggraphRunContext


class ResponseStreamEventGenerator(ResponseEventGenerator):
    """
    :meta private:
    Response stream event generator.
    """

    def __init__(self, logger, parent, *, hitl_helper=None):
        """Initialize the top-level response stream generator.

        :param logger: The logger used for diagnostics.
        :type logger: logging.Logger
        :param parent: The parent generator, if any.
        :type parent: ResponseEventGenerator | None
        :keyword hitl_helper: Optional helper for human-in-the-loop interrupts.
        :type hitl_helper: Any
        """
        super().__init__(logger, parent)
        self.hitl_helper = hitl_helper
        self.aggregated_contents: List[project_models.ItemResource] = []

    def on_start(
        self,
        _message: ResponseGeneratorMessage,
        context: LanggraphRunContext,
        stream_state: StreamEventState,
    ) -> tuple[bool, ResponseGeneratorEvents]:
        """Emit the initial response-created and in-progress stream events.

        :param context: The run context for the current request.
        :type context: LanggraphRunContext
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Whether generation started and the emitted events.
        :rtype: tuple[bool, List[project_models.ResponseStreamEvent]]
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
        """Determine whether the current event represents stream completion.

        :param event: The current stream event.
        :type event: langgraph_messages.AnyMessage

        :return: True when the stream should be considered complete.
        :rtype: bool
        """
        if event is None:
            return True
        return False

    def try_process_message(
        self,
        message: ResponseGeneratorMessage,
        context: LanggraphRunContext,
        stream_state: StreamEventState,
    ) -> ResponseGeneratorResult:
        """Process a streamed message or transition to a child generator.

        :param message: The streamed message to process.
        :type message: Optional[langgraph_messages.AnyMessage]
        :param context: The run context for the current request.
        :type context: LanggraphRunContext
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Processing status, next generator, and emitted events.
        :rtype: tuple[bool, Optional[ResponseEventGenerator], List[project_models.ResponseStreamEvent]]
        """
        is_processed = False
        next_processor: Optional[ResponseEventGenerator] = self
        events: ResponseGeneratorEvents = []

        if not self.started:
            self.started, start_events = self.on_start(message, context, stream_state)
            events.extend(start_events)

        if message is not None:
            # create a child processor
            next_processor = ResponseOutputItemEventGenerator(
                self.logger, self, len(self.aggregated_contents), message.id, hitl_helper=self.hitl_helper
            )
            return is_processed, next_processor, events

        if self.should_end(message):
            # received a None message, indicating end of the stream
            is_processed, done_events = self.on_end(message, context, stream_state)
            events.extend(done_events)
            next_processor = None

        return is_processed, next_processor, events

    def should_end(self, event: ResponseGeneratorMessage) -> bool:
        """Determine whether the stream should end for the current event.

        :param event: The current stream event.
        :type event: langgraph_messages.AnyMessage

        :return: True when the generator should end.
        :rtype: bool
        """
        if event is None:
            return True
        return False

    def on_end(
        self,
        _message: ResponseGeneratorMessage,
        context: LanggraphRunContext,
        stream_state: StreamEventState,
    ) -> tuple[bool, ResponseGeneratorEvents]:
        """Emit the final response-completed event for the stream.

        :param _message: The terminal message for the stream.
        :type _message: Optional[langgraph_messages.AnyMessage]
        :param context: The run context for the current request.
        :type context: LanggraphRunContext
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Completion status and the final stream events.
        :rtype: tuple[bool, List[project_models.ResponseStreamEvent]]
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
        return True, [done_event]

    def aggregate_content(self, content: Any) -> None:
        """Collect item resources produced by child generators.

        :param content: The child content to aggregate.
        :type content: Any
        """
        if isinstance(content, list):
            for c in content:
                self.aggregate_content(c)
            return
        if isinstance(content, project_models.ItemResource):
            self.aggregated_contents.append(content)
        else:
            raise ValueError(f"Invalid content type: {type(content)}, expected: {project_models.ItemResource}")
