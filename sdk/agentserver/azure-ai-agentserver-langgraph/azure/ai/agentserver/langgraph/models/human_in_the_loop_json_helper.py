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
from azure.ai.agentserver.core.server.common.constants import HUMAN_IN_THE_LOOP_FUNCTION_NAME

from .human_in_the_loop_helper import HumanInTheLoopHelper

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
            logger.warning(f"Interrupt is not of type Interrupt: {interrupt_info}")
            return None
        name, call_id, arguments = self.interrupt_to_function_call(interrupt_info)
        return project_models.FunctionToolCallItemResource(
            call_id=call_id,
            name=name,
            arguments=arguments,
            id=self.context.id_generator.generate_function_call_id(),
            status="inprogress",
        )
    
    def interrupt_to_function_call(self, interrupt: Interrupt) :
        """
        Convert an Interrupt to a function call tuple.

        :param interrupt: The Interrupt object to convert.
        :type interrupt: Interrupt

        :return: A tuple of (name, call_id, argument).
        :rtype: tuple[str | None, str | None, str | None]
        """
        if isinstance(interrupt.value, str):
            arguments = interrupt.value
        else:
            try:
                arguments = json.dumps(interrupt.value)
            except Exception as e:  # pragma: no cover - fallback # pylint: disable=broad-exception-caught
                logger.error(f"Failed to serialize interrupt value to JSON: {interrupt.value}, error: {e}")
                arguments = str(interrupt.value)
        return HUMAN_IN_THE_LOOP_FUNCTION_NAME, interrupt.id, arguments

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
