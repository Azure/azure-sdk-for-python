# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
from typing import Optional

from typing_extensions import override
from promptflow.core import AsyncPrompty

from azure.ai.evaluation._evaluators._common import PromptyEvaluatorBase
from ..._common.utils import construct_prompty_model_config, validate_model_config

try:
    from ..._user_agent import USER_AGENT
except ImportError:
    USER_AGENT = "None"


class GroundednessEvaluator(PromptyEvaluatorBase):
    """
    Initialize a groundedness evaluator configured for a specific Azure OpenAI model.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]

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
            "groundedness": 5,
            "gpt_groundedness": 5,
        }

    Note: To align with our support of a diverse set of models, a key without the `gpt_` prefix has been added.
    To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
    however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    _PROMPTY_FILE_NO_QUERY = "groundedness_without_query.prompty"
    _PROMPTY_FILE_WITH_QUERY = "groundedness_with_query.prompty"
    _RESULT_KEY = "groundedness"
    _OPTIONAL_PARAMS = ["query"]

    @override
    def __init__(self, model_config):
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE_NO_QUERY)  # Default to no query

        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self._RESULT_KEY)
        self._model_config = model_config
        # Needs to be set because it's used in call method to re-validate prompt if `query` is provided

    @override
    def __call__(
        self,
        *,
        query: Optional[str] = None,
        response: Optional[str] = None,
        context: Optional[str] = None,
        conversation=None,
        **kwargs,
    ):
        """Evaluate groundedness. Accepts either a query, response, and context for a single evaluation,
        or a conversation for a multi-turn evaluation. If the conversation has more than one turn,
        the evaluator will aggregate the results of each turn.

        :keyword query: The query to be evaluated. Mutually exclusive with `conversation`. Optional parameter for use
            with the `response` and `context` parameters. If provided, a different prompt template will be used for
            evaluation.
        :paramtype query: Optional[str]
        :keyword response: The response to be evaluated. Mutually exclusive with the `conversation` parameter.
        :paramtype response: Optional[str]
        :keyword context: The context to be evaluated. Mutually exclusive with the `conversation` parameter.
        :paramtype context: Optional[str]
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The relevance score.
        :rtype: Union[Dict[str, float], Dict[str, Union[float, Dict[str, List[float]]]]]
        """

        if query:
            current_dir = os.path.dirname(__file__)
            prompty_path = os.path.join(current_dir, self._PROMPTY_FILE_WITH_QUERY)
            self._prompty_file = prompty_path
            prompty_model_config = construct_prompty_model_config(
                validate_model_config(self._model_config),
                self._DEFAULT_OPEN_API_VERSION,
                USER_AGENT,
            )
            self._flow = AsyncPrompty.load(source=self._prompty_file, model=prompty_model_config)

        return super().__call__(query=query, response=response, context=context, conversation=conversation, **kwargs)
