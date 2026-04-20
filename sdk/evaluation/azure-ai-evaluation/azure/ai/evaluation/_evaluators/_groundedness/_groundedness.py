# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import math
import os
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from typing_extensions import overload, override

if os.getenv("AI_EVALS_USE_PF_PROMPTY", "false").lower() == "true":
    from promptflow.core._flow import AsyncPrompty
else:
    from azure.ai.evaluation._legacy.prompty import AsyncPrompty

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from azure.ai.evaluation._evaluators._common._validators import ConversationValidator, ValidatorInterface
from azure.ai.evaluation._evaluators._common._validators._validation_constants import ContentType, MessageRole
from azure.ai.evaluation._model_configurations import Conversation
from ..._common.utils import (
    ErrorBlame,
    ErrorCategory,
    ErrorTarget,
    EvaluationException,
    _extract_text_from_content,
    _get_agent_response,
    _pretty_format_conversation_history,
    construct_prompty_model_config,
    reformat_tool_definitions,
    simplify_messages,
    validate_model_config,
)

try:
    from ..._user_agent import UserAgentSingleton
except ImportError:

    class UserAgentSingleton:
        @property
        def value(self) -> str:
            return "None"


logger = logging.getLogger(__name__)


class EvaluationLevel(str, Enum):
    """Supported evaluation levels for GroundednessEvaluator."""

    CONVERSATION = "conversation"
    TRACE = "trace"


def _resolve_evaluation_level(
    evaluation_level: Optional[Union["EvaluationLevel", str]],
    error_target: ErrorTarget,
) -> Optional[EvaluationLevel]:
    """Validate and normalize the evaluation_level parameter."""

    valid = [level.value for level in EvaluationLevel]
    if evaluation_level is None:
        return None
    if isinstance(evaluation_level, EvaluationLevel):
        return evaluation_level
    if isinstance(evaluation_level, str):
        try:
            return EvaluationLevel(evaluation_level)
        except ValueError as exc:
            raise EvaluationException(
                message=f"Invalid evaluation_level '{evaluation_level}'. Must be one of: {valid}.",
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=error_target,
            ) from exc
    raise EvaluationException(
        message=f"Invalid evaluation_level '{evaluation_level}'. Must be one of: {valid}.",
        blame=ErrorBlame.USER_ERROR,
        category=ErrorCategory.INVALID_VALUE,
        target=error_target,
    )


def _merge_query_response_messages(query: List[dict], response: List[dict]) -> List[dict]:
    """Merge query and response message lists into a single conversation."""

    return [*query, *response]


def _split_messages_at_latest_user(messages: List[dict]) -> Tuple[List[dict], List[dict]]:
    """Split messages into query/response slices at the latest user turn."""

    latest_user_index = max(i for i, message in enumerate(messages) if message.get("role") == MessageRole.USER)
    return messages[: latest_user_index + 1], messages[latest_user_index + 1 :]


def _wrap_string_messages(query: str, response: str) -> Tuple[List[dict], List[dict]]:
    """Wrap string query/response into separate message lists."""

    return (
        [{"role": MessageRole.USER.value, "content": [{"type": ContentType.TEXT.value, "text": query}]}],
        [{"role": MessageRole.ASSISTANT.value, "content": [{"type": ContentType.TEXT.value, "text": response}]}],
    )


def _normalize_openapi_call_types(messages):
    """Normalize openapi_call/openapi_call_output types to tool_call/tool_result."""

    if not isinstance(messages, list):
        return messages
    for msg in messages:
        if not isinstance(msg, dict) or not isinstance(msg.get("content"), list):
            continue
        for item in msg["content"]:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            if item_type == ContentType.OPENAPI_CALL.value:
                item["type"] = ContentType.TOOL_CALL.value
            elif item_type == ContentType.OPENAPI_CALL_OUTPUT.value:
                item["type"] = ContentType.TOOL_RESULT.value
                if ContentType.OPENAPI_CALL_OUTPUT.value in item:
                    item[ContentType.TOOL_RESULT.value] = item.pop(ContentType.OPENAPI_CALL_OUTPUT.value)
    return messages


