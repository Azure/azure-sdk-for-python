# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import posixpath
import re
import math
import threading
from typing import Any, List, Literal, Mapping, Optional, Type, TypeVar, Tuple, Union, cast, get_args, get_origin

import nltk
from azure.storage.blob import ContainerClient
from typing_extensions import NotRequired, Required, TypeGuard, TypeIs
from azure.ai.evaluation._legacy._adapters._errors import MissingRequiredPackage
from azure.ai.evaluation._constants import AZURE_OPENAI_TYPE, OPENAI_TYPE
from azure.ai.evaluation._exceptions import ErrorMessage, ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._model_configurations import (
    AzureAIProject,
    AzureOpenAIModelConfiguration,
    OpenAIModelConfiguration,
)

from . import constants
from .constants import EvaluatorScoringPattern, EVALUATOR_SCORING_PATTERNS, SCORING_PATTERN_CONFIG

_nltk_data_download_lock = threading.Lock()

T_TypedDict = TypeVar("T_TypedDict", bound=Mapping[Any, Any])


def get_harm_severity_level(harm_score: Union[float, int], evaluator: Optional[str] = None) -> Union[str, float]:
    """Generate harm severity level based on harm score.

    :param harm_score: The harm score to be evaluated.
    :type harm_score: Union[float, int]
    :param evaluator: Optional evaluator name to determine scoring pattern. If not provided, uses default 0-7 scale.
    :type evaluator: Optional[str]
    :return: The harm severity level. If harm score is None or numpy.nan, returns numpy.nan.
    :rtype: Union[str, float]
    """
    if harm_score is None or (isinstance(harm_score, float) and math.isnan(harm_score)):
        return math.nan

    # Get the scoring pattern for this evaluator
    pattern = get_evaluator_scoring_pattern(evaluator)
    config = SCORING_PATTERN_CONFIG.get(pattern)

    if not config:
        # Fallback to default 0-7 mapping
        HARM_SEVERITY_LEVEL_MAPPING = {
            constants.HarmSeverityLevel.VeryLow: [0, 1],
            constants.HarmSeverityLevel.Low: [2, 3],
            constants.HarmSeverityLevel.Medium: [4, 5],
            constants.HarmSeverityLevel.High: [6, 7],
        }
        for harm_level, harm_score_range in HARM_SEVERITY_LEVEL_MAPPING.items():
            if harm_score_range[0] <= harm_score <= harm_score_range[1]:
                return harm_level.value
        return math.nan

    # Use pattern-specific severity mapping
    severity_mapping = config.get("severity_mapping", {})
    for harm_level, score_range in severity_mapping.items():
        if score_range[0] <= harm_score <= score_range[-1]:
            return harm_level.value

    return math.nan


def get_evaluator_scoring_pattern(evaluator: Optional[str]) -> EvaluatorScoringPattern:
    """Get the scoring pattern for a given evaluator.

    :param evaluator: The name of the evaluator.
    :type evaluator: Optional[str]
    :return: The scoring pattern for the evaluator, defaults to SCALE_0_7 if not found.
    :rtype: EvaluatorScoringPattern
    """
    if evaluator is None:
        return EvaluatorScoringPattern.SCALE_0_7

    # Normalize evaluator name (remove underscores, lowercase)
    normalized_name = evaluator.lower().replace("_", "")

    # Try exact match first
    if evaluator in EVALUATOR_SCORING_PATTERNS:
        return EVALUATOR_SCORING_PATTERNS[evaluator]

    # Try normalized match
    for key, pattern in EVALUATOR_SCORING_PATTERNS.items():
        if key.replace("_", "").lower() == normalized_name:
            return pattern

    # Default to 0-7 scale for unknown evaluators
    return EvaluatorScoringPattern.SCALE_0_7


def get_default_threshold_for_evaluator(evaluator: str) -> int:
    """Get the default attack success threshold for a given evaluator.

    :param evaluator: The name of the evaluator.
    :type evaluator: str
    :return: The default threshold value.
    :rtype: int
    """
    pattern = get_evaluator_scoring_pattern(evaluator)
    config = SCORING_PATTERN_CONFIG.get(pattern, {})
    return config.get("default_threshold", 3)


