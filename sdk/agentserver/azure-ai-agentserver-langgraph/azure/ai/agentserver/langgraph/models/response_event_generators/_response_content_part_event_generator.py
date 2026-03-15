# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Optional

from langchain_core import messages as langgraph_messages

from azure.ai.agentserver.core.models import _projects as project_models

from . import _item_content_helpers as item_content_helpers
from ._response_event_generator import (
    ResponseEventGenerator,
    ResponseGeneratorEvents,
    ResponseGeneratorMessage,
    ResponseGeneratorResult,
    StreamEventState,
)
from ._response_output_text_event_generator import ResponseOutputTextEventGenerator
from ..._context import LanggraphRunContext


class ResponseContentPartEventGenerator(ResponseEventGenerator):
    """Generate content-part events for a single response item."""

    def __init__(
        self,
        logger,
        parent: ResponseEventGenerator,
        item_id: str,
        message_id: Optional[str],
        output_index: int,
        content_index: int,
    ):
        """Initialize the content-part event generator.

        :param logger: The logger used for diagnostics.
        :type logger: logging.Logger
        :param parent: The parent generator in the event chain.
        :type parent: ResponseEventGenerator
        :param item_id: The response item identifier.
        :type item_id: str
        :param message_id: The originating message identifier.
        :type message_id: Optional[str]
        :param output_index: The output item index.
        :type output_index: int
        :param content_index: The content part index within the item.
        :type content_index: int
        """
        super().__init__(logger, parent)
        self.output_index = output_index
        self.content_index = content_index
        self.item_id = item_id
        self.message_id = message_id
        self.aggregated_content = ""
        self.item_content_helper: Optional[item_content_helpers.ItemContentHelper] = None

    def try_process_message(
        self, message: ResponseGeneratorMessage, context: LanggraphRunContext, stream_state: StreamEventState
    ) -> ResponseGeneratorResult:
        """Process a message into content-part events.

        :param message: The message to process.
        :type message: Any
        :param context: The run context for the current request.
        :type context: Any
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Processing status, next generator, and emitted events.
        :rtype: tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]
        """
        is_processed = False
        events: ResponseGeneratorEvents = []
        next_processor: Optional[ResponseEventGenerator] = self
        if not self.item_content_helper:
            if not self.try_create_item_content_helper(message):
                # cannot create item content, skip this message
                self.logger.warning("Cannot create item content helper for message: %s", message)
                return True, self, []
        if self.item_content_helper and not self.started:
            self.started, start_events = self.on_start(message, context, stream_state)
            if not self.started:
                # could not start processing, skip this message
                return True, self, []
            events.extend(start_events)

        if self.should_end(message):
            _, complete_events = self.on_end(message, context, stream_state)
            events.extend(complete_events)
            next_processor = self.parent
            is_processed = self.has_finish_reason(message) if message else False
            return is_processed, next_processor, events

        child_processor = self.create_child_processor(message)
        if child_processor:
            next_processor = child_processor

        return is_processed, next_processor, events

    def on_start(
        self, _event: ResponseGeneratorMessage, _run_details: LanggraphRunContext, stream_state: StreamEventState
    ) -> tuple[bool, ResponseGeneratorEvents]:
        """Emit the content-part-added event.

        :param _event: The current message.
        :type _event: Any
        :param _run_details: The run context, unused by this generator.
        :type _run_details: Any
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Start status and emitted events.
        :rtype: tuple[bool, List[project_models.ResponseStreamEvent]]
        """
        if self.started:
            return False, []
        if self.item_content_helper is None:
            return False, []

        start_event = project_models.ResponseContentPartAddedEvent(
            item_id=self.item_id,
            output_index=self.output_index,
            content_index=self.content_index,
            part=self.item_content_helper.create_item_content(),
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1
        self.started = True

        return True, [start_event]

    def on_end(
        self, _message: ResponseGeneratorMessage, _context: LanggraphRunContext, stream_state: StreamEventState
    ) -> tuple[bool, ResponseGeneratorEvents]:
        """Emit the content-part-done event.

        :param _message: The terminal message.
        :type _message: Any
        :param _context: The run context, unused by this generator.
        :type _context: Any
        :param stream_state: The mutable stream state.
        :type stream_state: StreamEventState

        :return: Completion status and the completion events.
        :rtype: tuple[bool, List[project_models.ResponseStreamEvent]]
        """
        if self.item_content_helper is None:
            return False, []
        aggregated_content = self.item_content_helper.create_item_content()
        done_event = project_models.ResponseContentPartDoneEvent(
            item_id=self.item_id,
            output_index=self.output_index,
            content_index=self.content_index,
            part=aggregated_content,
            sequence_number=stream_state.sequence_number,
        )
        stream_state.sequence_number += 1
        if self.parent:
            self.parent.aggregate_content(aggregated_content.as_dict())
        return True, [done_event]

    def try_create_item_content_helper(self, message: ResponseGeneratorMessage) -> bool:
        """Create the content helper that matches the message payload.

        :param message: The message to inspect.
        :type message: Any

        :return: True when a helper was created.
        :rtype: bool
        """
        if isinstance(message, (langgraph_messages.AIMessage, langgraph_messages.ToolMessage)):
            if self.is_text_content(message.content):
                self.item_content_helper = item_content_helpers.OutputTextItemContentHelper()
                return True
        if isinstance(message, (langgraph_messages.HumanMessage, langgraph_messages.SystemMessage)):
            if self.is_text_content(message.content):
                self.item_content_helper = item_content_helpers.InputTextItemContentHelper()
                return True
        return False

    def aggregate_content(self, content: Any) -> None:
        """Aggregate child content into the current content helper.

        :param content: The child content to aggregate.
        :type content: Any
        """
        if self.item_content_helper is None:
            return None
        self.item_content_helper.aggregate_content(content)
        return None

    def is_text_content(self, content: Any) -> bool:
        """Check whether the message content can be treated as plain text.

        :param content: The content payload to inspect.
        :type content: Any

        :return: True when the content is representable as text.
        :rtype: bool
        """
        if isinstance(content, str):
            return True
        if isinstance(content, list) and all(isinstance(c, str) for c in content):
            return True
        return False

    def create_child_processor(self, _message: ResponseGeneratorMessage) -> Optional[ResponseEventGenerator]:
        """Create the child generator for the current content helper.

        :param _message: The originating message, unused by this generator.
        :type _message: Any

        :return: The child generator.
        :rtype: Optional[ResponseEventGenerator]
        """
        if self.item_content_helper is None:
            return None
        if self.item_content_helper.content_type in (
            project_models.ItemContentType.INPUT_TEXT,
            project_models.ItemContentType.OUTPUT_TEXT,
        ):
            return ResponseOutputTextEventGenerator(
                logger=self.logger,
                parent=self,
                content_index=self.content_index,
                output_index=self.output_index,
                item_id=self.item_id,
                message_id=self.message_id,
            )
        raise ValueError(f"Unsupported item content type for child processor: {self.item_content_helper.content_type}")

    def has_finish_reason(self, message: ResponseGeneratorMessage) -> bool:
        """Check whether the message contains a finish reason.

        :param message: The message to inspect.
        :type message: Any

        :return: True when a finish reason is present.
        :rtype: bool
        """
        if not isinstance(message, langgraph_messages.BaseMessageChunk):
            return False
        if message.response_metadata and message.response_metadata.get("finish_reason"):
            return True
        return False

    def should_end(self, event: ResponseGeneratorMessage) -> bool:
        """Determine whether content generation for this item should end.

        :param event: The current message or chunk.
        :type event: Any

        :return: True when the generator should stop.
        :rtype: bool
        """
        if event is None:
            return True
        if not isinstance(event, langgraph_messages.BaseMessage):
            return True
        if event.id != self.message_id:
            return True
        # if is Message not MessageChunk, should create child and end in the second iteration
        if not isinstance(event, langgraph_messages.BaseMessageChunk):
            if self.item_content_helper is None:
                return True
            return self.item_content_helper.has_aggregated_content
        return False