def _preprocess_groundedness_messages(messages):
    """Apply standard message preprocessing plus openapi normalization."""

    from azure.ai.evaluation._evaluators._common._base_prompty_eval import _preprocess_messages

    messages = _preprocess_messages(messages)
    messages = _normalize_openapi_call_types(messages)
    return messages


def serialize_messages(messages: List[dict]) -> str:
    """Serialize chat messages into a labeled transcript for conversation-level groundedness."""

    if not messages:
        return ""

    all_user_queries: List[Any] = []
    all_agent_responses: List[Any] = []
    cur_user_query: List[Any] = []
    cur_agent_response: List[Any] = []
    system_message = None

    for msg in messages:
        if not isinstance(msg, dict):
            continue

        role = msg.get("role")
        if not role:
            continue

        normalized = msg
        if role == MessageRole.ASSISTANT and isinstance(msg.get("content"), str):
            normalized = {**msg, "content": [{"type": ContentType.TEXT.value, "text": msg["content"]}]}

        if role == MessageRole.SYSTEM:
            content = msg.get("content", "")
            system_message = "\n".join(_extract_text_from_content(content)) if isinstance(content, list) else content
        elif role == MessageRole.USER and "content" in msg:
            if cur_agent_response:
                formatted = _get_agent_response(cur_agent_response, include_tool_messages=True)
                all_agent_responses.append([formatted])
                cur_agent_response = []

            content = msg["content"]
            text_in_msg = [content] if isinstance(content, str) else _extract_text_from_content(content)
            if text_in_msg:
                cur_user_query.append(text_in_msg)
        elif role in (MessageRole.ASSISTANT, MessageRole.TOOL):
            if cur_user_query:
                all_user_queries.append(cur_user_query)
                cur_user_query = []
            cur_agent_response.append(normalized)

    if cur_user_query:
        all_user_queries.append(cur_user_query)
    if cur_agent_response:
        formatted = _get_agent_response(cur_agent_response, include_tool_messages=True)
        all_agent_responses.append([formatted])

    conversation_history: Dict[str, Any] = {
        "user_queries": all_user_queries,
        "agent_responses": all_agent_responses[: len(all_user_queries) - 1] if len(all_user_queries) > 0 else [],
    }
    if system_message:
        conversation_history["system_message"] = system_message

    result = _pretty_format_conversation_history(conversation_history)
    start = max(len(all_user_queries) - 1, 0)
    for i, agent_response in enumerate(all_agent_responses[start:], start=start):
        result += f"Agent turn {i + 1}:\n"
        for msg_text in agent_response:
            if isinstance(msg_text, list):
                for submsg in msg_text:
                    result += "  " + "\n  ".join(submsg.split("\n")) + "\n"
            else:
                result += "  " + "\n  ".join(msg_text.split("\n")) + "\n"
        result += "\n"

    return result.rstrip("\n")


