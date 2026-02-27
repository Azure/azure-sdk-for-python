# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=unused-argument,consider-using-in,consider-merging-isinstance
# mypy: ignore-errors
from typing import List

from langchain_core import messages as langgraph_messages

from azure.ai.agentserver.core.models import projects as project_models

from . import item_content_helpers
from .response_event_generator import ResponseEventGenerator, StreamEventState
from .response_output_text_event_generator import ResponseOutputTextEventGenerator


class ResponseContentPartEventGenerator(ResponseEventGenerator):
    """Event generator for a single content part within an output item.

    Emits ``response.content_part.added`` and ``response.content_part.done``
    events, and delegates text streaming to a :class:`ResponseOutputTextEventGenerator`.
    """

    def __init__(
        self,
        logger,
        parent: ResponseEventGenerator,
        item_id: str,
        message_id: str,
        output_index: int,
        content_index: int,
    ) -> None:
        """
        :param logger: Logger instance for diagnostics.
        :param parent: Parent :class:`ResponseEventGenerator`.
        :type parent: ResponseEventGenerator
        :param item_id: ID of the parent output item.
        :type item_id: str
        :param message_id: ID of the LangGraph message this generator is bound to.
        :type message_id: str
        :param output_index: Zero-based index of the output item.
        :type output_index: int
        :param content_index: Zero-based index of this content part within the output item.
        :type content_index: int
        """
        super().__init__(logger, parent)
        self.output_index = output_index
        self.content_index = content_index
        self.item_id = item_id
        self.message_id = message_id
        self.aggregated_content = ""
        self.item_content_helper = None

    def try_process_message(
        self, message, context, stream_state: StreamEventState
    ) -> tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]:
        """Initialise the content helper and route the message to a child text processor.

        :param message: The incoming LangGraph message.
        :param context: The agent run context.
        :param stream_state: Mutable stream sequencing state.
        :type stream_state: StreamEventState
        :return: Tuple of ``(is_processed, next_processor, events)``.
        :rtype: tuple[bool, ResponseEventGenerator, list[project_models.ResponseStreamEvent]]
        """
        is_processed = False
        events = []
        next_processor = self
        if not self.item_content_helper:
            if not self.try_create_item_content_helper(message):
                # cannot create item content, skip this message
                self.logger.warning(f"Cannot create item content helper for message: {message}")
                return True, self, []
        if self.item_content_helper and not self.started:
            self.started, start_events = self.on_start(message, context, stream_state)
            if not self.started:
                # could not start processing, skip this message
                return True, self, []
            events.extend(start_events)

        if self.should_end(message):
            complete_events = self.on_end(message, context, stream_state)
            events.extend(complete_events)
            next_processor = self.parent
            is_processed = self.has_finish_reason(message) if message else False
            return is_processed, next_processor, events

        child_processor = self.create_child_processor(message)
        if child_processor:
            next_processor = child_processor

        return is_processed, next_processor, events

    def on_start(  # mypy: ignore[override]
        self, event, run_details, stream_state: StreamEventState
    ) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """Emit the ``response.content_part.added`` event.

        :param event: The triggering message.
        :param run_details: Agent run details (unused).
        :param stream_state: Mutable stream sequencing state.
        :type stream_state: StreamEventState
        :return: Tuple of ``(started, events)``.
        :rtype: tuple[bool, list[project_models.ResponseStreamEvent]]
        """
        if self.started:
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
        self, message, context, stream_state: StreamEventState
    ) -> List[project_models.ResponseStreamEvent]:  # mypy: ignore[override]
        """Emit the ``response.content_part.done`` event and propagate content to the parent.

        :param message: The terminating message.
        :param context: The agent run context.
        :param stream_state: Mutable stream sequencing state.
        :type stream_state: StreamEventState
        :return: List containing the ``ResponseContentPartDoneEvent``.
        :rtype: list[project_models.ResponseStreamEvent]
        """
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
        return [done_event]

    def try_create_item_content_helper(self, message) -> bool:
        """Detect the message role and create the matching :class:`ItemContentHelper`.

        :param message: The LangGraph message to inspect.
        :return: ``True`` if a helper was created; ``False`` if the type is unsupported.
        :rtype: bool
        """
        if isinstance(message, langgraph_messages.AIMessage) or isinstance(message, langgraph_messages.ToolMessage):
            if self.is_text_content(message.content):
                self.item_content_helper = item_content_helpers.OutputTextItemContentHelper()
                return True
        if isinstance(message, langgraph_messages.HumanMessage) or isinstance(
            message, langgraph_messages.SystemMessage
        ):
            if self.is_text_content(message.content):
                self.item_content_helper = item_content_helpers.InputTextItemContentHelper()
                return True
        return False

    def aggregate_content(self, content) -> None:
        """Forward a content chunk to the item content helper for accumulation.

        :param content: The content chunk (string or dict) from the child processor.
        :type content: str | dict
        """
        return self.item_content_helper.aggregate_content(content)

    def is_text_content(self, content) -> bool:
        """Return ``True`` if ``content`` is a plain string or a list of plain strings.

        :param content: Message content to inspect.
        :return: ``True`` if the content is text-only.
        :rtype: bool
        """
        if isinstance(content, str):
            return True
        if isinstance(content, list) and all(isinstance(c, str) for c in content):
            return True
        return False

    def create_child_processor(self, message) -> ResponseEventGenerator:
        """Create a :class:`ResponseOutputTextEventGenerator` for text content parts.

        :param message: The message that triggered child creation.
        :return: An appropriate child :class:`ResponseEventGenerator`.
        :rtype: ResponseEventGenerator
        :raises ValueError: If the content type is not supported for child processing.
        """
        if (
            self.item_content_helper.content_type == project_models.ItemContentType.INPUT_TEXT
            or self.item_content_helper.content_type == project_models.ItemContentType.OUTPUT_TEXT
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

    def has_finish_reason(self, message) -> bool:
        """Return ``True`` if the message carries a ``finish_reason`` in its metadata.

        :param message: The message to inspect.
        :return: ``True`` if a finish reason is present.
        :rtype: bool
        """
        if not isinstance(message, langgraph_messages.BaseMessageChunk):
            return False
        if message.response_metadata and message.response_metadata.get("finish_reason"):
            return True
        return False

    def should_end(self, event) -> bool:
        """Return ``True`` when this generator should stop handling events.

        :param event: The message event to evaluate.
        :return: ``True`` if ``event`` is ``None``, belongs to a different message, or
            is a non-chunk message whose content has already been aggregated.
        :rtype: bool
        """
        if event is None:
            return True
        if event.id != self.message_id:
            return True
        # if is Message not MessageChunk, should create child and end in the second iteration
        if not isinstance(event, langgraph_messages.BaseMessageChunk):
            return self.item_content_helper.has_aggregated_content
        return False
