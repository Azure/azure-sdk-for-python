# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import math
from concurrent.futures import as_completed
from typing import Callable, Dict, List, Union
from azure.ai.inference.models import ChatRequestMessage, UserMessage, AssistantMessage, SystemMessage, ToolMessage, ContentItem, ImageContentItem

from promptflow.tracing import ThreadPoolExecutorWithContext as ThreadPoolExecutor
from azure.ai.evaluation._common._experimental import experimental
from azure.ai.evaluation._common.constants import HarmSeverityLevel
from azure.ai.evaluation._common.math import list_mean_nan_safe
from azure.ai.evaluation._exceptions import ErrorBlame, ErrorCategory, ErrorTarget, EvaluationException

from ._hate_unfairness import HateUnfairnessMultimodalEvaluator
from ._self_harm import SelfHarmMultimodalEvaluator
from ._sexual import SexualMultimodalEvaluator
from ._violence import ViolenceMultimodalEvaluator

logger = logging.getLogger(__name__)

@experimental
class ContentSafetyMultimodalEvaluator:
    """
    Initialize a content safety multimodal evaluator configured to evaluate content safety metrics for multimodal scenario.
    :param azure_ai_project: The scope of the Azure AI project.
        It contains subscription id, resource group, and project name.
    :type azure_ai_project: ~azure.ai.evaluation.AzureAIProject
    :param parallel: If True, use parallel execution for evaluators. Else, use sequential execution.
        Default is True.
    :type parallel: bool
    :param credential: The credential for connecting to Azure AI project.
    :type credential: ~azure.core.credentials.TokenCredential
    :return: A function that evaluates multimodal chat messages and generates metrics.
    :rtype: Callable
    
    **Usage**
    .. code-block:: python
        azure_ai_project = {
            "subscription_id": "<subscription_id>",
            "resource_group_name": "<resource_group_name>",
            "project_name": "<project_name>",
        }
        eval_fn = ContentSafetyMultimodalEvaluator(azure_ai_project)
        result = eval_fn(
            messages= [
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
                    "content": "This picture shows an astronaut standing in desert."
                }
            ]
        )
        
    **Output format**
    .. code-block:: python
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
    
    def __init__(self, credential, azure_ai_project: dict, parallel: bool = False):
        self._parallel = parallel
        self._evaluators: List[Callable[..., Dict[str, Union[str, float]]]] = [
            ViolenceMultimodalEvaluator(azure_ai_project, credential),
            SexualMultimodalEvaluator(azure_ai_project, credential),
            SelfHarmMultimodalEvaluator(azure_ai_project, credential),
            HateUnfairnessMultimodalEvaluator(azure_ai_project, credential),
        ]

    def __call__(
            self, 
            *, 
            messages, 
            **kwargs):
        """
        Evaluates content-safety metrics for list of messages.
        :keyword messages: The messages to be evaluated. Each message should have "role" and "content" keys.
        :paramtype messages: Dict
        :return: The scores for messages.
        :rtype: Dict
        """
        self._validate_messages(messages)
        
        results: Dict[str, Union[str, float]] = {}
        if self._parallel:
            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(evaluator, messages=messages, **kwargs): evaluator
                    for evaluator in self._evaluators
                }

                for future in as_completed(futures):
                    results.update(future.result())
        else:
            for evaluator in self._evaluators:
                result = evaluator(messages=messages, **kwargs)
                results.update(result)

        return results
    
    def _validate_messages(self, messages):
        if messages is None or not isinstance(messages, list):
            msg = "messages parameter must be a list of JSON representation of chat messages or strong typed child class of ChatRequestMessage"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.CONTENT_SAFETY_MULTIMODAL_EVALUATOR,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )
        expected_roles = [ "user", "assistant", "system", "tool" ]
        image_found = False
        for num, message in enumerate(messages):
            msg_num = num + 1
            if not isinstance(message, dict) and not isinstance(message, ChatRequestMessage):
                msg = f"Messsage in array must be a dictionary or class of ChatRequestMessage [UserMessage, SystemMessage, AssistantMessage, ToolMessage]. Message number: {msg_num}"
                raise EvaluationException(
                    message=msg,
                    internal_message=msg,
                    target=ErrorTarget.CONTENT_SAFETY_MULTIMODAL_EVALUATOR,
                    category=ErrorCategory.INVALID_VALUE,
                    blame=ErrorBlame.USER_ERROR,
                )
            if isinstance(message, dict):
                if "role" in message or "content" in message:
                    if message["role"] not in expected_roles:
                        msg = f"Invalid role provided: {message['role']}. Message number: {msg_num}"
                        raise EvaluationException(
                            message=msg,
                            internal_message=msg,
                            target=ErrorTarget.CONTENT_SAFETY_MULTIMODAL_EVALUATOR,
                            category=ErrorCategory.INVALID_VALUE,
                            blame=ErrorBlame.USER_ERROR,
                        )
                    if not isinstance(message["content"], str) and not isinstance(message["content"], list):
                        msg = f"Content in each turn must be a string or array. Message number: {msg_num}"
                        raise EvaluationException(
                            message=msg,
                            internal_message=msg,
                            target=ErrorTarget.CONTENT_SAFETY_MULTIMODAL_EVALUATOR,
                            category=ErrorCategory.INVALID_VALUE,
                            blame=ErrorBlame.USER_ERROR,
                        )
                    if isinstance(message["content"], list):
                        for content in message["content"]:
                            if content.get("type") == "image_url":
                                image_url = content.get("image_url")
                                if image_url and 'url' in image_url:
                                    image_found = True
                                    
                    if isinstance(message["content"], dict):
                        msg = f"Content in each turn must be a string or array. Message number: {msg_num}"
                        raise EvaluationException(
                            message=msg,
                            internal_message=msg,
                            target=ErrorTarget.CONTENT_SAFETY_MULTIMODAL_EVALUATOR,
                            category=ErrorCategory.INVALID_VALUE,
                            blame=ErrorBlame.USER_ERROR,
                        )         
            if isinstance(message, ChatRequestMessage):
                if not isinstance(message, UserMessage) and not isinstance(message, AssistantMessage) and not isinstance(message, SystemMessage) and not isinstance(message, ToolMessage):
                    msg = f"Messsage in array must be a strongly typed class of ChatRequestMessage [UserMessage, SystemMessage, AssistantMessage, ToolMessage]. Message number: {msg_num}"
                    raise EvaluationException(
                        message=msg,
                        internal_message=msg,
                        target=ErrorTarget.CONTENT_SAFETY_MULTIMODAL_EVALUATOR,
                        category=ErrorCategory.INVALID_VALUE,
                        blame=ErrorBlame.USER_ERROR,
                    )  
                if message.content and isinstance(message.content, list):
                    image_items = [item for item in message.content if isinstance(item, ImageContentItem)]
                    if len(image_items) > 0:
                        image_found = True
        if image_found is False:    
            msg = f"Message needs to have multimodal input like images"
            raise EvaluationException(
                message=msg,
                internal_message=msg,
                target=ErrorTarget.CONTENT_SAFETY_MULTIMODAL_EVALUATOR,
                category=ErrorCategory.INVALID_VALUE,
                blame=ErrorBlame.USER_ERROR,
            )

        
    def _get_harm_severity_level(self, harm_score: float) -> Union[HarmSeverityLevel, float]:
        HARM_SEVERITY_LEVEL_MAPPING = {
            HarmSeverityLevel.VeryLow: (0, 1),
            HarmSeverityLevel.Low: (2, 3),
            HarmSeverityLevel.Medium: (4, 5),
            HarmSeverityLevel.High: (6, 7),
        }

        if math.isnan(harm_score) or harm_score is None:
            return math.nan

        for harm_level, harm_score_range in HARM_SEVERITY_LEVEL_MAPPING.items():
            if harm_score_range[0] <= harm_score <= harm_score_range[1]:
                return harm_level

        return math.nan