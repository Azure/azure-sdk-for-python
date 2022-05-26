# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from ctypes import cast
from typing import List, MutableMapping
from async_timeout import Any
JSON = MutableMapping[str, Any] # pylint: disable=unsubscriptable-object

from azure.core.tracing.decorator import distributed_trace

from _operations import ConversationAnalysisClientOperationsMixin as ConversationAnalysisClientOperationsMixinGenerated

class ConversationAnalysisClientOperationsMixin(ConversationAnalysisClientOperationsMixinGenerated):
        @distributed_trace
        def analyze_conversation(
            self,
            task: JSON,
            **kwargs: Any
        ) -> JSON:
            """Analyzes the input conversation utterance.

            :param task: A single conversational task to execute.
            :type task: JSON
            :return: JSON object
            :rtype: JSON
            :raises: ~azure.core.exceptions.HttpResponseError

            Example:
                .. code-block:: python

                    kind = 'Conversation'

                    # JSON input template you can fill out and use as your body input.
                    task = {
                        "kind": "Conversation",
                        "analysisInput": {
                            "conversationItem": {
                                "id": "",
                                "participantId": "",
                                "modality": "text",
                                "language": "",
                                "text": ""
                            }
                        },
                        "parameters": {
                            "projectName": "",
                            "deploymentName": "",
                        }
                    }

                    # response body for status code(s): 200
                    response.json() == {
                        "kind": "ConversationResult",
                        "result": {
                        "query": "",
                            "prediction": {
                                "topIntent": "",
                                "projectKind": "Conversation",
                                "intents": [
                                    {
                                        "category": "",
                                        "confidenceScore": 1
                                    },
                                    {
                                        "category": "",
                                        "confidenceScore": 0
                                    },
                                    {
                                        "category": "",
                                        "confidenceScore": 0
                                    }
                                ],
                                "entities": [
                                    {
                                        "category": "",
                                        "text": "",
                                        "offset": 29,
                                        "length": 12,
                                        "confidenceScore": 1
                                    }
                                ]
                            }
                        }
                    }
            """
            return super().analyze_conversation(task, **kwargs)


__all__: List[str] = [
    "ConversationAnalysisClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
