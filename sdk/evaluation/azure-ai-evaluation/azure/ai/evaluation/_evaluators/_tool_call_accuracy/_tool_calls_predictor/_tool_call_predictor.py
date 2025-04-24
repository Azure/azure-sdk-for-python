# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
import os
import re
from typing import Dict, TypeVar, Union

from azure.ai.evaluation._legacy.prompty import AsyncPrompty
from typing_extensions import override

from azure.ai.evaluation._common.constants import PROMPT_BASED_REASON_EVALUATORS
from azure.ai.evaluation._constants import EVALUATION_PASS_FAIL_MAPPING
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from ...._common.utils import construct_prompty_model_config, validate_model_config, \
    parse_quality_evaluator_reason_score

try:
    from ..._user_agent import USER_AGENT
except ImportError:
    USER_AGENT = "None"

T = TypeVar("T")

#
from azure.ai.evaluation._legacy._adapters.utils import async_run_allowing_running_loop

from promptflow.core import AsyncPrompty

from ...._common.utils import construct_prompty_model_config, validate_model_config, \
    parse_quality_evaluator_reason_score

try:
    from ..._user_agent import USER_AGENT
except ImportError:
    USER_AGENT = "None"


def predict_tools(model_config, query: Union[str, list], tool_definition: list):
    """Generate ground truth for the given query and tool definition.

    :param query: The input query or a list of queries.
    :type query: Union[str, list]
    :param tool_definition: The tool definition to use for generating ground truth.
    :type tool_definition: list
    :return: The generated ground truth.
    :rtype: dict
    """
    _PROMPTY_FILE = "tool_call_predictor.prompty"
    current_dir = os.path.dirname(__file__)
    prompty_path = os.path.join(current_dir, _PROMPTY_FILE)
    _LLM_CALL_TIMEOUT = 600
    _DEFAULT_OPEN_API_VERSION = "2024-02-15-preview"

    user_agent = f"{USER_AGENT} (type=evaluator subtype=ground_truth_generator)"  # type: ignore[assignment]
    prompty_model_config = construct_prompty_model_config(
        validate_model_config(model_config),
        _DEFAULT_OPEN_API_VERSION,
        user_agent,
    )

    flow = AsyncPrompty.load(source=prompty_path, model=prompty_model_config)
    eval_input = {
        "query": query,
        "tool_definition": tool_definition,
    }
    llm_output = async_run_allowing_running_loop(flow, **{"timeout": _LLM_CALL_TIMEOUT, **eval_input})
    if isinstance(llm_output, dict):
        return llm_output
    return {"tools": []}
