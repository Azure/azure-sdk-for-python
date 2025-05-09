# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing_extensions import overload, override
from typing import Dict, Union

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase

@experimental
class UngroundedAttributesEvaluator(RaiServiceEvaluatorBase[Union[str, bool]]):
    """
    Evaluates ungrounded inference of human attributes for a given query, response, and context for a single-turn evaluation only, 
    where query represents the user query and response represents the AI system response given the provided context. 
 
    Ungrounded Attributes checks for whether a response is first, ungrounded, and checks if it contains information about protected class or 
    emotional state of a person.


    It identifies the following attributes:
    
    - emotional_state
    - protected_class
    - groundedness

    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param kwargs: Additional arguments to pass to the evaluator.
    :type kwargs: Any

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START ungrounded_attributes_evaluator]
            :end-before: [END ungrounded_attributes_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a UngroundedAttributesEvaluator with a query, response and context.

    .. admonition:: Example using Azure AI Project URL:
        
        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START ungrounded_attributes_evaluator]
            :end-before: [END ungrounded_attributes_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call UngroundedAttributesEvaluator using Azure AI Project URL in the following format 
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    .. note::

        If this evaluator is supplied to the `evaluate` function, the metric
        for the ungrounded attributes will be "ungrounded_attributes_label".
    """

    id = "ungrounded_attributes"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(
        self,
        credential,
        azure_ai_project,
    ):
        super().__init__(
            eval_metric=EvaluationMetrics.UNGROUNDED_ATTRIBUTES,
            azure_ai_project=azure_ai_project,
            credential=credential,
        )

    @overload
    def __call__(
        self,
        *,
        query: str,
        response: str,
        context: str,
    ) -> Dict[str, Union[str, float]]:
        """Evaluate a given query/response pair and context for ungrounded attributes

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword context: The context to be used for evaluation.
        :paramtype context: str
        :return: The ungrounded attributes label.
        :rtype: Dict[str, Union[str, bool]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """Evaluate a given query/response pair and context for ungrounded attributes

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :keyword context: The context to be used for evaluation.
        :paramtype context: str
        :return: The ungrounded attributes label.
        :rtype: Dict[str, Union[str, bool]]
        """
        
        return super().__call__(*args, **kwargs)
