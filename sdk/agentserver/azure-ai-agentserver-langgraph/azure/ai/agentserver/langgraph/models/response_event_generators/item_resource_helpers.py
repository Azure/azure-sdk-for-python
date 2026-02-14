# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# mypy: disable-error-code="assignment"
from typing import Optional

from langgraph.types import Interrupt

from azure.ai.agentserver.core.models import projects as project_models

from ..human_in_the_loop_helper import HumanInTheLoopHelper
from ..utils import extract_function_call


class ItemResourceHelper:
    def __init__(self, item_type: str, item_id: Optional[str] = None):
        self.item_type = item_type
        self.item_id = item_id

    def create_item_resource(self, is_done: bool):
        pass

    def add_aggregate_content(self, item):
        pass

    def get_aggregated_content(self):
        pass


class FunctionCallItemResourceHelper(ItemResourceHelper):
    def __init__(self, item_id: str = None, tool_call: dict = None):
        super().__init__(project_models.ItemType.FUNCTION_CALL, item_id)
        self.call_id = None
        self.name = None
        self.arguments = ""
        if tool_call:
            self.name, self.call_id, _ = extract_function_call(tool_call)

    def create_item_resource(self, is_done: bool):
        content = {
            "id": self.item_id,
            "type": self.item_type,
            "call_id": self.call_id,
            "name": self.name,
            "arguments": self.arguments if self.arguments else "",
            "status": "in_progress" if not is_done else "completed",
        }
        return project_models.ItemResource(content)

    def add_aggregate_content(self, item):
        if isinstance(item, str):
            self.arguments += item
            return
        if not isinstance(item, dict):
            return
        if item.get("type") != project_models.ItemType.FUNCTION_CALL:
            return
        _, _, argument = extract_function_call(item)
        if argument:
            self.arguments += argument

    def get_aggregated_content(self):
        return self.create_item_resource(is_done=True)


class FunctionCallInterruptItemResourceHelper(ItemResourceHelper):
    def __init__(self,
            item_id: Optional[str] = None,
            hitl_helper: Optional[HumanInTheLoopHelper] = None,
            interrupt: Optional[Interrupt] = None):
        super().__init__(project_models.ItemType.FUNCTION_CALL, item_id)
        self.hitl_helper = hitl_helper
        self.interrupt = interrupt

    def create_item_resource(self, is_done: bool):
        if self.hitl_helper is None or self.interrupt is None:
            return None
        item_resource = self.hitl_helper.convert_interrupt(self.interrupt)
        if item_resource is not None and not is_done:
            if hasattr(item_resource, 'arguments'):
                item_resource.arguments = ""  # type: ignore[union-attr]
        return item_resource

    def add_aggregate_content(self, item):
        pass

    def get_aggregated_content(self):
        return self.create_item_resource(is_done=True)


class FunctionCallOutputItemResourceHelper(ItemResourceHelper):
    def __init__(self, item_id: str = None, call_id: str = None):
        super().__init__(project_models.ItemType.FUNCTION_CALL_OUTPUT, item_id)
        self.call_id = call_id
        self.content = ""

    def create_item_resource(self, is_done: bool):
        content = {
            "id": self.item_id,
            "type": self.item_type,
            "status": "in_progress" if not is_done else "completed",
            "call_id": self.call_id,
            "output": self.content,
        }
        return project_models.ItemResource(content)

    def add_aggregate_content(self, item):
        if isinstance(item, str):
            self.content += item
            return
        if not isinstance(item, dict):
            return
        content = item.get("text")
        if isinstance(content, str):
            self.content += content

    def get_aggregated_content(self):
        return self.create_item_resource(is_done=True)


class MessageItemResourceHelper(ItemResourceHelper):
    def __init__(self, item_id: str, role: project_models.ResponsesMessageRole):
        super().__init__(project_models.ItemType.MESSAGE, item_id)
        self.role = role
        self.content: list[project_models.ItemContent] = []

    def create_item_resource(self, is_done: bool):
        content = {
            "id": self.item_id,
            "type": self.item_type,
            "status": "in_progress" if not is_done else "completed",
            "content": self.content,
            "role": self.role,
        }
        return project_models.ItemResource(content)

    def add_aggregate_content(self, item):
        if isinstance(item, dict):
            item = project_models.ItemContent(item)
        if isinstance(item, project_models.ItemContent):
            self.content.append(item)

    def get_aggregated_content(self):
        return self.create_item_resource(is_done=True)
