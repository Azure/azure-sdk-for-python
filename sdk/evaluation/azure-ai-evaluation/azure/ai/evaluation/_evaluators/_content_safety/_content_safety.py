# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Dict, List, Union

from typing_extensions import overload, override

from azure.ai.evaluation._evaluators._common import MultiEvaluatorBase
from azure.ai.evaluation._model_configurations import Conversation
from azure.ai.evaluation._common._experimental import experimental

from ._hate_unfairness import HateUnfairnessEvaluator
from ._self_harm import SelfHarmEvaluator
from ._sexual import SexualEvaluator
from ._violence import ViolenceEvaluator


@experimental
class ContentSafetyEvaluator(MultiEvaluatorBase[Union[str, float]]):
    """
    Initialize a content safety evaluator configured to evaluate content safety metrics for QA scenario.

    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param kwargs: Additional arguments to pass to the evaluator.
    :type kwargs: Any
    :return: A function that evaluates content-safety metrics for "question-answering" scenario.

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START content_safety_evaluator]
            :end-before: [END content_safety_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a ContentSafetyEvaluator.
    """

    id = "content_safety"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    def __init__(self, credential, azure_ai_project, **kwargs):
        evaluators = [
            ViolenceEvaluator(credential, azure_ai_project),
            SexualEvaluator(credential, azure_ai_project),
            SelfHarmEvaluator(credential, azure_ai_project),
            HateUnfairnessEvaluator(credential, azure_ai_project),
        ]
        super().__init__(evaluators=evaluators, **kwargs)

    @overload
    def __call__(
        self,
        *,
        query: str,
        response: str,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate a collection of content safety metrics for the given query/response pair

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :return: The content safety scores.
        :rtype: Dict[str, Union[str, float]]
        """

    @overload
    def __call__(
        self,
        *,
        conversation: Conversation,
    ) -> Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]:
        """Evaluate a collection of content safety metrics for a conversation

        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The content safety scores.
        :rtype: Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """Evaluate a collection of content safety metrics for the given query/response pair or conversation.
        This inputs must supply either a query AND response, or a conversation, but not both.

        :keyword query: The query to evaluate.
        :paramtype query: Optional[str]
        :keyword response: The response to evaluate.
        :paramtype response: Optional[str]
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The evaluation result.
        :rtype: Union[Dict[str, Union[str, float]], Dict[str, Union[float, Dict[str, List[Union[str, float]]]]]]
        """
        return super().__call__(*args, **kwargs)
