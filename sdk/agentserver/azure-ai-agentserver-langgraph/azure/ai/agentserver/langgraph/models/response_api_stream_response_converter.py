# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation,C4751
# mypy: disable-error-code="assignment,valid-type"
from abc import ABC, abstractmethod
from typing import Any, List, Union

from langchain_core.messages import AnyMessage

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import ResponseStreamEvent
from .human_in_the_loop_helper import HumanInTheLoopHelper
from .response_event_generators import (
    ResponseEventGenerator,
    ResponseStreamEventGenerator,
    StreamEventState,
)
from .._context import LanggraphRunContext

logger = get_logger()


class ResponseAPIStreamResponseConverter(ABC):
    """
    Abstract base class for converting Langgraph streamed output to ResponseStreamEvent objects.
    One converter instance handles one response stream.
    """
    @abstractmethod
    def convert(self, event: Union[AnyMessage, dict, Any, None]):
        """
        Convert the Langgraph streamed output to ResponseStreamEvent objects.

        :param event: The event to convert.
        :type event: Union[AnyMessage, dict, Any, None]
        :return: An asynchronous generator yielding ResponseStreamEvent objects.
        :rtype: AsyncGenerator[ResponseStreamEvent, None]
        """
        raise NotImplementedError

    @abstractmethod
    def finalize(self, graph_state=None):
        """
        Finalize the conversion process after the stream ends.

        :param graph_state: The final graph state.
        :type graph_state: Any
        :return: An asynchronous generator yielding final ResponseStreamEvent objects.
        :rtype: AsyncGenerator[ResponseStreamEvent, None]
        """


class ResponseAPIMessagesStreamResponseConverter(ResponseAPIStreamResponseConverter):
    def __init__(self, context: LanggraphRunContext, *, hitl_helper: HumanInTheLoopHelper):
        # self.stream = stream
        self.context = context
        self.hitl_helper = hitl_helper

        self.stream_state = StreamEventState()
        self.current_generator: ResponseEventGenerator = None

    def convert(self, event: Union[AnyMessage, dict, Any, None]):
        try:
            if self.current_generator is None:
                self.current_generator = ResponseStreamEventGenerator(logger, None, hitl_helper=self.hitl_helper)
            if event is None or not hasattr(event, '__getitem__'):
                raise ValueError(f"Event is not indexable: {event}")
            message = event[0]  # expect a tuple
            converted = self.try_process_message(message, self.context)
            return converted
        except Exception as e:
            logger.error(f"Error converting message {event}: {e}")
            raise ValueError(f"Error converting message {event}") from e

    def finalize(self, graph_state=None):
        logger.info("Stream ended, finalizing response.")
        res = []
        # check and convert interrupts
        if self.hitl_helper.has_interrupt(graph_state):
            interrupt = graph_state.interrupts[0]  # should have only one interrupt
            converted = self.try_process_message(interrupt, self.context)
            res.extend(converted)
        # finalize the stream
        converted = self.try_process_message(None, self.context)
        res.extend(converted)
        return res

    def try_process_message(
        self, event: Union[AnyMessage, Any, None], context: LanggraphRunContext
    ) -> List[ResponseStreamEvent]:
        if event and not self.current_generator:
            self.current_generator = ResponseStreamEventGenerator(logger, None, hitl_helper=self.hitl_helper)

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
