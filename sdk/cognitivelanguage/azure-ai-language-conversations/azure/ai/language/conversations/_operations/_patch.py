# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from async_timeout import Any
from ._operations import ConversationAnalysisClientOperationsMixin as ConversationAnalysisClientOperationsMixinGenerated
from azure.core.tracing.decorator import distributed_trace
from typing import List, MutableMapping

JSON = MutableMapping[str, Any] # pylint: disable=unsubscriptable-object

class ConversationAnalysisClientOperationsMixin(ConversationAnalysisClientOperationsMixinGenerated):
    @distributed_trace
    def analyze_text(
        self,
        query: str,
        project_name: str,
        deployment_name: str,
        **kwargs: Any
    ) -> JSON:
        """Analyzes the input conversation utterance.

        :param query: user query you want to analyze.
        :type task: str
        :param project_name: language project's name you're calling (conversation and workflow).
        :type project_name: str
        :param deployment_name: language project's deployment name you're calling.
        :type deployment_name: str
        :return: JSON object
        :rtype: JSON
        :raises: ~azure.core.exceptions.HttpResponseError

        """
        return self.analyze_conversation(
            task={
                "kind": "Conversation",
                "analysisInput": {
                    "conversationItem": {
                        "participantId": "1",
                        "id": "1",
                        "modality": "text",
                        "language": "en",
                        "text": query
                    },
                    "isLoggingEnabled": False
                },
                "parameters": {
                    "projectName": project_name,
                    "deploymentName": deployment_name,
                    "verbose": True
                }
            }
        )

__all__: List[str] = [
    "ConversationAnalysisClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
