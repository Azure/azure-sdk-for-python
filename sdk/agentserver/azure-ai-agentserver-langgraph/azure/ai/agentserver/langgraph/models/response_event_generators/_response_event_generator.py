# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import List

from langchain_core.messages import AnyMessage

from azure.ai.agentserver.core.models import _projects as project_models
from ..._context import LanggraphRunContext


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

    def __init__(self, logger, parent):
        """Initialize the response event generator.

        :param logger: The logger used for diagnostics.
        :type logger: logging.Logger
        :param parent: The parent generator in the event chain.
        :type parent: ResponseEventGenerator | None
        """
        self.logger = logger
        self.parent = parent  # parent generator

    @abstractmethod
    def try_process_message(
        self,
        message: AnyMessage,
        context: LanggraphRunContext,
        stream_state: StreamEventState,
    ) -> tuple[bool, "ResponseEventGenerator | None", List[project_models.ResponseStreamEvent]]:
        """
        Try to process the incoming message.

        :param message: The incoming message to process.
        :type message: AnyMessage
        :param context: The agent run context.
        :type context: LanggraphRunContext
        :param stream_state: The current stream event state.
        :type stream_state: StreamEventState

        :return: tuple of (is_processed, next_processor, events)
        :rtype: tuple[bool, ResponseEventGenerator, List[ResponseStreamEvent]]
        """
        raise NotImplementedError

    def on_start(
        self,
        _message: AnyMessage,
        _context: LanggraphRunContext,
        _stream_state: StreamEventState,
    ) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """
        Generate the starting events for this layer.

        :param _message: The incoming message to process.
        :type _message: AnyMessage
        :param _context: The agent run context.
        :type _context: LanggraphRunContext
        :param _stream_state: The current stream event state.
        :type _stream_state: StreamEventState

        :return: tuple of (started, events)
        :rtype: tuple[bool, List[ResponseStreamEvent]]
        """
        return False, []

    def on_end(
        self, _message: AnyMessage, _context: LanggraphRunContext, _stream_state: StreamEventState
    ) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """
        Generate the ending events for this layer.
        TODO: handle different end conditions, e.g. normal end, error end, etc.

        :param _message: The incoming message to process.
        :type _message: AnyMessage
        :param _context: The agent run context.
        :type _context: LanggraphRunContext
        :param _stream_state: The current stream event state.
        :type _stream_state: StreamEventState

        :return: tuple of (started, events)
        :rtype: tuple[bool, List[ResponseStreamEvent]]
        """
        return False, []

    def aggregate_content(self):
        """
        Aggregate the content for this layer.
        It is called by its child processor to pass up aggregated content.

        :return: content from child processor
        :rtype: str | dict
        """
        return None
