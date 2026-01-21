import datetime
import json

from pydantic import BaseModel

from typing import TYPE_CHECKING, Any, List, Optional, Union

# Models moved in a later version of agents SDK, so try a few different locations
# Only import for type checking to avoid runtime import errors
if TYPE_CHECKING:
    try:
        from azure.ai.projects.models import RunStepFunctionToolCall
    except ImportError:
        try:
            from azure.ai.agents.models import RunStepFunctionToolCall
        except ImportError:
            # Create a protocol for type checking when the real class isn't available
            from typing import Protocol

            class RunStepFunctionToolCall(Protocol):
                """Protocol defining the expected interface for RunStepFunctionToolCall."""

                id: str
                type: str

                def get(self, key: str, default: Any = None) -> Any: ...

else:
    # At runtime, we don't need the actual class since it's only used in type annotations
    RunStepFunctionToolCall = Any

# Message roles constants.
_SYSTEM = "system"
_USER = "user"
_AGENT = "assistant"
_TOOL = "tool"
_DEVELOPER = "developer"  # part of the semantic kernel

# Constant definitions for what tool details include.
_TOOL_CALL = "tool_call"
_TOOL_RESULT = "tool_result"
_FUNCTION = "function"

# This is returned by AI services in the API to filter against tool invocations.
_TOOL_CALLS = "tool_calls"

# Constants to only be used internally in this file for the built-in tools.
_CODE_INTERPRETER = "code_interpreter"
_BING_GROUNDING = "bing_grounding"
_BING_CUSTOM_SEARCH = "bing_custom_search"
_FILE_SEARCH = "file_search"
_AZURE_AI_SEARCH = "azure_ai_search"
_SHAREPOINT_GROUNDING = "sharepoint_grounding"
_FABRIC_DATAAGENT = "fabric_dataagent"
_OPENAPI = "openapi"

# Built-in tool descriptions and parameters are hidden, but we include basic descriptions
# for evaluation purposes.
_BUILT_IN_DESCRIPTIONS = {
    _CODE_INTERPRETER: "Use code interpreter to read and interpret information from datasets, "
    + "generate code, and create graphs and charts using your data. Supports "
    + "up to 20 files.",
    _BING_GROUNDING: "Enhance model output with web data.",
    _BING_CUSTOM_SEARCH: "Enables agents to retrieve content from a curated subset of websites, enhancing relevance and reducing noise from public web searches.",
    _FILE_SEARCH: "Search for data across uploaded files. A single call can return multiple results/files in the 'results' field.",
    _AZURE_AI_SEARCH: "Search an Azure AI Search index for relevant data.",
    _SHAREPOINT_GROUNDING: "Allows agents to access and retrieve relevant content from Microsoft SharePoint document libraries, grounding responses in organizational knowledge.",
    _FABRIC_DATAAGENT: "Connect to Microsoft Fabric data agents to retrieve data across different data sources.",
}

# Built-in tool parameters are hidden, but we include basic parameters for evaluation purposes.
_BUILT_IN_PARAMS = {
    _CODE_INTERPRETER: {
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "Generated code to be executed."}
        },
    },
    _BING_GROUNDING: {
        "type": "object",
        "properties": {
            "requesturl": {
                "type": "string",
                "description": "URL used in Bing Search API.",
            }
        },
    },
    _BING_CUSTOM_SEARCH: {
        "type": "object",
        "properties": {
            "requesturl": {
                "type": "string",
                "description": "Search queries, along with pre-configured site restrictions or domain filters.",
            }
        },
    },
    _FILE_SEARCH: {
        "type": "object",
        "properties": {
            "ranking_options": {
                "type": "object",
                "properties": {
                    "ranker": {
                        "type": "string",
                        "description": "Ranking algorithm to use.",
                    },
                    "score_threshold": {
                        "type": "number",
                        "description": "Threshold for search results.",
                    },
                },
                "description": "Ranking options for search results.",
            }
        },
    },
    _AZURE_AI_SEARCH: {
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "Search terms to use."}
        },
    },
    _SHAREPOINT_GROUNDING: {
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "A natural language query to search SharePoint content.",
            }
        },
    },
    _FABRIC_DATAAGENT: {
        "type": "object",
        "properties": {
            "input": {"type": "string", "description": "Search terms to use."}
        },
    },
}


