# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, List
import re

from abc import ABC
from typing_extensions import override


import numpy as np

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
from azure.ai.evaluation._evaluators._common._base_eval import _BaseConversationEval

class _BaseContextFlowEval(_BaseConversationEval):
    """Base class for all evaluators that make use of context as an input. It's also assumed that such evaluators
    make use of a prompty file, and return their results as a dictionary, with a single key-value pair
    linking the result name to a float value (unless multi-turn evaluation occurs, in which case the
    per-turn results are stored in a list under the key "evaluation_per_turn").

    :param result_key: The key to use for the result of the evaluation. Single turn evaluations will return
        a dictionary in the format {result_key: float}.
    :type result_key: str
    :param prompty_file: The path to the prompty file to use for evaluation.
    :type prompty_file: str
    :param model_config: The model configuration to use for evaluation.
    :type model_config: Union[AzureOpenAIModelConfiguration, OpenAIModelConfiguration]
    :param ignore_queries: If True, queries will be ignored in conversation evaluations. Default is False.
        Useful since some evaluators of this format are response-only.
    :type ignore_queries: bool
    """


    LLM_CALL_TIMEOUT = 600
    DEFAULT_OPEN_API_VERSION = "2024-02-15-preview"
    def __init__(self, *, result_key: str, prompty_file: str, model_config: Dict, ignore_queries: bool = False):
        self._result_key = result_key
        self._prompty_file = prompty_file
        self._ignore_queries = ignore_queries
        super().__init__()
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

        self._flow = AsyncPrompty.load(source=self._prompty_file, model=prompty_model_config)

    @override
    async def _do_eval(self, eval_input: Dict) -> Dict:
        """Do a relevance evaluation.
        
        :param eval_input: The input to the evaluator. Expected to contain
        whatever inputs are needed for the _flow method, including context
        and other fields depending on the child class.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        llm_output = await self._flow(timeout=self.LLM_CALL_TIMEOUT, **eval_input)

        score = np.nan
        if llm_output:
            match = re.search(r"\d", llm_output)
            if match:
                score = float(match.group())
        return {self._result_key: float(score)}

    @override
    def _convert_conversation_to_eval_input(self, conversation: Dict) -> List:
        """Convert a conversation into a list of inputs for this evaluator.
        Crucially, this variant gathers a 'context' value from the conversation.

        param conversation: The conversation to convert.
        type conversation: Dict
        return: A list of arbitrary values that are valid inputs for this evaluator's do_eval function.
        rtype: List
        """
        
        messages = conversation['messages']
        global_context = conversation.get('context', None)
        # Extract queries, responses from conversation
        queries = []
        responses = []

        # Convert conversation slice into queries and responses.
        # Assume that 'user' role is asking queries and 'assistant' role is responding.
        for each_turn in messages:
            role = each_turn["role"]
            if role == "user":
                queries.append(each_turn)
            elif role == "assistant":
                responses.append(each_turn)

        eval_inputs = []
        for query, response in zip(queries, responses):
            query_context = query.get("context", None)
            response_context = query.get("context", None)
            context = {}
            if global_context:
                context["global_context"] = global_context
            if query_context and not self._ignore_queries:
                context["query_context"] = query_context
            if response_context:
                context["response_context"] = response_context
            eval_inputs.append({"query": query, "response": response, "context": str(context)})
        return eval_inputs
