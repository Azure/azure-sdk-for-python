# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List, Optional, Union

from langchain_core import messages as langgraph_messages
from langchain_core.messages import AnyMessage
from langgraph.types import Interrupt

from azure.ai.agentserver.core.models import _projects as project_models
from ._response_event_generator import (
    ResponseEventGenerator,
    ResponseGeneratorEvents,
    ResponseGeneratorMessage,
    ResponseGeneratorResult,
    StreamEventState,
)
from .._human_in_the_loop_helper import HumanInTheLoopHelper
from .._utils import extract_function_call
from ..._context import LanggraphRunContext


class ResponseFunctionCallArgumentEventGenerator(ResponseEventGenerator):  # pylint: disable=C4751
    """Generate function-call-argument delta and done events."""

    def __init__(
        self,
        logger,
        parent: ResponseEventGenerator,
        item_id,
        message_id,
        output_index: int,
        *,
        hitl_helper: Optional[HumanInTheLoopHelper] = None,
    ):
        """Initialize the function-call-argument generator.

        :param logger: The logger used for diagnostics.
        :type logger: logging.Logger
        :param parent: The parent generator in the event chain.
        :type parent: ResponseEventGenerator
        :param item_id: The response item identifier.
        :type item_id: str
        :param message_id: The originating message identifier.
        :type message_id: str
        :param output_index: The output item index.
        :type output_index: int
        :param hitl_helper: Optional helper for interrupt conversion.
        :type hitl_helper: HumanInTheLoopHelper
        """
        super().__init__(logger, parent)
        self.item_id = item_id
        self.output_index = output_index
        self.aggregated_content = ""
        self.message_id = message_id
        self.hitl_helper = hitl_helper

    def try_process_message(
        self, message: ResponseGeneratorMessage, context: LanggraphRunContext, stream_state: StreamEventState
    ) -> ResponseGeneratorResult:
        """Process one message into function-call argument events.

        :param message: The message or interrupt to process.
        :type message: Union[langgraph_messages.AnyMessage, Interrupt]
        :param context: The run context for the current request.
        :type context: LanggraphRunContext
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Processing status, next generator, and emitted events.
        :rtype: tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]
        """
        is_processed = False
        events: ResponseGeneratorEvents = []
        next_processor: Optional[ResponseEventGenerator] = self
        if not self.started:
            self.started = True  # does not need to do anything special on start

        is_processed, next_processor, processed_events = self.process(message, context, stream_state)
        if not is_processed:
            self.logger.warning("FunctionCallArgumentEventGenerator did not process message: %s", message)
        events.extend(processed_events)

        if self.should_end(message):
            has_finish_reason = self.has_finish_reason(message)
            is_processed, complete_events = self.on_end(message, context, stream_state)
            events.extend(complete_events)
            next_processor = self.parent
            is_processed = has_finish_reason  # if has finish reason, mark as processed and stop further processing

        return is_processed, next_processor, events

    def on_start(
        self, _event: ResponseGeneratorMessage, _run_details, _stream_state: StreamEventState
    ) -> tuple[bool, ResponseGeneratorEvents]:
        """Start argument generation for the current function call.

        :param _event: The current message.
        :type _event: AnyMessage
        :param _run_details: The run context, unused by this generator.
        :type _run_details: LanggraphRunContext
        :param _stream_state: The mutable stream state, unused on start.
        :type _stream_state: StreamEventState

        :return: Start status and emitted events.
        :rtype: tuple[bool, List[project_models.ResponseStreamEvent]]
        """
        if self.started:
            return True, []
        self.started = True
        return True, []

    def process(
        self,
        message: ResponseGeneratorMessage,
        _run_details,
        stream_state: StreamEventState,
    ) -> ResponseGeneratorResult:
        """Convert one message into function-call argument delta events.

        :param message: The message or interrupt to process.
        :type message: Union[langgraph_messages.AnyMessage, Interrupt]
        :param _run_details: The run context, unused by this generator.
        :type _run_details: LanggraphRunContext
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Processing status, current generator, and emitted events.
        :rtype: tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]
        """
        if self.should_end(message):
            return False, self, []

        argument = None
        if isinstance(message, Interrupt):
            if self.hitl_helper:
                _, _, argument = self.hitl_helper.interrupt_to_function_call(message)
            else:
                argument = None
        elif isinstance(message, langgraph_messages.BaseMessage):
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

    def has_finish_reason(self, message: ResponseGeneratorMessage) -> bool:
        """Check whether the message marks completion for this argument stream.

        :param message: The message to inspect.
        :type message: AnyMessage

        :return: True when the argument stream should finish.
        :rtype: bool
        """
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

    def should_end(self, event: ResponseGeneratorMessage) -> bool:
        """Determine whether this generator should stop processing.

        :param event: The current event.
        :type event: AnyMessage

        :return: True when processing should stop.
        :rtype: bool
        """
        if event is None:
            return True
        if event.id != self.message_id:
            return True
        return False

    def on_end(
        self, _message: ResponseGeneratorMessage, _context: LanggraphRunContext, stream_state: StreamEventState
    ) -> tuple[bool, ResponseGeneratorEvents]:
        """Emit the final function-call-arguments-done event.

        :param _message: The terminal message for the argument stream.
        :type _message: AnyMessage
        :param _context: The run context, unused by this generator.
        :type _context: LanggraphRunContext
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Completion status and final events.
        :rtype: tuple[bool, List[project_models.ResponseStreamEvent]]
        """
        done_event = project_models.ResponseFunctionCallArgumentsDoneEvent(
            item_id=self.item_id,
            output_index=self.output_index,
            arguments=self.aggregated_content,
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1
        if self.parent:
            self.parent.aggregate_content(self.aggregated_content)  # pass aggregated content to parent
        return True, [done_event]

    def get_tool_call_info(self, message: ResponseGeneratorMessage):
        """Extract the first tool call from a message when present.

        :param message: The message to inspect.
        :type message: Union[langgraph_messages.AnyMessage, Interrupt]

        :return: The first tool call payload, if any.
        :rtype: Optional[dict]
        """
        if isinstance(message, langgraph_messages.AIMessageChunk):
            if message.tool_call_chunks:
                if len(message.tool_call_chunks) > 1:
                    self.logger.warning(
                        "There are %s tool calls found. Only the first one will be processed.",
                        len(message.tool_call_chunks),
                    )
                return message.tool_call_chunks[0]
        elif isinstance(message, langgraph_messages.AIMessage):
            if message.tool_calls:
                if len(message.tool_calls) > 1:
                    self.logger.warning(
                        "There are %s tool calls found. Only the first one will be processed.",
                        len(message.tool_calls),
                    )
                return message.tool_calls[0]
        return None
