
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
    Optional
)
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.credentials import AzureKeyCredential
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import HttpResponseError
from .._generated_author.aio import MicrosoftCognitiveLanguageService
from .._version import USER_AGENT

if TYPE_CHECKING:
    from azure.core.async_credentials import AsyncTokenCredential


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


class KnowledgebaseAuthoringClient(object):
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

    def __init__(self, endpoint: str, credential: Union[AzureKeyCredential, 'AsyncTokenCredential'], **kwargs):
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

    async def __aenter__(self) -> "KnowledgebaseAuthoringClient":
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *args: "Any") -> None:
        await self._client.__aexit__(*args)

    async def close(self) -> None:
        """Close sockets opened by the client.
        Calling this method is unnecessary when using the client as a context manager.
        """
        await self._client.__aexit__()
    
    def send_request(self, request, **kwargs):
        """Runs the network request through the client's chained policies.
        >>> from azure.core.rest import HttpRequest
        >>> request = HttpRequest("GET", "http://localhost:3000/helloWorld")
        <HttpRequest [GET], url: 'http://localhost:3000/helloWorld'>
        >>> response = await client.send_request(request)
        <AsyncHttpResponse: 200 OK>
        For more information on this code flow, see https://aka.ms/azsdk/python/protocol/quickstart
        :param request: The network request you want to make. Required.
        :type request: ~azure.core.rest.HttpRequest
        :keyword bool stream: Whether the response payload will be streamed. Defaults to False.
        :return: The response of your network call. Does not do error handling on your response.
        :rtype: ~azure.core.rest.AsyncHttpResponse
        """
        return self._client._send_request(request, **kwargs)

    def list_projects(self, **kwargs: Any) -> "AsyncItemPaged[ProjectMetadata]":
        """Gets all projects for a user.

        Gets all projects for a user.

        :return: An iterable of ProjectMetadata
        :rtype: ~azure.core.AsyncItemPaged[ProjectMetadata]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        self._client.question_answering_projects.list_projects(**kwargs)

    async def get_project_details(self, project_name: str, **kwargs: Any) -> "ProjectMetadata":
        """Get the requested project metadata.

        Get the requested project metadata.

        :param project_name: The name of the project to use.
        :type project_name: str
        :return: ProjectMetadata
        :rtype: ~azure.ai.language.questionanswering.ProjectMetadata
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return await self._client.question_answering_projects.get_project_details(
            project_name=project_name,
            **kwargs
        )

    async def create_project(
        self, project_name: str, project: "CreateProjectParameters", **kwargs: Any
    ) -> "ProjectMetadata":
        """Create or update a project.

        Create or update a project.

        :param project_name: The name of the project to use.
        :type project_name: str
        :param body: Parameters needed to create the project.
        :type body: ~microsoft_cognitive_language_service.models.CreateProjectParameters
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: ProjectMetadata, or the result of cls(response)
        :rtype: ~microsoft_cognitive_language_service.models.ProjectMetadata
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return await self._client.question_answering_projects.create_project(
            project_name=project_name,
            body=project,
            **kwargs
        )

    async def delete_project(self, project_name: str, **kwargs: Any) -> None:
        """Delete the project.

        Delete the project.

        :param project_name: The name of the project to use.
        :type project_name: str
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return await self._client.question_answering_projects.delete_project(
            project_name=project_name,
            **kwargs
        )

    async def begin_export(
        self,
        project_name: str,
        export_job: Optional["ExportJobParameters"] = None,
        *,
        format: Optional[Union[str, "Format"]] = "json",
        **kwargs: Any
    ) -> AsyncLROPoller["ExportResult"]:
        """Export project metadata and assets.

        Export project metadata and assets.

        :param project_name: The name of the project to use.
        :type project_name: str
        :keyword format: Knowledgebase Import or Export format.
        :paramtype format: str or ~microsoft_cognitive_language_service.models.Format
        :param body: Parameters required for export project job.
        :type body: ~microsoft_cognitive_language_service.models.ExportJobParameters
        :keyword callable cls: A custom type or function that will be passed the direct response
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be AsyncLROBasePolling. Pass in False
         for this operation to not poll, or pass in your own initialized polling object for a personal
         polling strategy.
        :paramtype polling: bool or ~azure.core.polling.AsyncPollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
         Retry-After header is present.
        :return: An instance of AsyncLROPoller that returns either None or the result of cls(response)
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        # TODO: Convert ExportJobState into ExportResult with result_url
        return self._client.question_answering_projects.begin_export(
            project_name=project_name,
            body=export_job,
            format=format,
            **kwargs
        )

    async def begin_import(
        self,
        project_name: str,
        import_job: Optional["ImportJobParameters"] = None,
        *,
        format: Optional[Union[str, "Format"]] = "json",
        **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Import project assets.

        Import project assets.

        :param project_name: The name of the project to use.
        :type project_name: str
        :keyword format: Knowledgebase Import or Export format.
        :paramtype format: str or ~microsoft_cognitive_language_service.models.Format
        :param body: Project assets the needs to be imported.
        :type body: ~microsoft_cognitive_language_service.models.ImportJobParameters
        :keyword callable cls: A custom type or function that will be passed the direct response
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be AsyncLROBasePolling. Pass in False
         for this operation to not poll, or pass in your own initialized polling object for a personal
         polling strategy.
        :paramtype polling: bool or ~azure.core.polling.AsyncPollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
         Retry-After header is present.
        :return: An instance of AsyncLROPoller that returns either None or the result of cls(response)
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.question_answering_projects.begin_import_method(
            project_name=project_name,
            body=import_job,
            format=format,
            **kwargs
        )

    async def begin_deploy_project(
        self, project_name: str, deployment_name: str, **kwargs: Any
    ) -> AsyncLROPoller[None]:
        """Deploy project to production.

        Deploy project to production.

        :param project_name: The name of the project to use.
        :type project_name: str
        :param deployment_name: The name of the specific deployment of the project to use.
        :type deployment_name: str
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be AsyncLROBasePolling. Pass in False
         for this operation to not poll, or pass in your own initialized polling object for a personal
         polling strategy.
        :paramtype polling: bool or ~azure.core.polling.AsyncPollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
         Retry-After header is present.
        :return: An instance of AsyncLROPoller that returns either None or the result of cls(response)
        :rtype: ~azure.core.polling.AsyncLROPoller[None]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.question_answering_projects.begin_deploy_project(
            project_name=project_name,
            deployment_name=deployment_name,
            **kwargs
        )