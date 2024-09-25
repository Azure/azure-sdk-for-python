# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from typing import Dict, Optional
from typing_extensions import override

from azure.ai.evaluation._evaluators._common._base_context_flow_eval import _BaseContextFlowEval


class GroundednessEvaluator(_BaseContextFlowEval):
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
    PROMPTY_FILE = "groundedness.prompty"
    RESULT_KEY = "gpt_groundedness"
    
    @override
    def __init__(self, model_config: Dict):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self.PROMPTY_FILE)
        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self.RESULT_KEY, ignore_queries=True)

    @override
    def __call__(self, *, response: Optional[str] = None, context: Optional[str] = None, conversation: Optional[Dict] = None, **kwargs):
        """Evaluate groundedless. Accepts either a response and context a single evaluation,
        or a conversation for a multi-turn evaluation. If the conversation has more than one turn,
        the evaluator will aggregate the results of each turn.

        :keyword response: The response to be evaluated.
        :paramtype response: Optional[str]
        :keyword context: The context to be evaluated.
        :paramtype context: Optional[str]
        param conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        type conversation: Optional[Dict]
        :return: The relevance score.
        :rtype: dict
        """
        return super().__call__(response=response, context=context, conversation=conversation, **kwargs)
    