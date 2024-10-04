# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
import threading
from typing import List, Union

import nltk

from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from azure.ai.evaluation._constants import AZURE_OPENAI_TYPE, OPENAI_TYPE

from . import constants

_nltk_data_download_lock = threading.Lock()


def get_harm_severity_level(harm_score: int) -> str:
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


def parse_model_config_type(
    model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
) -> None:
    if "azure_endpoint" in model_config or "azure_deployment" in model_config:
        model_config["type"] = AZURE_OPENAI_TYPE
    else:
        model_config["type"] = OPENAI_TYPE


def construct_prompty_model_config(
    model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
    default_api_version: str,
    user_agent: str,
) -> dict:
    parse_model_config_type(model_config)

    if model_config["type"] == AZURE_OPENAI_TYPE:
        model_config["api_version"] = model_config.get("api_version", default_api_version)

    prompty_model_config = {"configuration": model_config, "parameters": {"extra_headers": {}}}

    # Handle "RuntimeError: Event loop is closed" from httpx AsyncClient
    # https://github.com/encode/httpx/discussions/2959
    prompty_model_config["parameters"]["extra_headers"].update({"Connection": "close"})

    if model_config["type"] == AZURE_OPENAI_TYPE and user_agent:
        prompty_model_config["parameters"]["extra_headers"].update({"x-ms-useragent": user_agent})

    return prompty_model_config
