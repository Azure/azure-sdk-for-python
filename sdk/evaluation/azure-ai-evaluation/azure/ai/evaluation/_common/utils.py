# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Optional, Union

from azure.ai.evaluation._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration

try:
    from . import constants
except ImportError:
    import constants

from typing import List

import threading
import numpy as np
import nltk

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
    if harm_score == np.nan or harm_score is None:
        return np.nan
    for harm_level, harm_score_range in HARM_SEVERITY_LEVEL_MAPPING.items():
        if harm_score_range[0] <= harm_score <= harm_score_range[1]:
            return harm_level.value
    return np.nan


def ensure_nltk_data_downloaded():
    """Download NLTK data packages if not already downloaded."""
    with _nltk_data_download_lock:
        try:
            from nltk.tokenize.nist import NISTTokenizer
        except LookupError:
            nltk.download("perluniprops")
            nltk.download("punkt")
            nltk.download("punkt_tab")


def nltk_tokenize(text: str) -> List[str]:
    """Tokenize the input text using the NLTK tokenizer."""
    ensure_nltk_data_downloaded()

    if not text.isascii():
        # Use NISTTokenizer for international tokenization
        from nltk.tokenize.nist import NISTTokenizer
        tokens = NISTTokenizer().international_tokenize(text)
    else:
        # By default, use NLTK word tokenizer
        tokens = nltk.word_tokenize(text)

    return list(tokens)


def check_and_add_api_version_for_aoai_model_config(
    model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
    default_api_version: str,
) -> None:
    if (
        "azure_endpoint" in model_config or "azure_deployment" in model_config
    ):
        model_config["api_version"] = model_config.get("api_version", default_api_version)


def check_and_add_user_agent_for_aoai_model_config(
    model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration],
    prompty_model_config: dict,
    user_agent: Optional[str] = None,
) -> None:
    if user_agent and ("azure_endpoint" in model_config or "azure_deployment" in model_config):
        prompty_model_config["parameters"]["extra_headers"].update({"x-ms-useragent": user_agent})