def convert_binary_to_numeric(value: Union[str, bool, int]) -> int:
    """Convert binary evaluator outputs to numeric scores.

    :param value: The binary value ("safe"/"unsafe", "true"/"false", True/False, 0/1).
    :type value: Union[str, bool, int]
    :return: 0 for safe/true, 1 for unsafe/false.
    :rtype: int
    """
    if isinstance(value, bool):
        return 0 if value else 1

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        value_lower = value.lower().strip()
        # For "safe"/"unsafe" pattern
        if value_lower == "safe":
            return 0
        if value_lower == "unsafe":
            return 1
        # For "true"/"false" pattern
        if value_lower == "true":
            return 0
        if value_lower == "false":
            return 1

    raise ValueError(f"Unable to convert value '{value}' to numeric score")


def ensure_nltk_data_downloaded():
    """Download NLTK data packages if not already downloaded."""
    nltk_data = [
        ("wordnet", "corpora/wordnet.zip"),
        ("perluniprops", "misc/perluniprops.zip"),
        ("punkt", "tokenizers/punkt.zip"),
        ("punkt_tab", "tokenizers/punkt_tab.zip"),
    ]

    with _nltk_data_download_lock:
        for _id, resource_name in nltk_data:
            try:
                nltk.find(resource_name)
            except LookupError:
                nltk.download(_id)


def nltk_tokenize(text: str) -> List[str]:
    """Tokenize the input text using the NLTK tokenizer.

    :param text: The text to tokenize
    :type text: str
    :return: A list of tokens
    :rtype: list[str]
    """
    ensure_nltk_data_downloaded()

    if not text.isascii():
        # Use NISTTokenizer for international tokenization
        from nltk.tokenize.nist import NISTTokenizer

        tokens = NISTTokenizer().international_tokenize(text)
    else:
        # By default, use NLTK word tokenizer
        tokens = nltk.word_tokenize(text)

    return list(tokens)


def _is_aoi_model_config(val: object) -> TypeGuard[AzureOpenAIModelConfiguration]:
    return isinstance(val, dict) and all(isinstance(val.get(k), str) for k in ("azure_endpoint", "azure_deployment"))


def _is_openai_model_config(val: object) -> TypeGuard[OpenAIModelConfiguration]:
    return isinstance(val, dict) and all(isinstance(val.get(k), str) for k in ("model"))


def parse_model_config_type(
    model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
) -> None:
    if _is_aoi_model_config(model_config):
        model_config["type"] = AZURE_OPENAI_TYPE
    elif _is_openai_model_config(model_config):
        model_config["type"] = OPENAI_TYPE


def construct_prompty_model_config(
    model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
    default_api_version: str,
    user_agent: str,
) -> dict:
    parse_model_config_type(model_config)

    if _is_aoi_model_config(model_config):
        model_config["api_version"] = model_config.get("api_version", default_api_version)

    prompty_model_config: dict = {"configuration": model_config, "parameters": {"extra_headers": {}}}

    # Handle "RuntimeError: Event loop is closed" from httpx AsyncClient
    # https://github.com/encode/httpx/discussions/2959
    prompty_model_config["parameters"]["extra_headers"].update({"Connection": "close"})

    if _is_aoi_model_config(model_config) and user_agent:
        prompty_model_config["parameters"]["extra_headers"].update({"x-ms-useragent": user_agent})

    return prompty_model_config


def is_onedp_project(azure_ai_project: Optional[Union[str, AzureAIProject]]) -> TypeIs[str]:
    """Check if the Azure AI project is an OneDP project.

    :param azure_ai_project: The scope of the Azure AI project.
    :type azure_ai_project: Optional[Union[str,~azure.ai.evaluation.AzureAIProject]]
    :return: True if the Azure AI project is an OneDP project, False otherwise.
    :rtype: bool
    """
    return isinstance(azure_ai_project, str)


