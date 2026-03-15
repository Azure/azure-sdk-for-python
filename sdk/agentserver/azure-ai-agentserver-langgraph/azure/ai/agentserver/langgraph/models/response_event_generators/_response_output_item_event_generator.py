# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Optional, Union

from langchain_core import messages as langgraph_messages
from langchain_core.messages import AnyMessage
from langgraph.types import Interrupt

from azure.ai.agentserver.core.models import _projects as project_models
from azure.ai.agentserver.core.server.common.id_generator._id_generator import IdGenerator
from . import _item_resource_helpers as item_resource_helpers
from ._response_event_generator import (
    ResponseEventGenerator,
    ResponseGeneratorEvents,
    ResponseGeneratorMessage,
    ResponseGeneratorResult,
    StreamEventState,
)
from ._response_content_part_event_generator import ResponseContentPartEventGenerator
from ._response_function_call_argument_event_generator import ResponseFunctionCallArgumentEventGenerator
from .._human_in_the_loop_helper import HumanInTheLoopHelper
from ..._context import LanggraphRunContext


class ResponseOutputItemEventGenerator(ResponseEventGenerator):
    """Generate output-item added and done events for one streamed message."""

    def __init__(self, logger, parent: ResponseEventGenerator,
                 output_index: int, message_id: Optional[str] = None,
                 *, hitl_helper: Optional[HumanInTheLoopHelper] = None):
        """Initialize the output-item event generator.

        :param logger: The logger used for diagnostics.
        :type logger: logging.Logger
        :param parent: The parent generator in the event chain.
        :type parent: ResponseEventGenerator
        :param output_index: The output item index.
        :type output_index: int
        :param message_id: The originating message identifier.
        :type message_id: str
        :param hitl_helper: Optional helper for human-in-the-loop interrupts.
        :type hitl_helper: HumanInTheLoopHelper
        """
        super().__init__(logger, parent)
        self.output_index = output_index
        self.message_id = message_id
        self.item_resource_helper: Optional[item_resource_helpers.ItemResourceHelper] = None
        self.hitl_helper = hitl_helper

    def try_process_message(
        self, message: ResponseGeneratorMessage, context: LanggraphRunContext, stream_state: StreamEventState
    ) -> ResponseGeneratorResult:
        """Process one streamed message into output-item events.

        :param message: The message or interrupt to process.
        :type message: Union[AnyMessage, Interrupt, None]
        :param context: The run context for the current request.
        :type context: LanggraphRunContext
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Processing status, next generator, and emitted events.
        :rtype: tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]
        """
        is_processed = False
        next_processor: Optional[ResponseEventGenerator] = self
        events: ResponseGeneratorEvents = []
        if self.item_resource_helper is None:
            if not self.try_create_item_resource_helper(message, context.agent_run.id_generator):
                # cannot create item resource, skip this message
                self.logger.warning("Cannot create item resource helper for message: %s, skipping.", message)
                return True, self, []

        if self.item_resource_helper and not self.started:
            self.started, start_events = self.on_start(message, context, stream_state)
            if not self.started:
                # could not start processing, skip this message
                self.logger.warning("Cannot create start events for message: %s, skipping.", message)
                return True, self, []
            events.extend(start_events)

        if self.should_end(message):
            # not the message this processor is handling
            _, complete_events = self.on_end(message, context, stream_state)
            is_processed = self.message_id == message.id if message else False
            next_processor = self.parent
            events.extend(complete_events)
            return is_processed, next_processor, events

        child_processor = self.create_child_processor(message)
        if child_processor:
            self.logger.info("Created child processor: %s", child_processor)
            return False, child_processor, events

        if message and not isinstance(message, Interrupt):
            # no child processor, process the content directly
            self.aggregate_content(message.content)
            is_processed = True

        return is_processed, next_processor, events

    def on_start(
        self, _event: ResponseGeneratorMessage, _context: LanggraphRunContext, stream_state: StreamEventState
    ) -> tuple[bool, ResponseGeneratorEvents]:
        """Emit the output-item-added event for this message.

        :param _event: The current message or interrupt.
        :type _event: Union[AnyMessage, Interrupt]
        :param _context: The run context, unused by this generator.
        :type _context: LanggraphRunContext
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Start status and emitted events.
        :rtype: tuple[bool, List[project_models.ResponseStreamEvent]]
        """
        if self.started:
            return True, []
        if self.item_resource_helper is None:
            return False, []

        item_resource = self.item_resource_helper.create_item_resource(is_done=False)
        if item_resource is None:
            # cannot know what item resource to create
            return False, []
        item_added_event = project_models.ResponseOutputItemAddedEvent(
            output_index=self.output_index,
            sequence_number=stream_state.sequence_number,
            item=item_resource,
        )
        stream_state.sequence_number += 1
        self.started = True
        return True, [item_added_event]

    def should_end(self, event: ResponseGeneratorMessage) -> bool:
        """Determine whether this output-item generator should end.

        :param event: The current message or interrupt.
        :type event: Union[AnyMessage, Interrupt]

        :return: True when the generator should end.
        :rtype: bool
        """
        if event is None:
            self.logger.info("Received None event, ending processor.")
            return True
        if event.id != self.message_id:
            return True
        return False

    def on_end(
        self, _message: ResponseGeneratorMessage, _context: LanggraphRunContext, stream_state: StreamEventState
    ) -> tuple[bool, ResponseGeneratorEvents]:
        """Emit the output-item-done event for this generator.

        :param _message: The terminal message or interrupt.
        :type _message: Union[AnyMessage, Interrupt]
        :param _context: The run context, unused by this generator.
        :type _context: LanggraphRunContext
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Completion status and the emitted completion events.
        :rtype: tuple[bool, List[project_models.ResponseStreamEvent]]
        """
        if not self.started or self.item_resource_helper is None:  # should not happen
            return False, []

        item_resource = self.item_resource_helper.create_item_resource(is_done=True)
        # response item done event
        done_event = project_models.ResponseOutputItemDoneEvent(
            output_index=self.output_index,
            sequence_number=stream_state.sequence_number,
            item=item_resource,
        )
        stream_state.sequence_number += 1
        if self.parent:
            self.parent.aggregate_content(item_resource)  # pass aggregated content to parent
        return True, [done_event]

    def aggregate_content(self, content: Any) -> None:
        """Aggregate child content into the current item resource helper.

        :param content: The child content to aggregate.
        :type content: Any
        """
        if self.item_resource_helper is None:
            return None
        self.item_resource_helper.add_aggregate_content(content)

    def try_create_item_resource_helper(self, event: ResponseGeneratorMessage, id_generator: IdGenerator) -> bool:
        """Create the item-resource helper for the current message type.

        :param event: The message or interrupt to inspect.
        :type event: Optional[Union[AnyMessage, Interrupt]]
        :param id_generator: The identifier generator for new item ids.
        :type id_generator: IdGenerator

        :return: True when a helper was created.
        :rtype: bool
        """
        helper: Optional[item_resource_helpers.ItemResourceHelper] = None
        if isinstance(event, langgraph_messages.AIMessageChunk) and event.tool_call_chunks:
            helper = item_resource_helpers.FunctionCallItemResourceHelper(
                item_id=id_generator.generate_function_call_id(), tool_call=event.tool_call_chunks[0]
            )
        elif isinstance(event, langgraph_messages.AIMessage) and event.tool_calls:
            helper = item_resource_helpers.FunctionCallItemResourceHelper(
                item_id=id_generator.generate_function_call_id(), tool_call=event.tool_calls[0]
            )
        elif isinstance(event, langgraph_messages.AIMessage) and event.content:
            helper = item_resource_helpers.MessageItemResourceHelper(
                item_id=id_generator.generate_message_id(), role=project_models.ResponsesMessageRole.ASSISTANT
            )
        elif isinstance(event, langgraph_messages.HumanMessage) and event.content:
            helper = item_resource_helpers.MessageItemResourceHelper(
                item_id=id_generator.generate_message_id(), role=project_models.ResponsesMessageRole.USER
            )
        elif isinstance(event, langgraph_messages.SystemMessage) and event.content:
            helper = item_resource_helpers.MessageItemResourceHelper(
                item_id=id_generator.generate_message_id(), role=project_models.ResponsesMessageRole.SYSTEM
            )
        elif isinstance(event, langgraph_messages.ToolMessage):
            helper = item_resource_helpers.FunctionCallOutputItemResourceHelper(
                item_id=id_generator.generate_function_output_id(), call_id=event.tool_call_id
            )
        elif isinstance(event, Interrupt):
            helper = item_resource_helpers.FunctionCallInterruptItemResourceHelper(
                item_id=id_generator.generate_function_output_id(),
                hitl_helper=self.hitl_helper,
                interrupt=event,
            )

        if helper is None:
            return False

        self.item_resource_helper = helper
        return True

    def create_child_processor(self, message: ResponseGeneratorMessage) -> Optional[ResponseEventGenerator]:
        """Create the child generator for the current item resource type.

        :param message: The originating message or interrupt.
        :type message: Optional[Union[AnyMessage, Interrupt]]

        :return: The child generator, if one is required.
        :rtype: Optional[ResponseEventGenerator]
        """
        if self.item_resource_helper is None or message is None:
            return None
        if self.item_resource_helper.item_type == project_models.ItemType.FUNCTION_CALL:
            return ResponseFunctionCallArgumentEventGenerator(
                self.logger,
                self,
                item_id=self.item_resource_helper.item_id,
                message_id=message.id,
                output_index=self.output_index,
                hitl_helper=self.hitl_helper,
            )
        if self.item_resource_helper.item_type == project_models.ItemType.MESSAGE:
            if self.item_resource_helper.item_id is None or self.message_id is None:
                return None
            return ResponseContentPartEventGenerator(
                self.logger, self, self.item_resource_helper.item_id, message.id, self.output_index, content_index=0
            )
        return None
