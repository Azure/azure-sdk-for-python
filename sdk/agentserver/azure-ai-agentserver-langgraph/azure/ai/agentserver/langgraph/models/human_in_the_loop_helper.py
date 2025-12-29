# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Union

from langgraph.types import (
    Command,
    Interrupt,
    StateSnapshot,
)

from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.models.openai import (
    ResponseInputParam,
    ResponseInputItemParam,
)
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

INTERRUPT_NODE_NAME = "__interrupt__"
INTERRUPT_TOOL_NAME = "__hosted_agent_adapter_interrupt__"


class HumanInTheLoopHelper:
    """Helper class for managing human-in-the-loop interactions in LangGraph."""
    def __init__(self, context: AgentRunContext = None):
        self.context = context

    def has_interrupt(self, state: StateSnapshot) -> bool:
        """Check if the LangGraph state contains an interrupt node."""
        if not state or not isinstance(state, StateSnapshot):
            return False
        return state.interrupts is not None and len(state.interrupts) > 0

    def convert_interrupts(self, interrupts: tuple) -> list[project_models.ItemResource]:
        """Convert LangGraph interrupts to ItemResource objects."""
        if not interrupts or not isinstance(interrupts, tuple):
            return []
        result = []
        # should be only one interrupt for now
        for interrupt_info in interrupts:
            item = self.convert_interrupt(interrupt_info)
            if item:
                result.append(item)
        return result
    
    def convert_interrupt(self, interrupt_info: Interrupt) -> project_models.ItemResource:
        """Convert a single LangGraph Interrupt to an ItemResource object.

        :param interrupt_info: The interrupt information from LangGraph.
        :type interrupt_info: Interrupt

        :return: The corresponding ItemResource object.
        :rtype: project_models.ItemResource
        """
        raise NotImplementedError("Subclasses must implement convert_interrupt method.")

    def validate_and_convert_human_feedback(
            self, state: StateSnapshot, input: Union[str, ResponseInputParam]
            ) -> Union[Command, None]:
        """Validate if the human feedback input corresponds to the interrupt in state.
        If valid, convert the input to a LangGraph Command.

        :param state: The current LangGraph state snapshot.
        :type state: StateSnapshot
        :param input: The human feedback input from the request.
        :type input: Union[str, ResponseInputParam]

        :return: Command if valid feedback is provided, else None.
        :rtype: Union[Command, None]
        """
        raise NotImplementedError("Subclasses must implement validate_and_convert_human_feedback method.")

    def convert_input_item_to_command(self, input: ResponseInputItemParam) -> Union[Command, None]:
        """Convert ItemParams to a LangGraph Command for interrupt handling.

        :param input: The item parameters containing interrupt information.
        :type input: ResponseInputItemParam
        :return: The LangGraph Command.
        :rtype: Union[Command, None]
        """
        raise NotImplementedError("Subclasses must implement convert_request_to_command method.")
