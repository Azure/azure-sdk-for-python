# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional

from langgraph.types import Interrupt

from azure.ai.agentserver.core.models import _projects as project_models

from .._human_in_the_loop_helper import HumanInTheLoopHelper
from .._utils import extract_function_call


class ItemResourceHelper(ABC):
    """Base helper for constructing response item resources during streaming."""

    def __init__(self, item_type: str, item_id: Optional[str] = None):
        """Initialize the item-resource helper.

        :param item_type: The response item type handled by this helper.
        :type item_type: str
        :param item_id: The optional response item identifier.
        :type item_id: Optional[str]
        """
        self.item_type = item_type
        self.item_id = item_id

    @abstractmethod
    def create_item_resource(self, is_done: bool) -> Optional[project_models.ItemResource]:
        """Create the current item resource representation.

        :param is_done: Whether the created item should be marked completed.
        :type is_done: bool
        :return: The current item resource or None if not applicable.
        :rtype: Optional[project_models.ItemResource]
        """
        raise NotImplementedError

    @abstractmethod
    def add_aggregate_content(self, item: Any) -> None:
        """Accumulate child content into the helper state.

        :param item: The child content to aggregate.
        :type item: Any
        :return: None
        :rtype: None
        """
        raise NotImplementedError

    @abstractmethod
    def get_aggregated_content(self) -> Optional[project_models.ItemResource]:
        """Return the aggregated item resource representation.

        :return: The aggregated item resource or None if not applicable.
        :rtype: Optional[project_models.ItemResource]
        """
        raise NotImplementedError


class FunctionCallItemResourceHelper(ItemResourceHelper):
    """Helper for streaming function-call item resources."""

    def __init__(self, item_id: Optional[str] = None, tool_call: Optional[Mapping[str, Any]] = None):
        """Initialize the function-call item helper.

        :param item_id: The response item identifier.
        :type item_id: str
        :param tool_call: The initial tool-call payload, if available.
        :type tool_call: dict
        """
        super().__init__(project_models.ItemType.FUNCTION_CALL, item_id)
        self.call_id: Optional[str] = None
        self.name: Optional[str] = None
        self.arguments = ""
        if tool_call:
            self.name, self.call_id, _ = extract_function_call(tool_call)

    def create_item_resource(self, is_done: bool):
        """Create the current function-call item resource.

        :param is_done: Whether the item is complete.
        :type is_done: bool

        :return: The current item resource.
        :rtype: project_models.ItemResource
        """
        content = {
            "id": self.item_id,
            "type": self.item_type,
            "call_id": self.call_id,
            "name": self.name,
            "arguments": self.arguments if self.arguments else "",
            "status": "in_progress" if not is_done else "completed",
        }
        return project_models.ItemResource(content)

    def add_aggregate_content(self, item: Any) -> None:
        """Accumulate additional function-call arguments.

        :param item: The content fragment to aggregate.
        :type item: Any
        """
        if isinstance(item, str):
            self.arguments += item
            return
        if not isinstance(item, Mapping):
            return
        if item.get("type") != project_models.ItemType.FUNCTION_CALL:
            return
        _, _, argument = extract_function_call(item)
        if argument:
            self.arguments += argument

    def get_aggregated_content(self):
        """Return the completed function-call item resource.

        :return: The completed item resource.
        :rtype: project_models.ItemResource
        """
        return self.create_item_resource(is_done=True)