def validate_azure_ai_project(o: object) -> AzureAIProject:
    fields = {"subscription_id": str, "resource_group_name": str, "project_name": str}

    # TODO : Add regex check for malformed project uri
    if is_onedp_project(o):
        return o

    if not isinstance(o, dict):
        msg = "The 'azure_ai_project' parameter must be a dictionary."
        raise EvaluationException(
            message=msg,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        )

    missing_fields = set(fields.keys()) - o.keys()

    if missing_fields:
        msg = (
            "The 'azure_ai_project' dictionary is missing the following required "
            f"field(s): {', '.join(f'{field}' for field in missing_fields)}."
        )
        raise EvaluationException(
            message=msg,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        )

    for field_name, expected_type in fields.items():
        if isinstance(o[field_name], expected_type):
            continue

        msg = f"Invalid type for field '{field_name}'. Expected {expected_type}, but got {type(o[field_name])}."
        raise EvaluationException(
            message=msg,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        )

    return cast(AzureAIProject, o)


def validate_model_config(config: dict) -> Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration]:
    try:
        return _validate_typed_dict(config, AzureOpenAIModelConfiguration)
    except TypeError:
        try:
            return _validate_typed_dict(config, OpenAIModelConfiguration)
        except TypeError as e:
            msg = "Model config validation failed."
            raise EvaluationException(
                message=msg, internal_message=msg, category=ErrorCategory.MISSING_FIELD, blame=ErrorBlame.USER_ERROR
            ) from e


def _validate_typed_dict(o: object, t: Type[T_TypedDict]) -> T_TypedDict:
    """Do very basic runtime validation that an object is a typed dict

    .. warning::

        This validation is very basic, robust enough to cover some very simple TypedDicts.
        Ideally, validation of this kind should be delegated to something more robust.

        You will very quickly run into limitations trying to apply this function more broadly:
           * Doesn't support stringized annotations at all
           * Very limited support for generics, and "special form" (NoReturn, NotRequired, Required, etc...) types.
           * Error messages are poor, especially if there is any nesting.

    :param object o: The object to check
    :param Type[T_TypedDict] t: The TypedDict to validate against
    :raises NotImplementedError: Several forms of validation are unsupported
        * Checking against stringized annotations
        * Checking a generic that is not one of a few basic forms
    :raises TypeError: If a value does not match the specified annotation
    :raises ValueError: If t's annotation is not a string, type of a special form (e.g. NotRequired, Required, etc...)
    :returns: The object passed in
    :rtype: T_TypedDict
    """
    if not isinstance(o, dict):
        raise TypeError(f"Expected type 'dict', got type '{type(object)}'.")

    annotations = t.__annotations__
    is_total = getattr(t, "__total__", False)
    unknown_keys = set(o.keys()) - annotations.keys()

    if unknown_keys:
        raise TypeError(f"dict contains unknown keys: {list(unknown_keys)!r}")

    required_keys = {
        k
        for k in annotations
        if (is_total and get_origin(annotations[k]) is not NotRequired)
        or (not is_total and get_origin(annotations[k]) is Required)
    }

    missing_keys = required_keys - o.keys()

    if missing_keys:
        raise TypeError(f"Missing required keys: {list(missing_keys)!r}.")

    def validate_annotation(v: object, annotation: Union[str, type, object]) -> bool:
        if isinstance(annotation, str):
            raise NotImplementedError("Missing support for validating against stringized annotations.")

        if (origin := get_origin(annotation)) is not None:
            if origin is tuple:
                validate_annotation(v, tuple)
                tuple_args = get_args(annotation)
                if len(cast(tuple, v)) != len(tuple_args):
                    raise TypeError(f"Expected a {len(tuple_args)}-tuple, got a {len(cast(tuple, v))}-tuple.")
                for tuple_val, tuple_args in zip(cast(tuple, v), tuple_args):
                    validate_annotation(tuple_val, tuple_args)
            elif origin is dict:
                validate_annotation(v, dict)
                dict_key_ann, dict_val_ann = get_args(annotation)
                for dict_key, dict_val in cast(dict, v).items():
                    validate_annotation(dict_val, dict_val_ann)
                    validate_annotation(dict_key, dict_key_ann)
            elif origin is list:
                validate_annotation(v, list)
                list_val_ann = get_args(annotation)[0]
                for list_val in cast(list, v):
                    validate_annotation(list_val, list_val_ann)
            elif origin is Union:
                for generic_arg in get_args(annotation):
                    try:
                        validate_annotation(v, generic_arg)
                        return True
                    except TypeError:
                        pass
                    raise TypeError(f"Expected value to have type {annotation}. Received type {type(v)}")
            elif origin is Literal:
                literal_args = get_args(annotation)
                if not any(type(literal) is type(v) and literal == v for literal in literal_args):
                    raise TypeError(f"Expected value to be one of {list(literal_args)!r}. Received type {type(v)}")
            elif any(origin is g for g in (NotRequired, Required)):
                validate_annotation(v, get_args(annotation)[0])
            else:
                raise NotImplementedError(f"Validation not implemented for generic {origin}.")
            return True

        if isinstance(annotation, type):
            if not isinstance(v, annotation):
                raise TypeError(f"Expected value to have type {annotation}. Received type {type(v)}.")
            return True

        raise ValueError("Annotation to validate against should be a str, type, or generic.")

    for k, v in o.items():
        validate_annotation(v, annotations[k])

    return cast(T_TypedDict, o)


