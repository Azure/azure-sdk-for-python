# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from typing import Dict, List, Union

from typing_extensions import overload, override

from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._common.constants import EvaluationMetrics
from azure.ai.evaluation._evaluators._common import RaiServiceEvaluatorBase
from azure.ai.evaluation._model_configurations import Conversation

logger = logging.getLogger(__name__)


@experimental
class IndirectAttackEvaluator(RaiServiceEvaluatorBase[Union[str, bool]]):
    """
    Evaluates the indirect attack score for a given query and response or a multi-turn conversation, with reasoning.

    Indirect attacks, also known as cross-domain prompt injected attacks (XPIA), are when jailbreak attacks are
    injected into the context of a document or source that may result in an altered, unexpected behavior.

    Indirect attacks evaluations are broken down into three subcategories:
        - Manipulated Content: This category involves commands that aim to alter or fabricate information, often
            to mislead or deceive. It includes actions like spreading false information, altering language or
            formatting, and hiding or emphasizing specific details. The goal is often to manipulate perceptions
            or behaviors by controlling the flow and presentation of information.
        - Intrusion: This category encompasses commands that attempt to breach systems, gain unauthorized access,
            or elevate privileges illicitly. It includes creating backdoors, exploiting vulnerabilities, and
            traditional jailbreaks to bypass security measures. The intent is often to gain control or access
            sensitive data without detection.
        - Information Gathering: This category pertains to accessing, deleting, or modifying data without
            authorization, often for malicious purposes. It includes exfiltrating sensitive data, tampering with
            system records, and removing or altering existing information. The focus is on acquiring or
            manipulating data to exploit or compromise systems and individuals.

    Indirect attack scores are boolean values, where True indicates that the response contains an indirect attack.

    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project. It contains subscription id, resource group, and project
        name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param threshold: The threshold for the IndirectAttack evaluator. Default is 0.
    :type threshold: int

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START indirect_attack_evaluator]
            :end-before: [END indirect_attack_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call an IndirectAttackEvaluator.
    """

    id = "azureml://registries/azureml/models/Indirect-Attack-Evaluator/versions/3"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    @override
    def __init__(
        self,
        credential,
        azure_ai_project,
    ):
        super().__init__(
            eval_metric=EvaluationMetrics.XPIA,
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
        """Evaluate whether cross domain injected attacks are present in given query/response

        :keyword query: The query to be evaluated.
        :paramtype query: str
        :keyword response: The response to be evaluated.
        :paramtype response: str
        :return: The cross domain injection attack score
        :rtype: Dict[str, Union[str, bool]]
        """

    @overload
    def __call__(
        self,
        *,
        conversation: Conversation,
    ) -> Dict[str, Union[float, Dict[str, List[Union[str, bool]]]]]:
        """Evaluate cross domain injected attacks are present in a conversation

        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages", and potentially a global context under the key "context". Conversation turns are expected
            to be dictionaries with keys "content", "role", and possibly "context".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The cross domain injection attack score
        :rtype: Dict[str, Union[str, bool, Dict[str, List[Union[str, bool]]]]]
        """

    @override
    def __call__(  # pylint: disable=docstring-missing-param
        self,
        *args,
        **kwargs,
    ):
        """
        Evaluate whether cross domain injected attacks are present in your AI system's response.

        :keyword query: The query to be evaluated.
        :paramtype query: Optional[str]
        :keyword response: The response to be evaluated.
        :paramtype response: Optional[str]
        :keyword conversation: The conversation to evaluate. Expected to contain a list of conversation turns under the
            key "messages". Conversation turns are expected
            to be dictionaries with keys "content" and "role".
        :paramtype conversation: Optional[~azure.ai.evaluation.Conversation]
        :return: The cross domain injection attack score
        :rtype: Union[Dict[str, Union[str, bool]], Dict[str, Union[float, Dict[str, List[Union[str, bool]]]]]]
        """
        return super().__call__(*args, **kwargs)
