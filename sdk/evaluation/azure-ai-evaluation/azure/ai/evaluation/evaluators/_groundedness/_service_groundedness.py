# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from promptflow._utils.async_utils import async_run_allowing_running_loop
from azure.ai.evaluation._common.constants import EvaluationMetrics, Tasks
from azure.ai.evaluation._common.rai_service import evaluate_with_rai_service


class _AsyncGroundednessEvaluator:
    def __init__(self, project_scope: dict, credential=None):
        self._metric = EvaluationMetrics.GROUNDEDNESS
        self._metric_display_name = "groundedness"
        self._annotation_task = Tasks.GROUNDEDNESS
        self._project_scope = project_scope
        self._credential = credential

    async def __call__(self, *, answer: str, context: str, **kwargs):
        # Validate inputs
        # Raises value error if failed, so execution alone signifies success.
        if not (answer and answer.strip() and answer != "None") or not (
                context and context.strip() and context != "None"
        ):
            raise ValueError("Both 'answer' and 'context' must be non-empty strings.")

        result = await evaluate_with_rai_service(
            metric_name=self._metric,
            data={
                "answer": answer,
                "context": context
            },
            project_scope=self._project_scope,
            credential=self._credential,
            annotation_task=self._annotation_task,
            metric_display_name=self._metric_display_name,
        )

        result.pop("groundedness")

        return result


class GroundednessEvaluator:
    """
    Initialize a groundedness evaluator for groundedness score.

    :param project_scope: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type project_scope: dict
    :param credential: The credential for connecting to Azure AI project.
    :type credential: ~azure.core.credentials.TokenCredential

    **Usage**

    .. code-block:: python

        project_scope = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        eval_fn = GroundednessEvaluator(project_scope)
        result = eval_fn(
            answer="The capital of Japan is Tokyo.",
            context="Tokyo is Japan's capital, known for its blend of traditional culture \
                and technological advancements.")

    **Output format**

    .. code-block:: python

        {
            "gpt_groundedness": 5
        }
    """

    def __init__(self, project_scope: dict, credential=None):
        self._async_evaluator = _AsyncGroundednessEvaluator(project_scope, credential)

    def __call__(self, *, answer: str, context: str, **kwargs):
        """
        Evaluate groundedness of the answer in the context..

        :keyword answer: The answer to be evaluated.
        :paramtype answer: str
        :keyword context: The context in which the answer is evaluated.
        :paramtype context: str
        :return: The groundedness score.
        :rtype: dict
        """
        return async_run_allowing_running_loop(self._async_evaluator, answer=answer, context=context, **kwargs)

    def _to_async(self):
        return self._async_evaluator
