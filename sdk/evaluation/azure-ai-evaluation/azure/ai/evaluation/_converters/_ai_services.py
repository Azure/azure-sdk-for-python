import datetime
import json

from pydantic import BaseModel

from azure.ai.inference.models import ChatRequestMessage, FunctionDefinition
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ThreadRun, FunctionToolDefinition, ToolDefinition, MessageRole, RunStep, \
    RunStepFunctionToolCall, RunStepToolCallDetails, MessageTextContent

from typing import List, Optional, Union

_SYSTEM = 'system'
_USER = 'user'
_AGENT = 'assistant'
_TOOL = 'tool'

class Message(BaseModel):
    timestamp: datetime.datetime
    run_id: Optional[str] = None
    role: str
    content: Union[str, dict]

class SystemMessage(Message):
    role: str = _SYSTEM

class UserMessage(Message):
    role: str = _USER

class ToolMessage(Message):
    run_id: str
    role: str = _TOOL
    tool_call_id: Optional[str] = None

class AssistantMessage(Message):
    run_id: str
    role: str = _AGENT

class ToolCall:
    def __init__(self, created: datetime.datetime, completed: datetime.datetime, details: RunStepFunctionToolCall):
        self.created = created
        self.completed = completed
        self.details = details

class ConvertedResult(BaseModel):
    messages: List[Message]
    #tools: List[ToolDefinition]

    def to_json(self):
        return self.model_dump_json(exclude={'timestamp'}, exclude_none=True)

def break_tool_call_into_messages(tool_call: ToolCall, run_id: str) -> List[Message]:
    messages = []
    content_tool_call = {
        'type': 'tool_call',
        'tool_call': {
            'id': tool_call.details.id,
            'type': 'function',
            'function': {
                'name': tool_call.details.function.name,
                'arguments': json.loads(tool_call.details.function.arguments),
            }
        }
    }
    messages.append(ToolMessage(run_id=run_id,
                                content=json.loads(json.dumps(content_tool_call)),
                                timestamp=tool_call.created))

    # Now, onto the tool results
    content_tool_call_result = {
        'type': 'tool_result',
        'tool_result': json.loads(tool_call.details.function.output)
    }
    messages.append(ToolMessage(run_id=run_id,
                                tool_call_id=tool_call.details.id,
                                content=json.loads(json.dumps(content_tool_call_result)),
                                timestamp=tool_call.completed))
    return messages


class AIAgentConverter:
    def __init__(self, project_client: AIProjectClient):
        self.project_client = project_client

    # Get system messages
    def get_instructions(self, thread_id: str, run_id: str) -> str:
        # What if they use system messages instead?
        return self.project_client.agents.get_run(thread_id=thread_id, run_id=run_id).instructions

    # conversation history up to but not including the current run
    def get_conversation_history(self, thread_id: str, run_id: str):
        messages = self.project_client.agents.list_messages(thread_id=thread_id)
        ret = []
        for message in messages.data[::-1]:
            if message.run_id == run_id:
                break
            if message.role in ["user", "assistant"]:
                # theoretically there can be more than one system message
                # we are not handling if they are interspersed with user/assistant messages
                # just take them all before the current run
                ret.append(message)
        return ret

    def list_messages_chronological(self, thread_id: str, run_id: str):
        messages = self.project_client.agents.list_messages(thread_id=thread_id, run_id=run_id)
        return messages.data[::-1]

    # tool definitions for current run
    def get_tool_definitions(self, thread_id: str, run_id: str):
        return self.project_client.agents.get_run(thread_id=thread_id, run_id=run_id).tools

    def convert(self, thread_id: str, run_id: str) -> ConvertedResult:
        # Make the API call once and reuse the result.
        thread_run: ThreadRun = self.project_client.agents.get_run(thread_id=thread_id, run_id=run_id)

        run_steps_chronological: List[RunStep] = self.project_client.agents.list_run_steps(thread_id=thread_id, run_id=run_id).data[::-1]

        # Let's accumulate the function calls in chronological order.
        tool_calls_chronological: List[ToolCall] = []
        for run_step_chronological in run_steps_chronological:
            if run_step_chronological.type != 'tool_calls':
                continue
            step_details: RunStepToolCallDetails = run_step_chronological.step_details
            if step_details.type != 'tool_calls':
                continue
            if len(step_details.tool_calls) != 1:
                print(f"[WARNING] Unexpected number of tool calls: {len(step_details)} for step {run_step_chronological.id}")
                continue
            tool_calls_chronological.append(ToolCall(
                created=run_step_chronological.created_at,
                completed=run_step_chronological.completed_at,
                details=step_details.tool_calls[0]
            ))

        # We will collect messages in this accumulator.
        final_messages: List[Message] = []

        # First, we need to create the first system message of the thread.
        instructions = thread_run.instructions
        if instructions:
            final_messages.append(SystemMessage(content=instructions,
                                                timestamp=thread_run.created_at))

        # Second, walk through the "user-facing" conversation history and start adding messages.
        chronological_conversation = self.list_messages_chronological(thread_id, run_id)

        # Each visible message in the conversation is a message from the user or the assistant, we collect
        # both the text and timestamp, so we can recreate the chronological order.
        for single_turn in chronological_conversation:
            content = {
                'type': 'text',
                'text': single_turn.content[0].text.value,
            }

            if single_turn.role == _USER:
                final_messages.append(UserMessage(content=content,
                                                  timestamp=single_turn.created_at))

            if single_turn.role == _AGENT:
                # We are required to put the run_id in the assistant message.
                final_messages.append(AssistantMessage(content=content,
                                                       run_id=single_turn.run_id,
                                                       timestamp=single_turn.created_at))

        # Third, add all the tool calls and results as messages.
        for tool_call in tool_calls_chronological:
            # We need to add the tool call and the result as two separate messages.
            final_messages.extend(break_tool_call_into_messages(tool_call, run_id))

        # All of our final messages have to be in chronological order.
        final_messages.sort(key=lambda x: x.timestamp)

        # Let's get the tool definitions.

        # TODO: Add tools definitions
        # TODO: Do not serialize timestamp?
        # TODO: tool_result must come before assistant message if timestamps match
        return ConvertedResult(
            messages=final_messages
        )