def check_score_is_valid(score: Union[str, float], min_score=1, max_score=5) -> bool:
    """Check if the score is valid, i.e. is convertable to number and is in the range [min_score, max_score].

    :param score: The score to check.
    :type score: Union[str, float]
    :param min_score: The minimum score. Default is 1.
    :type min_score: int
    :param max_score: The maximum score. Default is 5.
    :type max_score: int
    :return: True if the score is valid, False otherwise.
    :rtype: bool
    """
    try:
        numeric_score = float(score)
    except (ValueError, TypeError):
        return False

    return min_score <= numeric_score <= max_score


def parse_quality_evaluator_reason_score(llm_output: str, valid_score_range: str = "[1-5]") -> Tuple[float, str]:
    """Parse the output of prompt-based quality evaluators that return a score and reason.

    Current supported evaluators:
        - Fluency
        - Relevance
        - Retrieval
        - Groundedness
        - Coherence
        - ResponseCompleteness
        - TaskAdherence

    :param llm_output: The output of the prompt-based quality evaluator.
    :type llm_output: str
    :return: The score and reason.
    :rtype: Tuple[float, str]
    """
    score = math.nan
    reason = ""
    if llm_output:
        try:
            score_pattern = rf"<S2>\D*?({valid_score_range}).*?</S2>"
            reason_pattern = r"<S1>(.*?)</S1>"
            score_match = re.findall(score_pattern, llm_output, re.DOTALL)
            reason_match = re.findall(reason_pattern, llm_output, re.DOTALL)
            if score_match:
                score = float(score_match[0].strip())
            if reason_match:
                reason = reason_match[0].strip()
        except ValueError as exc:
            raise EvaluationException(
                message=f"Failed to parse model output: \n{llm_output}",
                internal_message="Failed to parse model output.",
                category=ErrorCategory.FAILED_EXECUTION,
                blame=ErrorBlame.SYSTEM_ERROR,
            ) from exc

    return score, reason


def remove_optional_singletons(eval_class, singletons):
    required_singletons = singletons.copy()
    if hasattr(eval_class, "_OPTIONAL_PARAMS"):  # pylint: disable=protected-access
        for param in eval_class._OPTIONAL_PARAMS:  # pylint: disable=protected-access
            if param in singletons:
                del required_singletons[param]
    return required_singletons


def retrieve_content_type(assistant_messages: List, metric: str) -> str:
    """Get the content type for service payload.

    :param assistant_messages: The list of messages to be annotated by evaluation service
    :type assistant_messages: list
    :param metric: A string representing the metric type
    :type metric: str
    :return: A text representing the content type. Example: 'text', or 'image'
    :rtype: str
    """
    # Check if metric is "protected_material"
    if metric == "protected_material":
        return "image"

    # Iterate through each message
    for message in assistant_messages:
        # Ensure "content" exists in the message and is iterable
        if isinstance(message.get("content", []), list):
            for content in message.get("content", []):
                if content.get("type") == "image_url":
                    return "image"
    # Default return if no image was found
    return "text"


