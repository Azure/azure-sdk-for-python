# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, MutableMapping, Any

JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object

from azure.core.tracing.decorator import distributed_trace

from ._operations import ConversationAnalysisClientOperationsMixin as ConversationAnalysisClientOperationsMixinGenerated


class ConversationAnalysisClientOperationsMixin(ConversationAnalysisClientOperationsMixinGenerated):
    @distributed_trace
    async def analyze_conversation(self, task: JSON, **kwargs: Any) -> JSON:
        """Analyzes the input conversation utterance.

        :param task: A single conversational task to execute.
        :type task: JSON
        :return: JSON object
        :rtype: JSON
        :raises: ~azure.core.exceptions.HttpResponseError

        Example:
            .. code-block:: python

                # JSON input template you can fill out and use as your body input.
                task = {
                    "kind": "str", # Required. Enumeration of supported Conversation tasks. Known values are: "Conversation",
                    "analysisInput": {
                        "conversationItem": {
                            "id": "str", # Required. The ID of a conversation item.,
                            "participantId": "str", # Required. The participant ID of a conversation item.,
                            "role": "str", # Optional. The role of the participant. Known values are: "agent", "cutomer", and "generic".
                            "modality": "string", # Required, Enumeration of supported conversational modalities. Known values are: "text", and "transcript".,
                            "language": "str", # Optional. The override language of a conversation item in BCP 47 language representation.,
                            "text": "str", # Required. The text input.
                        }
                    },
                    "parameters": {
                        "projectName": "str", # Required. The name of the project to use.,
                        "deploymentName": "str", # Required. The name of the deployment to use.,
                        "verbose": "bool", # Optional. If true, the service will return more detailed information in the response.,
                        "isLoggingEnabled": "bool", # Optional. If true, the service will keep the query for further review.,
                        "directTarget": "str", # Optional. The name of a target project to forward the request to.
                    }
                }

                # response body for status code(s): 200
                response.json() == {
                    "kind": "str", # Required. Enumeration of supported conversational task results. Known values are: "ConversationResult",
                    "result": {
                        "query": "str", # Required. The conversation utterance given by the caller.,
                        "detectedLanguage": "str", # Optional. The system detected language for the query in BCP 47 language representation.,
                        "prediction": {
                            "topIntent": "str", # Required. The intent with the highest score.,
                            "projectKind": "str", # Required. The type of the project. Known values are: "Conversation", and "Orchestration",
                        }
                    }
                }
        """
        task["parameters"]["stringIndexType"] = "UnicodeCodePoint"
        return await super().analyze_conversation(task, **kwargs)


__all__: List[str] = [
    "ConversationAnalysisClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
