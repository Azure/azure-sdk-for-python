# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Union

from langgraph.types import (
    Command,
    Interrupt,
    StateSnapshot,
)

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.models.openai import (ResponseInputItemParam, ResponseInputParam)
from .._context import LanggraphRunContext

INTERRUPT_NODE_NAME = "__interrupt__"
logger = get_logger()


class HumanInTheLoopHelper:
    """Helper class for managing human-in-the-loop interactions in LangGraph."""
    def __init__(self, context: LanggraphRunContext):
        self.context = context

    def has_interrupt(self, state: Optional[StateSnapshot]) -> bool:
        """Check if the LangGraph state contains an interrupt node.

        :param state: The LangGraph state snapshot.
        :type state: Optional[StateSnapshot]
        :return: True if the state contains an interrupt, False otherwise.
        :rtype: bool
        """
        if not state or not isinstance(state, StateSnapshot):
            return False
        return state.interrupts is not None and len(state.interrupts) > 0

    def convert_interrupts(self, interrupts: tuple) -> list[project_models.ItemResource]:
        """Convert LangGraph interrupts to ItemResource objects.

        :param interrupts: A tuple of interrupt objects.
        :type interrupts: tuple
        :return: A list of ItemResource objects.
        :rtype: list[project_models.ItemResource]
        """
        if not interrupts or not isinstance(interrupts, tuple):
            return []
        result = []
        # should be only one interrupt for now
        for interrupt_info in interrupts:
            if not isinstance(interrupt_info, Interrupt):
                # skip invalid interrupt
                continue
            item = self.convert_interrupt(interrupt_info)
            if item:
                result.append(item)
        return result

    def convert_interrupt(self, interrupt_info: Interrupt) -> Optional[project_models.ItemResource]:
        """Convert a single LangGraph Interrupt to an ItemResource object.

        :param interrupt_info: The interrupt information from LangGraph.
        :type interrupt_info: Interrupt

        :return: The corresponding ItemResource object.
        :rtype: project_models.ItemResource
        """
        raise NotImplementedError("Subclasses must implement convert_interrupt method.")

    def validate_and_convert_human_feedback(
            self, state: Optional[StateSnapshot], input_data: Union[str, ResponseInputParam]
    ) -> Optional[Command]:
        """Validate if the human feedback input corresponds to the interrupt in state.
        If valid, convert the input to a LangGraph Command.

        :param state: The current LangGraph state snapshot.
        :type state: Optional[StateSnapshot]
        :param input_data: The human feedback input from the request.
        :type input_data: Union[str, ResponseInputParam]

        :return: Command if valid feedback is provided, else None.
        :rtype: Union[Command, None]
        """
        # Validate interrupt exists in state
        if not self.has_interrupt(state):
            logger.info("No interrupt found in state.")
            return None

        interrupt_obj = state.interrupts[0]  # type: ignore[union-attr] # Assume single interrupt for simplicity
        if not interrupt_obj or not isinstance(interrupt_obj, Interrupt):
            logger.warning("No interrupt object found in state")
            return None

        logger.info("Retrieved interrupt from state, validating and converting human feedback.")

        # Validate input format and extract item
        item = self._validate_input_format(input_data, interrupt_obj)
        if item is None:
            return None

        return self.convert_input_item_to_command(item)

    def _validate_input_format(
        self, input_data: Union[str, ResponseInputParam], interrupt_obj: Interrupt
    ) -> Optional[ResponseInputItemParam]:
        if isinstance(input_data, str):
            logger.warning("Expecting function call output item, got string: %s", input_data)
            return None

        if not isinstance(input_data, list):
            logger.error("Unsupported interrupt input type: %s, %s", type(input_data), input_data)
            return None

        if len(input_data) != 1:
            logger.warning("Expected exactly one interrupt input item, got %d items.", len(input_data))
            return None

        item = input_data[0]
        item_type = item.get("type", None)
        if item_type != project_models.ItemType.FUNCTION_CALL_OUTPUT:
            logger.warning(
                "Invalid interrupt input item type: %s, expected FUNCTION_CALL_OUTPUT.", item_type
            )
            return None

        if item.get("call_id") != interrupt_obj.id:
            logger.warning(
                "Interrupt input call_id %s does not match interrupt id %s.",
                item.get("call_id"), interrupt_obj.id
            )
            return None

        return item

    def convert_input_item_to_command(self, input_item: ResponseInputItemParam) -> Union[Command, None]:
        """Convert ItemParams to a LangGraph Command for interrupt handling.

        :param input_item: The item parameters containing interrupt information.
        :type input_item: ResponseInputItemParam
        :return: The LangGraph Command.
        :rtype: Union[Command, None]
        """
        raise NotImplementedError("Subclasses must implement convert_request_to_command method.")
