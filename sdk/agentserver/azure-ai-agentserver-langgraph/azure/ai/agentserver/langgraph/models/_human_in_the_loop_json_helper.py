# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
from typing import Optional

from langgraph.types import (
    Command,
    Interrupt,
)

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import _projects as project_models
from azure.ai.agentserver.core.models._openai import (
    ResponseInputItemParam,
)
from azure.ai.agentserver.core.server.common._constants import HUMAN_IN_THE_LOOP_FUNCTION_NAME

from ._human_in_the_loop_helper import HumanInTheLoopHelper

logger = get_logger()


class HumanInTheLoopJsonHelper(HumanInTheLoopHelper):
    """
    Helper class for managing human-in-the-loop interactions in LangGraph.
    Interrupts are converted to FunctionToolCallItemResource objects.
    Human feedback will be sent back as FunctionCallOutputItemParam.
    All values are serialized as JSON strings.
    """

    def convert_interrupt(self, interrupt_info: Interrupt) -> Optional[project_models.ItemResource]:
        """Convert an interrupt into an in-progress function-call item resource.

        :param interrupt_info: The interrupt emitted by LangGraph.
        :type interrupt_info: Interrupt

        :return: The corresponding function-call item resource, if conversion succeeds.
        :rtype: Optional[project_models.ItemResource]
        """
        if not isinstance(interrupt_info, Interrupt):
            logger.warning("Interrupt is not of type Interrupt: %s", interrupt_info)
            return None
        name, call_id, arguments = self.interrupt_to_function_call(interrupt_info)
        if name is None or call_id is None or arguments is None:
            logger.warning("Interrupt could not be converted to a function call: %s", interrupt_info)
            return None
        return project_models.FunctionToolCallItemResource(
            call_id=call_id,
            name=name,
            arguments=arguments,
            id=self.context.agent_run.id_generator.generate_function_call_id(),
            status="in_progress",
        )

    def interrupt_to_function_call(self, interrupt: Interrupt) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Convert an Interrupt to a function call tuple.

        :param interrupt: The Interrupt object to convert.
        :type interrupt: Interrupt

        :return: A tuple of (name, call_id, argument).
        :rtype: tuple[Optional[str], Optional[str], Optional[str]]
        """
        if isinstance(interrupt.value, str):
            arguments = interrupt.value
        else:
            try:
                arguments = json.dumps(interrupt.value)
            except (TypeError, ValueError) as error:  # pragma: no cover - fallback
                logger.error("Failed to serialize interrupt value to JSON: %s, error: %s", interrupt.value, error)
                arguments = str(interrupt.value)
        return HUMAN_IN_THE_LOOP_FUNCTION_NAME, interrupt.id, arguments

    def convert_input_item_to_command(self, input_item: ResponseInputItemParam) -> Optional[Command]:
        """Convert a function-call-output item into a LangGraph resume command.

        :param input_item: The function call output item supplied by the client.
        :type input_item: ResponseInputItemParam

        :return: The parsed LangGraph command, if valid.
        :rtype: Optional[Command]
        """
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
