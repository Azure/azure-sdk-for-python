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
    """A Cross-Domain Prompt Injection Attack (XPIA) jailbreak evaluator.

    Detect whether cross domain injected attacks are present in your AI system's response.
    Metrics include the overall evaluation label and reason for the Q/A Pair, as well as sub-labels
    for manipulated content, intrusion, and information.

    :param credential: The credential for connecting to Azure AI project. Required
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project. It contains subscription id, resource group, and project
        name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject

        **Usage**

        .. code-block:: python

            eval_fn = IndirectAttackEvaluator(model_config)
            result = eval_fn(query="What is the capital of France?", response="Paris.")

        **Output format for question-answer pair**

        .. code-block:: python

            {
                'xpia_label': False,
                'xpia_reason': 'The conversation does not contain any manipulated content, intrusion or
                              information gathering.'
                'xpia_information_gathering': False,
                'xpia_intrusion': False
                'xpia_manipulated_content': False
            }
    """

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
