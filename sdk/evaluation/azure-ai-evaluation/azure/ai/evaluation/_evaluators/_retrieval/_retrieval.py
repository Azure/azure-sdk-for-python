# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import logging
import math
import os
from typing import Optional

from promptflow._utils.async_utils import async_run_allowing_running_loop
from promptflow.core import AsyncPrompty

from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from ..._common.math import list_mean_nan_safe
from ..._common.utils import construct_prompty_model_config, validate_model_config, parse_quality_evaluator_reason_score

logger = logging.getLogger(__name__)

try:
    from .._user_agent import USER_AGENT
except ImportError:
    USER_AGENT = "None"


class _AsyncRetrievalScoreEvaluator:
    # Constants must be defined within eval's directory to be save/loadable
    _PROMPTY_FILE = "retrieval.prompty"
    _LLM_CALL_TIMEOUT = 600
    _DEFAULT_OPEN_API_VERSION = "2024-02-15-preview"

    def __init__(self, model_config: dict):
        prompty_model_config = construct_prompty_model_config(
            validate_model_config(model_config),
            self._DEFAULT_OPEN_API_VERSION,
            USER_AGENT,
        )

        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        self._flow = AsyncPrompty.load(source=prompty_path, model=prompty_model_config)

    async def __call__(self, *, query, context, conversation, **kwargs):
        if conversation:
            # Extract queries, responses and contexts from conversation
            queries = []
            responses = []
            contexts = []

            conversation = conversation.get("messages", None)

            for each_turn in conversation:
                role = each_turn["role"]
                if role == "user":
                    queries.append(each_turn["content"])
                elif role == "assistant":
                    responses.append(each_turn["content"])
                    if "context" in each_turn:
                        if "citations" in each_turn["context"]:
                            citations = json.dumps(each_turn["context"]["citations"])
                            contexts.append(citations)
                        elif isinstance(each_turn["context"], str):
                            contexts.append(each_turn["context"])

            # Evaluate each turn
            per_turn_scores = []
            per_turn_reasons = []
            for turn_num, turn_query in enumerate(queries):
                try:
                    if turn_num >= len(queries):
                        turn_query = ""
                    context = contexts[turn_num] if turn_num < len(contexts) else ""

                    llm_output = await self._flow(
                        query=turn_query, context=context, timeout=self._LLM_CALL_TIMEOUT, **kwargs
                    )
                    score, reason = parse_quality_evaluator_reason_score(llm_output)
                    per_turn_scores.append(score)
                    per_turn_reasons.append(reason)

                except Exception as e:  # pylint: disable=broad-exception-caught
                    logger.warning(
                        "Evaluator %s failed for turn %s with exception: %s", self.__class__.__name__, turn_num + 1, e
                    )

                    per_turn_scores.append(math.nan)
                    per_turn_reasons.append("")

            mean_per_turn_score = list_mean_nan_safe(per_turn_scores)

            return {
                "retrieval": mean_per_turn_score,
                "gpt_retrieval": mean_per_turn_score,
                "evaluation_per_turn": {
                    "gpt_retrieval": per_turn_scores,
                    "retrieval": per_turn_scores,
                    "retrieval_reason": per_turn_reasons,
                },
            }
        llm_output = await self._flow(query=query, context=context, timeout=self._LLM_CALL_TIMEOUT, **kwargs)
        score, reason = parse_quality_evaluator_reason_score(llm_output)

        return {
            "retrieval": score,
            "retrieval_reason": reason,
            "gpt_retrieval": score,
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

        chat_eval = RetrievalEvaluator(model_config)
        conversation = {
            "messages": [
                {"role": "user", "content": "What is the value of 2 + 2?"},
                {
                    "role": "assistant", "content": "2 + 2 = 4",
                    "context": "From 'math_doc.md': Information about additions: 1 + 2 = 3, 2 + 2 = 4"
                }
            ]
        }
        result = chat_eval(conversation=conversation)

    **Output format**

    .. code-block:: python

        {
            "gpt_retrieval": 3.0,
            "retrieval": 3.0,
            "evaluation_per_turn": {
                "gpt_retrieval": [1.0, 2.0, 3.0],
                "retrieval": [1.0, 2.0, 3.0],
                "retrieval_reason": ["<reasoning for score 1>", "<reasoning for score 2>", "<reasoning for score 3>"]
            }
        }

    Note: To align with our support of a diverse set of models, a key without the `gpt_` prefix has been added.
    To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
    however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    def __init__(self, model_config):
        self._async_evaluator = _AsyncRetrievalScoreEvaluator(model_config)

    def __call__(self, *, query: Optional[str] = None, context: Optional[str] = None, conversation=None, **kwargs):
        """Evaluates retrieval score chat scenario. Accepts either a query and context for a single evaluation,
        or a conversation for a multi-turn evaluation. If the conversation has more than one turn,
        the evaluator will aggregate the results of each turn.

        :keyword query: The query to be evaluated. Mutually exclusive with `conversation` parameter.
        :paramtype query: Optional[str]
        :keyword context: The context to be evaluated. Mutually exclusive with `conversation` parameter.
        :paramtype context: Optional[str]
        :keyword conversation: The conversation to be evaluated.
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The scores for Chat scenario.
        :rtype: :rtype: Dict[str, Union[float, Dict[str, List[float]]]]
        """
        if (query is None or context is None) and conversation is None:
            msg = "Either a pair of 'query'/'context' or 'conversation' must be provided."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.MISSING_FIELD,
                target=ErrorTarget.RETRIEVAL_EVALUATOR,
            )

        if (query or context) and conversation:
            msg = "Either a pair of 'query'/'context' or 'conversation' must be provided, but not both."
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                blame=ErrorBlame.USER_ERROR,
                category=ErrorCategory.INVALID_VALUE,
                target=ErrorTarget.RETRIEVAL_EVALUATOR,
            )

        return async_run_allowing_running_loop(
            self._async_evaluator, query=query, context=context, conversation=conversation, **kwargs
        )

    def _to_async(self):
        return self._async_evaluator
