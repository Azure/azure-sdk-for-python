# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
import math
import os
import re

from promptflow._utils.async_utils import async_run_allowing_running_loop
from promptflow.core import AsyncPrompty

from ..._common.math import list_mean_nan_safe
from ..._common.utils import construct_prompty_model_config

logger = logging.getLogger(__name__)

try:
    from .._user_agent import USER_AGENT
except ImportError:
    USER_AGENT = None


class _AsyncRetrievalScoreEvaluator:
    # Constants must be defined within eval's directory to be save/loadable
    PROMPTY_FILE = "retrieval.prompty"
    LLM_CALL_TIMEOUT = 600
    DEFAULT_OPEN_API_VERSION = "2024-02-15-preview"

    def __init__(self, model_config: dict):
        prompty_model_config = construct_prompty_model_config(
            model_config,
            self.DEFAULT_OPEN_API_VERSION,
            USER_AGENT,
        )

        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self.PROMPTY_FILE)
        self._flow = AsyncPrompty.load(source=prompty_path, model=prompty_model_config)

    async def __call__(self, *, conversation, **kwargs):
        # Extract queries, responses and contexts from conversation
        queries = []
        responses = []
        contexts = []

        for each_turn in conversation:
            role = each_turn["role"]
            if role == "user":
                queries.append(each_turn["content"])
            elif role == "assistant":
                responses.append(each_turn["content"])
                if "context" in each_turn and "citations" in each_turn["context"]:
                    citations = json.dumps(each_turn["context"]["citations"])
                    contexts.append(citations)

        # Evaluate each turn
        per_turn_scores = []
        history = []
        for turn_num, query in enumerate(queries):
            try:
                query = query if turn_num < len(queries) else ""
                answer = responses[turn_num] if turn_num < len(responses) else ""
                context = contexts[turn_num] if turn_num < len(contexts) else ""

                history.append({"user": query, "assistant": answer})

                llm_output = await self._flow(
                    query=query, history=history, documents=context, timeout=self.LLM_CALL_TIMEOUT, **kwargs
                )
                score = math.nan
                if llm_output:
                    parsed_score_response = re.findall(r"\d+", llm_output.split("# Result")[-1].strip())
                    if len(parsed_score_response) > 0:
                        score = float(parsed_score_response[0].replace("'", "").strip())

                per_turn_scores.append(score)

            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.warning(
                    "Evaluator %s failed for turn %s with exception: %s", self.__class__.__name__, turn_num + 1, e
                )

                per_turn_scores.append(math.nan)

        return {
            "gpt_retrieval": list_mean_nan_safe(per_turn_scores),
            "evaluation_per_turn": {
                "gpt_retrieval": {
                    "score": per_turn_scores,
                }
            },
        }


class RetrievalEvaluator:
    """
    Initialize an evaluator configured for a specific Azure OpenAI model.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :return: A function that evaluates and generates metrics for "chat" scenario.
    :rtype: Callable

    **Usage**

    .. code-block:: python

        chat_eval = RetrievalScoreEvaluator(model_config)
        conversation = [
            {"role": "user", "content": "What is the value of 2 + 2?"},
            {"role": "assistant", "content": "2 + 2 = 4", "context": {
                "citations": [
                        {"id": "math_doc.md", "content": "Information about additions: 1 + 2 = 3, 2 + 2 = 4"}
                        ]
                }
            }
        ]
        result = chat_eval(conversation=conversation)

    **Output format**

    .. code-block:: python

        {
            "gpt_retrieval": 3.0
            "evaluation_per_turn": {
                "gpt_retrieval": {
                    "score": [1.0, 2.0, 3.0]
                }
            }
        }
    """

    def __init__(self, model_config: dict):
        self._async_evaluator = _AsyncRetrievalScoreEvaluator(model_config)

    def __call__(self, *, conversation, **kwargs):
        """Evaluates retrieval score chat scenario.

        :keyword conversation: The conversation to be evaluated.
        :paramtype conversation: List[Dict]
        :return: The scores for Chat scenario.
        :rtype: dict
        """
        return async_run_allowing_running_loop(self._async_evaluator, conversation=conversation, **kwargs)

    def _to_async(self):
        return self._async_evaluator