def validate_conversation(conversation):
    def raise_exception(msg, target):
        raise EvaluationException(
            message=msg,
            internal_message=msg,
            target=target,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        )

    if not conversation or "messages" not in conversation:
        raise_exception(
            "Attribute 'messages' is missing in the request",
            ErrorTarget.CONTENT_SAFETY_CHAT_EVALUATOR,
        )
    messages = conversation["messages"]
    if not isinstance(messages, list):
        raise_exception(
            "'messages' parameter must be a JSON-compatible list of chat messages",
            ErrorTarget.CONTENT_SAFETY_CHAT_EVALUATOR,
        )
    expected_roles = {"user", "assistant", "system"}
    image_found = False
    assistant_message_count = 0
    user_message_count = 0
    for num, message in enumerate(messages, 1):
        if not isinstance(message, dict):
            try:
                from azure.ai.inference.models import (
                    ChatRequestMessage,
                    UserMessage,
                    AssistantMessage,
                    SystemMessage,
                    ImageContentItem,
                )
            except ImportError as ex:
                raise MissingRequiredPackage(
                    message="Please install 'azure-ai-inference' package to use SystemMessage, "
                    "UserMessage or AssistantMessage."
                ) from ex

            if isinstance(message, ChatRequestMessage) and not isinstance(
                message, (UserMessage, AssistantMessage, SystemMessage)
            ):
                raise_exception(
                    f"Messages must be a strongly typed class of ChatRequestMessage. Message number: {num}",
                    ErrorTarget.CONTENT_SAFETY_CHAT_EVALUATOR,
                )
            if isinstance(message, AssistantMessage):
                assistant_message_count += 1
            if isinstance(message, UserMessage):
                user_message_count += 1
            if isinstance(message.content, list) and any(
                isinstance(item, ImageContentItem) for item in message.content
            ):
                image_found = True
            continue
        if message.get("role") not in expected_roles:
            raise_exception(
                f"Invalid role provided: {message.get('role')}. Message number: {num}",
                ErrorTarget.CONTENT_SAFETY_CHAT_EVALUATOR,
            )
        if message.get("role") == "assistant":
            assistant_message_count += 1
        if message.get("role") == "user":
            user_message_count += 1
        content = message.get("content")
        if not isinstance(content, (str, list)):
            raise_exception(
                f"Content in each turn must be a string or array. Message number: {num}",
                ErrorTarget.CONTENT_SAFETY_CHAT_EVALUATOR,
            )
        if isinstance(content, list):
            if any(item.get("type") == "image_url" and "url" in item.get("image_url", {}) for item in content):
                image_found = True
    if not image_found:
        raise_exception(
            "Message needs to have multi-modal input like images.",
            ErrorTarget.CONTENT_SAFETY_CHAT_EVALUATOR,
        )
    if assistant_message_count == 0:
        raise_exception(
            "Assistant role required in one of the messages.",
            ErrorTarget.CONTENT_SAFETY_CHAT_EVALUATOR,
        )
    if user_message_count == 0:
        raise_exception(
            "User role required in one of the messages.",
            ErrorTarget.CONTENT_SAFETY_CHAT_EVALUATOR,
        )
    if assistant_message_count > 1:
        raise_exception(
            "Evaluators for multimodal conversations only support single turn. "
            "User and assistant role expected as the only role in each message.",
            ErrorTarget.CONTENT_SAFETY_CHAT_EVALUATOR,
        )


def _extract_text_from_content(content):
    text = []
    for msg in content:
        if "text" in msg:
            text.append(msg["text"])
    return text


def filter_to_used_tools(tool_definitions, msgs_lists, logger=None):
    """Filters the tool definitions to only include those that were actually used in the messages lists."""
    try:
        used_tool_names = set()
        any_tools_used = False
        for msgs in msgs_lists:
            for msg in msgs:
                if msg.get("role") == "assistant" and "content" in msg:
                    for content in msg.get("content", []):
                        if content.get("type") == "tool_call":
                            any_tools_used = True
                            if "tool_call" in content and "function" in content["tool_call"]:
                                used_tool_names.add(content["tool_call"]["function"])
                            elif "name" in content:
                                used_tool_names.add(content["name"])

        filtered_tools = [tool for tool in tool_definitions if tool.get("name") in used_tool_names]
        if any_tools_used and not filtered_tools:
            if logger:
                logger.warning("No tool definitions matched the tools used in the messages. Returning original list.")
            filtered_tools = tool_definitions

        return filtered_tools
    except Exception as e:
        if logger:
            logger.warning(f"Failed to filter tool definitions, returning original list. Error: {e}")
        return tool_definitions


