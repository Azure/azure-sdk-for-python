# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from abc import ABC, abstractmethod
import json
from typing import Any, Dict, List, Optional, cast

from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.messages.tool import ToolCall

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import (
    CreateResponse, _openai as openai_models, _projects as project_models
)

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


def convert_item_resource_to_message(item: Dict) -> Optional[AnyMessage]:
    """
    Convert an ItemResource (from AIProjectClient conversation items) to a LangGraph message.

    :param item: The ItemResource dict from AIProjectClient.conversations.items.list().
    :type item: Dict

    :return: The converted LangGraph message.
    :rtype: AnyMessage
    """
    item_type = item.get("type", project_models.ItemType.MESSAGE)

    if item_type == project_models.ItemType.MESSAGE:
        role = item.get("role", project_models.ResponsesMessageRole.USER)
        content = item.get("content", [])

        # Extract text content from the content list
        if isinstance(content, list) and len(content) > 0:
            # Get text from first text content item
            text_content = ""
            for content_item in content:
                content_type = content_item.get("type", "")
                if content_type in ("input_text", "output_text", "text"):
                    text_content = content_item.get("text", "")
                    break
            if not text_content:
                # Fallback: try to get any text field
                text_content = content[0].get("text", "")
            content = text_content
        elif not isinstance(content, str):
            content = str(content) if content else ""

        if role not in role_mapping:
            logger.warning("Unknown role '%s' in item resource, defaulting to USER", role)
            role = project_models.ResponsesMessageRole.USER

        return role_mapping[role](content=content)

    if item_type == project_models.ItemType.FUNCTION_CALL:
        call_id = item.get("call_id", "")
        name = item.get("name", "")
        arguments = item.get("arguments", "{}")
        try:
            args = json.loads(arguments) if arguments else {}
        except json.JSONDecodeError:
            args = {}
        return AIMessage(tool_calls=[ToolCall(id=call_id, name=name, args=args)], content="")

    if item_type == project_models.ItemType.FUNCTION_CALL_OUTPUT:
        call_id = item.get("call_id", "")
        output = item.get("output", "")
        if isinstance(output, list):
            # Extract text from output list
            text_parts = []
            for out_item in output:
                if out_item.get("type") in ("input_text", "output_text", "text"):
                    text_parts.append(out_item.get("text", ""))
            output = " ".join(text_parts)
        return ToolMessage(content=output, tool_call_id=call_id)

    logger.warning("Unsupported item type '%s' in item resource, skipping", item_type)
    return None


class ResponseAPIRequestConverter(ABC):
    """
    Convert CreateResponse to LangGraph request format.
    """
    @abstractmethod
    def convert(self) -> dict:
        """
        Convert the CreateResponse to a LangGraph request format.

        :return: The converted LangGraph request.
        :rtype: dict
        """
        raise NotImplementedError


class ResponseAPIMessageRequestConverter(ResponseAPIRequestConverter):
    """Convert Response API input items into LangGraph message inputs."""

    def __init__(self, data: CreateResponse):
        """Initialize the request converter.

        :param data: The incoming create-response payload.
        :type data: CreateResponse
        """
        self.data: CreateResponse = data

    def convert(self) -> dict:
        """Convert the request payload into LangGraph message input.

        :return: A LangGraph-compatible input dictionary.
        :rtype: dict
        """
        # Convert the CreateRunRequest input to a format suitable for LangGraph
        langgraph_input: dict[str, list[AnyMessage]] = {"messages": []}

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

    def convert_input(self, item: openai_models.ResponseInputItemParam) -> AnyMessage:
        """
        Convert ResponseInputItemParam to a LangGraph message

        :param item: The ResponseInputItemParam to convert from request.
        :type item: openai_models.ResponseInputItemParam

        :return: The converted LangGraph message.
        :rtype: AnyMessage
        """
        item_data = cast(Dict[str, Any], item)
        item_type = item_data.get("type", project_models.ItemType.MESSAGE)
        if item_type == project_models.ItemType.MESSAGE:
            # this is a message
            return self.convert_message(item_data)
        if item_type == project_models.ItemType.FUNCTION_CALL:
            return self.convert_function_call(item_data)
        if item_type == project_models.ItemType.FUNCTION_CALL_OUTPUT:
            return self.convert_function_call_output(item_data)
        raise ValueError(f"Unsupported OpenAIItemParam type: {item_type}, {item}")

    def convert_message(self, message: Dict[str, Any]) -> AnyMessage:
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

    def convert_function_call(self, item: Dict[str, Any]) -> AnyMessage:
        """Convert a function call input item into an AI message.

        :param item: The function call item payload.
        :type item: dict

        :return: The converted AI message.
        :rtype: AnyMessage
        """
        call_id = item.get("call_id")
        name = item.get("name")
        argument = item.get("arguments")

        if not isinstance(call_id, str) or not call_id:
            raise ValueError(f"Function call item missing call_id: {item}")
        if not isinstance(name, str) or not name:
            raise ValueError(f"Function call item missing name: {item}")
        if argument is not None and not isinstance(argument, str):
            raise ValueError(f"Function call arguments must be a string: {item}")

        try:
            args = json.loads(argument) if argument else {}
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON in function call arguments: {item}") from error
        return AIMessage(tool_calls=[ToolCall(id=call_id, name=name, args=args)], content="")

    def convert_function_call_output(self, item: Dict[str, Any]) -> ToolMessage:
        """Convert a function call output item into a tool message.

        :param item: The function call output payload.
        :type item: dict

        :return: The converted tool message.
        :rtype: ToolMessage
        """
        call_id = item.get("call_id")
        if not isinstance(call_id, str) or not call_id:
            raise ValueError(f"Function call output item missing call_id: {item}")

        output = item.get("output", None)
        if isinstance(output, str):
            return ToolMessage(content=output, tool_call_id=call_id)
        if isinstance(output, list):
            return ToolMessage(content=self.convert_OpenAIItemContentList(output), tool_call_id=call_id)
        raise ValueError(f"Unsupported function call output type: {type(output)}, {output}")

    def convert_OpenAIItemContentList(self, content: List[Dict[str, Any]]) -> List[str | Dict[str, Any]]:
        """
        Convert ItemContent to a list format

        :param content: The list of ItemContent to convert.
        :type content: List[Dict]

        :return: The converted list of ItemContent.
        :rtype: List[Dict]
        """
        result: List[str | Dict[str, Any]] = []
        for item in content:
            result.append(self.convert_OpenAIItemContent(item))
        return result

    def convert_OpenAIItemContent(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert ItemContent to a dict format

        :param content: The ItemContent to convert.
        :type content: Dict

        :return: The converted ItemContent.
        :rtype: Dict
        """
        res = content.copy()
        content_type = content.get("type")
        if content_type is None:
            return res
        res["type"] = item_content_type_mapping.get(content_type, content_type)
        return res
