# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Dict, TYPE_CHECKING

from azure.core.async_paging import AsyncItemPaged, AsyncList
from azure.core.exceptions import ClientAuthenticationError, ResourceExistsError, ResourceNotFoundError

from ._async_base_client import ContainerRegistryBaseClient
from ._async_container_repository_client import ContainerRepositoryClient
from .._helpers import _parse_next_link
from .._models import RepositoryProperties, DeletedRepositoryResult

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class ContainerRegistryClient(ContainerRegistryBaseClient):
    def __init__(
        self, endpoint: str, credential: "AsyncTokenCredential", **kwargs
    ):  # pylint: disable=client-method-missing-type-annotations
        if not endpoint.startswith("https://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._credential = credential
        super(ContainerRegistryClient, self).__init__(endpoint=endpoint, credential=credential, **kwargs)

    async def delete_repository(self, repository: str, **kwargs: Dict[str, Any]) -> DeletedRepositoryResult:
        """Delete a repository

        :param repository: The repository to delete
        :type repository: str
        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        result = await self._client.container_registry.delete_repository(repository, **kwargs)
        return DeletedRepositoryResult._from_generated(result)  # pylint: disable=protected-access

    async def list_repositories(self, **kwargs) -> AsyncItemPaged[str]:
        """List all repositories

        :keyword max: Maximum number of repositories to return
        :type max: int
        :keyword last: Query parameter for the last item in previous query
        :type last: str
        :returns: ~azure.core.paging.AsyncItemPaged[str]
        :raises: ResourceNotFoundError
        """
        n = kwargs.pop("page_size", None)
        last = kwargs.pop("last", None)

        cls = kwargs.pop('cls', None)
        error_map = {
            401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError
        }
        error_map.update(kwargs.pop('error_map', {}))
        accept = "application/json"

        def prepare_request(next_link=None):
            # Construct headers
            header_parameters = {}  # type: Dict[str, Any]
            header_parameters['Accept'] = self._client._serialize.header("accept", accept, 'str')

            if not next_link:
                # Construct URL
                url = '/acr/v1/_catalog'
                path_format_arguments = {
                    'url': self._client._serialize.url("self._config.url", self._client._config.url, 'str', skip_quote=True),
                }
                url = self._client._client.format_url(url, **path_format_arguments)
                # Construct parameters
                query_parameters = {}  # type: Dict[str, Any]
                if last is not None:
                    query_parameters['last'] = self._client._serialize.query("last", last, 'str')
                if n is not None:
                    query_parameters['n'] = self._client._serialize.query("n", n, 'int')

                request = self._client._client.get(url, query_parameters, header_parameters)
            else:
                url = next_link
                query_parameters = {}  # type: Dict[str, Any]
                path_format_arguments = {
                    'url': self._client._serialize.url("self._config.url", self._client._config.url, 'str', skip_quote=True),
                }
                url = self._client._client.format_url(url, **path_format_arguments)
                request = self._client._client.get(url, query_parameters, header_parameters)
            return request

        async def extract_data(pipeline_response):
            deserialized = self._client._deserialize('Repositories', pipeline_response)
            list_of_elem = deserialized.repositories
            if cls:
                list_of_elem = cls(list_of_elem)
            link = None
            if "Link" in pipeline_response.http_response.headers.keys():
                link = _parse_next_link(pipeline_response.http_response.headers["Link"])
            return link, AsyncList(list_of_elem)

        async def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = await self._client._client._pipeline.run(request, stream=False, **kwargs)
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                error = self._client._deserialize.failsafe_deserialize(_models.AcrErrors, response)
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response, model=error)

            return pipeline_response

        return AsyncItemPaged(
            get_next, extract_data
        )

    def get_repository_client(self, name: str, **kwargs) -> ContainerRepositoryClient:

        return ContainerRepositoryClient(self._endpoint, name, self._credential, **kwargs)
