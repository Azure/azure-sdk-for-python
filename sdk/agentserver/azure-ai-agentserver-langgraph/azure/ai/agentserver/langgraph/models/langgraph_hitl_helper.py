# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
from typing import List, Union

from langgraph.types import (
    Command,
    Interrupt,
    StateSnapshot,
)

from azure.ai.agentserver.core.constants import Constants
from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.models.openai import (
    ResponseInputParam,
    ResponseInputItemParam,
)
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

logger = get_logger()

INTERRUPT_NODE_NAME = "__interrupt__"
INTERRUPT_TOOL_NAME = "__hosted_agent_adapter_interrupt__"


class LanggraphHumanInTheLoopHelper:
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


class LanggraphHumanInTheLoopDefaultHelper(LanggraphHumanInTheLoopHelper):
    """
    Default helper class for managing human-in-the-loop interactions in LangGraph.
    Interrupts are converted to FunctionToolCallItemResource objects.
    Human feedback will be sent back as FunctionCallOutputItemParam.
    All values are serialized as JSON strings.
    """

    def convert_interrupt(self, interrupt_info: Interrupt) -> project_models.ItemResource:
        if not isinstance(interrupt_info, Interrupt):
            logger.warning(f"Interrupt info is not of type Interrupt: {interrupt_info}")
            return None
        if isinstance(interrupt_info.value, str):
            arguments = interrupt_info.value
        else:
            arguments = json.dumps(interrupt_info.value)
        return project_models.FunctionToolCallItemResource(
            call_id=interrupt_info.id,
            name=INTERRUPT_TOOL_NAME,
            arguments=arguments,
            id=self.context.id_generator.generate_function_call_id(),
            status="inprogress",
        )
    
    def validate_and_convert_human_feedback(
            self, state: StateSnapshot, input: Union[str, ResponseInputParam]
            ) -> Union[Command, None]:
        if not self.has_interrupt(state):
            # No interrupt in state
            logger.info("No interrupt found in state.")
            return None
        interrupt_obj = state.interrupts[0]  # Assume single interrupt for simplicity
        if not interrupt_obj or not isinstance(interrupt_obj, Interrupt):
            logger.warning(f"No interrupt object found in state")
            return None
        
        logger.info(f"Retrived interrupt from state, validating and convert human feedback.")
        if isinstance(input, str):
            # expect a list of function call output items
            logger.warning(f"Expecting function call output item, got string: {input}")
            return None
        if isinstance(input, list):
            if len(input) != 1:
                # expect exactly one function call output item
                logger.warning(f"Expected exactly one interrupt input item, got {len(input)} items.")
                return None
            item = input[0]
            # validate item type
            item_type = item.get("type", None)
            if item_type != project_models.ItemType.FUNCTION_CALL_OUTPUT:
                logger.warning(f"Invalid interrupt input item type: {item_type}, expected FUNCTION_CALL_OUTPUT.")
                return None
            
            # validate call_id matches
            if item.get("call_id") != interrupt_obj.id:
                logger.warning(f"Interrupt input call_id {item.call_id} does not match interrupt id {interrupt_obj.id}.")
                return None
            
            return self.convert_input_item_to_command(item)
        else:
            logger.error(f"Unsupported interrupt input type: {type(input)}, {input}")
            return None

    def convert_input_item_to_command(self, input: ResponseInputItemParam) -> Union[Command, None]:
        output_str = input.get("output")
        try:
            output = json.loads(output_str)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in function call output: {output_str}")
            return None
        resume = output.get("resume")
        update = output.get("update")
        goto = output.get("goto")
        if not resume and not update and not goto:
            logger.warning(f"No valid command fields found in function call output: {output}")
            return None
        return Command(
            resume=resume,
            update=update,
            goto=goto,
        )