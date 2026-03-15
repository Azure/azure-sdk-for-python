# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple, Union

from langchain_core.messages import AnyMessage
from langgraph.types import Interrupt

from azure.ai.agentserver.core.models import _projects as project_models
from ..._context import LanggraphRunContext

ResponseGeneratorMessage = Optional[Union[AnyMessage, Interrupt]]
ResponseGeneratorEvents = List[project_models.ResponseStreamEvent]
ResponseGeneratorResult = Tuple[bool, Optional["ResponseEventGenerator"], ResponseGeneratorEvents]


class StreamEventState:
    """
    :meta private:
    State information for the stream event processing.
    """

    sequence_number: int = 0


class ResponseEventGenerator(ABC):
    """
    :meta private:
    Abstract base class for response event generators.
    """

    started: bool = False

    def __init__(self, logger, parent: Optional["ResponseEventGenerator"]):
        """Initialize the response event generator.

        :param logger: The logger used for diagnostics.
        :type logger: logging.Logger
        :param parent: The parent generator in the event chain.
        :type parent: Optional[ResponseEventGenerator]
        """
        self.logger = logger
        self.parent = parent  # parent generator

    @abstractmethod
    def try_process_message(
        self,
        message: ResponseGeneratorMessage,
        context: LanggraphRunContext,
        stream_state: StreamEventState,
    ) -> ResponseGeneratorResult:
        """
        Try to process the incoming message.

        :param message: The incoming message to process.
        :type message: Optional[Union[AnyMessage, Interrupt]]
        :param context: The agent run context.
        :type context: LanggraphRunContext
        :param stream_state: The current stream event state.
        :type stream_state: StreamEventState

        :return: tuple of (is_processed, next_processor, events)
        :rtype: Tuple[bool, Optional[ResponseEventGenerator], List[ResponseStreamEvent]]
        """
        raise NotImplementedError

    def on_start(
        self,
        _message: ResponseGeneratorMessage,
        _context: LanggraphRunContext,
        _stream_state: StreamEventState,
    ) -> Tuple[bool, ResponseGeneratorEvents]:
        """
        Generate the starting events for this layer.

        :param _message: The incoming message to process.
        :type _message: Optional[Union[AnyMessage, Interrupt]]
        :param _context: The agent run context.
        :type _context: LanggraphRunContext
        :param _stream_state: The current stream event state.
        :type _stream_state: StreamEventState

        :return: tuple of (started, events)
        :rtype: tuple[bool, List[ResponseStreamEvent]]
        """
        return False, []

    def on_end(
        self,
        _message: ResponseGeneratorMessage,
        _context: LanggraphRunContext,
        _stream_state: StreamEventState,
    ) -> Tuple[bool, ResponseGeneratorEvents]:
        """
        Generate the ending events for this layer.
        TODO: handle different end conditions, e.g. normal end, error end, etc.

        :param _message: The incoming message to process.
        :type _message: Optional[Union[AnyMessage, Interrupt]]
        :param _context: The agent run context.
        :type _context: LanggraphRunContext
        :param _stream_state: The current stream event state.
        :type _stream_state: StreamEventState

        :return: tuple of (started, events)
        :rtype: tuple[bool, List[ResponseStreamEvent]]
        """
        return False, []

    def aggregate_content(self, _content: Any) -> None:
        """
        Aggregate the content for this layer.
        It is called by its child processor to pass up aggregated content.

        :param _content: The content contributed by a child generator.
        :type _content: Any
        """
        return None
