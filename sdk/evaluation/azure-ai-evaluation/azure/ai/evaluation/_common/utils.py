# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
import threading
from typing import Any, List, Literal, Mapping, Type, TypeVar, Union, cast, get_args, get_origin

import nltk
from typing_extensions import NotRequired, Required, TypeGuard

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


def get_harm_severity_level(harm_score: int) -> Union[str, float]:
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
    with _nltk_data_download_lock:
        try:
            from nltk.tokenize.nist import NISTTokenizer  # pylint: disable=unused-import
        except LookupError:
            nltk.download("perluniprops")
            nltk.download("punkt")
            nltk.download("punkt_tab")


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
        msg = "azure_ai_project must be a dictionary"
        raise EvaluationException(
            message=msg,
            internal_message=msg,
            target=ErrorTarget.DIRECT_ATTACK_SIMULATOR,
            category=ErrorCategory.MISSING_FIELD,
            blame=ErrorBlame.USER_ERROR,
        )

    missing_fields = set(fields.keys()) - o.keys()

    if missing_fields:
        msg = "azure_ai_project must contain keys: " + ", ".join(f'"{field}"' for field in missing_fields)
        raise EvaluationException(
            message=msg,
            internal_message=msg,
            target=ErrorTarget.DIRECT_ATTACK_SIMULATOR,
            category=ErrorCategory.MISSING_FIELD,
            blame=ErrorBlame.USER_ERROR,
        )

    for field_name, expected_type in fields.items():
        if isinstance(o[field_name], expected_type):
            continue

        msg = f"Expected azure_ai_project field {field_name!r} to be of type {expected_type}."

        raise EvaluationException(
            message=f"{msg}. Got {type(o[field_name])}.",
            internal_message=msg,
            target=ErrorTarget.DIRECT_ATTACK_SIMULATOR,
            category=ErrorCategory.MISSING_FIELD,
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
