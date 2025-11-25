# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# mypy: disable-error-code="assignment"
# from azure.ai.agentserver.core.models import projects as project_models
from typing import Optional, Union, Any, cast
from azure.ai.agentserver.core.models.projects import (
    ItemContent,
    FunctionToolCallItemResource,
    FunctionToolCallOutputItemResource,
    ResponsesMessageItemResource,
)
from azure.ai.agentserver.core.models.projects._enums import ResponsesMessageRole
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
    def __init__(self, item_id: Optional[str] = None, tool_call: Optional[dict] = None):
        super().__init__("function_call", item_id)
        self.call_id = None
        self.name = None
        self.arguments = ""
        if tool_call:
            self.name, self.call_id, _ = extract_function_call(tool_call)

    def create_item_resource(self, is_done: bool) -> FunctionToolCallItemResource:
        content: FunctionToolCallItemResource = {  # type: ignore[typeddict-item]
            "id": self.item_id,  # type: ignore[typeddict-item]
            "type": "function_call",
            "call_id": self.call_id,  # type: ignore[typeddict-item]
            "name": self.name,  # type: ignore[typeddict-item]
            "arguments": self.arguments if self.arguments else "",
            "status": "in_progress" if not is_done else "completed",
        }
        return content

    def add_aggregate_content(self, item):
        if isinstance(item, str):
            self.arguments += item
            return
        if not isinstance(item, dict):
            return
        if item.get("type") != "function_call":
            return
        _, _, argument = extract_function_call(item)
        if argument:
            self.arguments += argument

    def get_aggregated_content(self):
        return self.create_item_resource(is_done=True)


class FunctionCallOutputItemResourceHelper(ItemResourceHelper):
    def __init__(self, item_id: Optional[str] = None, call_id: Optional[str] = None):
        super().__init__("function_call_output", item_id)
        self.call_id = call_id
        self.content = ""

    def create_item_resource(self, is_done: bool) -> FunctionToolCallOutputItemResource:
        content: FunctionToolCallOutputItemResource = {  # type: ignore[typeddict-item]
            "id": self.item_id,  # type: ignore[typeddict-item]
            "type": "function_call_output",
            "status": "in_progress" if not is_done else "completed",
            "call_id": self.call_id,  # type: ignore[typeddict-item]
            "output": self.content,
        }
        return content

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
    def __init__(self, item_id: str, role: ResponsesMessageRole):
        super().__init__("message", item_id)
        self.role = role
        self.content: list[ItemContent] = []

    def create_item_resource(self, is_done: bool) -> ResponsesMessageItemResource:
        # Ensure item_id is not None
        if self.item_id is None:
            raise ValueError("item_id cannot be None for MessageItemResourceHelper")

        content: ResponsesMessageItemResource = {  # type: ignore[typeddict-item]
            "id": self.item_id,
            "type": "message",
            "status": "in_progress" if not is_done else "completed",
            "role": cast(Any, self.role),  # Cast to satisfy TypedDict role typing
        }
        return content

    def add_aggregate_content(self, item: Union[dict, ItemContent]) -> None:
        if isinstance(item, dict):
            typed_item: ItemContent = cast(ItemContent, item)
            self.content.append(typed_item)
        else:
            self.content.append(item)

    def get_aggregated_content(self):
        return self.create_item_resource(is_done=True)