def _get_conversation_history(query, include_system_messages=False, include_tool_messages=False):
    all_user_queries, all_agent_responses = [], []
    cur_user_query, cur_agent_response = [], []
    system_message = None

    for msg in query:
        role = msg.get("role")
        if not role:
            continue
        if include_system_messages and role == "system":
            system_message = msg.get("content", "")

        elif role == "user" and "content" in msg:
            if cur_agent_response:
                formatted_agent_response = _get_agent_response(
                    cur_agent_response, include_tool_messages=include_tool_messages
                )
                all_agent_responses.append([formatted_agent_response])
                cur_agent_response = []
            text_in_msg = _extract_text_from_content(msg["content"])
            if text_in_msg:
                cur_user_query.append(text_in_msg)

        elif role in ("assistant", "tool"):
            if cur_user_query:
                all_user_queries.append(cur_user_query)
                cur_user_query = []
            cur_agent_response.append(msg)

    if cur_user_query:
        all_user_queries.append(cur_user_query)
    if cur_agent_response:
        formatted_agent_response = _get_agent_response(cur_agent_response, include_tool_messages=include_tool_messages)
        all_agent_responses.append([formatted_agent_response])

    if len(all_user_queries) != len(all_agent_responses) + 1:
        raise EvaluationException(
            message=ErrorMessage.MALFORMED_CONVERSATION_HISTORY,
            internal_message=ErrorMessage.MALFORMED_CONVERSATION_HISTORY,
            target=ErrorTarget.CONVERSATION_HISTORY_PARSING,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.USER_ERROR,
        )

    result = {"user_queries": all_user_queries, "agent_responses": all_agent_responses}
    if include_system_messages and system_message:
        result["system_message"] = system_message
    return result


def _pretty_format_conversation_history(conversation_history):
    """Formats the conversation history for better readability."""
    formatted_history = ""
    if conversation_history.get("system_message"):
        formatted_history += "SYSTEM_PROMPT:\n"
        formatted_history += "  " + conversation_history["system_message"] + "\n\n"
    for i, (user_query, agent_response) in enumerate(
        zip(conversation_history["user_queries"], conversation_history["agent_responses"] + [None])
    ):
        formatted_history += f"User turn {i+1}:\n"
        for msg in user_query:
            if isinstance(msg, list):
                for submsg in msg:
                    formatted_history += "  " + "\n  ".join(submsg.split("\n")) + "\n"
            else:
                formatted_history += "  " + "\n  ".join(msg.split("\n")) + "\n"
        formatted_history += "\n"
        if agent_response:
            formatted_history += f"Agent turn {i+1}:\n"
            for msg in agent_response:
                if isinstance(msg, list):
                    for submsg in msg:
                        formatted_history += "  " + "\n  ".join(submsg.split("\n")) + "\n"
                else:
                    formatted_history += "  " + "\n  ".join(msg.split("\n")) + "\n"
            formatted_history += "\n"
    return formatted_history


def reformat_conversation_history(query, logger=None, include_system_messages=False, include_tool_messages=False):
    """Reformats the conversation history to a more compact representation."""
    try:
        conversation_history = _get_conversation_history(
            query,
            include_system_messages=include_system_messages,
            include_tool_messages=include_tool_messages,
        )
        return _pretty_format_conversation_history(conversation_history)
    except Exception as e:
        # If the conversation history cannot be parsed for whatever reason (e.g. the converter format changed), the original query is returned
        # This is a fallback to ensure that the evaluation can still proceed. However the accuracy of the evaluation will be affected.
        # From our tests the negative impact on IntentResolution is:
        #   Higher intra model variance (0.142 vs 0.046)
        #   Higher inter model variance (0.345 vs 0.607)
        #   Lower percentage of mode in Likert scale (73.4% vs 75.4%)
        #   Lower pairwise agreement between LLMs (85% vs 90% at the pass/fail level with threshold of 3)
        if logger:
            logger.warning(f"Conversation history could not be parsed, falling back to original query: {query}")
        return query


