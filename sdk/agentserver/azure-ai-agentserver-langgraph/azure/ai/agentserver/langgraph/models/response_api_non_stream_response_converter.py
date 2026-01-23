# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation,broad-exception-caught,logging-not-lazy
# mypy: disable-error-code="valid-type,call-overload,attr-defined"
import copy
from abc import ABC, abstractmethod
from typing import Any, Collection, Iterable, List, Union

from langchain_core import messages
from langchain_core.messages import AnyMessage

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import projects as project_models
from .human_in_the_loop_helper import (
    HumanInTheLoopHelper,
    INTERRUPT_NODE_NAME,
)
from .utils import extract_function_call
from .._context import LanggraphRunContext

logger = get_logger()


class ResponseAPINonStreamResponseConverter(ABC):
    """
    Abstract base class for converting Langgraph output to items in Response format.
    One converter instance handles one response.
    """
    @abstractmethod
    def convert(self, output: dict[str, Any]) -> list[project_models.ItemResource]:
        """
        Convert the Langgraph output to a list of ItemResource objects.

        :param output: The Langgraph output to be converted.
        :type output: dict[str, Any]

        :return: A list of ItemResource objects representing the converted output.
        :rtype: list[project_models.ItemResource]
        """
        raise NotImplementedError


class ResponseAPIMessagesNonStreamResponseConverter(ResponseAPINonStreamResponseConverter):  # pylint: disable=C4751
    """
    Convert Langgraph MessageState output to ItemResource objects.
    """
    def __init__(self,
            context: LanggraphRunContext,
            hitl_helper: HumanInTheLoopHelper):
        self.context = context
        self.hitl_helper = hitl_helper

    def convert(self, output: Union[dict[str, Any], Any]) -> list[project_models.ItemResource]:
        res: list[project_models.ItemResource] = []
        if not isinstance(output, list):
            logger.error(f"Expected output to be a list, got {type(output)}: {output}")
            raise ValueError(f"Invalid output format. Expected a list, got {type(output)}.")
        for step in output:
            for node_name, node_output in step.items():
                node_results = self._convert_node_output(node_name, node_output)
                res.extend(node_results)
        return res

    def _convert_node_output(
        self, node_name: str, node_output: Any
    ) -> Iterable[project_models.ItemResource]:
        if node_name == INTERRUPT_NODE_NAME:
            yield from self.hitl_helper.convert_interrupts(node_output)
        else:
            message_arr = node_output.get("messages")
            if not message_arr or not isinstance(message_arr, Collection):
                logger.warning(f"No messages found in node {node_name} output: {node_output}")
                return

            for message in message_arr:
                try:
                    converted = self.convert_output_message(message)
                    if converted:
                        yield converted
                except Exception as e:
                    logger.error(f"Error converting message {message}: {e}")

    def convert_output_message(self, output_message: AnyMessage):  # pylint: disable=inconsistent-return-statements
        # Implement the conversion logic for inner inputs
        if isinstance(output_message, messages.HumanMessage):
            return project_models.ResponsesUserMessageItemResource(
                content=self.convert_MessageContent(
                    output_message.content, role=project_models.ResponsesMessageRole.USER
                ),
                id=self.context.agent_run.id_generator.generate_message_id(),
                status="completed",  # temporary status, can be adjusted based on actual logic
            )
        if isinstance(output_message, messages.SystemMessage):
            return project_models.ResponsesSystemMessageItemResource(
                content=self.convert_MessageContent(
                    output_message.content, role=project_models.ResponsesMessageRole.SYSTEM
                ),
                id=self.context.agent_run.id_generator.generate_message_id(),
                status="completed",
            )
        if isinstance(output_message, messages.AIMessage):
            if output_message.tool_calls:
                # If there are tool calls, we assume there is only ONE function call
                if len(output_message.tool_calls) > 1:
                    logger.warning(
                        f"There are {len(output_message.tool_calls)} tool calls found. "
                        + "Only the first one will be processed."
                    )
                tool_call = output_message.tool_calls[0]
                name, call_id, argument = extract_function_call(tool_call)
                return project_models.FunctionToolCallItemResource(
                    call_id=call_id,
                    name=name,
                    arguments=argument,
                    id=self.context.agent_run.id_generator.generate_function_call_id(),
                    status="completed",
                )
            return project_models.ResponsesAssistantMessageItemResource(
                content=self.convert_MessageContent(
                    output_message.content, role=project_models.ResponsesMessageRole.ASSISTANT
                ),
                id=self.context.agent_run.id_generator.generate_message_id(),
                status="completed",
            )
        if isinstance(output_message, messages.ToolMessage):
            return project_models.FunctionToolCallOutputItemResource(
                call_id=output_message.tool_call_id,
                output=output_message.content,
                id=self.context.agent_run.id_generator.generate_function_output_id(),
            )
        logger.warning(f"Unsupported message type: {type(output_message)}, {output_message}")

    def convert_MessageContent(
        self, content, role: project_models.ResponsesMessageRole
    ) -> List[project_models.ItemContent]:
        if isinstance(content, str):
            return [self.convert_MessageContentItem(content, role)]
        return [self.convert_MessageContentItem(item, role) for item in content]

    def convert_MessageContentItem(
        self, content, role: project_models.ResponsesMessageRole
    ) -> project_models.ItemContent:
        content_dict = copy.deepcopy(content) if isinstance(content, dict) else {"text": content}

        content_type = None
        if isinstance(content, str):
            langgraph_content_type = "text"
        else:
            langgraph_content_type = content.get("type", "text")

        if langgraph_content_type == "text":
            if role == project_models.ResponsesMessageRole.ASSISTANT:
                content_type = project_models.ItemContentType.OUTPUT_TEXT
            else:
                content_type = project_models.ItemContentType.INPUT_TEXT
        elif langgraph_content_type == "image":
            if role == project_models.ResponsesMessageRole.USER:
                content_type = project_models.ItemContentType.INPUT_IMAGE
            else:
                raise ValueError("Image content from assistant is not supported")
        elif langgraph_content_type == "audio":
            if role == project_models.ResponsesMessageRole.USER:
                content_type = project_models.ItemContentType.INPUT_AUDIO
            else:
                content_type = project_models.ItemContentType.OUTPUT_AUDIO
        elif langgraph_content_type == "file":
            if role == project_models.ResponsesMessageRole.USER:
                content_type = project_models.ItemContentType.INPUT_FILE
            else:
                raise ValueError("File content from assistant is not supported")
        else:
            raise ValueError(f"Unsupported content: {content}")

        content_dict["type"] = content_type
        if content_type == project_models.ItemContentType.OUTPUT_TEXT:
            content_dict["annotations"] = []  # annotation is required for output_text

        return project_models.ItemContent(content_dict)
