import datetime
import json

from pydantic import BaseModel

from azure.ai.projects.models import RunStepFunctionToolCall

from typing import List, Optional, Union

# Message roles constants.
_SYSTEM = 'system'
_USER = 'user'
_AGENT = 'assistant'
_TOOL = 'tool'

# Constant definitions for what tool details include.
_TOOL_CALL = 'tool_call'
_TOOL_RESULT = 'tool_result'
_FUNCTION = 'function'

# This is returned by AI services in the API to filter against tool invocations.
_TOOL_CALLS = 'tool_calls'

class Message(BaseModel):
    """Represents a message in an agentic conversation.

    :param createdAt: The timestamp when the message was created.
    :type createdAt: datetime.datetime
    :param run_id: The ID of the run associated with the message. Optional.
    :type run_id: Optional[str]
    :param role: The role of the message sender (e.g., system, user, tool, assistant).
    :type role: str
    :param content: The content of the message, which can be a string or a list of dictionaries.
    :type content: Union[str, List[dict]]
    """
    createdAt: datetime.datetime
    run_id: Optional[str] = None
    tool_call_id: Optional[str] = None # see ToolMessage
    role: str
    content: Union[str, List[dict]]

class SystemMessage(Message):
    """Represents a system message in an agentic conversation.

    :param role: The role of the message sender, which is always 'system'.
    :type role: str
    """
    role: str = _SYSTEM

class UserMessage(Message):
    """Represents a user message in an agentic conversation.

    :param role: The role of the message sender, which is always 'user'.
    :type role: str
    """
    role: str = _USER

class ToolMessage(Message):
    """Represents a tool message in an agentic conversation, either a tool call or tool result.

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


class AssistantMessage(Message):
    """Represents an assistant message.

    :param run_id: The ID of the run associated with the message.
    :type run_id: str
    :param role: The role of the message sender, which is always 'assistant'.
    :type role: str
    """
    run_id: str
    role: str = _AGENT

class ToolDefinition(BaseModel):
    """Represents a tool definition that will be used in the agent.

    :param id: The unique identifier of the tool.
    :type id: str
    :param name: The name of the tool.
    :type name: str
    :param description: A description of the tool.
    :type description: str
    :param parameters: The parameters required by the tool.
    :type parameters: dict
    """
    id: str
    name: str
    description: str
    parameters: dict

class ToolCall:
    """Represents a tool call, used as an intermediate step in the conversion process.

    :param created: The timestamp when the tool call was created.
    :type created: datetime.datetime
    :param completed: The timestamp when the tool call was completed.
    :type completed: datetime.datetime
    :param details: The details of the tool call.
    :type details: RunStepFunctionToolCall
    """
    def __init__(self, created: datetime.datetime, completed: datetime.datetime, details: RunStepFunctionToolCall):
        self.created = created
        self.completed = completed
        self.details = details

class ConvertedResult(BaseModel):
    """Represents the result of a conversion.

    :param messages: A list of messages.
    :type messages: List[Message]
    :param tools: A list of tool definitions.
    :type tools: List[ToolDefinition]
    """
    messages: List[Message]
    tools: List[ToolDefinition]

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

    # This is the internals of the content object that will be included with the tool call.
    tool_call_id = tool_call.details.id
    content_tool_call = {
        'type': _TOOL_CALL,
        _TOOL_CALL: {
            'id': tool_call_id,
            'type': _FUNCTION,
            _FUNCTION: {
                'name': tool_call.details.function.name,
                'arguments': json.loads(tool_call.details.function.arguments),
            }
        }
    }

    # We format it into an assistant message, where the content is a singleton list of the content object.
    # I think it should be a tool message, since this is the call, but the given schema treats this message as
    # assistant's action of calling the tool.
    messages.append(AssistantMessage(run_id=run_id,
                                content=[to_dict(content_tool_call)],
                                createdAt=tool_call.created))

    # Now, onto the tool result, which only includes the result of the function call.
    content_tool_call_result = {
        'type': _TOOL_RESULT,
        _TOOL_RESULT: json.loads(tool_call.details.function.output)
    }

    # Since this is a tool's action of returning, we put it as a tool message.
    messages.append(ToolMessage(run_id=run_id,
                                tool_call_id=tool_call_id,
                                content=[to_dict(content_tool_call_result)],
                                createdAt=tool_call.completed))
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
