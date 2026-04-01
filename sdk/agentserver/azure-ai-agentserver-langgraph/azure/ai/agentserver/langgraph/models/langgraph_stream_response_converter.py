# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation
# mypy: disable-error-code="assignment,valid-type"
from typing import List

from langchain_core.messages import AnyMessage

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import ResponseStreamEvent
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

from .response_event_generators import (
    ResponseEventGenerator,
    ResponseStreamEventGenerator,
    StreamEventState,
)

logger = get_logger()


class LangGraphStreamResponseConverter:
    def __init__(self, stream, context: AgentRunContext):
        self.stream = stream
        self.context = context

        self.stream_state = StreamEventState()
        self.current_generator: ResponseEventGenerator = None

    async def convert(self):
        async for message, _ in self.stream:
            try:
                if self.current_generator is None:
                    self.current_generator = ResponseStreamEventGenerator(logger, None)

                converted = self.try_process_message(message, self.context)
                for event in converted:
                    yield event  # yield each event separately
            except Exception as e:
                logger.error(f"Error converting message {message}: {e}")
                raise ValueError(f"Error converting message {message}") from e

        logger.info("Stream ended, finalizing response.")
        # finalize the stream
        converted = self.try_process_message(None, self.context)
        for event in converted:
            yield event  # yield each event separately

    def try_process_message(self, event: AnyMessage, context: AgentRunContext) -> List[ResponseStreamEvent]:
        if event and not self.current_generator:
            self.current_generator = ResponseStreamEventGenerator(logger, None)

        is_processed = False
        next_processor = self.current_generator
        returned_events = []
        while not is_processed:
            is_processed, next_processor, processed_events = self.current_generator.try_process_message(
                event, context, self.stream_state
            )
            returned_events.extend(processed_events)
            if not is_processed and next_processor == self.current_generator:
                logger.warning(
                    f"Message can not be processed by current generator {type(self.current_generator).__name__}:"
                    + f" {type(event)}: {event}"
                )
                break
            if next_processor != self.current_generator:
                logger.info(
                    f"Switching processor from {type(self.current_generator).__name__} "
                    + f"to {type(next_processor).__name__}"
                )
                self.current_generator = next_processor
        return returned_events