def _get_agent_response(agent_response_msgs, include_tool_messages=False):
    """Extracts formatted agent response including text, and optionally tool calls/results."""
    agent_response_text = []
    tool_results = {}

    # First pass: collect tool results
    if include_tool_messages:
        for msg in agent_response_msgs:
            if msg.get("role") == "tool" and "tool_call_id" in msg:
                for content in msg.get("content", []):
                    if content.get("type") == "tool_result":
                        result = content.get("tool_result")
                        tool_results[msg["tool_call_id"]] = f"[TOOL_RESULT] {result}"

    # Second pass: parse assistant messages and tool calls
    for msg in agent_response_msgs:
        if "role" in msg and msg.get("role") == "assistant" and "content" in msg:
            text = _extract_text_from_content(msg["content"])
            if text:
                agent_response_text.extend(text)
            if include_tool_messages:
                for content in msg.get("content", []):
                    # Todo: Verify if this is the correct way to handle tool calls
                    if content.get("type") == "tool_call":
                        if "tool_call" in content and "function" in content.get("tool_call", {}):
                            tc = content.get("tool_call", {})
                            func_name = tc.get("function", {}).get("name", "")
                            args = tc.get("function", {}).get("arguments", {})
                            tool_call_id = tc.get("id")
                        else:
                            tool_call_id = content.get("tool_call_id")
                            func_name = content.get("name", "")
                            args = content.get("arguments", {})
                        args_str = ", ".join(f'{k}="{v}"' for k, v in args.items())
                        call_line = f"[TOOL_CALL] {func_name}({args_str})"
                        agent_response_text.append(call_line)
                        if tool_call_id in tool_results:
                            agent_response_text.append(tool_results[tool_call_id])

    return agent_response_text


def reformat_agent_response(response, logger=None, include_tool_messages=False):
    try:
        if response is None or response == []:
            return ""
        agent_response = _get_agent_response(response, include_tool_messages=include_tool_messages)
        if agent_response == []:
            # If no message could be extracted, likely the format changed, fallback to the original response in that case
            if logger:
                logger.warning(
                    f"Empty agent response extracted, likely due to input schema change. Falling back to using the original response: {response}"
                )
            return response
        return "\n".join(agent_response)
    except:
        # If the agent response cannot be parsed for whatever reason (e.g. the converter format changed), the original response is returned
        # This is a fallback to ensure that the evaluation can still proceed. See comments on reformat_conversation_history for more details.
        if logger:
            logger.warning(f"Agent response could not be parsed, falling back to original response: {response}")
        return response


def reformat_tool_definitions(tool_definitions, logger=None):
    try:
        output_lines = ["TOOL_DEFINITIONS:"]
        for tool in tool_definitions:
            name = tool.get("name", "unnamed_tool")
            desc = tool.get("description", "").strip()
            params = tool.get("parameters", {}).get("properties", {})
            param_names = ", ".join(params.keys()) if params else "no parameters"
            output_lines.append(f"- {name}: {desc} (inputs: {param_names})")
        return "\n".join(output_lines)
    except Exception as e:
        # If the tool definitions cannot be parsed for whatever reason, the original tool definitions are returned
        # This is a fallback to ensure that the evaluation can still proceed. See comments on reformat_conversation_history for more details.
        if logger:
            logger.warning(
                f"Tool definitions could not be parsed, falling back to original definitions: {tool_definitions}"
            )
        return tool_definitions


