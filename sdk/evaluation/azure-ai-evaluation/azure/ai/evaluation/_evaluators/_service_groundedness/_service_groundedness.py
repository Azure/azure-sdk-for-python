# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Optional, Dict
from typing_extensions import override

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase


@experimental
class GroundednessProEvaluator(RaiServiceEvaluatorBase):
    """
    Initialize a Groundedness Pro evaluator for determine if the response is grounded
    in the query and context.

    If this evaluator is supplied to the `evaluate` function, the aggregated metric
    for the groundedness pro label will be "groundedness_pro_passing_rate".

    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param kwargs: Additional arguments to pass to the evaluator.
    :type kwargs: Any

    **Usage**

    .. code-block:: python

        azure_ai_project = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        credential = DefaultAzureCredential()

        eval_fn = GroundednessProEvaluator(azure_ai_project, credential)
        result = eval_fn(query="What's the capital of France", response="Paris", context="Paris.")

    **Output format**

    .. code-block:: python

        {
            "groundedness_pro_label": True,
            "reason": "'All Contents are grounded"
        }

    **Usage with conversation input**

    .. code-block:: python

        azure_ai_project = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        credential = DefaultAzureCredential()

        eval_fn = GroundednessProEvaluator(azure_ai_project, credential)
        conversation = {
            "messages": [
                {"role": "user", "content": "What is the capital of France?"},
                {"role": "assistant", "content": "Paris.", "context": "Paris."}
                {"role": "user", "content": "What is the capital of Germany?"},
                {"role": "assistant", "content": "Berlin.", "context": "Berlin."}
            ]
        }
        result = eval_fn(conversation=conversation)

    **Output format**

    .. code-block:: python

            {
                "groundedness_pro_label": 1.0,
                "evaluation_per_turn": {
                    "groundedness_pro_label": [True, True],
                    "groundedness_pro_reason": ["All contents are grounded", "All contents are grounded"]
                }
            }
    """

    @override
    def __init__(
        self,
        credential,
        azure_ai_project,
        **kwargs,
    ):
        self._passing_score = 3  # TODO update once the binarization PR is merged
        self._output_prefix = "groundedness_pro"
        super().__init__(
            eval_metric=EvaluationMetrics.GROUNDEDNESS,
            azure_ai_project=azure_ai_project,
            credential=credential,
            **kwargs,
        )

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
        return super().__call__(query=query, response=response, context=context, conversation=conversation, **kwargs)

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
        real_result[self._output_prefix + "_label"] = (
            result[EvaluationMetrics.GROUNDEDNESS + "_score"] >= self._passing_score
        )
        real_result[self._output_prefix + "_reason"] = result[EvaluationMetrics.GROUNDEDNESS + "_reason"]
        return real_result
