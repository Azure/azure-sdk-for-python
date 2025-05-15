# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, List, Optional, Union

from typing_extensions import overload, override

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase
from azure.ai.evaluation._model_configurations import Conversation


@experimental
class ProtectedMaterialEvaluator(RaiServiceEvaluatorBase[Union[str, bool]]):
    """
    Evaluates the protected material score for a given query and response or a multi-turn conversation, with reasoning.

    Protected material is any text that is under copyright, including song lyrics, recipes, and articles. Protected
    material evaluation leverages the Azure AI Content Safety Protected Material for Text service to perform the
    classification.

    The protected material score is a boolean value, where True indicates that protected material was detected.

    :param credential: The credential required for connecting to the Azure AI project.
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project, containing the subscription ID,
        resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START protected_material_evaluator]
            :end-before: [END protected_material_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a ProtectedMaterialEvaluator.
    
    .. admonition:: Example using Azure AI Project URL:
        
        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START protected_material_evaluator]
            :end-before: [END protected_material_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call ProtectedMaterialEvaluator using Azure AI Project URL in the following format 
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}

    """

    id = "azureml://registries/azureml/models/Protected-Material-Evaluator/versions/3"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(
        self,
        credential,
        azure_ai_project,
    ):
        super().__init__(
            eval_metric=EvaluationMetrics.PROTECTED_MATERIAL,
            azure_ai_project=azure_ai_project,
            credential=credential,
        )

    @overload
    def __call__(
        self,
        *,
        query: str,
        response: str,
    ) -> Dict[str, Union[str, bool]]:
        """Evaluate a given query/response pair for protected material

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :return: The protected material score.
        :rtype: Dict[str, Union[str, bool]]
        """

    @overload
    def __call__(
        self,
        *,
        conversation: Conversation,
    ) -> Dict[str, Union[float, Dict[str, List[Union[str, bool]]]]]:
        """Evaluate a conversation for protected material

        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The protected material score.
        :rtype: Dict[str, Union[str, bool, Dict[str, List[Union[str, bool]]]]]
        """

    @override
    def __call__(
        self,
        *,
        query: Optional[str] = None,
        response: Optional[str] = None,
        conversation=None,
        **kwargs,
    ):
        """
        Evaluate if protected material is present in your AI system's response.

        :keyword query: The query to be evaluated.
        :paramtype query: Optional[str]
        :keyword response: The response to be evaluated.
        :paramtype response: Optional[str]
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages". Conversation turns are expected
            to be dictionaries with keys "content" and "role".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The fluency score.
        :rtype: Union[Dict[str, Union[str, bool]], Dict[str, Union[float, Dict[str, List[Union[str, bool]]]]]]
        """
        return super().__call__(query=query, response=response, conversation=conversation, **kwargs)