class Message(BaseModel):
    """Represents a message in a conversation with agents, assistants, and tools. We need to export these structures
    to JSON for evaluators and we have custom fields such as createdAt, run_id, and tool_call_id, so we cannot use
    the standard pydantic models provided by OpenAI.

    :param createdAt: The timestamp when the message was created.
    :type createdAt: datetime.datetime
    :param run_id: The ID of the run associated with the message. Optional.
    :type run_id: Optional[str]
    :param role: The role of the message sender (e.g., system, user, tool, assistant).
    :type role: str
    :param content: The content of the message, which can be a string or a list of dictionaries.
    :type content: Union[str, List[dict]]
    """

    createdAt: Optional[Union[datetime.datetime, int]] = (
        None  # SystemMessage wouldn't have this
    )
    run_id: Optional[str] = None
    tool_call_id: Optional[str] = None  # see ToolMessage
    role: str
    content: Union[str, List[dict]]


class SystemMessage(Message):
    """Represents a system message in a conversation with agents, assistants, and tools.

    :param role: The role of the message sender, which is always 'system'.
    :type role: str
    """

    role: str = _SYSTEM


class UserMessage(Message):
    """Represents a user message in a conversation with agents, assistants, and tools.

    :param role: The role of the message sender, which is always 'user'.
    :type role: str
    """

    role: str = _USER


class SKDeveloperMessage(Message):
    """Represents a developer message in a conversation with agents, assistants, and tools.
    This is used in the context of Semantic Kernel (SK) agents.

    :param role: The role of the message sender, which is always 'developer'.
    :type role: str
    """

    role: str = _DEVELOPER


class ToolMessage(Message):
    """Represents a tool message in a conversation with agents, assistants, and tools.

    :param run_id: The ID of the run associated with the message.
    :type run_id: str
    :param role: The role of the message sender, which is always 'tool'.
    :type role: str
    :param tool_call_id: The ID of the tool call associated with the message. Optional.
    :type tool_call_id: Optional[str]
    """

    run_id: str
    role: str = _TOOL
    tool_call_id: Optional[str] = None


class SKToolMessage(Message):
    """Represents a tool message in the context of a Semantic Kernel (SK) agent.

    :param role: The role of the message sender, which is always 'tool'.
    :type role: str
    :param tool_call_id: The ID of the tool call associated with the message. Optional.
    :type tool_call_id: Optional[str]
    """

    role: str = _TOOL
    tool_call_id: Optional[str] = None


class AssistantMessage(Message):
    """Represents an assistant message.

    :param run_id: The ID of the run associated with the message.
    :type run_id: str
    :param role: The role of the message sender, which is always 'assistant'.
    :type role: str
    """

    run_id: str
    role: str = _AGENT


class SKAssistantMessage(Message):
    """Represents an assistant message in the context of a Semantic Kernel (SK) agent.

    :param role: The role of the message sender, which is always 'assistant'.
    :type role: str
    """

    role: str = _AGENT


class SKAssistantMessage(Message):
    """Represents an assistant message in the context of a Semantic Kernel (SK) agent.

    :param role: The role of the message sender, which is always 'assistant'.
    :type role: str
    """

    role: str = _AGENT


class ToolDefinition(BaseModel):
    """Represents a tool definition that will be used in the agent.

    :param name: The name of the tool.
    :type name: str
    :param type: The type of the tool.
    :type type: str
    :param description: A description of the tool.
    :type description: str
    :param parameters: The parameters required by the tool.
    :type parameters: dict
    """

    name: str
    type: str
    description: Optional[str] = None
    parameters: dict


