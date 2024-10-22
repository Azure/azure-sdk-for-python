# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Coroutine, Optional, Dict
from typing_extensions import override

from azure.ai.evaluation._common.constants import EvaluationMetrics, Tasks
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase
from azure.ai.evaluation._common.constants import DEFAULT_PASSING_SCORE



class GroundednessProEvaluator(RaiServiceEvaluatorBase):
    """
    Initialize a hate-unfairness evaluator for hate unfairness score.

    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject

    **Usage**

    .. code-block:: python

        azure_ai_project = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        eval_fn = GroundednessProEvaluator(azure_ai_project)
        result = eval_fn(response="Paris", context="Paris.")

    **Output format**

    .. code-block:: python

        {
            "groundedness": 5,
            "reason": "The response is grounded"
        }
    """

    @override
    def __init__(
        self,
        credential,
        azure_ai_project: dict,
        **kwargs,
    ):
        self._passing_score = kwargs.get("passing_score", DEFAULT_PASSING_SCORE)
        self._output_prefix = "groundedness_pro"
        super().__init__(
            eval_metric=EvaluationMetrics.GROUNDEDNESS,
            azure_ai_project=azure_ai_project,
            credential=credential,
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
        """Evaluate groundedness. Accepts either a response and context a single evaluation,
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
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The relevance score.
        :rtype: Union[Dict[str, float], Dict[str, Union[float, Dict[str, List[float]]]]]
        """
        return super().__call__(query=query, response=response, context=context, conversation=conversation, **kwargs)


    @override
    async def _do_eval(self, eval_input: Dict):
        """ This evaluator has some unique post-processing that requires data that
        the rai_service script is not currently built to handle. So we post-post-process
        the result here to message it into the right form.
        """
        result = await super()._do_eval(eval_input)
        real_result = {}
        real_result[self._output_prefix + "_label"] = result[EvaluationMetrics.GROUNDEDNESS + "_score"] >= self._passing_score
        real_result[self._output_prefix + "_reason"] = result[EvaluationMetrics.GROUNDEDNESS + "_reason"]
        return real_result
