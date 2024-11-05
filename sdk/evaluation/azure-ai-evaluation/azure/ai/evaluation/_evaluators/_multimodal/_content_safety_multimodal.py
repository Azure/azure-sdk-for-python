# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
from concurrent.futures import as_completed
from typing import Callable, Dict, List, Union

from promptflow.tracing import ThreadPoolExecutorWithContext as ThreadPoolExecutor
from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._common.utils import validate_conversation
from ._hate_unfairness import HateUnfairnessMultimodalEvaluator
from ._self_harm import SelfHarmMultimodalEvaluator
from ._sexual import SexualMultimodalEvaluator
from ._violence import ViolenceMultimodalEvaluator


logger = logging.getLogger(__name__)


@experimental
class ContentSafetyMultimodalEvaluator:
    """
    Initialize a content safety multimodal evaluator configured to evaluate content safety metrics
    in a multimodal scenario.

    :param credential: The credential required for connecting to the Azure AI project.
    :type credential: ~azure.core.credentials.TokenCredential
    :param azure_ai_project: The scope of the Azure AI project, containing the subscription ID,
        resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param kwargs: Additional arguments to pass to the evaluator.
    :type kwargs: Any

    :return: A function that evaluates multimodal chat messages and generates content safety metrics.

    **Usage Example**

    .. code-block:: python

        azure_ai_project = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        eval_fn = ContentSafetyMultimodalEvaluator(azure_ai_project)
        result = eval_fn(conversation=
            {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "What's in this image?"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": "<image url or base64 encoded image>"
                                }
                            }
                        ]
                    },
                    {
                        "role": "assistant",
                        "content": "This picture shows an astronaut standing in the desert."
                    }
                ]
            }
        )

    **Output Format**

    .. code-block:: json

        {
            "violence": "Medium",
            "violence_score": 5.0,
            "violence_reason": "Some reason",
            "sexual": "Medium",
            "sexual_score": 5.0,
            "sexual_reason": "Some reason",
            "self_harm": "Medium",
            "self_harm_score": 5.0,
            "self_harm_reason": "Some reason",
            "hate_unfairness": "Medium",
            "hate_unfairness_score": 5.0,
            "hate_unfairness_reason": "Some reason"
        }

    """

    id = "content_safety_multimodal"
    """Evaluator identifier, experimental and to be used only with evaluation in cloud."""

    def __init__(self, credential, azure_ai_project, **kwargs):
        self._parallel = kwargs.pop("_parallel", False)
        self._evaluators: List[Callable[..., Dict[str, Union[str, float]]]] = [
            ViolenceMultimodalEvaluator(credential=credential, azure_ai_project=azure_ai_project),
            SexualMultimodalEvaluator(credential=credential, azure_ai_project=azure_ai_project),
            SelfHarmMultimodalEvaluator(credential=credential, azure_ai_project=azure_ai_project),
            HateUnfairnessMultimodalEvaluator(credential=credential, azure_ai_project=azure_ai_project),
        ]

    def __call__(self, *, conversation, **kwargs):
        """
        Evaluates content-safety metrics for list of messages.

        :keyword conversation: The conversation contains list of messages to be evaluated.
            Each message should have "role" and "content" keys. It supports single turn only.
        :paramtype conversation: ~azure.ai.evaluation.Conversation
        :return: The evaluation score based on the Content Safety Metrics.
        :rtype: Dict[str, Union[float, str]]
        """
        # validate inputs
        validate_conversation(conversation)
        results: Dict[str, Union[str, float]] = {}
        if self._parallel:
            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(evaluator, conversation=conversation, **kwargs): evaluator
                    for evaluator in self._evaluators
                }

                for future in as_completed(futures):
                    results.update(future.result())
        else:
            for evaluator in self._evaluators:
                result = evaluator(conversation=conversation, **kwargs)
                results.update(result)

        return results
