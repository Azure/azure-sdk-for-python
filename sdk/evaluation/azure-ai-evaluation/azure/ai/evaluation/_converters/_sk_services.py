import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple, Optional

from azure.ai.evaluation._common._experimental import experimental

from semantic_kernel.contents import (
    AuthorRole,
    TextContent,
    FunctionCallContent,
    FunctionResultContent,
)
from semantic_kernel.contents.chat_message_content import ChatMessageContent

from semantic_kernel.agents import (
    ChatCompletionAgent,
    ChatHistoryAgentThread,
)

from ._models import (
    Message,
    SystemMessage,
    UserMessage,
    SKToolMessage,
    SKAssistantMessage,
    ToolDefinition,
    ToolCall,
    EvaluatorData,
    SKDeveloperMessage,
)


@experimental
class SKAgentConverter:
    """
    A converter for SK agent data.
    """

    def __init__(self):
        try:
            import semantic_kernel as sk
        except ImportError as e:
            raise ImportError(
                "semantic_kernel package is not installed. Please install it to use SKAgentConverter."
            ) from e

    @staticmethod
    def _transform_tool_definitions(
        tool_list: List[Dict[str, Any]],
    ) -> List[ToolDefinition]:
        """
        Convert verbose tool definition dicts into the `ToolDefinition`s
        :param tool_list: List of tool definitions to transform.
        :type tool_list: List[Dict[str, Any]]
        :return: Transformed list of tool definitions.
        :rtype: List[Dict[str, Any]]
        """
        # TODO: Add required and default values when also supported by Foundry's converter

        final_tools: List[ToolDefinition] = []

        for tool in tool_list:
            filtered_tool = {
                "name": tool["fully_qualified_name"],
                "description": tool.get("description") or "No description",
                "type": "function",  # TODO: hardcoded for now.
                "parameters": {
                    "type": "object",  # Is this always the case?
                    "properties": {},  # Will be filled in below
                },
            }

            for param in tool.get("parameters", []):
                param_name = param.get("name")
                filtered_tool["parameters"]["properties"][param_name] = {
                    "type": param["type_"],
                    "description": param.get("description") or "No description",
                }

            final_tools.append(ToolDefinition(**filtered_tool))

        return final_tools

    @staticmethod
    def _get_tool_definitions(agent: ChatCompletionAgent) -> list:
        """
        Get tool definitions from the agent's plugins.
        :param agent: The ChatCompletionAgent from which to retrieve tool definitions.
        :type agent: ChatCompletionAgent
        :return: A list of tool definitions.
        :rtype: list
        """
        functions = []
        for plugin in agent.kernel.plugins:
            functions_metadata = agent.kernel.plugins[plugin].get_functions_metadata()
            for function in functions_metadata:
                # Serialize metadata to a dictionary
                function_dict = function.model_dump()
                function_dict["fully_qualified_name"] = function.fully_qualified_name
                # function_dict["type"] = "tool_call"
                functions.append(function_dict)

        return functions

    @staticmethod
    def _extract_function_tool_definitions(
        agent: ChatCompletionAgent,
    ) -> List[ToolDefinition]:
        """Get and transform tool definitions from the agent."""
        tool_definitions = SKAgentConverter._get_tool_definitions(agent)
        return SKAgentConverter._transform_tool_definitions(tool_definitions)

    @staticmethod
    def _is_output_role(role):
        return role in (AuthorRole.ASSISTANT, AuthorRole.TOOL)

    @staticmethod
    async def _get_messages_from_thread(
        thread: ChatHistoryAgentThread,
    ) -> List[ChatMessageContent]:
        """
        Get messages from a thread.
        :param thread: The ChatHistoryAgentThread to get messages from.
        :type thread: ChatHistoryAgentThread
        :return: A list of ChatMessageContent objects.
        :rtype: List[ChatMessageContent]
        """
        return [msg async for msg in thread.get_messages()]

    @staticmethod
    async def _get_messages_from_thread_with_agent(
        thread: ChatHistoryAgentThread,
        agent: ChatCompletionAgent = None,
    ) -> List[ChatMessageContent]:
        """
        Get messages from a thread with agent instructions included as a system message if available.
        :param thread: The ChatHistoryAgentThread to get messages from.
        :type thread: ChatHistoryAgentThread
        :param agent: The ChatCompletionAgent to use.
        :type agent: ChatCompletionAgent
        :return: A list of ChatMessageContent objects.
        :rtype: List[ChatMessageContent]
        """
        messages: List[ChatMessageContent] = []

        # If agent is provided, with instructions, add it as a system message
        if agent and agent.instructions:
            messages.append(
                ChatMessageContent(
                    role=AuthorRole.SYSTEM,
                    items=[TextContent(text=agent.instructions)],
                )
            )

        thread_messages = await SKAgentConverter._get_messages_from_thread(thread)
        messages.extend(thread_messages)

        return messages

    @staticmethod
    async def _convert_thread_to_eval_schema(
        thread: ChatHistoryAgentThread,
        turn_index: int,
        agent: ChatCompletionAgent = None,
    ):
        """
        Convert a thread to the evaluation schema.
        :param thread: The ChatHistoryAgentThread containing the conversation history.
        :type thread: ChatHistoryAgentThread
        :param turn_index: The index of the turn in the conversation.
        :type turn_index: int
        :param agent: The ChatCompletionAgent being evaluated.
        :type agent: ChatCompletionAgent
        :return: A dictionary containing the converted data.
        :rtype: dict
        """

        messages: List[ChatMessageContent] = (
            await SKAgentConverter._get_messages_from_thread_with_agent(
                thread=thread,
                agent=agent,
            )
        )

        turns = SKAgentConverter._extract_turns_from_messages(
            messages, turn_index_to_stop=turn_index
        )

        if turn_index >= len(turns):
            raise ValueError(
                f"Turn {turn_index} not found. Only {len(turns)} turns exist."
            )

        return turns[turn_index]

    @staticmethod
    def _extract_turns_from_messages(
        messages: List[ChatMessageContent],
        turn_index_to_stop: Optional[int] = None,
    ) -> List[Tuple[List[Message], List[Message]]]:
        turns = []
        query: List[Message] = []
        response: List[Message] = []

        queued_items = []
        is_queued_output = None

        for msg in messages:
            curr_items = SKAgentConverter._process_message_items(msg)
            curr_is_output = SKAgentConverter._is_output_role(msg.role)

            # Handle the first message to initialize the output/input mode
            if is_queued_output is None:
                queued_items.extend(curr_items)
                is_queued_output = curr_is_output
                continue  # This means if chat starts with an assistant/tool message, it's a separate turn

            # Same group: still within the same input/output block
            if is_queued_output == curr_is_output:
                queued_items.extend(curr_items)
                continue

            # Transition from input → output
            if not is_queued_output and curr_is_output:
                if queued_items:
                    query.extend(queued_items)
                queued_items = curr_items
                is_queued_output = True
                continue

            # Transition from output → input = End of a turn
            if is_queued_output and not curr_is_output:
                # Transition from output to input: end of turn
                response = list(queued_items)
                turns.append((query, response))
                # New turn's query would be the whole previous
                query = list(query) + response
                if turn_index_to_stop is not None and len(turns) > turn_index_to_stop:
                    break
                queued_items = curr_items
                is_queued_output = False

        # Handle if final message(s) are assistant/tool messages
        if queued_items and is_queued_output:
            response = list(queued_items)
            turns.append((query, response))

        return turns

    @staticmethod
    def _convert_messages_to_schema_new(
        messages: List[ChatMessageContent], turn_index: int
    ) -> Tuple[List[Message], List[Message]]:
        """
        Converts messages to schema for a specific turn.
        """
        turns = SKAgentConverter._extract_turns_from_messages(
            messages, turn_index_to_stop=turn_index
        )
        if turn_index >= len(turns):
            raise ValueError(
                f"Turn {turn_index} not found. Only {len(turns)} turns exist."
            )
        return turns[turn_index]

    @staticmethod
    def _safe_json_loads(value: Any) -> Any:
        """Safely parse a JSON string into a Python object, return original if parsing fails."""
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return value

    @staticmethod
    def _process_message_items(message: ChatMessageContent) -> List[Message]:
        """
        Processes the items in a message and converts them to the specified schema.
        Args:
            message (Any): The message object to process.
        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the message items in the specified schema.
        """
        converted_messages = []
        for item in message.items:
            message_dict = {
                "role": message.role.value,
                "content": [],  # will be filled in later
            }
            if "created" in message.metadata:
                message_dict["createdAt"] = SKAgentConverter._convert_timestamp_to_iso(
                    message.metadata["created"]
                )
            if isinstance(item, TextContent):
                item_text = item.to_dict()["text"]
                if message.role == AuthorRole.SYSTEM:  # to match other converters
                    message_dict["content"] = item_text
                else:
                    message_dict["content"] = [{"type": "text", "text": item_text}]

            elif isinstance(item, FunctionCallContent):
                item_dict = item.to_dict()
                item_func = item_dict["function"]
                arguments = SKAgentConverter._safe_json_loads(item_func["arguments"])

                message_dict["content"].append(
                    {
                        "type": "tool_call",
                        "tool_call_id": item_dict.get("id", None),
                        "name": item_func["name"],
                        "arguments": arguments,
                    }
                )
            elif isinstance(item, FunctionResultContent):
                item_dict = item.to_dict()
                message_dict["tool_call_id"] = item_dict.get("tool_call_id", None)

                item_content = SKAgentConverter._safe_json_loads(item_dict["content"])

                message_dict["content"].append(
                    {
                        "type": "tool_result",
                        "tool_result": item_content,
                    }
                )
            else:
                raise Exception(
                    f"Unexpected item type: {type(item)} in message: {message}"
                )

            if message.role == AuthorRole.SYSTEM:
                convert_message = SystemMessage(**message_dict)
            elif message.role == AuthorRole.USER:
                convert_message = UserMessage(**message_dict)
            elif message.role == AuthorRole.DEVELOPER:
                convert_message = SKDeveloperMessage(**message_dict)
            elif message.role == AuthorRole.ASSISTANT:
                convert_message = SKAssistantMessage(**message_dict)
            elif message.role == AuthorRole.TOOL:
                convert_message = SKToolMessage(**message_dict)
            else:
                raise ValueError(f"Unknown role: {message.role}")

            converted_messages.append(convert_message)
        return converted_messages

    @staticmethod
    def is_turn_complete(message: ChatMessageContent) -> bool:
        """
        Determines if a message completes a turn (assistant provides a response).
        :param message: The message object to check.
        :type message: ChatMessageContent
        :return: True if the message completes a turn, False otherwise.
        :rtype: bool
        """
        return any(isinstance(item, TextContent) for item in message.items)

    @staticmethod
    def _convert_timestamp_to_iso(timestamp: float) -> str:
        """
        Converts a timestamp to ISO format.
        :param timestamp: The timestamp to convert.
        :type timestamp: float
        :return: The timestamp in ISO format.
        :rtype: str
        """
        created_dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return created_dt.isoformat().replace("+00:00", "Z")

    async def convert(
        self,
        thread: ChatHistoryAgentThread,
        agent: ChatCompletionAgent,
        turn_index: int,
    ) -> dict:
        """Convert the sdk chat completion agent run to a format suitable for evaluation.

        :param thread: The ChatHistoryAgentThread containing the conversation history.
        :type thread: ChatHistoryAgentThread
        :param agent: The ChatCompletionAgent being evaluated.
        :type agent: ChatCompletionAgent
        :param turn_index: The index of the turn in the conversation.
        :type turn_index: int
        :return: The converted data in dictionary format.
        :rtype: dict
        """

        tool_definitions: List[ToolDefinition] = (
            SKAgentConverter._extract_function_tool_definitions(agent)
        )

        if not thread:
            raise ValueError("Thread cannot be None")

        query, response = await SKAgentConverter._convert_thread_to_eval_schema(
            thread=thread,
            turn_index=turn_index,
            agent=agent,
        )

        result = EvaluatorData(
            query=query,
            response=response,
            tool_definitions=tool_definitions,
        )

        return json.loads(result.to_json())

    async def prepare_evaluation_data(
        self,
        threads: List[ChatHistoryAgentThread],
        agent: ChatCompletionAgent,
        filename: Optional[str] = None,
    ) -> List[dict]:
        """
        Prepares evaluation data for a list of threads and optionally writes it to a file.

        :param threads: List of ChatHistoryAgentThread objects.
        :type threads: List[ChatHistoryAgentThread]
        :param agent: The ChatCompletionAgent being evaluated.
        :type agent: ChatCompletionAgent
        :param filename: Optional file path to save evaluation data as JSONL.
        :type filename: Optional[str]
        :return: List of evaluation data dictionaries.
        :rtype: List[dict]
        """

        if isinstance(threads, ChatHistoryAgentThread):
            threads = [threads]

        all_eval_data: List[dict] = []

        for thread in threads:
            thread_data = await self._prepare_single_thread_evaluation_data(
                thread, agent
            )
            all_eval_data.extend(thread_data)

        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                for item in all_eval_data:
                    f.write(json.dumps(item) + "\n")

        return all_eval_data

    async def _prepare_single_thread_evaluation_data(
        self,
        thread: ChatHistoryAgentThread,
        agent: ChatCompletionAgent,
    ) -> List[dict]:
        """
        Prepares evaluation data for a single thread.

        :param thread: A ChatHistoryAgentThread object.
        :type thread: ChatHistoryAgentThread
        :param agent: The ChatCompletionAgent being evaluated.
        :type agent: ChatCompletionAgent
        :return: A list of evaluation data dictionaries for the thread.
        :rtype: List[dict]
        """
        thread_eval_data: List[dict] = []

        tool_definitions: List[ToolDefinition] = (
            self._extract_function_tool_definitions(agent)
        )

        if not thread:
            raise ValueError("Thread cannot be None")

        messages: List[ChatMessageContent] = (
            await SKAgentConverter._get_messages_from_thread_with_agent(
                thread=thread,
                agent=agent,
            )
        )

        turns = SKAgentConverter._extract_turns_from_messages(messages)

        for query, response in turns:
            turn_eval_data = EvaluatorData(
                query=query,
                response=response,
                tool_definitions=tool_definitions,
            )

            thread_eval_data.append(json.loads(turn_eval_data.to_json()))

        return thread_eval_data

    @staticmethod
    async def _get_thread_turn_indices(thread: ChatHistoryAgentThread) -> List[int]:
        """
        Determines all complete turn indices in a thread.

        :param thread: The ChatHistoryAgentThread to analyze.
        :type thread: ChatHistoryAgentThread
        :return: A list of valid turn indices (0-based).
        :rtype: List[int]
        """

        messages: List[ChatMessageContent] = (
            await SKAgentConverter._get_messages_from_thread(thread)
        )
        if not messages:
            return []

        # Extract turns from the messages
        turns = SKAgentConverter._extract_turns_from_messages(messages)

        # Return indices of valid turns
        return SKAgentConverter._get_turn_indices(messages) if turns else []

    @staticmethod
    def _get_turn_indices(messages: List[ChatMessageContent]) -> List[int]:
        """
        Returns a list of valid turn indices.
        """
        return list(range(len(SKAgentConverter._extract_turns_from_messages(messages))))
