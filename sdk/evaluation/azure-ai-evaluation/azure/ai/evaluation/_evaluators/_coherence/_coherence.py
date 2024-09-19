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


class _AsyncCoherenceEvaluator:
    # Constants must be defined within eval's directory to be save/loadable
    PROMPTY_FILE = "coherence.prompty"
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
        prompty_path = os.path.join(current_dir, self.PROMPTY_FILE)
        self._flow = AsyncPrompty.load(source=prompty_path, model=prompty_model_config)

    async def __call__(self, *, query: str, response: str, **kwargs):
        # Validate input parameters
        query = str(query or "")
        response = str(response or "")

        if not (query.strip() and response.strip()):
            raise ValueError("Both 'query' and 'response' must be non-empty strings.")

        # Run the evaluation flow
        llm_output = await self._flow(query=query, response=response, timeout=self.LLM_CALL_TIMEOUT, **kwargs)

        score = np.nan
        if llm_output:
            match = re.search(r"\d", llm_output)
            if match:
                score = float(match.group())

        return {"gpt_coherence": float(score)}


class CoherenceEvaluator:
    """
    Initialize a coherence evaluator configured for a specific Azure OpenAI model.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    **Usage**

    .. code-block:: python

        eval_fn = CoherenceEvaluator(model_config)
        result = eval_fn(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.")

    **Output format**

    .. code-block:: python

        {
            "gpt_coherence": 1.0
        }
    """

    def __init__(self, model_config: dict):
        self._async_evaluator = _AsyncCoherenceEvaluator(model_config)

    def __call__(self, *, query: str, response: str, **kwargs):
        """
        Evaluate coherence.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :return: The coherence score.
        :rtype: Dict[str, float]
        """
        return async_run_allowing_running_loop(self._async_evaluator, query=query, response=response, **kwargs)

    def _to_async(self):
        return self._async_evaluator
