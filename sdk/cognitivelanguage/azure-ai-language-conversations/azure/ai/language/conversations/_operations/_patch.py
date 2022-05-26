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

from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ResourceExistsError, ResourceNotFoundError, map_error
from azure.core.utils import case_insensitive_dict
from azure.core.tracing.decorator import distributed_trace

from _operations import ConversationAnalysisClientOperationsMixin as ConversationAnalysisClientOperationsMixinGenerated
from _operations import build_analyze_conversation_request

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
            error_map = {
                401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
            }
            error_map.update(kwargs.pop('error_map', {}) or {})

            _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
            _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

            api_version = kwargs.pop('api_version', _params.pop('api-version', "2022-05-15-preview"))  # type: str
            content_type = kwargs.pop('content_type', _headers.pop('Content-Type', "application/json"))  # type: Optional[str]
            cls = kwargs.pop('cls', None)  # type: ClsType[JSON]

            _json = task

            request = build_analyze_conversation_request(
                api_version=api_version,
                content_type=content_type,
                json=_json,
                headers=_headers,
                params=_params,
            )
            path_format_arguments = {
                "Endpoint": self._serialize.url("self._config.endpoint", self._config.endpoint, 'str', skip_quote=True),
            }
            request.url = self._client.format_url(request.url, **path_format_arguments)  # type: ignore

            pipeline_response = self._client._pipeline.run(  # type: ignore # pylint: disable=protected-access
                request,
                stream=False,
                **kwargs
            )
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response)

            if response.content:
                deserialized = response.json()
            else:
                deserialized = None

            if cls:
                return cls(pipeline_response, cast(JSON, deserialized), {})

            return cast(JSON, deserialized)


__all__: List[str] = [
    "ConversationAnalysisClientOperationsMixin"
]  # Add all objects you want publicly available to users at this package level

def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
