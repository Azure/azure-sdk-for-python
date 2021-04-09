# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Dict, TYPE_CHECKING

from azure.core.async_paging import AsyncItemPaged, AsyncList
from azure.core.exceptions import (
    ClientAuthenticationError,
    ResourceExistsError,
    ResourceNotFoundError,
    HttpResponseError,
    map_error,
)
from azure.core.pipeline import AsyncPipeline
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from ._async_base_client import ContainerRegistryBaseClient, AsyncTransportWrapper
from ._async_container_repository_client import ContainerRepositoryClient
from .._generated.models import AcrErrors
from .._helpers import _parse_next_link
from .._models import RepositoryProperties, DeletedRepositoryResult

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class ContainerRegistryClient(ContainerRegistryBaseClient):
    def __init__(self, endpoint: str, credential: "AsyncTokenCredential", **kwargs: Dict[str, Any]) -> None:
        """Create a ContainerRegistryClient from an endpoint and a credential

        :param endpoint: An ACR endpoint
        :type endpoint: str
        :param credential: The credential with which to authenticate
        :type credential: :class:`~azure.core.credentials_async.AsyncTokenCredential`
        :returns: None
        :raises: None
        """
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._credential = credential
        super(ContainerRegistryClient, self).__init__(endpoint=endpoint, credential=credential, **kwargs)

    @distributed_trace_async
    async def delete_repository(self, repository: str, **kwargs: Dict[str, Any]) -> DeletedRepositoryResult:
        """Delete a repository

        :param repository: The repository to delete
        :type repository: str
        :returns: Object containing information about the deleted repository
        :rtype: :class:`~azure.containerregistry.DeletedRepositoryResult`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`
        """
        result = await self._client.container_registry.delete_repository(repository, **kwargs)
        return DeletedRepositoryResult._from_generated(result)  # pylint: disable=protected-access

    @distributed_trace
    def list_repositories(self, **kwargs: Dict[str, Any]) -> AsyncItemPaged[str]:
        """List all repositories

        :keyword last: Query parameter for the last item in the previous call. Ensuing
            call will return values after last lexicallyy
        :paramtype last: str
        :keyword max: Maximum number of repositories to return
        :paramtype max: int
        :keyword results_per_page: Number of repositories to return per page
        :paramtype results_per_page: int
        :return: ItemPaged[str]
        :rtype: :class:`~azure.core.async_paging.AsyncItemPaged`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`
        """
        n = kwargs.pop("results_per_page", None)
        last = kwargs.pop("last", None)

        cls = kwargs.pop("cls", None)
        error_map = {401: ClientAuthenticationError, 404: ResourceNotFoundError, 409: ResourceExistsError}
        error_map.update(kwargs.pop("error_map", {}))
        accept = "application/json"

        def prepare_request(next_link=None):
            # Construct headers
            header_parameters = {}  # type: Dict[str, Any]
            header_parameters["Accept"] = self._client._serialize.header(  # pylint: disable=protected-access
                "accept", accept, "str"
            )

            if not next_link:
                # Construct URL
                url = "/acr/v1/_catalog"
                path_format_arguments = {
                    "url": self._client._serialize.url(  # pylint: disable=protected-access
                        "self._config.url",
                        self._client._config.url,  # pylint: disable=protected-access
                        "str",
                        skip_quote=True,
                    ),
                }
                url = self._client._client.format_url(url, **path_format_arguments)  # pylint: disable=protected-access
                # Construct parameters
                query_parameters = {}  # type: Dict[str, Any]
                if last is not None:
                    query_parameters["last"] = self._client._serialize.query(  # pylint: disable=protected-access
                        "last", last, "str"
                    )
                if n is not None:
                    query_parameters["n"] = self._client._serialize.query(  # pylint: disable=protected-access
                        "n", n, "int"
                    )

                request = self._client._client.get(  # pylint: disable=protected-access
                    url, query_parameters, header_parameters
                )
            else:
                url = next_link
                query_parameters = {}  # type: Dict[str, Any]
                path_format_arguments = {
                    "url": self._client._serialize.url(  # pylint: disable=protected-access
                        "self._config.url",
                        self._client._config.url,  # pylint: disable=protected-access
                        "str",
                        skip_quote=True,
                    ),
                }
                url = self._client._client.format_url(url, **path_format_arguments)  # pylint: disable=protected-access
                request = self._client._client.get(  # pylint: disable=protected-access
                    url, query_parameters, header_parameters
                )
            return request

        async def extract_data(pipeline_response):
            deserialized = self._client._deserialize(  # pylint: disable=protected-access
                "Repositories", pipeline_response
            )
            list_of_elem = deserialized.repositories
            if cls:
                list_of_elem = cls(list_of_elem)
            link = None
            if "Link" in pipeline_response.http_response.headers.keys():
                link = _parse_next_link(pipeline_response.http_response.headers["Link"])
            return link, AsyncList(list_of_elem)

        async def get_next(next_link=None):
            request = prepare_request(next_link)

            pipeline_response = await self._client._client._pipeline.run(  # pylint: disable=protected-access
                request, stream=False, **kwargs
            )
            response = pipeline_response.http_response

            if response.status_code not in [200]:
                error = self._client._deserialize.failsafe_deserialize(  # pylint: disable=protected-access
                    AcrErrors, response
                )
                map_error(status_code=response.status_code, response=response, error_map=error_map)
                raise HttpResponseError(response=response, model=error)

            return pipeline_response

        return AsyncItemPaged(get_next, extract_data)

    @distributed_trace
    def get_repository_client(self, repository: str, **kwargs: Dict[str, Any]) -> ContainerRepositoryClient:
        """Get a repository client

        :param repository: The repository to create a client for
        :type repository: str
        :returns: :class:`~azure.containerregistry.aio.ContainerRepositoryClient`
        """
        _pipeline = AsyncPipeline(
            transport=AsyncTransportWrapper(
                self._client._client._pipeline._transport  # pylint: disable=protected-access
            ),
            policies=self._client._client._pipeline._impl_policies,  # pylint: disable=protected-access
        )
        return ContainerRepositoryClient(
            self._endpoint, repository, credential=self._credential, pipeline=_pipeline, **kwargs
        )
