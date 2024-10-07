# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Optional
from typing_extensions import override

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase


class FluencyEvaluator(PromptyEvaluatorBase):
    """
    Initialize a fluency evaluator configured for a specific Azure OpenAI model.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    **Usage**

    .. code-block:: python

        eval_fn = FluencyEvaluator(model_config)
        result = eval_fn(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.")

    **Output format**

    .. code-block:: python

        {
            "gpt_fluency": 4.0
        }
    """

    PROMPTY_FILE = "fluency.prompty"
    RESULT_KEY = "gpt_fluency"

    @override
    def __init__(self, model_config: dict):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self.PROMPTY_FILE)
        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self.RESULT_KEY)

    @override
    def __call__(
        self,
        *,
        query: Optional[str] = None,
        response: Optional[str] = None,
        conversation: Optional[dict] = None,
        **kwargs
    ):
        """
        Evaluate fluency. Accepts either a query and response for a single evaluation,
        or a conversation for a multi-turn evaluation. If the conversation has more than one turn,
        the evaluator will aggregate the results of each turn.

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages". Conversation turns are expected
            to be dictionaries with keys "content" and "role".
        :paramtype conversation: Optional[Dict]
        :return: The fluency score.
        :rtype: dict
        """
        return super().__call__(query=query, response=response, conversation=conversation, **kwargs)