class OpenAPIToolDefinition(BaseModel):
    """Represents OpenAPI tool definition that will be used in the agent.
    :param name: The name of the tool.
    :type name: str
    :param type: The type of the tool.
    :type type: str
    :param description: A description of the tool.
    :type description: str
    :param parameters: The parameters required by the tool.
    :type parameters: dict
    """

    name: str
    type: str
    description: Optional[str] = None
    spec: object
    auth: object
    default_params: Optional[list[str]] = None
    functions: list[ToolDefinition]


class ToolCall:
    """Represents a tool call, used as an intermediate step in the conversion process.

    :param created: The timestamp when the tool call was created.
    :type created: datetime.datetime
    :param completed: The timestamp when the tool call was completed.
    :type completed: datetime.datetime
    :param details: The details of the tool call.
    :type details: RunStepFunctionToolCall
    """

    def __init__(
        self,
        created: datetime.datetime,
        completed: datetime.datetime,
        details: RunStepFunctionToolCall,
    ):
        self.created = created
        self.completed = completed
        self.details = details


class EvaluatorData(BaseModel):
    """Represents the result of a conversion.

    :param query: A list of messages representing the system message, chat history, and user query.
    :type query: List[Message]
    :param response: A list of messages representing the assistant's response, including tool calls and results.
    :type response: List[Message]
    :param tool_definitions: A list of tool definitions used in the agent.
    :type tool_definitions: List[ToolDefinition]
    """

    query: List[Message]
    response: List[Message]
    tool_definitions: List[Union[ToolDefinition, OpenAPIToolDefinition]]

    def to_json(self):
        """Converts the result to a JSON string.

        :return: The JSON representation of the result.
        :rtype: str
        """
        return self.model_dump_json(exclude={}, exclude_none=True)


