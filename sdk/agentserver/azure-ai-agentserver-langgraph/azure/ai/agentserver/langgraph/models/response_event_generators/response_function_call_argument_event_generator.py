# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=unused-argument,name-too-long
# mypy: ignore-errors
from typing import List

from langchain_core import messages as langgraph_messages
from langchain_core.messages import AnyMessage

from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core import AgentRunContext

from ..utils import extract_function_call
from . import ResponseEventGenerator, StreamEventState


class ResponseFunctionCallArgumentEventGenerator(ResponseEventGenerator):
    def __init__(self, logger, parent: ResponseEventGenerator, item_id, message_id, output_index: int):
        super().__init__(logger, parent)
        self.item_id = item_id
        self.output_index = output_index
        self.aggregated_content = ""
        self.message_id = message_id

    def try_process_message(
        self, message, context: AgentRunContext, stream_state: StreamEventState
    ) -> tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]:
        is_processed = False
        events = []
        next_processor = self
        if not self.started:
            self.started = True  # does not need to do anything special on start

        is_processed, next_processor, processed_events = self.process(message, context, stream_state)
        if not is_processed:
            self.logger.warning(f"FunctionCallArgumentEventGenerator did not process message: {message}")
        events.extend(processed_events)

        if self.should_end(message):
            has_finish_reason = self.has_finish_reason(message)
            complete_events = self.on_end(message, context, stream_state)
            events.extend(complete_events)
            next_processor = self.parent
            is_processed = has_finish_reason  # if has finish reason, mark as processed and stop further processing

        return is_processed, next_processor, events

    def on_start(
        self, event: AnyMessage, run_details, stream_state: StreamEventState
    ) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        if self.started:
            return True, []
        self.started = True
        return True, []

    def process(
        self, message: AnyMessage, run_details, stream_state: StreamEventState
    ) -> tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]:
        tool_call = self.get_tool_call_info(message)
        if tool_call:
            _, _, argument = extract_function_call(tool_call)
            if argument:
                argument_delta_event = project_models.ResponseFunctionCallArgumentsDeltaEvent(
                    item_id=self.item_id,
                    output_index=self.output_index,
                    delta=argument,
                    sequence_number=stream_state.sequence_number,
                )
                stream_state.sequence_number += 1
                self.aggregated_content += argument
                return True, self, [argument_delta_event]
        return False, self, []

    def has_finish_reason(self, message: AnyMessage) -> bool:
        if not message or message.id != self.message_id:
            return False
        if isinstance(message, langgraph_messages.AIMessageChunk):
            if not message.tool_call_chunks:
                # new tool call started, end this argument processing
                return True
            if message.response_metadata.get("finish_reason"):
                # tool call finished
                return True
        elif isinstance(message, langgraph_messages.AIMessage):
            return True
        return False

    def should_end(self, event: AnyMessage) -> bool:
        if event is None:
            return True
        if event.id != self.message_id:
            return True
        return False

    def on_end(
        self, message: AnyMessage, context: AgentRunContext, stream_state: StreamEventState
    ) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        done_event = project_models.ResponseFunctionCallArgumentsDoneEvent(
            item_id=self.item_id,
            output_index=self.output_index,
            arguments=self.aggregated_content,
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1
        self.parent.aggregate_content(self.aggregated_content)  # pass aggregated content to parent
        return [done_event]

    def get_tool_call_info(self, message: langgraph_messages.AnyMessage):
        if isinstance(message, langgraph_messages.AIMessageChunk):
            if message.tool_call_chunks:
                if len(message.tool_call_chunks) > 1:
                    self.logger.warning(
                        f"There are {len(message.tool_call_chunks)} tool calls found. "
                        + "Only the first one will be processed."
                    )
                return message.tool_call_chunks[0]
        elif isinstance(message, langgraph_messages.AIMessage):
            if message.tool_calls:
                if len(message.tool_calls) > 1:
                    self.logger.warning(
                        f"There are {len(message.tool_calls)} tool calls found. "
                        + "Only the first one will be processed."
                    )
                return message.tool_calls[0]
        return None
