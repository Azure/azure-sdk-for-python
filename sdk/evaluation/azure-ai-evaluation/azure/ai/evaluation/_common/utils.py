# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
import math
import threading
from typing import Any, List, Literal, Mapping, Type, TypeVar, Tuple, Union, cast, get_args, get_origin

import nltk
from typing_extensions import NotRequired, Required, TypeGuard
from azure.ai.evaluation._legacy._adapters._errors import MissingRequiredPackage
from azure.ai.evaluation._constants import AZURE_OPENAI_TYPE, OPENAI_TYPE
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException
from azure.ai.evaluation._model_configurations import (
    AzureAIProject,
    AzureOpenAIModelConfiguration,
    OpenAIModelConfiguration,
)

from . import constants

_nltk_data_download_lock = threading.Lock()

T_TypedDict = TypeVar("T_TypedDict", bound=Mapping[Any, Any])


def get_harm_severity_level(harm_score: Union[float, int]) -> Union[str, float]:
    """Generate harm severity level based on harm score.

    :param harm_score: The harm score to be evaluated.
    :type harm_score: int
    :return: The harm severity level. If harm score is None or numpy.nan, returns numpy.nan.
    :rtype: str
    """
    HARM_SEVERITY_LEVEL_MAPPING = {
        constants.HarmSeverityLevel.VeryLow: [0, 1],
        constants.HarmSeverityLevel.Low: [2, 3],
        constants.HarmSeverityLevel.Medium: [4, 5],
        constants.HarmSeverityLevel.High: [6, 7],
    }
    if math.isnan(harm_score) or harm_score is None:
        return math.nan
    for harm_level, harm_score_range in HARM_SEVERITY_LEVEL_MAPPING.items():
        if harm_score_range[0] <= harm_score <= harm_score_range[1]:
            return harm_level.value
    return math.nan


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


def validate_azure_ai_project(o: object) -> AzureAIProject:
    fields = {"subscription_id": str, "resource_group_name": str, "project_name": str}

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

def check_score_is_valid(score: Union[str, float], min_score = 1, max_score = 5) -> bool:
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
