# flake8: noqa
# pylint: disable=W0102,W0613,R0914,C0301,E0401,E0611,C0114,R0913,E0702,R0903,C0411
# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import asyncio
import importlib.resources as pkg_resources
import json
import os
import re
import warnings
from typing import Any, Callable, Dict, List, Optional, Union, Tuple

from azure.ai.evaluation._legacy._adapters._flows import AsyncPrompty
from tqdm import tqdm

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._common.utils import construct_prompty_model_config
from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration

from .._exceptions import ErrorBlame, ErrorCategory, EvaluationException
from .._user_agent import USER_AGENT
from ._conversation.constants import ConversationRole
from ._helpers import ConversationHistory, Turn
from ._utils import JsonLineChatProtocol


USER_AGENT += " (type=simulator; subtype=Simulator)"


@experimental
class Simulator:
    """
    Simulator for generating synthetic conversations.

    :param model_config: A dictionary defining the configuration for the model. Acceptable types are AzureOpenAIModelConfiguration and OpenAIModelConfiguration.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration, ~azure.ai.evaluation.OpenAIModelConfiguration]
    :raises ValueError: If the model_config does not contain the required keys or any value is None.

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_simulate.py
            :start-after: [START nonadversarial_simulator]
            :end-before: [END nonadversarial_simulator]
            :language: python
            :dedent: 8
            :caption: Run a Simulator for 2 queries and 4 conversation turns.
    """

    def __init__(self, model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration]):
        self._validate_model_config(model_config)
        self.model_config = model_config
        if "api_version" not in self.model_config:
            self.model_config["api_version"] = "2024-06-01"  # type: ignore

    @staticmethod
    def _validate_model_config(model_config: Any):
        """
        Validates the model_config to ensure all required keys are present and have non-None values.
        If 'type' is not specified, it will attempt to infer the type based on the keys present.

        :param model_config: The model configuration dictionary.
        :type model_config: Dict[str, Any]
        :raises ValueError: If required keys are missing or any of the values are None.
        """
        # Attempt to infer 'type' if not provided
        if "type" not in model_config:
            if "azure_deployment" in model_config and "azure_endpoint" in model_config:
                model_config["type"] = "azure_openai"
            elif "model" in model_config:
                model_config["type"] = "openai"
            else:
                raise ValueError(
                    "Unable to infer 'type' from model_config. Please specify 'type' as 'azure_openai' or 'openai'."
                )

        if model_config["type"] == "azure_openai":
            required_keys = ["azure_deployment", "azure_endpoint"]
        elif model_config["type"] == "openai":
            required_keys = ["api_key", "model"]
        else:
            raise ValueError("model_config 'type' must be 'azure_openai' or 'openai'.")

        missing_keys = [key for key in required_keys if key not in model_config]
        if missing_keys:
            raise ValueError(f"model_config is missing required keys: {', '.join(missing_keys)}")
        none_keys = [key for key in required_keys if model_config.get(key) is None]
        if none_keys:
            raise ValueError(f"The following keys in model_config must not be None: {', '.join(none_keys)}")

    async def __call__(
        self,
        *,
        target: Callable,
        max_conversation_turns: int = 5,
        tasks: List[str] = [],
        text: str = "",
        num_queries: int = 5,
        query_response_generating_prompty: Optional[str] = None,
        user_simulator_prompty: Optional[str] = None,
        api_call_delay_sec: float = 1,
        query_response_generating_prompty_options: Dict[str, Any] = {},
        user_simulator_prompty_options: Dict[str, Any] = {},
        conversation_turns: List[List[Union[str, Dict[str, Any]]]] = [],
        concurrent_async_tasks: int = 5,
        **kwargs,
    ) -> List[JsonLineChatProtocol]:
        """
        Generates synthetic conversations based on provided parameters.

        :keyword target: The target function to call during the simulation.
        :paramtype target: Callable
        :keyword max_conversation_turns: Maximum number of conversation turns for the simulation. Each turn consists of a user and an assistant message.
        :paramtype max_conversation_turns: int
        :keyword tasks: A list of user tasks, each represented as a list of strings. Text should be relevant for the tasks and facilitate the simulation. One example is to use text to provide context for the tasks.
        :paramtype tasks: List[str]
        :keyword text: The initial input text for generating query responses. Given that the same 'text' is provided for a list of tasks, one example use is to break down a user task into sub-tasks that can share the 'text' variable for context.
        :paramtype text: str
        :keyword num_queries: The number of queries to generate.
        :paramtype num_queries: int
        :keyword query_response_generating_prompty: Path to the query response generating prompty file.
        :paramtype query_response_generating_prompty: Optional[str]
        :keyword user_simulator_prompty: Path to the user simulator prompty file.
        :paramtype user_simulator_prompty: Optional[str]
        :keyword api_call_delay_sec: Delay in seconds between API calls.
        :paramtype api_call_delay_sec: float
        :keyword query_response_generating_prompty_options: Additional keyword arguments for the query response generating prompty.
        :paramtype query_response_generating_prompty_options: Dict[str, Any]
        :keyword user_simulator_prompty_options: Additional keyword arguments for the user simulator prompty.
        :paramtype user_simulator_prompty_options: Dict[str, Any]
        :keyword conversation_turns: Predefined conversation turns to simulate.
        :paramtype conversation_turns: List[List[Union[str, Dict[str, Any]]]]
        :keyword concurrent_async_tasks: The number of asynchronous tasks to run concurrently during the simulation.
            Defaults to 5.
        :paramtype concurrent_async_tasks: int
        :return: A list of simulated conversations represented as JsonLineChatProtocol objects.
        :rtype: List[JsonLineChatProtocol]

        Return Value:
        The method returns a list of JsonLineChatProtocol objects, which are essentially a list of dictionaries where the dictionary contains the messages and context. Context includes all the metadata related to the conversation, such as the task, expected response, and query. The messages contain the conversation history, including the user and assistant messages.

        Modes:
        - Task-Free Mode: When only num_queries is specified and tasks is not, the method generates num_queries x max_conversation_turns lines of simulated data grounded in the context of the text.
        - Task-Specific Mode: When both num_queries and tasks are specified, the method generates lines of simulated data based on the tasks. If num_queries > len(tasks), the remaining lines will be simulated in task-free mode. If num_queries < len(tasks), only the first num_queries tasks are used.
        - Conversation Starter Mode: When conversation_turns are specified, the method starts each conversation with the user-specified queries and then follows the conversation history for the remaining turns.
        """
        if conversation_turns and (text or tasks):
            raise ValueError("Cannot specify both conversation_turns and text/tasks")

        if text and num_queries > len(tasks):
            warnings.warn(
                f"You have specified 'num_queries' > len('tasks') ({num_queries} > {len(tasks)}). "
                f"All tasks will be used for generation and the remaining {num_queries - len(tasks)} lines will be simulated in task-free mode"
            )
        elif text and num_queries < len(tasks):
            warnings.warn(
                f"You have specified 'num_queries' < len('tasks') ({num_queries} < {len(tasks)}). "
                f"Only the first {num_queries} lines of the specified tasks will be simulated."
            )

        max_conversation_turns *= 2  # account for both user and assistant turns

        prompty_model_config = self.model_config
        if conversation_turns:
            return await self._simulate_with_predefined_turns(
                target=target,
                max_conversation_turns=max_conversation_turns,
                conversation_turns=conversation_turns,
                user_simulator_prompty=user_simulator_prompty,
                user_simulator_prompty_options=user_simulator_prompty_options,
                api_call_delay_sec=api_call_delay_sec,
                prompty_model_config=prompty_model_config,
                concurrent_async_tasks=concurrent_async_tasks,
            )

        query_responses = await self._generate_query_responses(
            text=text,
            num_queries=num_queries,
            query_response_generating_prompty=query_response_generating_prompty,
            query_response_generating_prompty_options=query_response_generating_prompty_options,
            prompty_model_config=prompty_model_config,
            **kwargs,
        )
        return await self._create_conversations_from_query_responses(
            query_responses=query_responses,
            max_conversation_turns=max_conversation_turns,
            tasks=tasks,
            user_simulator_prompty=user_simulator_prompty,
            user_simulator_prompty_options=user_simulator_prompty_options,
            target=target,
            api_call_delay_sec=api_call_delay_sec,
            text=text,
        )

    async def _simulate_with_predefined_turns(
        self,
        *,
        target: Callable,
        max_conversation_turns: int,
        conversation_turns: List[List[Union[str, Dict[str, Any]]]],
        user_simulator_prompty: Optional[str],
        user_simulator_prompty_options: Dict[str, Any],
        api_call_delay_sec: float,
        prompty_model_config: Any,
        concurrent_async_tasks: int,
    ) -> List[JsonLineChatProtocol]:
        """
        Simulates conversations using predefined conversation turns.

        :keyword target: The target function to call during each turn of the simulation.
        :paramtype target: Callable
        :keyword max_conversation_turns: Maximum number of turns for the simulation.
        :paramtype max_conversation_turns: int
        :keyword conversation_turns: A list of predefined conversation turns.
        :paramtype conversation_turns: List[List[Union[str, Dict[str, Any]]]]
        :keyword user_simulator_prompty: Path to the user simulator prompty file.
        :paramtype user_simulator_prompty: Optional[str]
        :keyword user_simulator_prompty_options: Additional keyword arguments for the user simulator prompty.
        :paramtype user_simulator_prompty_options: Dict[str, Any]
        :keyword api_call_delay_sec: Delay in seconds between API calls.
        :paramtype api_call_delay_sec: float
        :keyword prompty_model_config: The configuration for the prompty model.
        :paramtype prompty_model_config: Any
        :keyword concurrent_async_tasks: The number of asynchronous tasks to run concurrently during the simulation.
        :paramtype concurrent_async_tasks: int
        :return: A list of simulated conversations represented as JsonLineChatProtocol objects.
        :rtype: List[JsonLineChatProtocol]
        """
        progress_bar = tqdm(
            total=int(len(conversation_turns) * (max_conversation_turns / 2)),
            desc="Simulating with predefined conversation turns: ",
            ncols=100,
            unit="messages",
        )
        semaphore = asyncio.Semaphore(concurrent_async_tasks)
        progress_bar_lock = asyncio.Lock()

        async def run_simulation(simulation: List[Union[str, Dict[str, Any]]]) -> JsonLineChatProtocol:
            async with semaphore:
                current_simulation = ConversationHistory()
                for simulated_turn in simulation:
                    if isinstance(simulated_turn, str):
                        user_turn = Turn(role=ConversationRole.USER, content=simulated_turn)
                    elif isinstance(simulated_turn, dict):
                        user_turn = Turn(
                            role=ConversationRole.USER,
                            content=str(simulated_turn.get("content")),
                            context=str(simulated_turn.get("context")),
                        )
                    else:
                        raise ValueError(
                            "Each simulated turn must be a string or a dict with 'content' and 'context' keys"
                        )
                    current_simulation.add_to_history(user_turn)
                    assistant_response, assistant_context = await self._get_target_response(
                        target=target, api_call_delay_sec=api_call_delay_sec, conversation_history=current_simulation
                    )
                    assistant_turn = Turn(
                        role=ConversationRole.ASSISTANT, content=assistant_response, context=assistant_context
                    )
                    current_simulation.add_to_history(assistant_turn)
                    async with progress_bar_lock:
                        progress_bar.update(1)

                if len(current_simulation) < max_conversation_turns:
                    await self._extend_conversation_with_simulator(
                        current_simulation=current_simulation,
                        max_conversation_turns=max_conversation_turns,
                        user_simulator_prompty=user_simulator_prompty,
                        user_simulator_prompty_options=user_simulator_prompty_options,
                        api_call_delay_sec=api_call_delay_sec,
                        prompty_model_config=prompty_model_config,
                        target=target,
                        progress_bar=progress_bar,
                        progress_bar_lock=progress_bar_lock,
                    )
                return JsonLineChatProtocol(
                    {
                        "messages": current_simulation.to_list(),
                        "finish_reason": ["stop"],
                        "context": {},
                        "$schema": "http://azureml/sdk-2-0/ChatConversation.json",
                    }
                )

        tasks = [asyncio.create_task(run_simulation(simulation)) for simulation in conversation_turns]
        results = await asyncio.gather(*tasks)
        progress_bar.close()
        return results

    async def _extend_conversation_with_simulator(
        self,
        *,
        current_simulation: ConversationHistory,
        max_conversation_turns: int,
        user_simulator_prompty: Optional[str],
        user_simulator_prompty_options: Dict[str, Any],
        api_call_delay_sec: float,
        prompty_model_config: Dict[str, Any],
        target: Callable,
        progress_bar: tqdm,
        progress_bar_lock: asyncio.Lock,
    ):
        """
        Extends an ongoing conversation using a user simulator until the maximum number of turns is reached.

        :keyword current_simulation: The current state of the conversation history.
        :paramtype current_simulation: ConversationHistory,
        :keyword max_conversation_turns: The maximum number of conversation turns.
        :paramtype max_conversation_turns: int,
        :keyword user_simulator_prompty: Path to the user simulator prompty file.
        :paramtype user_simulator_prompty: Optional[str],
        :keyword user_simulator_prompty_options: Additional keyword arguments for the user simulator prompty.
        :paramtype user_simulator_prompty_options: Dict[str, Any],
        :keyword api_call_delay_sec: Delay in seconds between API calls.
        :paramtype api_call_delay_sec: float,
        :keyword prompty_model_config: The configuration for the prompty model.
        :paramtype prompty_model_config: Dict[str, Any],
        :keyword target: The target function to call for responses.
        :paramtype target: Callable,
        :keyword progress_bar: Progress bar for tracking simulation progress.
        :paramtype progress_bar: tqdm,
        :keyword progress_bar_lock: Lock for updating the progress bar safely.
        :paramtype progress_bar_lock: asyncio.Lock
        """
        user_flow = self._load_user_simulation_flow(
            user_simulator_prompty=user_simulator_prompty,  # type: ignore
            prompty_model_config=prompty_model_config,
            user_simulator_prompty_options=user_simulator_prompty_options,
        )

        while len(current_simulation) < max_conversation_turns:
            user_response_content = await user_flow(
                task="Continue the conversation",
                conversation_history=current_simulation.to_context_free_list(),
                **user_simulator_prompty_options,
            )
            user_response = self._parse_prompty_response(response=user_response_content)
            user_turn = Turn(role=ConversationRole.USER, content=user_response["content"])
            current_simulation.add_to_history(user_turn)
            await asyncio.sleep(api_call_delay_sec)
            assistant_response, assistant_context = await self._get_target_response(
                target=target, api_call_delay_sec=api_call_delay_sec, conversation_history=current_simulation
            )
            assistant_turn = Turn(
                role=ConversationRole.ASSISTANT, content=assistant_response, context=assistant_context
            )
            current_simulation.add_to_history(assistant_turn)
            async with progress_bar_lock:
                progress_bar.update(1)

    def _load_user_simulation_flow(
        self,
        *,
        user_simulator_prompty: Optional[Union[str, os.PathLike]],
        prompty_model_config: Dict[str, Any],
        user_simulator_prompty_options: Dict[str, Any],
    ) -> "AsyncPrompty":  # type: ignore
        """
        Loads the flow for simulating user interactions.

        :keyword user_simulator_prompty: Path to the user simulator prompty file.
        :paramtype user_simulator_prompty: Optional[Union[str, os.PathLike]]
        :keyword prompty_model_config: The configuration for the prompty model.
        :paramtype prompty_model_config: Dict[str, Any]
        :keyword user_simulator_prompty_options: Additional keyword arguments for the user simulator prompty.
        :paramtype user_simulator_prompty_options: Dict[str, Any]
        :return: The loaded flow for simulating user interactions.
        :rtype: AsyncPrompty
        """
        if not user_simulator_prompty:
            package = "azure.ai.evaluation.simulator._prompty"
            resource_name = "task_simulate.prompty"
            try:
                # Access the resource as a file path
                # pylint: disable=deprecated-method
                with pkg_resources.path(package, resource_name) as prompty_path:
                    prompty_model_config = construct_prompty_model_config(
                        model_config=prompty_model_config,  # type: ignore
                        default_api_version="2024-06-01",
                        user_agent=USER_AGENT,
                    )
                    return AsyncPrompty.load(source=prompty_path, model=prompty_model_config)  # type: ignore
            except FileNotFoundError as e:
                msg = f"Flow path for {resource_name} does not exist in package {package}."
                raise EvaluationException(
                    message=msg,
                    internal_message=msg,
                    error_category=ErrorCategory.FILE_OR_FOLDER_NOT_FOUND,
                    blame=ErrorBlame.USER_ERROR,
                ) from e
        prompty_model_config = construct_prompty_model_config(
            model_config=prompty_model_config,  # type: ignore
            default_api_version="2024-06-01",
            user_agent=USER_AGENT,
        )
        return AsyncPrompty.load(
            source=user_simulator_prompty,
            model=prompty_model_config,
            **user_simulator_prompty_options,
        )  # type: ignore

    def _parse_prompty_response(self, *, response: str) -> Dict[str, Any]:
        """
        Parses the response from the prompty execution.

        :keyword response: The raw response from the prompty.
        :paramtype response: str
        :return: A dictionary representing the parsed response content.
        :rtype: Dict[str, Any]
        :raises ValueError: If the response cannot be parsed.
        """
        try:
            if isinstance(response, str):
                response = response.replace("\u2019", "'").replace("\u2018", "'")
                response = response.replace("\u201C", '"').replace("\u201D", '"')

                # Replace None with null
                response = response.replace("None", "null")

                # Escape unescaped single quotes inside string values
                def escape_single_quotes(match):
                    s = match.group(0)
                    # Remove the outer single quotes
                    s_content = s[1:-1]
                    # Escape single quotes within the content
                    s_content_escaped = s_content.replace("'", "\\'")
                    return f"'{s_content_escaped}'"

                # Pattern to match single-quoted strings
                pattern = r"'(.*?)'"
                response = re.sub(pattern, escape_single_quotes, response)

                # Now replace single quotes around keys and values with double quotes
                response = re.sub(r"'([^']+)'", r'"\1"', response)
                parsed_data = json.loads(response)
                return parsed_data
            return response
        except Exception as e:
            raise ValueError("Error parsing response content") from e

    async def _generate_query_responses(
        self,
        *,
        text: str,
        num_queries: int,
        query_response_generating_prompty: Optional[str],
        query_response_generating_prompty_options: Dict[str, Any],
        prompty_model_config: Any,
        **kwargs,
    ) -> List[Dict[str, str]]:
        """
        Generates query responses using the specified prompty configuration.

        :keyword text: The input text for generating queries.
        :paramtype text: str
        :keyword num_queries: The number of queries to generate.
        :paramtype num_queries: int
        :keyword query_response_generating_prompty: Path to the query response generating prompty file.
        :paramtype query_response_generating_prompty: Optional[str]
        :keyword query_response_generating_prompty_options: Additional keyword arguments for the query response generating prompty.
        :paramtype query_response_generating_prompty_options: Dict[str, Any]
        :keyword prompty_model_config: The configuration for the prompty model.
        :paramtype prompty_model_config: Any
        :return: A list of query-response dictionaries.
        :rtype: List[Dict[str, str]]
        :raises RuntimeError: If an error occurs during query generation.
        """
        query_flow = self._load_query_generation_flow(
            query_response_generating_prompty=query_response_generating_prompty,  # type: ignore
            prompty_model_config=prompty_model_config,
            query_response_generating_prompty_options=query_response_generating_prompty_options,
        )
        try:
            query_responses = await query_flow(text=text, num_queries=num_queries)
            if isinstance(query_responses, dict):
                keys = list(query_responses.keys())
                return query_responses[keys[0]]
            if isinstance(query_responses, str):
                query_responses = json.loads(query_responses)
                if isinstance(query_responses, dict):
                    if len(query_responses.keys()) == 1:
                        return query_responses[list(query_responses.keys())[0]]
                    return query_responses  # type: ignore
                if isinstance(query_responses, list):
                    return query_responses
            return json.loads(query_responses)
        except Exception as e:
            raise RuntimeError("Error generating query responses") from e

    def _load_query_generation_flow(
        self,
        *,
        query_response_generating_prompty: Optional[Union[str, os.PathLike]],
        prompty_model_config: Dict[str, Any],
        query_response_generating_prompty_options: Dict[str, Any],
    ) -> "AsyncPrompty":
        """
        Loads the flow for generating query responses.

        :keyword query_response_generating_prompty: Path to the query response generating prompty file.
        :paramtype query_response_generating_prompty: Optional[Union[str, os.PathLike]]
        :keyword prompty_model_config: The configuration for the prompty model.
        :paramtype prompty_model_config: Dict[str, Any]
        :keyword query_response_generating_prompty_options: Additional keyword arguments for the flow.
        :paramtype query_response_generating_prompty_options: Dict[str, Any]
        :return: The loaded flow for generating query responses.
        :rtype: AsyncPrompty
        """
        if not query_response_generating_prompty:
            package = "azure.ai.evaluation.simulator._prompty"
            resource_name = "task_query_response.prompty"
            try:
                # Access the resource as a file path
                # pylint: disable=deprecated-method
                with pkg_resources.path(package, resource_name) as prompty_path:
                    prompty_model_config = construct_prompty_model_config(
                        model_config=prompty_model_config,  # type: ignore
                        default_api_version="2024-06-01",
                        user_agent=USER_AGENT,
                    )
                    return AsyncPrompty.load(source=prompty_path, model=prompty_model_config)  # type: ignore
            except FileNotFoundError as e:
                msg = f"Flow path for {resource_name} does not exist in package {package}."
                raise EvaluationException(
                    message=msg,
                    internal_message=msg,
                    error_category=ErrorCategory.FILE_OR_FOLDER_NOT_FOUND,
                    blame=ErrorBlame.USER_ERROR,
                ) from e
        prompty_model_config = construct_prompty_model_config(
            model_config=prompty_model_config,  # type: ignore
            default_api_version="2024-06-01",
            user_agent=USER_AGENT,
        )
        return AsyncPrompty.load(
            source=query_response_generating_prompty,
            model=prompty_model_config,
            **query_response_generating_prompty_options,
        )  # type: ignore

    async def _create_conversations_from_query_responses(
        self,
        *,
        query_responses: List[Dict[str, str]],
        max_conversation_turns: int,
        tasks: List[str],
        user_simulator_prompty: Optional[str],
        user_simulator_prompty_options: Dict[str, Any],
        target: Callable,
        api_call_delay_sec: float,
        text: str,
    ) -> List[JsonLineChatProtocol]:
        """
        Creates full conversations from query-response pairs.

        :keyword query_responses: A list of query-response pairs.
        :paramtype query_responses: List[Dict[str, str]]
        :keyword max_conversation_turns: The maximum number of conversation turns.
        :paramtype max_conversation_turns: int
        :keyword tasks: A list of tasks for the simulation.
        :paramtype tasks: List[str]
        :keyword user_simulator_prompty: Path to the user simulator prompty file.
        :paramtype user_simulator_prompty: Optional[str]
        :keyword user_simulator_prompty_options: Additional keyword arguments for the user simulator prompty.
        :paramtype user_simulator_prompty_options: Dict[str, Any]
        :keyword target: The target function to call for responses.
        :paramtype target: Callable
        :keyword api_call_delay_sec: Delay in seconds between API calls.
        :paramtype api_call_delay_sec: float
        :keyword text: The initial input text for generating query responses.
        :paramtype text: str
        :return: A list of simulated conversations represented as JsonLineChatProtocol objects.
        :rtype: List[JsonLineChatProtocol]
        """
        total_turns = len(query_responses) * max_conversation_turns

        progress_bar = tqdm(
            total=int(total_turns / 2),
            desc="Generating: ",
            ncols=100,
            unit="message",
        )
        all_conversations = []

        for i, query_response_pair in enumerate(query_responses):
            query = query_response_pair["q"]
            response = query_response_pair["r"]
            try:
                task = tasks[i]
            except IndexError:
                task = None

            conversation = await self._complete_conversation(
                conversation_starter=query,
                max_conversation_turns=max_conversation_turns,
                task=task,  # type: ignore
                user_simulator_prompty=user_simulator_prompty,
                user_simulator_prompty_options=user_simulator_prompty_options,
                target=target,
                api_call_delay_sec=api_call_delay_sec,
                progress_bar=progress_bar,
            )
            all_conversations.append(
                JsonLineChatProtocol(
                    {
                        "messages": conversation,
                        "finish_reason": ["stop"],
                        "context": {
                            "task": task,
                            "expected_response": response,
                            "query": query,
                            "original_text": text,
                        },
                        "$schema": "http://azureml/sdk-2-0/ChatConversation.json",
                    }
                )
            )
        progress_bar.close()
        return all_conversations

    async def _complete_conversation(
        self,
        *,
        conversation_starter: str,
        max_conversation_turns: int,
        task: Optional[str],
        user_simulator_prompty: Optional[str],
        user_simulator_prompty_options: Dict[str, Any],
        target: Callable,
        api_call_delay_sec: float,
        progress_bar: tqdm,
    ) -> List[Dict[str, Optional[str]]]:
        """
        Completes a conversation with the target model based on the conversation starter.

        :keyword conversation_starter: The initial message to start the conversation.
        :paramtype conversation_starter: str
        :keyword max_conversation_turns: The maximum number of turns in the conversation.
        :paramtype max_conversation_turns: int
        :keyword task: A string representing the task details.
        :paramtype task: str
        :keyword user_simulator_prompty: Path to the user simulator prompty file.
        :paramtype user_simulator_prompty: Optional[str]
        :keyword user_simulator_prompty_options: Additional keyword arguments for the user simulator prompty.
        :paramtype user_simulator_prompty_options: Dict[str, Any]
        :keyword target: The target function to call for responses.
        :paramtype target: Callable
        :keyword api_call_delay_sec: Delay in seconds between API calls.
        :paramtype api_call_delay_sec: float
        :keyword progress_bar: Progress bar for tracking simulation progress.
        :paramtype progress_bar: tqdm
        :return: A list representing the conversation history with each turn's content.
        :rtype: List[Dict[str, Optional[str]]]
        """
        conversation_history = ConversationHistory()

        while len(conversation_history) < max_conversation_turns:
            user_flow = self._load_user_simulation_flow(
                user_simulator_prompty=user_simulator_prompty,  # type: ignore
                prompty_model_config=self.model_config,  # type: ignore
                user_simulator_prompty_options=user_simulator_prompty_options,
            )
            if len(conversation_history) == 0:
                if task:
                    conversation_starter_from_simulated_user = await user_flow(
                        task=task,
                        conversation_history=[
                            {
                                "role": "assistant",
                                "content": conversation_starter,
                            }
                        ],
                        action="rewrite the assistant's message as you have to accomplish the task by asking the right questions. Make sure the original question is not lost in your rewrite.",
                    )
                else:
                    conversation_starter_from_simulated_user = {
                        "content": conversation_starter,
                    }
            else:
                conversation_starter_from_simulated_user = await user_flow(
                    task=task,
                    conversation_history=conversation_history.to_context_free_list(),
                    action="Your goal is to make sure the task is completed by asking the right questions. Do not ask the same questions again.",
                )
            if isinstance(conversation_starter_from_simulated_user, dict):
                conversation_starter_from_simulated_user = conversation_starter_from_simulated_user["content"]
            user_turn = Turn(role=ConversationRole.USER, content=conversation_starter_from_simulated_user)
            conversation_history.add_to_history(user_turn)
            assistant_response, assistant_context = await self._get_target_response(
                target=target, api_call_delay_sec=api_call_delay_sec, conversation_history=conversation_history
            )
            assistant_turn = Turn(
                role=ConversationRole.ASSISTANT, content=assistant_response, context=assistant_context
            )
            conversation_history.add_to_history(assistant_turn)
            progress_bar.update(1)

            if len(conversation_history) >= max_conversation_turns:
                break

        return conversation_history.to_list()

    async def _get_target_response(
        self, *, target: Callable, api_call_delay_sec: float, conversation_history: ConversationHistory
    ) -> Tuple[str, Optional[str]]:
        """
        Retrieves the response from the target callback based on the current conversation history.

        :keyword target: The target function to call for a response.
        :paramtype target: Callable
        :keyword api_call_delay_sec: Delay in seconds before retrieving the response.
        :paramtype api_call_delay_sec: float
        :keyword conversation_history: The current conversation history.
        :paramtype conversation_history: ConversationHistory
        :return: The content of the response from the target and an optional context.
        :rtype: str, Optional[str]
        """
        response = await target(
            messages={"messages": conversation_history.to_list()},
            stream=False,
            session_state=None,
            context=None,
        )
        await asyncio.sleep(api_call_delay_sec)
        latest_message = response["messages"][-1]
        return latest_message["content"], latest_message.get("context", "")  # type: ignore
