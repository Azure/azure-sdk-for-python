# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
from typing import Union

from langgraph.types import (
    Command,
    Interrupt,
    StateSnapshot,
)

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.models.openai import (
    ResponseInputParam,
    ResponseInputItemParam,
)

from .human_in_the_loop_helper import (
    HumanInTheLoopHelper,
    INTERRUPT_TOOL_NAME,
)

logger = get_logger()


class HumanInTheLoopJsonHelper(HumanInTheLoopHelper):
    """
    Helper class for managing human-in-the-loop interactions in LangGraph.
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
        
        logger.info(f"Retrived interrupt from state, validating and converting human feedback.")
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
            logger.error(f"Invalid JSON in function call output: {input}")
            return None
        resume = output.get("resume", None)
        update = output.get("update", None)
        goto = output.get("goto", None)
        if resume is None and update is None and goto is None:
            logger.warning(f"No valid Command fields found in function call output: {input}")
            return None
        return Command(
            resume=resume,
            update=update,
            goto=goto,
        )
