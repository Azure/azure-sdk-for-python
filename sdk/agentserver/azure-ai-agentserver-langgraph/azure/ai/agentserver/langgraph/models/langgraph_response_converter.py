# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=logging-fstring-interpolation,broad-exception-caught,logging-not-lazy
# mypy: disable-error-code="valid-type,call-overload,attr-defined"
import copy
from typing import List, cast

from langchain_core import messages
from langchain_core.messages import AnyMessage

from azure.ai.agentserver.core.logger import get_logger
from azure.ai.agentserver.core.models import projects as project_models
from azure.ai.agentserver.core.models.projects._enums import ResponsesMessageRole, ItemContentType
from azure.ai.agentserver.core.server.common.agent_run_context import AgentRunContext

from .utils import extract_function_call

logger = get_logger()


class LangGraphResponseConverter:
    def __init__(self, context: AgentRunContext, output):
        self.context = context
        self.output = output

    def convert(self) -> list[project_models.ItemResource]:
        res = []
        for step in self.output:
            for node_name, node_output in step.items():
                message_arr = node_output.get("messages")
                if not message_arr:
                    logger.warning(f"No messages found in node {node_name} output: {node_output}")
                    continue
                for message in message_arr:
                    try:
                        converted = self.convert_output_message(message)
                        res.append(converted)
                    except Exception as e:
                        logger.error(f"Error converting message {message}: {e}")
        return res

    def convert_output_message(self, output_message: AnyMessage):  # pylint: disable=inconsistent-return-statements
        # Implement the conversion logic for inner inputs
        if isinstance(output_message, messages.HumanMessage):
            return project_models.ResponsesUserMessageItemResource(
                content=self.convert_MessageContent(
                    output_message.content, role=ResponsesMessageRole.USER
                ),
                id=self.context.id_generator.generate_message_id(),
                status="completed",  # temporary status, can be adjusted based on actual logic
            )
        if isinstance(output_message, messages.SystemMessage):
            return project_models.ResponsesSystemMessageItemResource(
                content=self.convert_MessageContent(
                    output_message.content, role=ResponsesMessageRole.SYSTEM
                ),
                id=self.context.id_generator.generate_message_id(),
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
                # Convert ToolCall to dict for extract_function_call
                tool_call_dict = {
                    "name": tool_call.get("name"),
                    "id": tool_call.get("id"),
                    "args": tool_call.get("args"),
                }
                name, call_id, argument = extract_function_call(tool_call_dict)
                return project_models.FunctionToolCallItemResource(
                    type="function_call",
                    call_id=call_id,
                    name=name,
                    arguments=argument,
                    id=self.context.id_generator.generate_function_call_id(),
                    status="completed",
                )
            return project_models.ResponsesAssistantMessageItemResource(
                type="message",
                role="assistant",
                content=self.convert_MessageContent(
                    output_message.content, role=ResponsesMessageRole.ASSISTANT
                ),
                id=self.context.id_generator.generate_message_id(),
                status="completed",
            )
        if isinstance(output_message, messages.ToolMessage):
            # Ensure output is a string for FunctionToolCallOutputItemResource
            output_content = output_message.content
            if isinstance(output_content, list):
                # Convert list to string representation
                output_str = str(output_content)
            else:
                output_str = str(output_content) if output_content else ""

            return project_models.FunctionToolCallOutputItemResource(
                type="function_call_output",
                status="completed",
                call_id=output_message.tool_call_id,
                output=output_str,
                id=self.context.id_generator.generate_function_output_id(),
            )

    def convert_MessageContent(
        self, content, role: ResponsesMessageRole
    ) -> List[project_models.ItemContent]:
        if isinstance(content, str):
            return [self.convert_MessageContentItem(content, role)]
        return [self.convert_MessageContentItem(item, role) for item in content]

    def convert_MessageContentItem(
        self, content, role: ResponsesMessageRole
    ) -> project_models.ItemContent:
        content_dict = copy.deepcopy(content) if isinstance(content, dict) else {"text": content}

        content_type = None
        if isinstance(content, str):
            langgraph_content_type = "text"
        else:
            langgraph_content_type = content.get("type", "text")

        if langgraph_content_type == "text":
            if role == ResponsesMessageRole.ASSISTANT:
                content_type = ItemContentType.OUTPUT_TEXT
            else:
                content_type = ItemContentType.INPUT_TEXT
        elif langgraph_content_type == "image":
            if role == ResponsesMessageRole.USER:
                content_type = ItemContentType.INPUT_IMAGE
            else:
                raise ValueError("Image content from assistant is not supported")
        elif langgraph_content_type == "audio":
            if role == ResponsesMessageRole.USER:
                content_type = ItemContentType.INPUT_AUDIO
            else:
                content_type = ItemContentType.OUTPUT_AUDIO
        elif langgraph_content_type == "file":
            if role == ResponsesMessageRole.USER:
                content_type = ItemContentType.INPUT_FILE
            else:
                raise ValueError("File content from assistant is not supported")
        else:
            raise ValueError(f"Unsupported content: {content}")

        content_dict["type"] = content_type
        if content_type == ItemContentType.OUTPUT_TEXT:
            content_dict["annotations"] = []  # annotation is required for output_text

        return cast(project_models.ItemContent, content_dict)