class MessagesOrQueryResponseInputValidator(ConversationValidator):
    """Validator that supports both single-turn query/response and conversation-level messages inputs."""

    @override
    def validate_eval_input(self, eval_input: Dict[str, Any]) -> bool:
        messages = eval_input.get("messages")
        if messages is not None:
            if not isinstance(messages, list):
                raise EvaluationException(
                    message="messages must be provided as a list of message dictionaries.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )
            if len(messages) == 0:
                raise EvaluationException(
                    message="messages list must not be empty.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )

            messages_validation_exception = self._validate_input_messages_list(messages, "messages")
            if messages_validation_exception:
                raise messages_validation_exception

            valid_roles = {role.value for role in MessageRole}
            for index, message in enumerate(messages):
                role = message.get("role")
                if role not in valid_roles:
                    raise EvaluationException(
                        message=f"Invalid role '{role}' at message index {index}. Must be one of: {sorted(valid_roles)}.",
                        blame=ErrorBlame.USER_ERROR,
                        category=ErrorCategory.INVALID_VALUE,
                        target=self.error_target,
                    )

            roles_present = {msg.get("role") for msg in messages if isinstance(msg, dict)}
            if MessageRole.USER not in roles_present:
                raise EvaluationException(
                    message="messages must contain at least one message with role 'user'.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )
            if MessageRole.ASSISTANT not in roles_present:
                raise EvaluationException(
                    message="messages must contain at least one message with role 'assistant'.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )
            if messages[-1]["role"] != MessageRole.ASSISTANT:
                raise EvaluationException(
                    message=f"The last message must have role 'assistant', but found role '{messages[-1]['role']}'.",
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )

            last_content = messages[-1].get("content", "")
            if isinstance(last_content, str):
                has_text = bool(last_content.strip())
            else:
                has_text = any(
                    (
                        isinstance(item, dict)
                        and item.get("type") in (ContentType.TEXT.value, ContentType.OUTPUT_TEXT.value)
                        and isinstance(item.get("text"), str)
                        and item["text"].strip()
                    )
                    or (isinstance(item, str) and item.strip())
                    for item in last_content
                )
            if not has_text:
                raise EvaluationException(
                    message=(
                        "The last assistant message must contain text content, not only tool calls. "
                        "The conversation appears to be mid-execution — provide the agent's final text response."
                    ),
                    blame=ErrorBlame.USER_ERROR,
                    category=ErrorCategory.INVALID_VALUE,
                    target=self.error_target,
                )
            return True

        return super().validate_eval_input(eval_input)


class GroundednessEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """Evaluates groundedness score for a given query (optional), response, and context or a multi-turn conversation,
    including reasoning.

    The groundedness measure assesses the correspondence between claims in an AI-generated answer and the source
    context, making sure that these claims are substantiated by the context. Even if the responses from LLM are
    factually correct, they'll be considered ungrounded if they can't be verified against the provided sources
    (such as your input source or your database). Use the groundedness metric when you need to verify that
    AI-generated responses align with and are validated by the provided context.

    Groundedness scores range from 1 to 5, with 1 being the least grounded and 5 being the most grounded.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :param threshold: The threshold for the groundedness evaluator. Default is 3.
    :type threshold: int
    :param credential: The credential for authenticating to Azure AI service.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword evaluation_level: Force a specific groundedness mode. When omitted, `messages=` uses conversation-level
        scoring while `query`/`response` uses trace-level scoring. Accepted values are `"conversation"` and `"trace"`.
    :paramtype evaluation_level: Optional[Union[EvaluationLevel, str]]
    :keyword is_reasoning_model: If True, the evaluator will use reasoning model configuration (o1/o3 models).
        This will adjust parameters like max_completion_tokens and remove unsupported parameters. Default is False.
    :paramtype is_reasoning_model: bool

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START groundedness_evaluator]
            :end-before: [END groundedness_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a GroundednessEvaluator.

    .. admonition:: Example with Threshold:

        .. literalinclude:: ../samples/evaluation_samples_threshold.py
            :start-after: [START threshold_groundedness_evaluator]
            :end-before: [END threshold_groundedness_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize with threshold and call a GroundednessEvaluator.

    .. admonition:: Example using Azure AI Project URL:

        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START groundedness_evaluator]
            :end-before: [END groundedness_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call GroundednessEvaluator using Azure AI Project URL in the following format
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. note::

        To align with our support of a diverse set of models, an output key without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
        however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    _PROMPTY_FILE_NO_QUERY = "groundedness_without_query.prompty"
    _PROMPTY_FILE_WITH_QUERY = "groundedness_with_query.prompty"
    _MULTI_TURN_PROMPTY_FILE = "groundedness_multi_turn.prompty"
    _RESULT_KEY = "groundedness"
    _OPTIONAL_PARAMS = ["query", "messages", "tool_definitions"]
    _SUPPORTED_TOOLS = ["file_search"]

    _validator: ValidatorInterface
    _validator_with_query: ValidatorInterface
    _validator_messages: ValidatorInterface

    id = "azureai://built-in/evaluators/groundedness"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config, *, threshold=3, credential=None, evaluation_level=None, **kwargs):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE_NO_QUERY)

        self._higher_is_better = True
        self._evaluation_level = _resolve_evaluation_level(evaluation_level, ErrorTarget.GROUNDEDNESS_EVALUATOR)

        self._validator = ConversationValidator(
            error_target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            requires_query=False,
            check_for_unsupported_tools=True,
        )
        self._validator_with_query = ConversationValidator(
            error_target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            requires_query=True,
            check_for_unsupported_tools=True,
        )
        self._validator_messages = MessagesOrQueryResponseInputValidator(
            error_target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            requires_query=False,
            check_for_unsupported_tools=False,
        )

        super().__init__(
            model_config=model_config,
            prompty_file=prompty_path,
            result_key=self._RESULT_KEY,
            threshold=threshold,
            credential=credential,
            _higher_is_better=self._higher_is_better,
            **kwargs,
        )
        self._model_config = model_config
        self._credential = credential
        self.threshold = threshold

        multi_turn_prompty_path = os.path.join(current_dir, self._MULTI_TURN_PROMPTY_FILE)
        prompty_model_config = construct_prompty_model_config(
            validate_model_config(model_config),
            self._DEFAULT_OPEN_API_VERSION,
            UserAgentSingleton().value,
        )
        self._multi_turn_flow = AsyncPrompty.load(
            source=multi_turn_prompty_path,
            model=prompty_model_config,
            token_credential=credential,
            is_reasoning_model=self._is_reasoning_model,
        )

    @overload
    def __call__(
        self,
        *,
        response: str,
        context: str,
        query: Optional[str] = None,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate groundedness for given input of response, context, and optional query."""

    @overload
    def __call__(
        self,
        *,
        query: Union[str, List[dict]],
        response: Union[str, List[dict]],
        tool_definitions: Optional[List[dict]] = None,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate groundedness for agent response with tool calls."""

    @overload
    def __call__(
        self,
        *,
        conversation: Conversation,
    ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]:
        """Evaluate groundedness for a conversation using per-turn aggregation."""

    @overload
    def __call__(
        self,
        *,
        messages: List[dict],
        tool_definitions: Optional[Union[dict, List[dict]]] = None,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate groundedness for a full multi-turn conversation."""

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """Evaluate groundedness for single-turn, agent trace, or full-conversation multi-turn inputs."""

        if kwargs.get("query", None):
            self._ensure_query_prompty_loaded()

        return super().__call__(*args, **kwargs)

    def _ensure_query_prompty_loaded(self):
        """Switch to the query prompty file if not already loaded."""

        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE_WITH_QUERY)

        self._prompty_file = prompty_path
        prompty_model_config = construct_prompty_model_config(
            validate_model_config(self._model_config),
            self._DEFAULT_OPEN_API_VERSION,
            UserAgentSingleton().value,
        )
        self._flow = AsyncPrompty.load(
            source=self._prompty_file,
            model=prompty_model_config,
            token_credential=self._credential,
            is_reasoning_model=self._is_reasoning_model,
        )

    def _has_context(self, eval_input: dict) -> bool:
        """Return True if eval_input contains a non-empty context field."""

        context = eval_input.get("context", None)
        return self._validate_context(context)

    def _validate_context(self, context) -> bool:
        """Validate if the provided context is non-empty and meaningful."""

        if not context:
            return False
        if context == "<>":
            return False
        if isinstance(context, list):
            return any(str(c).strip() for c in context)
        if isinstance(context, str):
            return bool(context.strip())
        return True

    def _should_use_conversation_level(self, eval_input: Dict[str, Any]) -> bool:
        """Determine whether to use conversation-level groundedness evaluation."""

        if self._evaluation_level == EvaluationLevel.CONVERSATION:
            return True
        if self._evaluation_level == EvaluationLevel.TRACE:
            return False
        return eval_input.get("messages") is not None

    def _parse_conversation_prompty_output(self, prompty_output_dict: Dict[str, Any]) -> Dict[str, Union[float, str]]:
        """Parse the multi-turn prompty output into the standard groundedness result shape."""

        llm_output = prompty_output_dict.get("llm_output", prompty_output_dict)
        if not isinstance(llm_output, dict):
            raise EvaluationException(
                message="Evaluator returned invalid output.",
                blame=ErrorBlame.SYSTEM_ERROR,
                category=ErrorCategory.FAILED_EXECUTION,
                target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            )

        score = llm_output.get("score")
        if score is None or not isinstance(score, (int, float)):
            raise EvaluationException(
                message="Evaluator returned invalid output: missing or invalid 'score' field.",
                blame=ErrorBlame.SYSTEM_ERROR,
                category=ErrorCategory.FAILED_EXECUTION,
                target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            )

        score = int(score)
        return {
            self._result_key: score,
            f"{self._result_key}_result": "pass" if score >= self.threshold else "fail",
            f"{self._result_key}_threshold": self.threshold,
            f"{self._result_key}_reason": llm_output.get("reason", ""),
            f"{self._result_key}_details": llm_output.get("properties", {}),
            f"{self._result_key}_prompt_tokens": prompty_output_dict.get("input_token_count", 0),
            f"{self._result_key}_completion_tokens": prompty_output_dict.get("output_token_count", 0),
            f"{self._result_key}_total_tokens": prompty_output_dict.get("total_token_count", 0),
            f"{self._result_key}_finish_reason": prompty_output_dict.get("finish_reason", ""),
            f"{self._result_key}_model": prompty_output_dict.get("model_id", ""),
            f"{self._result_key}_sample_input": prompty_output_dict.get("sample_input", ""),
            f"{self._result_key}_sample_output": prompty_output_dict.get("sample_output", ""),
        }

    async def _do_eval_conversation_level(self, eval_input: Dict[str, Any]) -> Dict[str, Union[float, str]]:
        """Evaluate groundedness for a full conversation-level messages input."""

        messages = _preprocess_groundedness_messages(eval_input["messages"])
        conversation_text = serialize_messages(messages)

        prompty_kwargs: Dict[str, Any] = {"messages": conversation_text}
        tool_definitions = eval_input.get("tool_definitions")
        if tool_definitions:
            prompty_kwargs["tool_definitions"] = reformat_tool_definitions(tool_definitions, logger)

        prompty_output_dict = await self._multi_turn_flow(timeout=self._LLM_CALL_TIMEOUT, **prompty_kwargs)
        return self._parse_conversation_prompty_output(prompty_output_dict)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict[str, Union[float, str]]:
        from azure.ai.evaluation._evaluators._common._base_prompty_eval import _is_intermediate_response

        if self._should_use_conversation_level(eval_input):
            return await self._do_eval_conversation_level(eval_input)

        if _is_intermediate_response(eval_input.get("response")):
            return self._not_applicable_result(
                "Intermediate response. Please provide the agent's final response for evaluation.",
                self._threshold,
            )

        if isinstance(eval_input.get("response"), list):
            eval_input["response"] = _preprocess_groundedness_messages(eval_input["response"])
        if isinstance(eval_input.get("query"), list):
            eval_input["query"] = _preprocess_groundedness_messages(eval_input["query"])

        if eval_input.get("query", None) is None:
            result = await super()._do_eval(eval_input)
            if math.isnan(result.get(self._result_key, 0)):
                raise EvaluationException(
                    message="Evaluator returned invalid output.",
                    blame=ErrorBlame.SYSTEM_ERROR,
                    category=ErrorCategory.FAILED_EXECUTION,
                    target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
                )
            return result

        contains_context = self._has_context(eval_input)
        simplified_query = simplify_messages(eval_input["query"], drop_tool_calls=contains_context)
        simplified_response = simplify_messages(eval_input["response"], drop_tool_calls=False)
        simplified_eval_input = {
            "query": simplified_query,
            "response": simplified_response,
            "context": eval_input["context"],
        }

        result = await super()._do_eval(simplified_eval_input)
        if math.isnan(result.get(self._result_key, 0)):
            raise EvaluationException(
                message="Evaluator returned invalid output.",
                blame=ErrorBlame.SYSTEM_ERROR,
                category=ErrorCategory.FAILED_EXECUTION,
                target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            )
        return result

    async def _real_call(self, **kwargs):
        """The asynchronous call where real end-to-end evaluation logic is performed."""

        if self._evaluation_level == EvaluationLevel.CONVERSATION and not kwargs.get("messages"):
            query = kwargs.get("query")
            response = kwargs.get("response")
            if isinstance(query, str) and isinstance(response, str) and query and response:
                query, response = _wrap_string_messages(query, response)
            if isinstance(query, list) and isinstance(response, list):
                kwargs["messages"] = _merge_query_response_messages(query, response)
        elif self._evaluation_level == EvaluationLevel.TRACE and kwargs.get("messages"):
            messages = kwargs["messages"]
            if any(isinstance(message, dict) and message.get("role") == MessageRole.USER for message in messages):
                query_messages, response_messages = _split_messages_at_latest_user(messages)
                kwargs["query"] = query_messages
                kwargs["response"] = response_messages
                kwargs.pop("messages", None)

        if kwargs.get("messages"):
            self._validator_messages.validate_eval_input(kwargs)
        elif kwargs.get("query"):
            self._validator_with_query.validate_eval_input(kwargs)
        else:
            self._validator.validate_eval_input(kwargs)

        try:
            return await super()._real_call(**kwargs)
        except EvaluationException as ex:
            if ex.category == ErrorCategory.NOT_APPLICABLE:
                return self._not_applicable_result(ex.message, self.threshold, has_details=True)
            raise ex

    def _is_single_entry(self, value):
        """Determine if the input value represents a single entry."""

        if isinstance(value, str):
            return True
        if isinstance(value, list) and len(value) == 1:
            return True
        return False

    def _convert_kwargs_to_eval_input(self, **kwargs):
        if kwargs.get("messages") is not None:
            return super()._convert_kwargs_to_eval_input(**kwargs)

        if kwargs.get("context") or kwargs.get("conversation"):
            return super()._convert_kwargs_to_eval_input(**kwargs)

        query = kwargs.get("query")
        response = kwargs.get("response")
        tool_definitions = kwargs.get("tool_definitions")

        if query and self._prompty_file != self._PROMPTY_FILE_WITH_QUERY:
            self._ensure_query_prompty_loaded()

        if (not query) or (not response):
            msg = (
                f"{type(self).__name__}: Either 'conversation' or individual inputs must be provided. "
                "For Agent groundedness 'query' and 'response' are required."
            )
            raise EvaluationException(
                message=msg,
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            )

        if response and isinstance(response, str):
            return super()._convert_kwargs_to_eval_input(query=query, response=response, context=response)

        context = self._get_context_from_agent_response(response, tool_definitions)

        if not self._validate_context(context) and self._is_single_entry(response) and self._is_single_entry(query):
            msg = (
                f"{type(self).__name__}: No valid context provided or could be extracted from the query or response. "
                "Please either provide valid context or pass the full items list for 'response' and 'query' "
                "to extract context from tool calls."
            )
            raise EvaluationException(
                message=msg,
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.NOT_APPLICABLE,
                target=ErrorTarget.GROUNDEDNESS_EVALUATOR,
            )

        filtered_response = self._filter_file_search_results(response) if self._validate_context(context) else response
        return super()._convert_kwargs_to_eval_input(response=filtered_response, context=context, query=query)

    def _filter_file_search_results(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out file_search tool results from the messages."""

        file_search_ids = self._get_file_search_tool_call_ids(messages)
        return [
            msg for msg in messages if not (msg.get("role") == "tool" and msg.get("tool_call_id") in file_search_ids)
        ]

    def _get_context_from_agent_response(self, response, tool_definitions):
        """Extract context text from file_search tool results in the agent response."""

        NO_CONTEXT = "<>"
        context = ""
        try:
            logger.debug("Extracting context from response")
            tool_calls = self._parse_tools_from_response(response=response)
            logger.debug(f"Tool Calls parsed successfully: {tool_calls}")

            if not tool_calls:
                return NO_CONTEXT

            context_lines = []
            for tool_call in tool_calls:
                if not isinstance(tool_call, dict) or tool_call.get("type") != "tool_call":
                    continue

                tool_name = tool_call.get("name")
                if tool_name != "file_search":
                    continue

                for result in tool_call.get("tool_result", []):
                    results = result if isinstance(result, list) else [result]
                    for tool_result in results:
                        file_name = tool_result.get("file_name", "Unknown file name")
                        for content in tool_result.get("content", []):
                            text = content.get("text")
                            if text:
                                context_lines.append(f"{file_name}:\n- {text}---\n\n")

            context = "\n".join(context_lines) if len(context_lines) > 0 else None
        except Exception as ex:
            logger.debug(f"Error extracting context from agent response : {str(ex)}")
            context = None

        return context if context else NO_CONTEXT

    def _get_file_search_tool_call_ids(self, query_or_response):
        """Return a list of tool_call_ids for file search tool calls."""

        tool_calls = self._parse_tools_from_response(query_or_response)
        return [tool_call.get("tool_call_id") for tool_call in tool_calls if tool_call.get("name") == "file_search"]
