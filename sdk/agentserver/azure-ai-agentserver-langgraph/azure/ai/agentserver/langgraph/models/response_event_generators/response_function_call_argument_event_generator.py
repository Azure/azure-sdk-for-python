# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=unused-argument,name-too-long
# mypy: ignore-errors
from typing import List, Union

from langchain_core import messages as langgraph_messages
from langchain_core.messages import AnyMessage
from langgraph.types import Interrupt

from azure.ai.agentserver.core.models import projects as project_models
from . import ResponseEventGenerator, StreamEventState
from ..human_in_the_loop_helper import HumanInTheLoopHelper
from ..utils import extract_function_call
from ..._context import LanggraphRunContext


class ResponseFunctionCallArgumentEventGenerator(ResponseEventGenerator):
    """Event generator that streams function-call argument deltas.

    Emits ``response.function_call_arguments.delta`` events for each
    argument chunk and a final ``response.function_call_arguments.done``
    event on completion.
    """

    def __init__(
        self,
        logger,
        parent: ResponseEventGenerator,
        item_id,
        message_id,
        output_index: int,
        *,
        hitl_helper: HumanInTheLoopHelper | None = None,
    ) -> None:
        """
        :param logger: Logger instance for diagnostics.
        :param parent: Parent :class:`ResponseEventGenerator`.
        :type parent: ResponseEventGenerator
        :param item_id: ID of the parent output item (function call).
        :param message_id: ID of the LangGraph message this generator is bound to.
        :param output_index: Zero-based index of the output item.
        :type output_index: int
        :param hitl_helper: Optional human-in-the-loop helper for interrupt handling.
        :type hitl_helper: HumanInTheLoopHelper | None
        """
        super().__init__(logger, parent)
        self.item_id = item_id
        self.output_index = output_index
        self.aggregated_content = ""
        self.message_id = message_id
        self.hitl_helper = hitl_helper

    def try_process_message(
        self, message, context: LanggraphRunContext, stream_state: StreamEventState
    ) -> tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]:
        """Process one argument chunk and optionally finalise the function call.

        :param message: The incoming LangGraph message or Interrupt.
        :param context: The agent run context.
        :type context: LanggraphRunContext
        :param stream_state: Mutable stream sequencing state.
        :type stream_state: StreamEventState
        :return: Tuple of ``(is_processed, next_processor, events)``.
        :rtype: tuple[bool, ResponseEventGenerator, list[project_models.ResponseStreamEvent]]
        """
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
        """Mark this generator as started (no events emitted).

        :param event: The triggering message.
        :type event: AnyMessage
        :param run_details: Agent run details (unused).
        :param stream_state: Mutable stream sequencing state.
        :type stream_state: StreamEventState
        :return: Tuple of ``(True, [])``. 
        :rtype: tuple[bool, list]
        """
        if self.started:
            return True, []
        self.started = True
        return True, []

    def process(
        self, message: Union[langgraph_messages.AnyMessage, Interrupt], run_details, stream_state: StreamEventState
    ) -> tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]:
        """Extract argument data from the message and emit a delta event.

        :param message: The LangGraph message or Interrupt to extract arguments from.
        :type message: AnyMessage | Interrupt
        :param run_details: Agent run details (unused).
        :param stream_state: Mutable stream sequencing state.
        :type stream_state: StreamEventState
        :return: Tuple of ``(is_processed, next_processor, events)``.
        :rtype: tuple[bool, ResponseEventGenerator, list[project_models.ResponseStreamEvent]]
        """
        if self.should_end(message):
            return False, self, []

        argument = None
        if isinstance(message, Interrupt):
            if self.hitl_helper:
                _, _, argument = self.hitl_helper.interrupt_to_function_call(message)
            else:
                argument = None
        else:
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
        """Return ``True`` if the message signals end of this function call's argument stream.

        :param message: The message to inspect.
        :type message: AnyMessage
        :return: ``True`` when a ``finish_reason`` is present or a new tool call starts.
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

    def should_end(self, event: AnyMessage) -> bool:
        """Return ``True`` when this generator should stop handling events.

        :param event: The message event to evaluate.
        :type event: AnyMessage
        :return: ``True`` if ``event`` is ``None`` or belongs to a different message ID.
        :rtype: bool
        """
        if event is None:
            return True
        if event.id != self.message_id:
            return True
        return False

    def on_end(
        self, message: AnyMessage, context: LanggraphRunContext, stream_state: StreamEventState
    ) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """Emit the ``response.function_call_arguments.done`` event and propagate to parent.

        :param message: The terminating message.
        :type message: AnyMessage
        :param context: The agent run context.
        :type context: LanggraphRunContext
        :param stream_state: Mutable stream sequencing state.
        :type stream_state: StreamEventState
        :return: List containing the ``ResponseFunctionCallArgumentsDoneEvent``.
        :rtype: list[project_models.ResponseStreamEvent]
        """
        done_event = project_models.ResponseFunctionCallArgumentsDoneEvent(
            item_id=self.item_id,
            output_index=self.output_index,
            arguments=self.aggregated_content,
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1
        self.parent.aggregate_content(self.aggregated_content)  # pass aggregated content to parent
        return [done_event]

    def get_tool_call_info(self, message: Union[langgraph_messages.AnyMessage, Interrupt]) -> dict | None:
        """Extract the first tool call or tool call chunk from a message.

        :param message: The LangGraph message to inspect.
        :type message: AnyMessage | Interrupt
        :return: The first tool-call dict/chunk, or ``None`` if none is present.
        :rtype: dict | None
        """
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
