# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=unused-argument,unnecessary-pass
from typing import List

from langchain_core.messages import AnyMessage

from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext


class StreamEventState:
    """
    :meta private:
    State information for the stream event processing.
    """

    sequence_number: int = 0


class ResponseEventGenerator:
    """
    :meta private:
    Abstract base class for response event generators.
    """

    started: bool = False

    def __init__(self, logger, parent):
        self.logger = logger
        self.parent = parent  # parent generator

    def try_process_message(self, message: AnyMessage, context: AgentRunContext, stream_state: StreamEventState):
        """
        Try to process the incoming message.

        :param message: The incoming message to process.
        :type message: AnyMessage
        :param context: The agent run context.
        :type context: AgentRunContext
        :param stream_state: The current stream event state.
        :type stream_state: StreamEventState

        :return: tuple of (is_processed, next_processor, events)
        :rtype: tuple[bool, ResponseEventGenerator, List[ResponseStreamEvent]]
        """
        pass

    def on_start(self) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """
        Generate the starting events for this layer.

        :return: tuple of (started, events)
        :rtype: tuple[bool, List[ResponseStreamEvent]]
        """
        pass

    def on_end(self) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """
        Generate the ending events for this layer.
        TODO: handle different end conditions, e.g. normal end, error end, etc.

        :return: tuple of (started, events)
        :rtype: tuple[bool, List[ResponseStreamEvent]]
        """
        pass

    def aggregate_content(self):
        """
        Aggregate the content for this layer.
        It is called by its child processor to pass up aggregated content.

        :return: content from child processor
        :rtype: str | dict
        """
        pass