class FunctionCallInterruptItemResourceHelper(ItemResourceHelper):
    """Helper for converting interrupt payloads into function-call resources."""

    def __init__(self,
            item_id: Optional[str] = None,
            hitl_helper: Optional[HumanInTheLoopHelper] = None,
            interrupt: Optional[Interrupt] = None):
        """Initialize the interrupt item helper.

        :param item_id: The response item identifier.
        :type item_id: Optional[str]
        :param hitl_helper: The helper used to convert interrupts.
        :type hitl_helper: Optional[HumanInTheLoopHelper]
        :param interrupt: The interrupt being represented.
        :type interrupt: Optional[Interrupt]
        """
        super().__init__(project_models.ItemType.FUNCTION_CALL, item_id)
        self.hitl_helper = hitl_helper
        self.interrupt = interrupt

    def create_item_resource(self, is_done: bool):
        """Create the interrupt-backed item resource.

        :param is_done: Whether the item is complete.
        :type is_done: bool

        :return: The current interrupt item resource, if available.
        :rtype: Optional[project_models.ItemResource]
        """
        if self.hitl_helper is None or self.interrupt is None:
            return None
        item_resource = self.hitl_helper.convert_interrupt(self.interrupt)
        if item_resource is not None and not is_done:
            item_resource_data = item_resource.as_dict()
            if "arguments" in item_resource_data:
                item_resource_data["arguments"] = ""
            return project_models.ItemResource(item_resource_data)
        return item_resource

    def add_aggregate_content(self, item: Any) -> None:
        """Ignore aggregated content for interrupt-backed items.

        :param item: The content fragment to aggregate.
        :type item: Any
        """
        return None

    def get_aggregated_content(self):
        """Return the completed interrupt-backed item resource.

        :return: The completed item resource, if available.
        :rtype: Optional[project_models.ItemResource]
        """
        return self.create_item_resource(is_done=True)


class FunctionCallOutputItemResourceHelper(ItemResourceHelper):
    """Helper for streaming function-call-output item resources."""

    def __init__(self, item_id: Optional[str] = None, call_id: Optional[str] = None):
        """Initialize the function-call-output helper.

        :param item_id: The response item identifier.
        :type item_id: str
        :param call_id: The function call identifier.
        :type call_id: str
        """
        super().__init__(project_models.ItemType.FUNCTION_CALL_OUTPUT, item_id)
        self.call_id = call_id
        self.content = ""

    def create_item_resource(self, is_done: bool):
        """Create the current function-call-output item resource.

        :param is_done: Whether the item is complete.
        :type is_done: bool

        :return: The current item resource.
        :rtype: project_models.ItemResource
        """
        content = {
            "id": self.item_id,
            "type": self.item_type,
            "status": "in_progress" if not is_done else "completed",
            "call_id": self.call_id,
            "output": self.content,
        }
        return project_models.ItemResource(content)

    def add_aggregate_content(self, item: Any) -> None:
        """Accumulate additional function-call-output content.

        :param item: The content fragment to aggregate.
        :type item: Any
        """
        if isinstance(item, str):
            self.content += item
            return
        if not isinstance(item, Mapping):
            return
        content = item.get("text")
        if isinstance(content, str):
            self.content += content

    def get_aggregated_content(self):
        """Return the completed function-call-output item resource.

        :return: The completed item resource.
        :rtype: project_models.ItemResource
        """
        return self.create_item_resource(is_done=True)


class MessageItemResourceHelper(ItemResourceHelper):
    """Helper for streaming message item resources."""

    def __init__(self, item_id: str, role: project_models.ResponsesMessageRole):
        """Initialize the message item helper.

        :param item_id: The response item identifier.
        :type item_id: str
        :param role: The response message role.
        :type role: project_models.ResponsesMessageRole
        """
        super().__init__(project_models.ItemType.MESSAGE, item_id)
        self.role = role
        self.content: list[project_models.ItemContent] = []

    def create_item_resource(self, is_done: bool):
        """Create the current message item resource.

        :param is_done: Whether the item is complete.
        :type is_done: bool

        :return: The current item resource.
        :rtype: project_models.ItemResource
        """
        content = {
            "id": self.item_id,
            "type": self.item_type,
            "status": "in_progress" if not is_done else "completed",
            "content": self.content,
            "role": self.role,
        }
        return project_models.ItemResource(content)

    def add_aggregate_content(self, item: Any) -> None:
        """Accumulate additional message content.

        :param item: The content fragment to aggregate.
        :type item: Any
        """
        if isinstance(item, dict):
            item = project_models.ItemContent(item)
        if isinstance(item, project_models.ItemContent):
            self.content.append(item)

    def get_aggregated_content(self):
        """Return the completed message item resource.

        :return: The completed item resource.
        :rtype: project_models.ItemResource
        """
        return self.create_item_resource(is_done=True)
