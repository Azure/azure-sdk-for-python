import json

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ThreadRun, RunStep, RunStepToolCallDetails, FunctionDefinition

from typing import List

# Constants.
from ._models import _SYSTEM, _USER, _AGENT, _TOOL, _TOOL_CALLS, _FUNCTION
# Message instances.
from ._models import Message, SystemMessage, UserMessage, AssistantMessage, ToolCall
# Intermediate definitions to hold results.
from ._models import ToolDefinition, ConvertedResult
# Utilities.
from ._models import break_tool_call_into_messages

class AIAgentConverter:
    """
    A converter for AI agent data.

    :param project_client: The AI project client used for API interactions.
    :type project_client: AIProjectClient
    """

    def __init__(self, project_client: AIProjectClient):
        self.project_client = project_client

    def list_messages_chronological(self, thread_id: str, run_id: str):
        """
        Lists messages in chronological order for a given thread and run.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :param run_id: The ID of the run.
        :type run_id: str
        :return: A list of messages in chronological order.
        :rtype: List[Message]
        """
        messages = self.project_client.agents.list_messages(thread_id=thread_id, run_id=run_id)
        return messages.data[::-1]

    def convert(self, thread_id: str, run_id: str) -> dict:
        """
        Converts the agent run to a format suitable for the OpenAI API.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :param run_id: The ID of the run.
        :type run_id: str
        :return: The converted data in dictionary format.
        :rtype: dict
        """
        # Make the API call once and reuse the result.
        thread_run: ThreadRun = self.project_client.agents.get_run(thread_id=thread_id, run_id=run_id)

        # We will collect messages in this accumulator.
        final_messages: List[Message] = []

        # First, we need to create the first system message of the thread.
        instructions = thread_run.instructions
        if instructions:
            # The system message will have a string content.
            final_messages.append(SystemMessage(content=instructions,
                                                createdAt=thread_run.created_at))

        # Second, walk through the "user-facing" conversation history and start adding messages.
        chronological_conversation = self.list_messages_chronological(thread_id, run_id)

        # Each visible message in the conversation is a message from the user or the assistant, we collect
        # both the text and timestamp, so we can recreate the chronological order.
        for single_turn in chronological_conversation:
            content = {
                'type': 'text',
                'text': single_turn.content[0].text.value,
            }

            # If we have a user message, then we save it as such and since it's a human message, there is no
            # run_id associated with it.
            if single_turn.role == _USER:
                final_messages.append(UserMessage(content=[content],
                                                  createdAt=single_turn.created_at))

            # In this case, we have an assistant message. Unfortunately, this would only have the user-facing
            # agent's response, without any details on what tool was called, with what parameters, and what
            # the result was. That will be added later in the method.
            if single_turn.role == _AGENT:
                # We are required to put the run_id in the assistant message.
                final_messages.append(AssistantMessage(content=[content],
                                                       run_id=single_turn.run_id,
                                                       createdAt=single_turn.created_at))

        # This is the other API request that we need to make to AI service, such that we can get the details about
        # the tool calls and results. Since the list is given in reverse chronological order, we need to reverse it.
        run_steps_chronological: List[RunStep] = self.project_client.agents.list_run_steps(thread_id=thread_id,
                                                                                           run_id=run_id).data[::-1]

        # Let's accumulate the function calls in chronological order. Function calls
        tool_calls_chronological: List[ToolCall] = []
        for run_step_chronological in run_steps_chronological:
            if run_step_chronological.type != _TOOL_CALLS:
                continue
            step_details: RunStepToolCallDetails = run_step_chronological.step_details
            if step_details.type != _TOOL_CALLS:
                continue
            if len(step_details.tool_calls) != 1:
                continue
            tool_calls_chronological.append(ToolCall(
                created=run_step_chronological.created_at,
                completed=run_step_chronological.completed_at,
                details=step_details.tool_calls[0]
            ))

        # Third, add all the tool calls and results as messages.
        for tool_call in tool_calls_chronological:
            # We need to add the tool call and the result as two separate messages.
            final_messages.extend(break_tool_call_into_messages(tool_call, run_id))

        # All of our final messages have to be in chronological order. We use a secondary sorting key,
        # since the tool_result and assistant events would come with the same timestamp, so we need to
        # sort them by role, such that the assistant's message would come after the tool result it's sending.
        final_messages.sort(key=lambda x: (x.createdAt, x.role == _AGENT))

        # Let's get the tool definitions.
        final_tools: List[ToolDefinition] = []
        for tool in thread_run.tools:
            if tool.type == _FUNCTION:
                tool_function: FunctionDefinition = tool.function
                parameters = tool_function.parameters

                # The target schema doesn't support required fields, so we omit it for now.
                if 'required' in parameters:
                    del parameters['required']

                final_tools.append(ToolDefinition(
                    id=tool_function.name,
                    name=tool_function.name,
                    description=tool_function.description,
                    parameters=parameters,
                ))

        final_result = ConvertedResult(
            messages=final_messages,
            tools=final_tools
        )

        return json.loads(final_result.to_json())

    def convert_to_query_response(self, thread_id: str, run_id: str) -> dict:
        """
        Converts the agent run to a query-response format.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :param run_id: The ID of the run.
        :type run_id: str
        :return: The converted data in dictionary format.
        :rtype: dict
        """
        converted_result = self.convert(thread_id, run_id)

        # Find all the user and system messages.
        user_messages = [msg for msg in converted_result['messages'] if msg['role'] == _USER or msg['role'] == _SYSTEM]
        assistant_messages = [msg for msg in converted_result['messages'] if msg['role'] == _AGENT or msg['role'] == _TOOL]

        # Package it up as json into each and dump.
        return {
            'query': json.dumps(user_messages),
            'response': json.dumps(assistant_messages),
            'tools': json.dumps(converted_result['tools'])
        }

    def convert_to_instructions_history(self, thread_id: str, run_id: str) -> dict:
        """
        Converts the agent run to an instructions-history format.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :param run_id: The ID of the run.
        :type run_id: str
        :return: The converted data in dictionary format.
        :rtype: dict
        """
        converted_result = self.convert(thread_id, run_id)

        # There is only one system message.
        system_messages = [msg for msg in converted_result['messages'] if msg['role'] == _SYSTEM]

        # Get all the user messages.
        user_messages = [msg for msg in converted_result['messages'] if msg['role'] == _USER]

        # Get all the assistant messages.
        assistant_messages = [msg for msg in converted_result['messages'] if msg['role'] == _AGENT or msg['role'] == _TOOL]

        # Package it up as json into each and dump.
        return {
            'instructions': system_messages,
            'chat_history': user_messages,
            'response': assistant_messages,
            'tool_definitions': converted_result['tools']
        }