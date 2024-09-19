# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import re
from typing import Union

import numpy as np

from promptflow._utils.async_utils import async_run_allowing_running_loop
from promptflow.core import AsyncPrompty

from ..._model_configurations import AzureOpenAIModelConfiguration, OpenAIModelConfiguration
from ..._common.utils import (
    check_and_add_api_version_for_aoai_model_config,
    check_and_add_user_agent_for_aoai_model_config,
)

try:
    from ..._user_agent import USER_AGENT
except ImportError:
    USER_AGENT = None


class _AsyncGroundednessEvaluator:
    # Constants must be defined within eval's directory to be save/loadable
    PROMPTY_FILE = "groundedness.prompty"
    LLM_CALL_TIMEOUT = 600
    DEFAULT_OPEN_API_VERSION = "2024-02-15-preview"

    def __init__(self, model_config: dict):
        check_and_add_api_version_for_aoai_model_config(model_config, self.DEFAULT_OPEN_API_VERSION)

        prompty_model_config = {"configuration": model_config, "parameters": {"extra_headers": {}}}

        # Handle "RuntimeError: Event loop is closed" from httpx AsyncClient
        # https://github.com/encode/httpx/discussions/2959
        prompty_model_config["parameters"]["extra_headers"].update({"Connection": "close"})

        check_and_add_user_agent_for_aoai_model_config(
            model_config,
            prompty_model_config,
            USER_AGENT,
        )

        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, "groundedness.prompty")
        self._flow = AsyncPrompty.load(source=prompty_path, model=prompty_model_config)

    async def __call__(self, *, response: str, context: str, **kwargs):
        # Validate input parameters
        response = str(response or "")
        context = str(context or "")

        if not response.strip() or not context.strip():
            raise ValueError("Both 'response' and 'context' must be non-empty strings.")

        # Run the evaluation flow
        llm_output = await self._flow(response=response, context=context, timeout=self.LLM_CALL_TIMEOUT, **kwargs)

        score = np.nan
        if llm_output:
            match = re.search(r"\d", llm_output)
            if match:
                score = float(match.group())

        return {"gpt_groundedness": float(score)}


class GroundednessEvaluator:
    """
    Initialize a groundedness evaluator configured for a specific Azure OpenAI model.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evalation.AzureOpenAIModelConfiguration,
        ~azure.ai.evalation.OpenAIModelConfiguration]

    **Usage**

    .. code-block:: python

        eval_fn = GroundednessEvaluator(model_config)
        result = eval_fn(
            response="The capital of Japan is Tokyo.",
            context="Tokyo is Japan's capital, known for its blend of traditional culture \
                and technological advancements.")

    **Output format**

    .. code-block:: python

        {
            "gpt_groundedness": 5
        }
    """

    def __init__(self, model_config: dict):
        self._async_evaluator = _AsyncGroundednessEvaluator(model_config)

    def __call__(self, *, response: str, context: str, **kwargs):
        """
        Evaluate groundedness of the response in the context.

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword context: The context in which the response is evaluated.
        :paramtype context: str
        :return: The groundedness score.
        :rtype: dict
        """
        return async_run_allowing_running_loop(self._async_evaluator, response=response, context=context, **kwargs)

    def _to_async(self):
        return self._async_evaluator
