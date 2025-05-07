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

from typing import List, Union

from azure.ai.evaluation._common._experimental import experimental

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

# Maximum number of workers allowed to make API calls at the same time.
_MAX_WORKERS = 10

# Constants to only be used internally in this file for the built-in tools.
_CODE_INTERPRETER = "code_interpreter"
_BING_GROUNDING = "bing_grounding"
_FILE_SEARCH = "file_search"

# Built-in tool descriptions and parameters are hidden, but we include basic descriptions
# for evaluation purposes.
_BUILT_IN_DESCRIPTIONS = {
    _CODE_INTERPRETER: "Use code interpreter to read and interpret information from datasets, "
    + "generate code, and create graphs and charts using your data. Supports "
    + "up to 20 files.",
    _BING_GROUNDING: "Enhance model output with web data.",
    _FILE_SEARCH: "Search for data across uploaded files.",
}

# Built-in tool parameters are hidden, but we include basic parameters for evaluation purposes.
_BUILT_IN_PARAMS = {
    _CODE_INTERPRETER: {
        "type": "object",
        "properties": {"input": {"type": "string", "description": "Generated code to be executed."}},
    },
    _BING_GROUNDING: {
        "type": "object",
        "properties": {"requesturl": {"type": "string", "description": "URL used in Bing Search API."}},
    },
    _FILE_SEARCH: {
        "type": "object",
        "properties": {
            "ranking_options": {
                "type": "object",
                "properties": {
                    "ranker": {"type": "string", "description": "Ranking algorithm to use."},
                    "score_threshold": {"type": "number", "description": "Threshold for search results."},
                },
                "description": "Ranking options for search results.",
            }
        },
    },
}

