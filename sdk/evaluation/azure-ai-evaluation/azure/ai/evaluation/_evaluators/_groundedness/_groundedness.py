# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from typing import Optional

from typing_extensions import override

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase


class GroundednessEvaluator(PromptyEvaluatorBase):
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
    def __init__(self, model_config: dict):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self.PROMPTY_FILE)
        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self.RESULT_KEY)

    @override
    def __call__(
        self,
        *,
        response: Optional[str] = None,
        context: Optional[str] = None,
        messages: Optional[dict] = None,
        **kwargs,
    ):
        """Evaluate groundedless. Accepts either a response and context a single evaluation,
        or a messages for a multi-turn evaluation. If the messages or conversation has more than one turn,
        the evaluator will aggregate the results of each turn.

        :keyword response: The response to be evaluated.
        :paramtype response: Optional[str]
        :keyword context: The context to be evaluated.
        :paramtype context: Optional[str]
        :keyword messages: The list of messages (aka conversation). Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype messages: Optional[Dict]
        :return: The relevance score.
        :rtype: Dict[str, float]
        """
        return super().__call__(response=response, context=context, messages=messages, **kwargs)
