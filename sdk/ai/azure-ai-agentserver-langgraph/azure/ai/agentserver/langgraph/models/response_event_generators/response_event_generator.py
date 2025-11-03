from typing import List

from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext
from langchain_core.messages import AnyMessage


class StreamEventState:
    sequence_number: int = 0


class ResponseEventGenerator:
    started: bool = False

    def __init__(self, logger, parent):
        self.logger = logger
        self.parent = parent  # parent generator

    def try_process_message(self, message: AnyMessage, context: AgentRunContext, stream_state: StreamEventState):
        """
        Try to process the incoming message.
        Returns a tuple of (is_processed, next_processor, events)
        is_processed: bool - whether the message was processed by this generator,
                    if True, the message has been fully handled and should not be passed to other generators
                    if False, the message was not fully handled and should be passed to the next processor
        next_processor: ResponseEventGenerator - the next processor to handle subsequent messages
        events: List[ResponseStreamEvent] - list of generated events, will be sent to client
        """
        pass

    def on_start(self) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """
        Generate the starting events for this layer.
        Returns a tuple of (started, events)
        """
        pass

    def on_end(self) -> tuple[bool, List[project_models.ResponseStreamEvent]]:
        """
        Generate the ending events for this layer.
        TODO: handle different end conditions, e.g. normal end, error end, etc.
        Returns a tuple of (ended, events)
        """
        pass

    def aggregate_content(self):
        """
        Aggregate the content for this layer.
        It is called by its child processor to pass up aggregated content.
        """
        pass
