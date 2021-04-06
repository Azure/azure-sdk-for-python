# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.paging import ItemPaged
from azure.core.pipeline import Pipeline
from azure.core.tracing.decorator import distributed_trace

from ._base_client import ContainerRegistryBaseClient, TransportWrapper
from ._container_repository_client import ContainerRepositoryClient
from ._models import DeletedRepositoryResult

if TYPE_CHECKING:
    from typing import Any, Dict
    from azure.core.credentials import TokenCredential


class ContainerRegistryClient(ContainerRegistryBaseClient):
    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, TokenCredential, Dict[str, Any]) -> None
        """Create a ContainerRegistryClient from an ACR endpoint and a credential

        :param str endpoint: An ACR endpoint
        :param TokenCredential credential: The credential with which to authenticate
        :returns: None
        :raises: None
        """
        if not endpoint.startswith("https://") and not endpoint.startswith("http://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._credential = credential
        super(ContainerRegistryClient, self).__init__(endpoint=endpoint, credential=credential, **kwargs)

    @distributed_trace
    def delete_repository(self, repository, **kwargs):
        # type: (str, Dict[str, Any]) -> DeletedRepositoryResult
        """Delete a repository

        :param str repository: The repository to delete
        :returns: Object containing information about the deleted repository
        :rtype: :class:`~azure.containerregistry.DeletedRepositoryResult`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`
        """
        return DeletedRepositoryResult._from_generated(  # pylint: disable=protected-access
            self._client.container_registry.delete_repository(repository, **kwargs)
        )

    @distributed_trace
    def list_repositories(self, **kwargs):
        # type: (Dict[str, Any]) -> ItemPaged[str]
        """List all repositories

        :keyword max: Maximum number of repositories to return
        :type max: int
        :keyword last: Query parameter for the last item in the previous call. Ensuing
            call will return values after last lexically
        :type last: str
        :keyword results_per_page: Numer of repositories to return in a single page
        :type results_per_page: int
        :return: ItemPaged[str]
        :rtype: :class:`~azure.core.paging.ItemPaged`
        :raises: :class:`~azure.core.exceptions.ResourceNotFoundError`
        """
        return self._client.container_registry.get_repositories(
            last=kwargs.pop("last", None), n=kwargs.pop("max", None), **kwargs
        )

    @distributed_trace
    def get_repository_client(self, repository, **kwargs):
        # type: (str, Dict[str, Any]) -> ContainerRepositoryClient
        """Get a repository client

        :param str repository: The repository to create a client for
        :returns: :class:`~azure.containerregistry.ContainerRepositoryClient`
        :raises: None
        """
        _pipeline = Pipeline(
            transport=TransportWrapper(self._client._client._pipeline._transport),  # pylint: disable=protected-access
            policies=self._client._client._pipeline._impl_policies,  # pylint: disable=protected-access
        )
        return ContainerRepositoryClient(
            self._endpoint, repository, credential=self._credential, pipeline=_pipeline, **kwargs
        )
