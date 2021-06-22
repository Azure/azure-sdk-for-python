
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
from ._generated_author import MicrosoftCognitiveLanguageService
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

    def list_projects(
        self, **kwargs  # type: Any
    ):
        # type: (...) -> "ItemPaged[ProjectMetadata]"
        """Gets all projects for a user.

        Gets all projects for a user.

        :return: An iterable of ProjectMetadata
        :rtype: ~azure.core.ItemPaged[ProjectMetadata]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        # TODO: wrap in ItemPaged
        return self._client.question_answering_projects.list_projects(**kwargs)

    def get_project_details(
        self,
        project_name,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> "ProjectMetadata"
        """Get the requested project metadata.

        Get the requested project metadata.

        :param project_name: The name of the project to use.
        :type project_name: str
        :return: ProjectMetadata
        :rtype: ~azure.ai.language.questionanswering.ProjectMetadata
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.question_answering_projects.get_project_details(
            project_name=project_name,
            **kwargs
        )

    def create_project(
        self,
        project_name,  # type: str
        project,  # type: "CreateProjectParameters"
        **kwargs  # type: Any
    ):
        # type: (...) -> "ProjectMetadata"
        """Create or update a project.

        Create or update a project.

        :param project_name: The name of the project to use.
        :type project_name: str
        :param project: Parameters needed to create the project.
        :type project: ~azure.ai.language.questionanswering.CreateProjectParameters
        :return: ProjectMetadata
        :rtype: ~azure.ai.language.questionanswering.ProjectMetadata
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.question_answering_projects.create_project(
            project_name=project_name,
            body=project,
            **kwargs
        )

    def delete_project(
        self,
        project_name,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        """Delete the project.

        Delete the project.

        :param project_name: The name of the project to use.
        :type project_name: str
        :return: None
        :rtype: None
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.question_answering_projects.delete_project(
            project_name=project_name,
            **kwargs
        )

    def begin_export(
        self,
        project_name,  # type: str
        export_job=None,  # type: Optional["ExportJobParameters"]
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller[ExportResult]
        """Export project metadata and assets.

        Export project metadata and assets.

        :param project_name: The name of the project to use.
        :type project_name: str
        :keyword format: Knowledgebase Import or Export format.
        :paramtype format: str or ~azure.ai.language.questionanswering.Format
        :param body: Parameters required for export project job.
        :type body: ~azure.ai.language.questionanswering.ExportJobParameters
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be LROBasePolling. Pass in False for
         this operation to not poll, or pass in your own initialized polling object for a personal
         polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
         Retry-After header is present.
        :return: An instance of LROPoller that returns either None or the result of cls(response)
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        # TODO: Convert ExportJobState into ExportResult with result_url
        return self._client.question_answering_projects.begin_export(
            project_name=project_name,
            body=export_job,
            **kwargs
        )

    def begin_import(
        self,
        project_name,  # type: str
        import_job=None,  # type: Optional["ImportJobParameters"]
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller[None]
        """Import project assets.

        Import project assets.

        :param project_name: The name of the project to use.
        :type project_name: str
        :keyword format: Knowledgebase Import or Export format.
        :paramtype format: str or ~azure.ai.language.questionanswering.Format
        :param body: Project assets the needs to be imported.
        :type body: ~azure.ai.language.questionanswering.ImportJobParameters
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be LROBasePolling. Pass in False for
         this operation to not poll, or pass in your own initialized polling object for a personal
         polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
         Retry-After header is present.
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.question_answering_projects.begin_import_method(
            project_name=project_name,
            body=import_job,
            **kwargs
        )


    def begin_deploy_project(
        self,
        project_name,  # type: str
        deployment_name,  # type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller[None]
        """Deploy project to production.

        Deploy project to production.

        :param project_name: The name of the project to use.
        :type project_name: str
        :param deployment_name: The name of the specific deployment of the project to use.
        :type deployment_name: str
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be LROBasePolling. Pass in False for
         this operation to not poll, or pass in your own initialized polling object for a personal
         polling strategy.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
         Retry-After header is present.
        :return: An instance of LROPoller that returns None
        :rtype: ~azure.core.polling.LROPoller[None]
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        return self._client.question_answering_projects.begin_deploy_project(
            project_name=project_name,
            deployment_name=deployment_name,
            **kwargs
        )
