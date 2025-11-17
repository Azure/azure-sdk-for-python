# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation
# mypy: ignore-errors
import json
from typing import TYPE_CHECKING, Dict, List

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.messages.tool import ToolCall

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import CreateResponse, projects as project_models

if TYPE_CHECKING:
    from azure.ai.agentserver.core.models import openai as openai_models

logger = get_logger()

role_mapping = {
    project_models.ResponsesMessageRole.USER: HumanMessage,
    project_models.ResponsesMessageRole.SYSTEM: SystemMessage,
    project_models.ResponsesMessageRole.ASSISTANT: AIMessage,
}

item_content_type_mapping = {
    project_models.ItemContentType.INPUT_TEXT: "text",
    project_models.ItemContentType.INPUT_AUDIO: "audio",
    project_models.ItemContentType.INPUT_IMAGE: "image",
    project_models.ItemContentType.INPUT_FILE: "file",
    project_models.ItemContentType.OUTPUT_TEXT: "text",
    project_models.ItemContentType.OUTPUT_AUDIO: "audio",
    # project_models.ItemContentType.REFUSAL: "refusal",
}


class LangGraphRequestConverter:
    def __init__(self, data: CreateResponse):
        self.data: CreateResponse = data

    def convert(self) -> dict:
        # Convert the CreateRunRequest input to a format suitable for LangGraph
        langgraph_input = {"messages": []}

        instructions = self.data.get("instructions")
        if instructions and isinstance(instructions, str):
            langgraph_input["messages"].append(SystemMessage(content=instructions))

        input = self.data.get("input")
        if isinstance(input, str):
            langgraph_input["messages"].append(HumanMessage(content=input))
        elif isinstance(input, List):
            for inner in input:
                message = self.convert_input(inner)
                langgraph_input["messages"].append(message)
        else:
            raise ValueError(f"Unsupported input type: {type(input)}, {input}")
        return langgraph_input

    def convert_input(self, item: "openai_models.ResponseInputItemParam") -> AnyMessage:
        """
        Convert ResponseInputItemParam to a LangGraph message

        :param item: The ResponseInputItemParam to convert from request.
        :type item: openai_models.ResponseInputItemParam

        :return: The converted LangGraph message.
        :rtype: AnyMessage
        """
        item_type = item.get("type", project_models.ItemType.MESSAGE)
        if item_type == project_models.ItemType.MESSAGE:
            # this is a message
            return self.convert_message(item)
        if item_type == project_models.ItemType.FUNCTION_CALL:
            return self.convert_function_call(item)
        if item_type == project_models.ItemType.FUNCTION_CALL_OUTPUT:
            return self.convert_function_call_output(item)
        raise ValueError(f"Unsupported OpenAIItemParam type: {item_type}, {item}")

    def convert_message(self, message: dict) -> AnyMessage:
        """
        Convert a message dict to a LangGraph message

        :param message: The message dict to convert.
        :type message: dict

        :return: The converted LangGraph message.
        :rtype: AnyMessage
        """
        content = message.get("content")
        role = message.get("role", project_models.ResponsesMessageRole.USER)
        if not content:
            raise ValueError(f"Message missing content: {message}")
        if isinstance(content, str):
            return role_mapping[role](content=content)
        if isinstance(content, list):
            return role_mapping[role](content=self.convert_OpenAIItemContentList(content))
        raise ValueError(f"Unsupported ResponseMessagesItemParam content type: {type(content)}, {content}")

    def convert_function_call(self, item: dict) -> AnyMessage:
        # Function call items should have: call_id, name, and arguments
        call_id = item.get("call_id")
        name = item.get("name")
        argument = item.get("arguments", None)
        
        if not call_id or not name:
            raise ValueError(f"Invalid function call item missing call_id or name: {item}")
        
        try:
            args = json.loads(argument) if argument else {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in function call arguments: {item}") from e
        
        return AIMessage(tool_calls=[ToolCall(id=call_id, name=name, args=args)], content="")

    def convert_function_call_output(self, item: dict) -> ToolMessage:
        # Function call output should have: call_id and output
        call_id = item.get("call_id")
        output = item.get("output", None)
        
        if not call_id:
            raise ValueError(f"Invalid function call output item missing call_id: {item}")

        if isinstance(output, str):
            return ToolMessage(content=output, tool_call_id=call_id)
        if isinstance(output, list):
            return ToolMessage(content=self.convert_OpenAIItemContentList(output), tool_call_id=call_id)
        raise ValueError(f"Unsupported function call output type: {type(output)}, {output}")

    def convert_OpenAIItemContentList(self, content: List[Dict]) -> List[Dict]:
        """
        Convert ItemContent to a list format

        :param content: The list of ItemContent to convert.
        :type content: List[Dict]

        :return: The converted list of ItemContent.
        :rtype: List[Dict]
        """
        result = []
        for item in content:
            result.append(self.convert_OpenAIItemContent(item))
        return result

    def convert_OpenAIItemContent(self, content: Dict) -> Dict:
        """
        Convert ItemContent to a dict format

        :param content: The ItemContent to convert.
        :type content: Dict

        :return: The converted ItemContent.
        :rtype: Dict
        """
        res = content.copy()
        content_type = content.get("type")
        res["type"] = item_content_type_mapping.get(content_type, content_type)
        return res
