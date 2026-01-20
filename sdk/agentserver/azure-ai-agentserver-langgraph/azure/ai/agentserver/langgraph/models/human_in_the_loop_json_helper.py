# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
from typing import Optional, Union

from langgraph.types import (
    Command,
    Interrupt,
)

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.models.openai import (
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

    def convert_interrupt(self, interrupt_info: Interrupt) -> Optional[project_models.ItemResource]:
        if not isinstance(interrupt_info, Interrupt):
            logger.warning("Interrupt is not of type Interrupt: %s", interrupt_info)
            return None
        name, call_id, arguments = self.interrupt_to_function_call(interrupt_info)
        return project_models.FunctionToolCallItemResource(
            call_id=call_id,
            name=name,
            arguments=arguments,
            id=self.context.agent_run.id_generator.generate_function_call_id(),
            status="in_progress",
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
                logger.error("Failed to serialize interrupt value to JSON: %s, error: %s", interrupt.value, e)
                arguments = str(interrupt.value)
        return HUMAN_IN_THE_LOOP_FUNCTION_NAME, interrupt.id, arguments

    def convert_input_item_to_command(self, input_item: ResponseInputItemParam) -> Union[Command, None]:
        output_str = input_item.get("output")
        if not isinstance(output_str, str):
            logger.error("Invalid output type in function call output: %s", input_item)
            return None
        try:
            output = json.loads(output_str)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in function call output: %s", input_item)
            return None
        resume = output.get("resume", None)
        update = output.get("update", None)
        goto = output.get("goto", None)
        if resume is None and update is None and goto is None:
            logger.warning("No valid Command fields found in function call output: %s", input_item)
            return None
        return Command(
            resume=resume,
            update=update,
            goto=goto,
        )