def break_tool_call_into_messages(tool_call: ToolCall, run_id: str) -> List[Message]:
    """
    Breaks a tool call into a list of messages, including the tool call and its result.

    :param tool_call: The tool call to be broken into messages.
    :type tool_call: ToolCall
    :param run_id: The ID of the run associated with the messages.
    :type run_id: str
    :return: A list of messages representing the tool call and its result.
    :rtype: List[Message]
    """
    # We will use this as our accumulator.
    messages: List[Message] = []

    # As of March 17th, 2025, we only support custom functions due to built-in code interpreters and bing grounding
    # tooling not reporting their function calls in the same way. Code interpreters don't include the tool call at
    # all in most of the cases, and bing would only show the API URL, without arguments or results.
    # Bing grounding would have "bing_grounding" in details with "requesturl" that will just be the API path with query.
    # TODO: Work with AI Services to add converter support for BingGrounding and CodeInterpreter.
    if hasattr(tool_call.details, _FUNCTION) or tool_call.details.get("function"):
        # This is the internals of the content object that will be included with the tool call.
        tool_call_id = tool_call.details.id
        content_tool_call = {
            "type": _TOOL_CALL,
            "tool_call_id": tool_call_id,
            "name": (
                tool_call.details.get(_FUNCTION).get("name")
                if tool_call.details.get(_FUNCTION)
                else None
            ),
            "arguments": safe_loads(
                tool_call.details.get(_FUNCTION).get("arguments")
                if tool_call.details.get(_FUNCTION)
                else None
            ),
        }
    else:
        # Treat built-in tools separately.  Object models may be unique so handle each case separately
        # Just converting to dicts here rather than custom serializers for simplicity for now.
        # Don't fail if we run into a newly seen tool, just skip
        if tool_call.details["type"] == "code_interpreter":
            arguments = {"input": tool_call.details.code_interpreter.input}
        elif tool_call.details["type"] == "bing_grounding":
            arguments = {
                "requesturl": tool_call.details["bing_grounding"]["requesturl"]
            }
        elif tool_call.details["type"] == "file_search":
            options = tool_call.details["file_search"]["ranking_options"]
            arguments = {
                "ranking_options": {
                    "ranker": options["ranker"],
                    "score_threshold": options["score_threshold"],
                }
            }
        elif tool_call.details["type"] == "azure_ai_search":
            arguments = {"input": tool_call.details["azure_ai_search"]["input"]}
        elif tool_call.details["type"] == "fabric_dataagent":
            arguments = {"input": tool_call.details["fabric_dataagent"]["input"]}
        else:
            # unsupported tool type, skip
            return messages
        try:
            tool_call_id = tool_call.details.id
            content_tool_call = {
                "type": _TOOL_CALL,
                "tool_call_id": tool_call_id,
                "name": tool_call.details.type,
                "arguments": arguments,
            }
        except:
            return messages

    # We format it into an assistant message, where the content is a singleton list of the content object.
    # It should be a tool message, since this is the call, but the given schema treats this message as
    # assistant's action of calling the tool.
    messages.append(
        AssistantMessage(
            run_id=run_id,
            content=[to_dict(content_tool_call)],
            createdAt=tool_call.created,
        )
    )

    if hasattr(tool_call.details, _FUNCTION) or tool_call.details.get("function"):
        output = safe_loads(tool_call.details.get("function")["output"])
    else:
        try:
            # Some built-ins may have output, others may not
            # Try to retrieve it, but if we don't find anything, skip adding the message
            # Just manually converting to dicts for easy serialization for now rather than custom serializers
            if tool_call.details.type == _CODE_INTERPRETER:
                output = [
                    result.as_dict()
                    for result in tool_call.details.code_interpreter.outputs
                ]
            elif tool_call.details.type == _BING_GROUNDING:
                return messages  # not supported yet from bing grounding tool
            elif tool_call.details.type == _FILE_SEARCH:
                output = [
                    result.as_dict() for result in tool_call.details.file_search.results
                ]
            elif tool_call.details.type == _AZURE_AI_SEARCH:
                output = tool_call.details.azure_ai_search["output"]
            elif tool_call.details.type == _FABRIC_DATAAGENT:
                output = tool_call.details.fabric_dataagent["output"]
        except:
            return messages

    # Now, onto the tool result, which only includes the result of the function call.
    content_tool_call_result = {"type": _TOOL_RESULT, _TOOL_RESULT: output}

    # Since this is a tool's action of returning, we put it as a tool message.
    messages.append(
        ToolMessage(
            run_id=run_id,
            tool_call_id=tool_call_id,
            content=[to_dict(content_tool_call_result)],
            createdAt=tool_call.completed,
        )
    )
    return messages


def to_dict(obj) -> dict:
    """
    Converts an object to a dictionary.

    :param obj: The object to be converted.
    :type obj: Any
    :return: The dictionary representation of the object.
    :rtype: dict
    """
    return json.loads(json.dumps(obj))


def safe_loads(data: str) -> Union[dict, str]:
    """
    Safely loads a JSON string into a Python dictionary or returns the original string if loading fails.
    :param data: The JSON string to be loaded.
    :type data: str
    :return: The loaded dictionary or the original string.
    :rtype: Union[dict, str]
    """
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return data


def convert_message(msg: dict) -> Message:
    """
    Converts a dictionary to the appropriate Message subclass.

    :param msg: The message dictionary.
    :type msg: dict
    :return: The Message object.
    :rtype: Message
    """
    role = msg["role"]
    if role == "system":
        return SystemMessage(content=str(msg["content"]))
    elif role == "user":
        return UserMessage(content=msg["content"], createdAt=msg["createdAt"])
    elif role == "assistant":
        return AssistantMessage(
            run_id=str(msg["run_id"]),
            content=msg["content"],
            createdAt=msg["createdAt"],
        )
    elif role == "tool":
        return ToolMessage(
            run_id=str(msg["run_id"]),
            tool_call_id=str(msg["tool_call_id"]),
            content=msg["content"],
            createdAt=msg["createdAt"],
        )
    else:
        raise ValueError(f"Unknown role: {role}")
