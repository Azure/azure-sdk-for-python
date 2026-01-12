# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=unused-argument
# mypy: ignore-errors
import time
from typing import List

from langchain_core import messages as langgraph_messages

from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

from .response_event_generator import (
    ResponseEventGenerator,
    StreamEventState,
)
from .response_output_item_event_generator import ResponseOutputItemEventGenerator


class ResponseStreamEventGenerator(ResponseEventGenerator):
    """
    :meta private:
    Response stream event generator.
    """

    def __init__(self, logger, parent, *, hitl_helper=None):
        super().__init__(logger, parent)
        self.hitl_helper = hitl_helper
        self.aggregated_contents: List[project_models.ItemResource] = []

    def on_start(
        self, context: AgentRunContext, stream_state: StreamEventState
    ) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        if self.started:
            return True, []
        agent_id = context.get_agent_id_object()
        conversation = context.get_conversation_object()
        # response create event
        response_dict = {
            "object": "response",
            "agent_id": agent_id,
            "conversation": conversation,
            "id": context.response_id,
            "status": "in_progress",
            "created_at": int(time.time()),
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
            "id": context.response_id,
            "status": "in_progress",
            "created_at": int(time.time()),
        }
        in_progress_event = project_models.ResponseInProgressEvent(
            response=project_models.Response(response_dict),
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1
        self.started = True
        return True, [created_event, in_progress_event]

    def should_complete(self, event: langgraph_messages.AnyMessage) -> bool:
        # Determine if the event indicates completion
        if event is None:
            return True
        return False

    def try_process_message(
        self, message: langgraph_messages.AnyMessage, context: AgentRunContext, stream_state: StreamEventState
    ) -> tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]:
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
        # Determine if the event indicates end of the stream
        if event is None:
            return True
        return False

    def on_end(self, message: langgraph_messages.AnyMessage, context: AgentRunContext, stream_state: StreamEventState):
        agent_id = context.get_agent_id_object()
        conversation = context.get_conversation_object()
        response_dict = {
            "object": "response",
            "agent_id": agent_id,
            "conversation": conversation,
            "id": context.response_id,
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

    def aggregate_content(self, content):
        # aggregate content from children
        if isinstance(content, list):
            for c in content:
                self.aggregate_content(c)
        if isinstance(content, project_models.ItemResource):
            self.aggregated_contents.append(content)
        else:
            raise ValueError(f"Invalid content type: {type(content)}, expected: {project_models.ItemResource}")
