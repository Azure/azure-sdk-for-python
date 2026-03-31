# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List, Optional

from langchain_core import messages as langgraph_messages

from azure.ai.agentserver.core.models import _projects as project_models
from ._response_event_generator import (
    ResponseEventGenerator,
    ResponseGeneratorEvents,
    ResponseGeneratorMessage,
    ResponseGeneratorResult,
    StreamEventState,
)
from ..._context import LanggraphRunContext


class ResponseOutputTextEventGenerator(ResponseEventGenerator):
    """Generate text delta and done events for one response content part."""

    def __init__(
        self,
        logger,
        parent: ResponseEventGenerator,
        content_index: int,
        output_index: int,
        item_id: str,
        message_id: Optional[str],
    ):
        """Initialize the output-text event generator.

        :param logger: The logger used for diagnostics.
        :type logger: logging.Logger
        :param parent: The parent generator in the event chain.
        :type parent: ResponseEventGenerator
        :param content_index: The content index within the output item.
        :type content_index: int
        :param output_index: The output item index.
        :type output_index: int
        :param item_id: The response item identifier.
        :type item_id: str
        :param message_id: The originating message identifier.
        :type message_id: Optional[str]
        """
        super().__init__(logger, parent)
        self.output_index = output_index
        self.content_index = content_index
        self.item_id = item_id
        self.message_id = message_id
        self.aggregated_content = ""

    def try_process_message(
        self, message: ResponseGeneratorMessage, _context, stream_state: StreamEventState
    ) -> ResponseGeneratorResult:
        """Process a message into text delta and completion events.

        :param message: The message chunk to process.
        :type message: AnyMessage
        :param _context: The run context, unused by this generator.
        :type _context: LanggraphRunContext
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Processing status, next generator, and emitted events.
        :rtype: tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]
        """
        is_processed = False
        events: ResponseGeneratorEvents = []
        next_processor: Optional[ResponseEventGenerator] = self
        if not self.started:
            self.started = True

        if isinstance(message, langgraph_messages.BaseMessage):
            is_processed, next_processor, processed_events = self.process(message, stream_state)
            if not is_processed:
                self.logger.warning("OutputTextEventGenerator did not process message: %s", message)
            events.extend(processed_events)

        if self.should_end(message):
            is_processed, complete_events = self.on_end(message, _context, stream_state)
            events.extend(complete_events)
            next_processor = self.parent

        return is_processed, next_processor, events

    def process(
        self, message: langgraph_messages.BaseMessage, stream_state: StreamEventState
    ) -> ResponseGeneratorResult:
        """Convert message content into text delta events.

        :param message: The message containing text content.
        :type message: AnyMessage
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Processing status, current generator, and emitted events.
        :rtype: tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]
        """
        if message and message.content:
            content = [message.content] if isinstance(message.content, str) else message.content
            res: ResponseGeneratorEvents = []
            for item in content:
                if not isinstance(item, str):
                    self.logger.warning("Skipping non-string content item: %s", item)
                    continue
                # create an event for each content item
                chunk_event = project_models.ResponseTextDeltaEvent(
                    item_id=self.item_id,
                    output_index=self.output_index,
                    content_index=self.content_index,
                    delta=item,
                    sequence_number=stream_state.sequence_number,
                )
                self.aggregated_content += item
                stream_state.sequence_number += 1
                res.append(chunk_event)
            return True, self, res
        return False, self, []

    def has_finish_reason(self, message: ResponseGeneratorMessage) -> bool:
        """Check whether the message marks completion for this text stream.

        :param message: The message to inspect.
        :type message: AnyMessage

        :return: True when the message carries a finish reason.
        :rtype: bool
        """
        if not isinstance(message, langgraph_messages.BaseMessage) or message.id != self.message_id:
            return False
        if message.response_metadata and message.response_metadata.get("finish_reason"):
            return True
        return False

    def should_end(self, message: ResponseGeneratorMessage) -> bool:
        """Determine whether text streaming for this item should end.

        :param message: The message to inspect.
        :type message: AnyMessage

        :return: True when the generator should end.
        :rtype: bool
        """
        if message is None:
            return True
        if not isinstance(message, langgraph_messages.BaseMessage):
            return True
        if message.id != self.message_id:
            return True
        return False

    def on_end(
        self, message: ResponseGeneratorMessage, _context: LanggraphRunContext, stream_state: StreamEventState
    ) -> tuple[bool, ResponseGeneratorEvents]:
        """Emit the final text-done event for the current content part.

        :param message: The terminal message for this text stream.
        :type message: AnyMessage
        :param _context: The run context, unused by this generator.
        :type _context: LanggraphRunContext
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Completion status and final events.
        :rtype: tuple[bool, List[project_models.ResponseStreamEvent]]
        """
        if not self.started:
            return False, []

        # finalize the item resource
        done_event = project_models.ResponseTextDoneEvent(
            item_id=self.item_id,
            output_index=self.output_index,
            content_index=self.content_index,
            text=self.aggregated_content,
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1
        if self.parent:
            self.parent.aggregate_content(self.aggregated_content)
        has_finish = self.has_finish_reason(message)
        return has_finish, [done_event]
