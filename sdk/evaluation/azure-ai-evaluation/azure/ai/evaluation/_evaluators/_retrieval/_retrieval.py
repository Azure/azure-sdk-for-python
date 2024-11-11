# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import os
from typing import Dict, List, Union
from typing_extensions import overload, override

from azure.ai.evaluation._evaluators._common._base_prompty_eval import PromptyEvaluatorBase
from azure.ai.evaluation._model_configurations import Conversation

logger = logging.getLogger(__name__)


class RetrievalEvaluator(PromptyEvaluatorBase[Union[str, float]]):
    """
    Evaluates retrieval score for a given query and context or a multi-turn conversation, including reasoning.

    The retrieval measure assesses the AI system's performance in retrieving information
    for additional context (e.g. a RAG scenario).

    Retrieval scores range from 1 to 5, with 1 being the worst and 5 being the best.

    High retrieval scores indicate that the AI system has successfully extracted and ranked
    the most relevant information at the top, without introducing bias from external knowledge
    and ignoring factual correctness. Conversely, low retrieval scores suggest that the AI system
    has failed to surface the most relevant context chunks at the top of the list
    and/or introduced bias and ignored factual correctness.

    :param model_config: Configuration for the Azure OpenAI model.
    :type model_config: Union[~azure.ai.evaluation.AzureOpenAIModelConfiguration,
        ~azure.ai.evaluation.OpenAIModelConfiguration]
    :return: A function that evaluates and generates metrics for "chat" scenario.
    :rtype: Callable

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START retrieval_evaluator]
            :end-before: [END retrieval_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a RetrievalEvaluator.

    .. note::

        To align with our support of a diverse set of models, an output key without the `gpt_` prefix has been added.
        To maintain backwards compatibility, the old key with the `gpt_` prefix is still be present in the output;
        however, it is recommended to use the new key moving forward as the old key will be deprecated in the future.
    """

    _PROMPTY_FILE = "retrieval.prompty"
    _RESULT_KEY = "retrieval"

    id = "azureml://registries/azureml/models/Retrieval-Evaluator/versions/1"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(self, model_config):  # pylint: disable=super-init-not-called
        current_dir = os.path.dirname(__file__)
        prompty_path = os.path.join(current_dir, self._PROMPTY_FILE)
        super().__init__(model_config=model_config, prompty_file=prompty_path, result_key=self._RESULT_KEY)

    @overload
    def __call__(
        self,
        *,
        query: str,
        context: str,
    ) -> Dict[str, Union[str, float]]:
        """Evaluates retrieval for a given a query and context

        :keyword query: The query to be evaluated. Mutually exclusive with `conversation` parameter.
        :paramtype query: Optional[str]
        :keyword context: The context to be evaluated. Mutually exclusive with `conversation` parameter.
        :paramtype context: Optional[str]
        :return: The scores for Chat scenario.
        :rtype: Dict[str, Union[str, float]]
        """

    @overload
    def __call__(
        self,
        *,
        conversation: Conversation,
    ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]:
        """Evaluates retrieval for a for a multi-turn evaluation. If the conversation has more than one turn,
        the evaluator will aggregate the results of each turn.

        :keyword conversation: The conversation to be evaluated.
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The scores for Chat scenario.
        :rtype: Dict[str, Union[float, Dict[str, List[float]]]]
        """

    @override
    def __call__(self, *args, **kwargs):  # pylint: disable=docstring-missing-param
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
        :rtype: :rtype: Dict[str, Union[float, Dict[str, List[str, float]]]]
        """
        return super().__call__(*args, **kwargs)
