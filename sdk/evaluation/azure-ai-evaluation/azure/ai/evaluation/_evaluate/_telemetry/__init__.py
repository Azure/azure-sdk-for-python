# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import functools
import inspect
import json
import logging
from typing import Callable, Dict, Literal, Optional, Union, cast

import pandas as pd
from azure.ai.evaluation._legacy._adapters._flows import FlexFlow as flex_flow
from azure.ai.evaluation._legacy._adapters._flows import AsyncPrompty as prompty_sdk
from azure.ai.evaluation._legacy._adapters._flows import Flow as dag_flow
from azure.ai.evaluation._legacy._adapters.client import PFClient
from typing_extensions import ParamSpec

from azure.ai.evaluation._model_configurations import AzureAIProject, EvaluationResult

from ..._user_agent import USER_AGENT
from .._utils import _trace_destination_from_project_scope

LOGGER = logging.getLogger(__name__)

P = ParamSpec("P")


def _get_evaluator_type(evaluator: Dict[str, Callable]) -> Literal["content-safety", "built-in", "custom"]:
    """
    Get evaluator type for telemetry.

    :param evaluator: The evaluator object
    :type evaluator: Dict[str, Callable]
    :return: The evaluator type. Possible values are "built-in", "custom", and "content-safety".
    :rtype: Literal["content-safety", "built-in", "custom"]
    """
    module = inspect.getmodule(evaluator)
    module_name = module.__name__ if module else ""

    built_in = module_name.startswith("azure.ai.evaluation._evaluators.")
    content_safety = built_in and module_name.startswith("azure.ai.evaluation._evaluators._content_safety")

    if content_safety:
        return "content-safety"
    if built_in:
        return "built-in"
    return "custom"


def _get_evaluator_properties(evaluator, evaluator_name):
    """
    Get evaluator properties for telemetry.

    :param: evaluator: The evaluator object
    :param: evaluator_name: The alias for the evaluator
    :type: str
    :raises Exception: If the evaluator properties cannot be retrieved
    :return: A dictionary containing the evaluator properties, including
        "name": A name for the evaluator
        "pf_type": The promptflow type being used
        "type": The evaluator type. Accepted values are "built-in", "custom", and "content-safety"
        "alias": The alias for the evaluator. Defaults to an empty string.
    :rtype: Dict[str, str]
    """

    try:
        # Cover flex flow and prompty based evaluator
        if isinstance(evaluator, (prompty_sdk, flex_flow)):
            name = evaluator.name
            pf_type = evaluator.__class__.__name__
        # Cover dag flow based evaluator
        elif isinstance(evaluator, dag_flow):
            name = evaluator.name
            pf_type = "DagFlow"
        elif inspect.isfunction(evaluator):
            name = evaluator.__name__
            pf_type = flex_flow.__name__
        elif hasattr(evaluator, "__class__") and callable(evaluator):
            name = evaluator.__class__.__name__
            pf_type = flex_flow.__name__
        else:
            # fallback option
            name = str(evaluator)
            pf_type = "Unknown"
    except Exception as e:  # pylint: disable=broad-exception-caught
        LOGGER.debug("Failed to get evaluator properties: %s", e)
        name = str(evaluator)
        pf_type = "Unknown"

    return {
        "name": name,
        "pf_type": pf_type,
        "type": _get_evaluator_type(evaluator),
        "alias": evaluator_name if evaluator_name else "",
    }