@experimental
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
                thread_id=thread_id,
                run_id=run_id,
                limit=_AI_SERVICES_API_MAX_LIMIT,
                order=ListSortOrder.ASCENDING,
                after=after,
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
            # Here we handle the custom functions and create tool definitions out of them.
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
            else:
                # Add limited support for built-in tools. Descriptions and parameters
                # are not published, but we'll include placeholders.
                if tool.type in _BUILT_IN_DESCRIPTIONS and tool.type in _BUILT_IN_PARAMS:
                    final_tools.append(
                        ToolDefinition(
                            name=tool.type,
                            description=_BUILT_IN_DESCRIPTIONS[tool.type],
                            parameters=_BUILT_IN_PARAMS[tool.type],
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
    def _filter_run_ids_up_to_run_id(run_ids: List[str], run_id: str, include_run_id: bool = True) -> List[str]:
        """
        Filters run IDs up to a specific run ID.

        This method processes a list of run IDs and filters out run IDs that come after the specified run ID.
        It ensures that only run IDs up to and including the specified run ID are included in the result.

        :param run_ids: The list of run IDs in chronological order.
        :type run_ids: List[str]
        :param run_id: The ID of the run to filter messages up to.
        :type run_id: str
        :return: The filtered list of run IDs up to the specified run ID.
        :rtype: List[str]
        """
        for index, single_run_id in enumerate(run_ids):
            # Since this is the conversation of the entire thread and we are interested in a given run, we need to
            # filter out the messages that came after the run.
            if single_run_id == run_id:
                if include_run_id:
                    return run_ids[: index + 1]
                return run_ids[:index]

        # If we didn't find the run_id, we return an empty list.
        return []

    @staticmethod
    def _filter_messages_up_to_run_id(
        chronological_messages, run_id: str, include_run_id: bool = True
    ) -> List[Message]:
        """
        Filters messages up to a specific run ID.

        This method processes a list of messages in chronological order and filters out messages that come after the specified run ID.
        It ensures that only messages up to and including the specified run ID are included in the result.

        :param chronological_messages: The list of messages in chronological order.
        :type chronological_messages: List[Message]
        :param run_id: The ID of the run to filter messages up to.
        :type run_id: str
        :return: The filtered list of messages up to the specified run ID.
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

                    # If we entered our current run and its the run that we have requested to filter up to, but
                    # not including, we can break out of the loop.
                    if not include_run_id:
                        break

            # Then, if we think that we are currently in our run and we have a message that is not from our run,
            # it means that we have left our run.
            if in_my_current_run and single_turn.run_id != run_id:
                break

            # We're good to add it.
            filtered_messages.append(single_turn)

        return filtered_messages

    @staticmethod
    def _extract_typed_messages(ai_services_messages) -> List[Message]:
        """
        Extracts and converts AI service messages to a list of typed Message objects.

        This method processes a list of messages from the AI service, converting them into
        appropriate Message subclass instances (UserMessage, AssistantMessage) based on their role.
        It filters out messages without content and handles different message roles accordingly.

        :param ai_services_messages: A list of messages from the AI service.
        :type ai_services_messages: _models.OpenAIPageableListOfThreadMessage (some internal type from ai projects)
        :return: A list of typed Message objects.
        :rtype: List[Message]
        """
        # We will collect messages in this accumulator.
        final_messages: List[Message] = []

        # Each visible message in the conversation is a message from the user or the assistant, we collect
        # both the text and timestamp, so we can recreate the chronological order.
        for single_turn in ai_services_messages:
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

        return final_messages

    def _fetch_tool_calls(self, thread_id: str, run_id: str) -> List[Message]:
        """
        Fetches tool calls for a given thread and run, and converts them into messages.

        This method retrieves tool calls for a specified thread and run, converts them into messages using the
        `break_tool_call_into_messages` utility function, and returns the list of messages.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :param run_id: The ID of the run.
        :type run_id: str
        :return: A list of messages converted from tool calls.
        :rtype: List[Message]
        """
        tool_calls: List[Message] = []
        for chrono_tool_call in self._list_tool_calls_chronological(thread_id, run_id):
            tool_calls.extend(break_tool_call_into_messages(chrono_tool_call, run_id))
        return tool_calls

    def _retrieve_tool_calls_up_to_including_run_id(
        self, thread_id: str, run_id: str, exclude_tool_calls_previous_runs: bool = False
    ) -> List[Message]:
        """
        Converts tool calls to messages for a given thread and run.

        This method retrieves tool calls for a specified thread and run, converts them into messages,
        and optionally includes tool calls from previous runs.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :param run_id: The ID of the run.
        :type run_id: str
        :param exclude_tool_calls_previous_runs: Whether to exclude tool calls from previous runs in the conversion. Default is False.
        :type exclude_tool_calls_previous_runs: bool
        :return: A list of messages converted from tool calls.
        :rtype: List[Message]
        """
        to_return: List[Message] = []

        # Add all the tool calls and results of this run as messages.
        for tool_call in self._list_tool_calls_chronological(thread_id, run_id):
            # We need to add the tool call and the result as two separate messages.
            to_return.extend(break_tool_call_into_messages(tool_call, run_id))

        # We also request to add all the tool calls and results of the previous runs into the chat history. This is
        # a bit of an expensive operation, but the requirement is to support this functionality, even at the penalty
        # in latency in performance. New agents api is to include these details cheaply through a single API call in
        # list_messages, but until that is available, we need to do this. User can also opt-out of this functionality
        # by setting the exclude_tool_calls_previous_runs flag to True.
        if not exclude_tool_calls_previous_runs:
            # These are all the assistant (any number) in the thread.
            # We set the include_run_id to False, since we don't want to include the current run's tool calls, which
            # are already included in the previous step.
            run_ids_up_to_run_id = AIAgentConverter._filter_run_ids_up_to_run_id(
                self._list_run_ids_chronological(thread_id), run_id, include_run_id=False
            )

            # Since each _list_tool_calls_chronological call is expensive, we can use a thread pool to speed
            # up the process by parallelizing the AI Services API requests.
            with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
                futures = {
                    executor.submit(self._fetch_tool_calls, thread_id, run_id): run_id
                    for run_id in run_ids_up_to_run_id
                }
                for future in as_completed(futures):
                    to_return.extend(future.result())

        return to_return

    def _retrieve_all_tool_calls(self, thread_id: str, run_ids: List[str]) -> List[Message]:
        """
        Converts all tool calls to messages for a given thread and list of run IDs.

        This method retrieves tool calls for a specified thread and list of run IDs, converts them into messages,
        and returns the list of messages.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :param run_ids: The list of run IDs.
        :type run_ids: List[str]
        :return: A list of messages converted from tool calls.
        :rtype: List[Message]
        """
        to_return: List[Message] = []

        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
            futures = {executor.submit(self._fetch_tool_calls, thread_id, run_id): run_id for run_id in run_ids}
            for future in as_completed(futures):
                to_return.extend(future.result())

        return to_return

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

        # Since this is Xth run of out possibly N runs, we are only interested is messages that are before the run X.
        chrono_until_run_id = AIAgentConverter._filter_messages_up_to_run_id(chronological_conversation, run_id)

        # Messages are now still in hidden AI services' type, so to get finer control over our typing, we need to
        # convert the message to a friendly schema.
        final_messages = AIAgentConverter._extract_typed_messages(chrono_until_run_id)

        # Third, add all the tool calls and results as messages.
        final_messages.extend(
            self._retrieve_tool_calls_up_to_including_run_id(thread_id, run_id, exclude_tool_calls_previous_runs)
        )

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
        query, responses = AIAgentConverter._break_into_query_responses(final_messages, run_id)

        # Collect it into the final result and dump it to JSON.
        final_result = EvaluatorData(
            query=query,
            response=responses,
            tool_definitions=AIAgentConverter._extract_function_tool_definitions(thread_run),
        )

        return json.loads(final_result.to_json())

    def _prepare_single_thread_evaluation_data(self, thread_id: str, filename: str = None) -> List[dict]:
        """
        Prepares evaluation data for a given thread and optionally writes it to a file.

        This method retrieves all run IDs and messages for the specified thread, processes them to create evaluation data,
        and optionally writes the evaluation data to a JSONL file. The evaluation data includes query and response messages
        as well as tool definitions.

        :param thread_id: The ID of the thread.
        :type thread_id: str
        :param filename: The name of the file to write the evaluation data to. If None, the data is not written to a file.
        :type filename: str, optional
        :return: A list of evaluation data dictionaries.
        :rtype: List[dict]
        """
        list_of_run_evaluations: List[dict] = []

        # These are all the run IDs.
        run_ids = self._list_run_ids_chronological(thread_id)

        # If there were no messages in the thread, we can return an empty list.
        if len(run_ids) < 1:
            return list_of_run_evaluations

        # These are all the messages.
        chronological_conversation = self._list_messages_chronological(thread_id)

        # If there are no messages in the thread, we can return an empty list.
        if len(chronological_conversation) < 1:
            return list_of_run_evaluations

        # These are all the tool calls.
        all_sorted_tool_calls = AIAgentConverter._sort_messages(self._retrieve_all_tool_calls(thread_id, run_ids))

        # The last run should have all the tool definitions.
        thread_run = self.project_client.agents.get_run(thread_id=thread_id, run_id=run_ids[-1])
        instructions = thread_run.instructions

        # So then we can get the tool definitions.
        tool_definitions = AIAgentConverter._extract_function_tool_definitions(thread_run)

        # Now, we create a new evaluator object for each run.
        for run_id in run_ids:
            # We need to filter out the messages that are not from the current run.
            simple_messages = AIAgentConverter._filter_messages_up_to_run_id(chronological_conversation, run_id)

            # Now we need to convert from OpenAI's general ThreadMessage model into our Azure Agents models.
            typed_simple_messages = AIAgentConverter._extract_typed_messages(simple_messages)

            # We also need to filter out the tool calls that are not from the current run.
            sorted_tool_calls = AIAgentConverter._filter_messages_up_to_run_id(all_sorted_tool_calls, run_id)

            # Build the big list.
            this_runs_messages = []
            this_runs_messages.extend(typed_simple_messages)
            this_runs_messages.extend(sorted_tool_calls)

            # Sort it, so it looks nicely in chronological order.
            this_runs_messages = AIAgentConverter._sort_messages(this_runs_messages)

            # If we have a system message, we need to put it at the top of the list.
            if instructions:
                # The system message will have a string content.
                this_runs_messages.insert(0, SystemMessage(content=instructions))

            # Since now we have the messages in the expected order, we need to break them into the query and
            # responses.
            query, responses = AIAgentConverter._break_into_query_responses(this_runs_messages, run_id)

            # Finally, let's pack it up into the final result.
            final_result = EvaluatorData(
                query=query,
                response=responses,
                tool_definitions=tool_definitions,
            )

            # Add it to the list of evaluations.
            list_of_run_evaluations.append(json.loads(final_result.to_json()))

        # So, if we have the filename, we can write it to the file, which is expected to be a JSONL file.
        if filename:
            with open(filename, mode="a", encoding="utf-8") as file:
                for evaluation in list_of_run_evaluations:
                    file.write(json.dumps(evaluation) + "\n")

        # We always return the list of evaluations, even if we didn't or did write it to a file.
        return list_of_run_evaluations

    def prepare_evaluation_data(self, thread_ids=Union[str, List[str]], filename: str = None) -> List[dict]:
        """
        Prepares evaluation data for a given thread or list of threads and optionally writes it to a file.

        This method retrieves all run IDs and messages for the specified thread(s), processes them to create evaluation data,
        and optionally writes the evaluation data to a JSONL file. The evaluation data includes query and response messages
        as well as tool definitions.

        :param thread_ids: The ID(s) of the thread(s). Can be a single thread ID or a list of thread IDs.
        :type thread_ids: Union[str, List[str]]
        :param filename: The name of the file to write the evaluation data to. If None, the data is not written to a file.
        :type filename: str, optional
        :return: A list of evaluation data dictionaries.
        :rtype: List[dict]
        """
        # Single instance, pretty much the same as the list.
        if isinstance(thread_ids, str):
            return self._prepare_single_thread_evaluation_data(thread_id=thread_ids, filename=filename)

        evaluations = []
        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
            # We override the filename, because we don't want to write the file for each thread, having to handle
            # threading issues and file being opened from multiple threads, instead, we just want to write it once
            # at the end.
            futures = {
                executor.submit(self._prepare_single_thread_evaluation_data, str(thread_id), None): thread_id
                for thread_id in thread_ids
            }
            for future in as_completed(futures):
                evaluations.extend(future.result())

        # So, if we have the filename, we can write it to the file, which is expected to be a JSONL file.
        if filename:
            with open(filename, mode="a", encoding="utf-8") as file:
                for evaluation in evaluations:
                    file.write(json.dumps(evaluation) + "\n")

        return evaluations

    @staticmethod
    def _run_ids_from_conversation(conversation: dict) -> List[str]:
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
    def _convert_from_conversation(
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
    def _convert_from_file(filename: str, run_id: str) -> dict:
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

        return AIAgentConverter._convert_from_conversation(data, run_id)
