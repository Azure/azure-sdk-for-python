# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=unused-argument
# mypy: disable-error-code="return-value,assignment"
from typing import List

from azure.ai.agentserver.core.models import projects as project_models
from .response_event_generator import (
    ResponseEventGenerator,
    StreamEventState,
)
from ..._context import LanggraphRunContext


class ResponseOutputTextEventGenerator(ResponseEventGenerator):
    """Event generator that streams text delta events for an output text content part.

    Emits ``response.text.delta`` events for each text chunk and a final
    ``response.text.done`` event on completion.
    """

    def __init__(
        self,
        logger,
        parent: ResponseEventGenerator,
        content_index: int,
        output_index: int,
        item_id: str,
        message_id: str,
    ) -> None:
        """
        :param logger: Logger instance for diagnostics.
        :param parent: Parent :class:`ResponseEventGenerator`.
        :type parent: ResponseEventGenerator
        :param content_index: Zero-based index of the content part within the output item.
        :type content_index: int
        :param output_index: Zero-based index of the output item in the response.
        :type output_index: int
        :param item_id: ID of the parent output item.
        :type item_id: str
        :param message_id: ID of the LangGraph message this generator is bound to.
        :type message_id: str
        """
        super().__init__(logger, parent)
        self.output_index = output_index
        self.content_index = content_index
        self.item_id = item_id
        self.message_id = message_id
        self.aggregated_content = ""

    def try_process_message(
        self, message, context, stream_state: StreamEventState
    ) -> tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]:
        """Stream text content from the message and optionally finalise the part.

        :param message: The incoming LangGraph message, or ``None`` to signal end-of-stream.
        :param context: The agent run context.
        :param stream_state: Mutable stream sequencing state.
        :type stream_state: StreamEventState
        :return: Tuple of ``(is_processed, next_processor, events)``.
        :rtype: tuple[bool, ResponseEventGenerator, list[project_models.ResponseStreamEvent]]
        """
        is_processed = False
        events = []
        next_processor = self
        if not self.started:
            self.started = True

        if message:
            is_processed, next_processor, processed_events = self.process(message, context, stream_state)
            if not is_processed:
                self.logger.warning(f"OutputTextEventGenerator did not process message: {message}")
            events.extend(processed_events)

        if self.should_end(message):
            is_processed, complete_events = self.on_end(message, context, stream_state)
            events.extend(complete_events)
            next_processor = self.parent

        return is_processed, next_processor, events

    def process(
        self, message, run_details, stream_state: StreamEventState
    ) -> tuple[bool, ResponseEventGenerator, List[project_models.ResponseStreamEvent]]:
        """Extract text from the message and emit a ``response.text.delta`` event for each chunk.

        :param message: The LangGraph message containing content.
        :param run_details: Agent run details (unused).
        :param stream_state: Mutable stream sequencing state.
        :type stream_state: StreamEventState
        :return: Tuple of ``(is_processed, next_processor, events)``.
        :rtype: tuple[bool, ResponseEventGenerator, list[project_models.ResponseStreamEvent]]
        """
        if message and message.content:
            content = [message.content] if isinstance(message.content, str) else message.content
            res = []
            for item in content:
                if not isinstance(item, str):
                    self.logger.warning(f"Skipping non-string content item: {item}")
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
            return True, self, res  # mypy: ignore[return-value]
        return False, self, []

    def has_finish_reason(self, message) -> bool:
        """Return ``True`` if the message carries a ``finish_reason`` in its metadata.

        :param message: The message to inspect.
        :return: ``True`` if a finish reason is present and the message belongs to this generator.
        :rtype: bool
        """
        if not message or message.id != self.message_id:
            return False
        if message.response_metadata and message.response_metadata.get("finish_reason"):
            return True
        return False

    def should_end(self, message) -> bool:
        """Return ``True`` when this generator should stop handling events.

        :param message: The message event to evaluate.
        :return: ``True`` if ``message`` is ``None`` or belongs to a different message ID.
        :rtype: bool
        """
        if message is None:
            return True
        if message.id != self.message_id:
            return True
        return False

    def on_end(  # mypy: ignore[override]
        self, message, context: LanggraphRunContext, stream_state: StreamEventState
    ) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """Emit the ``response.text.done`` event and propagate aggregated text to the parent.

        :param message: The terminating message.
        :param context: The agent run context.
        :type context: LanggraphRunContext
        :param stream_state: Mutable stream sequencing state.
        :type stream_state: StreamEventState
        :return: Tuple of ``(has_finish_reason, [ResponseTextDoneEvent])``.
        :rtype: tuple[bool, list[project_models.ResponseStreamEvent]]
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
        self.parent.aggregate_content(self.aggregated_content)
        has_finish = self.has_finish_reason(message)
        return has_finish, [done_event]
