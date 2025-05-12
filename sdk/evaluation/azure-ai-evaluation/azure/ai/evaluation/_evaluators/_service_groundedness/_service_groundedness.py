# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List, Union, Dict
from typing_extensions import overload, override

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase
from azure.ai.evaluation._model_configurations import Conversation


@experimental
class GroundednessProEvaluator(RaiServiceEvaluatorBase[Union[str, bool]]):
    """
    Evaluates service-based groundedness score for a given response, context, and query or a multi-turn conversation,
    including reasoning.

    The groundedness measure calls Azure AI Evaluation service to assess how well the AI-generated answer is grounded
    in the source context. Even if the responses from LLM are factually correct, they'll be considered ungrounded if
    they can't be verified against the provided sources (such as your input source or your database).

    Service-based groundedness scores are boolean values, where True indicates that the response is grounded.

    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param threshold: The threshold for the groundedness pro evaluator. Default is 5.
    :type threshold: int
    :param kwargs: Additional arguments to pass to the evaluator.
    :type kwargs: Any

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START groundedness_pro_evaluator]
            :end-before: [END groundedness_pro_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a GroundednessProEvaluator with a query, response, and context.

    .. admonition:: Example using Azure AI Project URL:
        
        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START groundedness_pro_evaluator]
            :end-before: [END groundedness_pro_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call GroundednessProEvaluator using Azure AI Project URL in the following format 
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. admonition:: Example with threshold:

        .. literalinclude:: ../samples/evaluation_samples_threshold.py
            :start-after: [START threshold_groundedness_pro_evaluator]
            :end-before: [END threshold_groundedness_pro_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize with a specified threshold and call GroundednessProEvaluator with a query, response, and context.

    .. note::

        If this evaluator is supplied to the `evaluate` function, the aggregated metric
        for the groundedness pro label will be "groundedness_pro_passing_rate".
    """

    id = "azureml://registries/azureml/models/Groundedness-Pro-Evaluator/versions/1"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(
        self,
        credential,
        azure_ai_project,
        *,
        threshold: int = 5,
        **kwargs,
    ):
        self.threshold = threshold
        self._higher_is_better = True
        self._output_prefix = "groundedness_pro"
        super().__init__(
            eval_metric=EvaluationMetrics.GROUNDEDNESS,
            azure_ai_project=azure_ai_project,
            credential=credential,
            threshold=self.threshold,
            **kwargs,
        )

    @overload
    def __call__(
        self,
        *,
        response: str,
        context: str,
        query: str,
    ) -> Dict[str, Union[str, bool]]:
        """Evaluate groundedness for a given query/response/context

        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword context: The context to be evaluated.
        :paramtype context: str
        :keyword query: The query to be evaluated.
        :paramtype query: Optional[str]
        :return: The relevance score.
        :rtype: Dict[str, Union[str, bool]]
        """

    @overload
    def __call__(
        self,
        *,
        conversation: Conversation,
    ) -> Dict[str, Union[float, Dict[str, List[Union[str, bool]]]]]:
        """Evaluate groundedness for a conversation for a multi-turn evaluation. If the conversation has
        more than one turn, the evaluator will aggregate the results of each turn, with the per-turn results
        available in the output under the "evaluation_per_turn" key.

        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The relevance score.
        :rtype: Dict[str, Union[float, Dict[str, List[Union[str, bool]]]]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """Evaluate groundedness. Accepts either a query, response and context for a single-turn evaluation, or a
        or a conversation for a multi-turn evaluation. If the conversation has more than one turn,
        the evaluator will aggregate the results of each turn, with the per-turn results available
        in the output under the "evaluation_per_turn" key.

        :keyword query: The query to be evaluated.
        :paramtype query: Optional[str]
        :keyword response: The response to be evaluated.
        :paramtype response: Optional[str]
        :keyword context: The context to be evaluated.
        :paramtype context: Optional[str]
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The relevance score.
        :rtype: Union[Dict[str, Union[str, bool]], Dict[str, Union[float, Dict[str, List[Union[str, bool]]]]]]
        """
        return super().__call__(*args, **kwargs)

    @override
    async def _do_eval(self, eval_input: Dict):
        """This evaluator has some unique post-processing that requires data that
        the rai_service script is not currently built to handle. So we post-post-process
        the result here to message it into the right form.

        :param eval_input: The input to the evaluation function.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict
        """
        result = await super()._do_eval(eval_input)
        real_result = {}
        real_result[self._output_prefix + "_reason"] = result[EvaluationMetrics.GROUNDEDNESS + "_reason"]
        real_result[self._output_prefix + "_label"] = (
            result[EvaluationMetrics.GROUNDEDNESS + "_score"] >= self.threshold
        )
        if self._higher_is_better:
            real_result[self._output_prefix + "_score"] = max(result[EvaluationMetrics.GROUNDEDNESS + "_score"], 0)
        else:
            real_result[self._output_prefix + "_score"] = min(result[EvaluationMetrics.GROUNDEDNESS + "_score"], 1)

        return real_result
