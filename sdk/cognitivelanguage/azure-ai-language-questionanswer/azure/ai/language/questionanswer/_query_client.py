
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import (
    Union,
    Any,
    List,
    Dict,
    TYPE_CHECKING,
)
from azure.core.paging import ItemPaged
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import HttpResponseError
from ._generated_query import MicrosoftCognitiveLanguageService
from ._version import USER_AGENT

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


def _authentication_policy(credential):
    authentication_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(
            name="Ocp-Apim-Subscription-Key", credential=credential
        )
    elif credential is not None and not hasattr(credential, "get_token"):
        raise TypeError("Unsupported credential: {}. Use an instance of AzureKeyCredential "
                        "or a token credential from azure.identity".format(type(credential)))
    return authentication_policy


class QuestionAnsweringClient(object):
    """
    :param str endpoint: Supported Cognitive Services resource
        endpoints (protocol and hostname, for example: https://westus2.api.cognitive.microsoft.com).
    :param credential: Credentials needed for the client to connect to Azure.
        This can be the an instance of AzureKeyCredential if using a
        cognitive services/QuestionAnswering API key or a token credential
        from :mod:`azure.identity`.
    :type credential: :class:`~azure.core.credentials.AzureKeyCredential` or
        :class:`~azure.core.credentials.TokenCredential`
    :keyword api_version: The API version of the service to use for requests. It defaults to the
        latest service version. Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str
    """

    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, Union[AzureKeyCredential, TokenCredential], Any) -> None
        if not endpoint.startswith('http'):
            endpoint = "https://" + endpoint
        self._client = MicrosoftCognitiveLanguageService(
            endpoint=endpoint,
            credential=credential,
            sdk_moniker=USER_AGENT,
            authentication_policy=_authentication_policy(credential),
            **kwargs
        )
        self._client._config.api_version = kwargs.get('api_version')

    def __enter__(self):
        self._client.__enter__()  # pylint:disable=no-member
        return self

    def __exit__(self, *args):
        self._client.__exit__(*args)  # pylint:disable=no-member

    def close(self):
        # type: () -> None
        """Close sockets opened by the client.
        Calling this method is unnecessary when using the client as a context manager.
        """
        self._client.close()
    
    def send_request(self, request, **kwargs):
        """Runs the network request through the client's chained policies.
        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest("GET", "http://localhost:3000/helloWorld")
        <HttpRequest [GET], url: 'http://localhost:3000/helloWorld'>
        >>> response = client.send_request(request)
        <HttpResponse: 200 OK>
        For more information on this code flow, see https://aka.ms/azsdk/python/protocol/quickstart
        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.HttpResponse
        """
        return self._client._send_request(request, **kwargs)

    def query_text(
        self,
        text_query_parameters,  # type: "TextQueryParameters"
        **kwargs  # type: Any
    ):
        # type: (...) -> "TextAnswers"
        """Answers the specified question using the provided text in the body.

        Answers the specified question using the provided text in the body.

        :param text_query_parameters: Post body of the request.
        :type text_query_parameters: ~microsoft_cognitive_language_service.models.TextQueryParameters
        :return: TextAnswers, or the result of cls(response)
        :rtype: ~microsoft_cognitive_language_service.models.TextAnswers
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.question_answering_text.query(
            text_query_parameters=text_query_parameters,
            **kwargs
        )

    def query_knowledgebase(
        self,
        project_name,  # type: str
        knowledgebase_query_parameters,  # type: "KnowledgebaseQueryParameters"
        **kwargs  # type: Any
    ):
        # type: (...) -> "KnowledgebaseAnswers"
        """Answers the specified question using your knowledgebase.

        Answers the specified question using your knowledgebase.

        :param project_name: The name of the project to use.
        :type project_name: str
        :param knowledgebase_query_parameters: Post body of the request.
        :type knowledgebase_query_parameters:
         ~azure.ai.language.questionanswering.KnowledgebaseQueryParameters
        :keyword deployment_name: The name of the specific deployment of the project to use.
        :paramtype deployment_name: str
        :return: KnowledgebaseAnswers
        :rtype: ~azure.ai.language.questionanswering.KnowledgebaseAnswers
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.question_answering_knowledgebase.query(
            project_name=project_name,
            knowledgebase_query_parameters=knowledgebase_query_parameters,
            **kwargs
        )