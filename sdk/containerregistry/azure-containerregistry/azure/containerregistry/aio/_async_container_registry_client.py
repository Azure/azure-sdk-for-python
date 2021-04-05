# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Dict, TYPE_CHECKING

from azure.core.async_paging import AsyncItemPaged
from azure.core.pipeline import AsyncPipeline
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from ._async_base_client import ContainerRegistryBaseClient, AsyncTransportWrapper
from ._async_container_repository_client import ContainerRepositoryClient
from .._models import RepositoryProperties, DeletedRepositoryResult

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class ContainerRegistryClient(ContainerRegistryBaseClient):
    def __init__(self, endpoint: str, credential: "AsyncTokenCredential", **kwargs: Dict[str, Any]) -> None:
        """Create a ContainerRegistryClient from an endpoint and a credential

        :param endpoint: An ACR endpoint
        :type endpoint: str
        :param credential: The credential with which to authenticate
        :type credential: AsyncTokenCredential
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
        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        result = await self._client.container_registry.delete_repository(repository, **kwargs)
        return DeletedRepositoryResult._from_generated(result)  # pylint: disable=protected-access

    @distributed_trace
    def list_repositories(self, **kwargs) -> AsyncItemPaged[str]:

        return self._client.container_registry.get_repositories(
            last=kwargs.pop("last", None), n=kwargs.pop("page_size", None), **kwargs
        )

    @distributed_trace
    def get_repository_client(self, repository: str, **kwargs) -> ContainerRepositoryClient:
        # type: (str, Dict[str, Any]) -> ContainerRepositoryClient
        """Get a repository client

        :param repository: The repository to create a client for
        :type repository: str
        :returns: :class:~azure.containerregistry.aio.ContainerRepositoryClient
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
