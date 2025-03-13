import json

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ThreadRun, RunStep, RunStepToolCallDetails, FunctionDefinition, ListSortOrder

from typing import List

# Constants.
from ._models import _USER, _AGENT, _TOOL, _TOOL_CALL, _TOOL_CALLS, _FUNCTION

# Message instances.
from ._models import Message, SystemMessage, UserMessage, AssistantMessage, ToolCall

# Intermediate definitions to hold results.
from ._models import ToolDefinition, ConvertedResult

# Utilities.
from ._models import break_tool_call_into_messages, convert_message


class AIAgentConverter:
    """
    A converter for AI agent data.

    :param project_client: The AI project client used for API interactions.
    :type project_client: AIProjectClient
    """

    def __init__(self, project_client: AIProjectClient):
        self.project_client = project_client

    def list_messages_chronological(self, thread_id: str):
        """
        Lists messages in chronological order for a given thread.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :return: A list of messages in chronological order.
        :rtype: List[Message]
        """
        messages = self.project_client.agents.list_messages(
            thread_id=thread_id, limit=100, order=ListSortOrder.ASCENDING
        )
        return messages.data

    def convert(self, thread_id: str, run_id: str) -> str:
        """
        Converts the agent run to a format suitable for the OpenAI API.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :param run_id: The ID of the run.
        :type run_id: str
        :return: The converted data in dictionary format.
        :rtype: str
        """
        # Make the API call once and reuse the result.
        thread_run: ThreadRun = self.project_client.agents.get_run(thread_id=thread_id, run_id=run_id)

        # We will collect messages in this accumulator.
        final_messages: List[Message] = []

        # Walk through the "user-facing" conversation history and start adding messages.
        chronological_conversation = self.list_messages_chronological(thread_id)

        # Each visible message in the conversation is a message from the user or the assistant, we collect
        # both the text and timestamp, so we can recreate the chronological order.
        in_my_current_run = False
        for single_turn in chronological_conversation:
            # Since this is the conversation of the entire thread and we are interested in a given run, we need to
            # filter out the messages that came after the run.
            if single_turn.run_id is not None:
                if single_turn.run_id == run_id:
                    in_my_current_run = True

            # Then, if we think that we are currently in our run and we have a message that is not from our run,
            # it means that we have left our run.
            if in_my_current_run and single_turn.run_id != run_id:
                break

            # Build the content of the text message.
            content = {
                "type": "text",
                "text": single_turn.content[0].text.value,
            }

            # If we have a user message, then we save it as such and since it's a human message, there is no
            # run_id associated with it.
            if single_turn.role == _USER:
                final_messages.append(UserMessage(content=[content], createdAt=single_turn.created_at))
                continue

            # In this case, we have an assistant message. Unfortunately, this would only have the user-facing
            # agent's response, without any details on what tool was called, with what parameters, and what
            # the result was. That will be added later in the method.
            if single_turn.role == _AGENT:
                # We are required to put the run_id in the assistant message.
                final_messages.append(
                    AssistantMessage(content=[content], run_id=single_turn.run_id, createdAt=single_turn.created_at)
                )
                continue

        # This is the other API request that we need to make to AI service, such that we can get the details about
        # the tool calls and results. Since the list is given in reverse chronological order, we need to reverse it.
        run_steps_chronological: List[RunStep] = self.project_client.agents.list_run_steps(
            thread_id=thread_id, run_id=run_id, limit=100, order=ListSortOrder.ASCENDING
        ).data

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
            tool_calls_chronological.append(
                ToolCall(
                    created=run_step_chronological.created_at,
                    completed=run_step_chronological.completed_at,
                    details=step_details.tool_calls[0],
                )
            )

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
                if "required" in parameters:
                    del parameters["required"]

                final_tools.append(
                    ToolDefinition(
                        name=tool_function.name,
                        description=tool_function.description,
                        parameters=parameters,
                    )
                )

        # Finally, we want to force the system message to be the first one in the list.
        # First, we need to create the first system message of the thread.
        instructions = thread_run.instructions
        if instructions:
            # The system message will have a string content.
            final_messages.insert(0, SystemMessage(content=instructions))

        # We need to collect all the messages that are not the current run's response.
        query: List[Message] = [what for what in final_messages if what.run_id != run_id]
        responses: List[Message] = [what for what in final_messages if what.run_id == run_id]

        # Collect it into the final result and dump it to JSON.
        final_result = ConvertedResult(
            query=query,
            response=responses,
            tool_definitions=final_tools,
        )

        return final_result.to_json()


def convert_from_file(filename: str, run_id: str) -> str:
    """
    Converts the agent run from a JSON file to a format suitable for the OpenAI API, the JSON file being a thread.

    :param filename: The path to the JSON file.
    :type filename: str
    :param run_id: The ID of the run.
    :type run_id: str
    :return: The converted data in dictionary format.
    :param already_sorted: Whether the messages are already sorted in chronological order.
    :type already_sorted: bool
    :rtype: str
    """
    with open(filename, "r") as file:
        data = json.load(file)

    # We need to type our messages to the correct type, so we can sliced and dice the way we like it.
    messages = data.get("messages", [])
    converted_messages: List[Message] = []

    # Accumulate the messages in the correct order, but only up to the run_id.
    in_my_current_run = False
    for message in messages:
        converted_message = convert_message(message)
        # We would not be interested in tool call messages in the query, unless it's the current run id.
        if converted_message.run_id != run_id:
            # Anything with tool, we can throw out.
            if converted_message.role == _TOOL:
                continue

            # We also don't want anything that is an assistant calling a tool.
            if converted_message.role == _AGENT:
                if isinstance(converted_message.content, list):
                    if len(converted_message.content) > 0:
                        if "type" in converted_message.content[0]:
                            if converted_message.content[0]["type"] == _TOOL_CALL:
                                continue

        # Since this is the conversation of the entire thread and we are interested in a given run, we need to
        # filter out the messages that came after the run.
        if converted_message.run_id is not None:
            if converted_message.run_id == run_id:
                in_my_current_run = True

        # Then, if we think that we are currently in our run and we have a message that is not from our run,
        # it means that we have left our run.
        if in_my_current_run and converted_message.run_id != run_id:
            break

        # We're good to add it.
        converted_messages.append(converted_message)

    # Create the tool definitions.
    tools = data.get("tools", [])
    tool_definitions = [
        ToolDefinition(name=tool["name"], description=tool.get("description"), parameters=tool["parameters"])
        for tool in tools
    ]

    # # Separate messages into query and response
    query_messages = [what for what in converted_messages if what.run_id != run_id]
    response_messages = [what for what in converted_messages if what.run_id == run_id]

    # Create the final result
    final_result = ConvertedResult(query=query_messages, response=response_messages, tool_definitions=tool_definitions)

    return final_result.to_json()
