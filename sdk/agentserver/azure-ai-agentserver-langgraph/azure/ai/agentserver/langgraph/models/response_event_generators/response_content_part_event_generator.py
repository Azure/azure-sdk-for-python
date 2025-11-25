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
    def __init__(
        self,
        logger,
        parent: ResponseEventGenerator,
        item_id: str,
        message_id: str,
        output_index: int,
        content_index: int,
    ):
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

    def on_start(   # mypy: ignore[override]
        self, event, run_details, stream_state: StreamEventState
    ) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
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

    def on_end(self, message, context, stream_state: StreamEventState
            ) -> List[project_models.ResponseStreamEvent]:   # mypy: ignore[override]
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
            self.parent.aggregate_content(aggregated_content)
        return [done_event]

    def try_create_item_content_helper(self, message):
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

    def aggregate_content(self, content):
        return self.item_content_helper.aggregate_content(content)

    def is_text_content(self, content):
        if isinstance(content, str):
            return True
        if isinstance(content, list) and all(isinstance(c, str) for c in content):
            return True
        return False

    def create_child_processor(self, message) -> ResponseEventGenerator:
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
        if not isinstance(message, langgraph_messages.BaseMessageChunk):
            return False
        if message.response_metadata and message.response_metadata.get("finish_reason"):
            return True
        return False

    def should_end(self, event) -> bool:
        # Determine if the event indicates end of the stream for this item
        if event is None:
            return True
        if event.id != self.message_id:
            return True
        # if is Message not MessageChunk, should create child and end in the second iteration
        if not isinstance(event, langgraph_messages.BaseMessageChunk):
            return self.item_content_helper.has_aggregated_content
        return False