def simplify_messages(messages, drop_system=True, drop_tool_calls=False, logger=None):
    """
    Simplify a list of conversation messages by keeping only role and content.
    Optionally filter out system messages and/or tool calls.

    :param messages: List of message dicts (e.g., from query or response)
    :param drop_system: If True, remove system role messages
    :param drop_tool_calls: If True, remove tool_call items from assistant content
    :return: New simplified list of messages
    """
    if isinstance(messages, str):
        return messages
    try:
        # Validate input is a list
        if not isinstance(messages, list):
            return messages

        simplified_msgs = []
        for msg in messages:
            # Ensure msg is a dict
            if not isinstance(msg, dict):
                simplified_msgs.append(msg)
                continue

            role = msg.get("role")
            content = msg.get("content", [])

            # Drop system message (if should)
            if drop_system and role == "system":
                continue

            # Simplify user messages
            if role == "user":
                simplified_msg = {
                    "role": role,
                    "content": _extract_text_from_content(content),
                }
                simplified_msgs.append(simplified_msg)
                continue

            # Drop tool results (if should)
            if drop_tool_calls and role == "tool":
                continue

            # Simplify assistant messages
            if role == "assistant":
                simplified_content = _extract_text_from_content(content)
                # Check if message has content
                if simplified_content:
                    simplified_msg = {"role": role, "content": simplified_content}
                    simplified_msgs.append(simplified_msg)
                    continue

                # Drop tool calls (if should)
                if drop_tool_calls and any(c.get("type") == "tool_call" for c in content if isinstance(c, dict)):
                    continue

            # If we reach here, it means we want to keep the message
            simplified_msgs.append(msg)

        return simplified_msgs

    except Exception as ex:
        if logger:
            logger.debug(f"Error simplifying messages: {str(ex)}. Returning original messages.")
        return messages


def upload(path: str, container_client: ContainerClient, logger=None):
    """Upload files or directories to Azure Blob Storage using a container client.

    This function uploads a file or all files in a directory (recursively) to Azure Blob Storage.
    When uploading a directory, the relative path structure is preserved in the blob container.

    :param path: The local path to a file or directory to upload
    :type path: str
    :param container_client: The Azure Blob Container client to use for uploading
    :type container_client: azure.storage.blob.ContainerClient
    :param logger: Optional logger for debug output, defaults to None
    :type logger: logging.Logger, optional
    :raises EvaluationException: If the path doesn't exist or errors occur during upload
    """

    if not os.path.isdir(path) and not os.path.isfile(path):
        raise EvaluationException(
            message=f"Path '{path}' is not a directory or a file",
            internal_message=f"Path '{path}' is not a directory or a file",
            target=ErrorTarget.RAI_CLIENT,
            category=ErrorCategory.INVALID_VALUE,
            blame=ErrorBlame.SYSTEM_ERROR,
        )

    remote_paths = []
    local_paths = []

    if os.path.isdir(path):
        for root, _, filenames in os.walk(path):
            upload_path = ""
            if root != path:
                rel_path = os.path.relpath(root, path)
                upload_path = posixpath.join(rel_path)
            for f in filenames:
                remote_file_path = posixpath.join(upload_path, f)
                remote_paths.append(remote_file_path)
                local_file_path = os.path.join(root, f)
                local_paths.append(local_file_path)

    if os.path.isfile(path):
        remote_paths = [os.path.basename(path)]
        local_paths = [path]

    try:
        # Open the file in binary read mode
        for local, remote in zip(local_paths, remote_paths):
            with open(local, "rb") as data:
                # Upload the file to Azure Blob Storage
                container_client.upload_blob(data=data, name=remote)
            if logger:
                logger.debug(f"File '{local}' uploaded successfully")

    except Exception as e:
        # Extract storage account information if available
        storage_info = ""
        try:
            account_name = container_client.account_name if hasattr(container_client, "account_name") else "unknown"
            storage_info = f" Storage account: {account_name}."
        except Exception:
            pass

        error_msg = (
            f"Failed to upload evaluation results to Azure Blob Storage.{storage_info} "
            f"Error: {str(e)}. "
            "Please verify that:\n"
            "  1. The storage account exists and is accessible\n"
            "  2. Your credentials have the necessary permissions (Storage Blob Data Contributor role)\n"
            "  3. Network access to the storage account is not blocked by firewall rules"
        )

        raise EvaluationException(
            message=error_msg,
            internal_message=f"Error uploading file to blob storage: {e}",
            target=ErrorTarget.RAI_CLIENT,
            category=ErrorCategory.UPLOAD_ERROR,
            blame=ErrorBlame.SYSTEM_ERROR,
        )
