import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    ThreadRun,
    RunStep,
    RunStepToolCallDetails,
    FunctionDefinition,
    ListSortOrder,
)

from typing import List

# Constants.
from ._models import _USER, _AGENT, _TOOL, _TOOL_CALL, _TOOL_CALLS, _FUNCTION

# Message instances.
from ._models import Message, SystemMessage, UserMessage, AssistantMessage, ToolCall

# Intermediate definitions to hold results.
from ._models import ToolDefinition, EvaluatorData

# Utilities.
from ._models import break_tool_call_into_messages, convert_message

# Maximum items to fetch in a single AI Services API call (imposed by the service).
_AI_SERVICES_API_MAX_LIMIT = 100

class AIAgentConverter:
    """
    A converter for AI agent data.

    :param project_client: The AI project client used for API interactions.
    :type project_client: AIProjectClient
    """

    def __init__(self, project_client: AIProjectClient):
        """
        Initializes the AIAgentConverter with the given AI project client.

        :param project_client: The AI project client used for API interactions.
        :type project_client: AIProjectClient
        """
        self.project_client = project_client

    def _list_messages_chronological(self, thread_id: str):
        """
        Lists messages in chronological order for a given thread.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :return: A list of messages in chronological order.
        :rtype: List[Message]
        """
        to_return = []

        has_more = True
        after = None
        while has_more:
            messages = self.project_client.agents.list_messages(
                thread_id=thread_id, limit=_AI_SERVICES_API_MAX_LIMIT, order=ListSortOrder.ASCENDING, after=after
            )
            has_more = messages.has_more
            after = messages.last_id
            if messages.data:
                # We need to add the messages to the accumulator.
                to_return.extend(messages.data)

        return to_return

    def _list_tool_calls_chronological(self, thread_id: str, run_id: str) -> List[ToolCall]:
        """
        Lists tool calls in chronological order for a given thread and run.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :param run_id: The ID of the run.
        :type run_id: str
        :return: A list of tool calls in chronological order.
        :rtype: List[ToolCall]
        """
        # This is the other API request that we need to make to AI service, such that we can get the details about
        # the tool calls and results. Since the list is given in reverse chronological order, we need to reverse it.
        run_steps_chronological: List[RunStep] = []
        has_more = True
        after = None
        while has_more:
            run_steps = self.project_client.agents.list_run_steps(
                thread_id=thread_id, run_id=run_id, limit=_AI_SERVICES_API_MAX_LIMIT, order=ListSortOrder.ASCENDING, after=after
            )
            has_more = run_steps.has_more
            after = run_steps.last_id
            if run_steps.data:
                # We need to add the run steps to the accumulator.
                run_steps_chronological.extend(run_steps.data)

        # Let's accumulate the function calls in chronological order. Function calls
        tool_calls_chronological: List[ToolCall] = []
        for run_step_chronological in run_steps_chronological:
            if run_step_chronological.type != _TOOL_CALLS:
                continue
            step_details: RunStepToolCallDetails = run_step_chronological.step_details
            if step_details.type != _TOOL_CALLS:
                continue
            if len(step_details.tool_calls) < 1:
                continue
            for tool_call in step_details.tool_calls:
                # We need to add the tool call and the result as two separate messages.
                tool_calls_chronological.append(
                    ToolCall(
                        created=run_step_chronological.created_at,
                        completed=run_step_chronological.completed_at,
                        details=tool_call,
                    )
                )

        return tool_calls_chronological

    def _list_run_ids_chronological(self, thread_id: str) -> List[str]:
        """
        Lists run IDs in chronological order for a given thread.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :return: A list of run IDs in chronological order.
        :rtype: List[str]
        """
        runs = self.project_client.agents.list_runs(thread_id=thread_id, order=ListSortOrder.ASCENDING)
        run_ids = [run["id"] for run in runs["data"]]
        return run_ids

    @staticmethod
    def _extract_function_tool_definitions(thread_run: ThreadRun) -> List[ToolDefinition]:
        """
        Extracts tool definitions from a thread run.

        :param thread_run: The thread run containing tool definitions.
        :type thread_run: ThreadRun
        :return: A list of tool definitions extracted from the thread run.
        :rtype: List[ToolDefinition]
        """
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
        return final_tools

    @staticmethod
    def _break_into_query_responses(messages: List[Message], run_id: str) -> (List[Message], List[Message]):
        """
        Breaks a list of messages into query and response messages based on the run ID.

        :param messages: The list of messages to be broken into query and response.
        :type messages: List[Message]
        :param run_id: The ID of the run to distinguish response messages.
        :type run_id: str
        :return: A tuple containing two lists - the first list contains query messages, and the second list contains response messages.
        :rtype: (List[Message], List[Message])
        """
        query: List[Message] = [what for what in messages if what.run_id != run_id]
        responses: List[Message] = [what for what in messages if what.run_id == run_id]
        return query, responses

    @staticmethod
    def _filter_messages_up_to_run_id(chronological_messages, run_id: str):
        """
        Filters messages up to a specific run ID.

        :param chronological_messages: The list of messages in chronological order.
        :type chronological_messages: List[Message]
        :param run_id: The ID of the run.
        :type run_id: str
        :return: The filtered list of messages.
        :rtype: List[Message]
        """
        filtered_messages = []
        in_my_current_run = False
        for single_turn in chronological_messages:
            # Since this is the conversation of the entire thread and we are interested in a given run, we need to
            # filter out the messages that came after the run.
            if single_turn.run_id is not None:
                if single_turn.run_id == run_id:
                    in_my_current_run = True

            # Then, if we think that we are currently in our run and we have a message that is not from our run,
            # it means that we have left our run.
            if in_my_current_run and single_turn.run_id != run_id:
                break

            # We're good to add it.
            filtered_messages.append(single_turn)

        return filtered_messages

    @staticmethod
    def _is_agent_tool_call(message: Message) -> bool:
        """
        Determines if a message is an agent tool call.

        :param message: The message to be checked.
        :type message: Message
        :return: True if the message is an agent tool call, False otherwise.
        :rtype: bool
        """
        return (
            message.role == _AGENT  # Any other agent that this run's.
            and isinstance(message.content, list)  # Content is of expected type.
            and len(message.content) > 0  # There are messages/calls/results present.
            and "type" in message.content[0]  # Being safe here.
            and message.content[0]["type"] == _TOOL_CALL  # Not interested in assistant's toolcalls.
        )

    @staticmethod
    def _sort_messages(messages: List[Message]) -> List[Message]:
        """
        Sorts a list of messages, placing messages with `createdAt` set to None at the beginning.

        :param messages: The list of messages to be sorted.
        :type messages: List[Message]
        :return: The sorted list of messages.
        :rtype: List[Message]
        """
        # Separate messages with createdAt set to None
        none_created_at = [message for message in messages if message.createdAt is None]

        # Filter out messages with createdAt set to None and sort the remaining messages
        sorted_messages = sorted(
            [message for message in messages if message.createdAt is not None],
            key=lambda x: (x.createdAt, x.role == _AGENT),
        )

        # Combine the lists, placing messages with None createdAt at the beginning
        return none_created_at + sorted_messages

    def convert(self, thread_id: str, run_id: str, exclude_tool_calls_previous_runs: bool = False) -> dict:
        """
        Converts the agent run to a format suitable for the OpenAI API.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :param run_id: The ID of the run.
        :type run_id: str
        :param exclude_tool_calls_previous_runs: Whether to exclude tool calls from previous runs in the conversion.
        :type exclude_tool_calls_previous_runs: bool
        :return: The converted data in dictionary format.
        :rtype: dict
        """
        # Make the API call once and reuse the result.
        thread_run: ThreadRun = self.project_client.agents.get_run(thread_id=thread_id, run_id=run_id)

        # Walk through the "user-facing" conversation history and start adding messages.
        chronological_conversation = self._list_messages_chronological(thread_id)

        # We will collect messages in this accumulator.
        final_messages: List[Message] = []

        # Each visible message in the conversation is a message from the user or the assistant, we collect
        # both the text and timestamp, so we can recreate the chronological order.
        for single_turn in AIAgentConverter._filter_messages_up_to_run_id(chronological_conversation, run_id):
            # This shouldn't really happen, ever. What's the point of a message without content? But to avoid a nasty
            # crash on one of the historical messages, let's check for it and bail out from this iteration.
            if len(single_turn.content) < 1:
                continue

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

        # Third, add all the tool calls and results as messages.
        for tool_call in self._list_tool_calls_chronological(thread_id, run_id):
            # We need to add the tool call and the result as two separate messages.
            final_messages.extend(break_tool_call_into_messages(tool_call, run_id))

        # We also request to add all the tool calls and results of the previous runs into the chat history. This is
        # a bit of an expensive operation, but the requirement is to support this functionality, even at the penalty
        # in latency in performance. New agents api is to include these details cheaply through a single API call in
        # list_messages, but until that is available, we need to do this. User can also opt-out of this functionality
        # by setting the exclude_tool_calls_previous_runs flag to True.
        if not exclude_tool_calls_previous_runs:
            # These are all the assistant (any number) in the thread.
            all_run_ids = self._list_run_ids_chronological(thread_id)

            # Helper method to fetch tool calls for a given run ID.
            def fetch_tool_calls(local_run_id) -> List[Message]:
                tool_calls: List[Message] = []
                if local_run_id != thread_run.id:
                    for chrono_tool_call in self._list_tool_calls_chronological(thread_id, local_run_id):
                        tool_calls.extend(break_tool_call_into_messages(chrono_tool_call, local_run_id))
                return tool_calls

            # Since each _list_tool_calls_chronological call is expensive, we can use a thread pool to speed
            # up the process by parallelizing the AI Services API requests.
            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(fetch_tool_calls, run_id): run_id for run_id in all_run_ids}
                for future in as_completed(futures):
                    final_messages.extend(future.result())

        # All of our final messages have to be in chronological order. We use a secondary sorting key,
        # since the tool_result and assistant events would come with the same timestamp, so we need to
        # sort them by role, such that the assistant's message would come after the tool result it's sending.
        final_messages = AIAgentConverter._sort_messages(final_messages)

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
        final_result = EvaluatorData(
            query=query,
            response=responses,
            tool_definitions=AIAgentConverter._extract_function_tool_definitions(thread_run),
        )

        return json.loads(final_result.to_json())

    @staticmethod
    def run_ids_from_conversation(conversation: dict) -> List[str]:
        """
        Extracts a list of unique run IDs from a conversation dictionary.

        :param conversation: The conversation dictionary containing messages.
        :type conversation: dict
        :return: A list of unique run IDs in the order they appear.
        :rtype: List[str]
        """
        if not isinstance(conversation, dict) or "messages" not in conversation:
            return []
        run_ids_with_repetitions = [message["run_id"] for message in conversation["messages"] if "run_id" in message]
        # Removes duplicates, requires Python 3.7+ to ensure order is preserved
        run_ids = list(dict.fromkeys(run_ids_with_repetitions))
        return run_ids

    @staticmethod
    def convert_from_conversation(
        conversation: dict, run_id: str, exclude_tool_calls_previous_runs: bool = False
    ) -> dict:
        """
        Converts the agent run from a conversation dictionary object (a loaded thread) to a format suitable for the OpenAI API.

        :param conversation: The conversation dictionary object.
            The expected schema for the conversation dictionary is as follows:
            {
                "messages": [
                    {
                        "role": str,  # The role of the message sender, e.g., "user", "assistant", "tool".
                        "content": list,  # A list of content dictionaries.
                        "run_id": str,  # The ID of the run associated with the message.
                        "createdAt": str,  # The timestamp when the message was created.
                        ...
                    },
                    ...
                ],
                "tools": [
                    {
                        "name": str,  # The name of the tool.
                        "description": str,  # The description of the tool.
                        "parameters": dict  # The parameters for the tool.
                    },
                    ...
                ]
            }
        :type conversation: dict
        :param run_id: The ID of the run.
        :type run_id: str
        :param exclude_tool_calls_previous_runs: Whether to exclude tool calls from previous runs in the conversion.
        :type exclude_tool_calls_previous_runs: bool
        :return: The converted data in dictionary format serialized as string.
        :rtype: dict
        """
        # We need to type our messages to the correct type, so we can sliced and dice the way we like it.
        messages: List[dict] = conversation.get("messages", [])
        converted_messages: List[Message] = [convert_message(message) for message in messages]

        # Accumulate the messages in the correct order, but only up to the run_id.
        final_messages: List[Message] = []
        for converted_message in AIAgentConverter._filter_messages_up_to_run_id(converted_messages, run_id):
            # By default, we want to add all the messages, even if we are on the 10th run of the thread, we want to know
            # what the assistant said, what the assistant called, and what the result was.
            if exclude_tool_calls_previous_runs:
                # We would not be interested in tool call messages in the query, unless it's the current run id.
                if converted_message.run_id != run_id:
                    # Anything with tool, we can throw out, since we don't care about the tooling of possibly other agents
                    # that came before the run we're interested in.
                    if converted_message.role == _TOOL:
                        continue

                    # We also don't want anything that is an assistant calling a tool.
                    if AIAgentConverter._is_agent_tool_call(converted_message):
                        continue

            # We're good to add it.
            final_messages.append(converted_message)

        # Just in case, sort them all out by putting the messages without createdAt, like SystemMessage's at the
        # top of the list, so they appear first.
        final_messages = AIAgentConverter._sort_messages(final_messages)

        # Create the tool definitions.
        tools = conversation.get("tools", [])
        tool_definitions = [
            ToolDefinition(name=tool["name"], description=tool.get("description"), parameters=tool["parameters"])
            for tool in tools
        ]

        # Separate into the chat history, with all other user-assistant messages, and the assistant's response, where
        # the latter would include
        query, responses = AIAgentConverter._break_into_query_responses(final_messages, run_id)

        # Create the final result
        final_result = EvaluatorData(query=query, response=responses, tool_definitions=tool_definitions)

        return json.loads(final_result.to_json())

    @staticmethod
    def convert_from_file(filename: str, run_id: str) -> dict:
        """
        Converts the agent run from a JSON file to a format suitable for the OpenAI API, the JSON file being a thread.

        :param filename: The path to the JSON file.
            The expected schema for the JSON file is as follows:
            {
                "messages": [
                    {
                        "role": str,  # The role of the message sender, e.g., "user", "assistant", "tool".
                        "content": list,  # A list of content dictionaries.
                        "run_id": str,  # The ID of the run associated with the message.
                        "createdAt": str,  # The timestamp when the message was created.
                        ...
                    },
                    ...
                ],
                "tools": [
                    {
                        "name": str,  # The name of the tool.
                        "description": str,  # The description of the tool.
                        "parameters": dict  # The parameters for the tool.
                    },
                    ...
                ]
            }
        :type filename: str
        :param run_id: The ID of the run.
        :type run_id: str
        :return: The converted data in dictionary format serialized as string.
        :rtype: dict
        """

        with open(filename, mode="r", encoding="utf-8") as file:
            data = json.load(file)

        return AIAgentConverter.convert_from_conversation(data, run_id)
