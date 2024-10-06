# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
from typing import Optional
from typing_extensions import override

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase


class RelevanceEvaluator(PromptyEvaluatorBase):
    """
    Initialize a relevance evaluator configured for a specific Azure OpenAI model.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

    **Usage**

    .. code-block:: python

        eval_fn = RelevanceEvaluator(model_config)
        result = eval_fn(
            query="What is the capital of Japan?",
            response="The capital of Japan is Tokyo.",
            context="Tokyo is Japan's capital, known for its blend of traditional culture \
                and technological advancements.")

    **Output format**

    .. code-block:: python

        {
            "gpt_relevance": 3.0
        }
    """

    # Constants must be defined within eval's directory to be save/loadable
    PROMPTY_FILE = "relevance.prompty"
    RESULT_KEY = "gpt_relevance"

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
        context: Optional[str] = None,
        conversation: Optional[dict] = None,
        **kwargs
    ):
        """Evaluate relevance. Accepts either a response and context a single evaluation,
        or a conversation for a multi-turn evaluation. If the conversation has more than one turn,
        the evaluator will aggregate the results of each turn.

        :keyword query: The query to be evaluated.
        :paramtype query: Optional[str]
        :keyword response: The response to be evaluated.
        :paramtype response: Optional[str]
        :keyword context: The context to be evaluated.
        :paramtype context: Optional[str]
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[Dict]
        :return: The relevance score.
        :rtype: dict
        """
        return super().__call__(query=query, response=response, context=context, conversation=conversation, **kwargs)
