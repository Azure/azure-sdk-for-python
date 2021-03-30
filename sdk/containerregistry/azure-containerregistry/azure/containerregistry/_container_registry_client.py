# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING
from azure.core.paging import ItemPaged

from ._base_client import ContainerRegistryBaseClient
from ._container_repository_client import ContainerRepositoryClient
from ._models import DeletedRepositoryResult

if TYPE_CHECKING:
    from typing import Any, Dict
    from azure.core.credentials import TokenCredential


class ContainerRegistryClient(ContainerRegistryBaseClient):
    def __init__(self, endpoint, credential, **kwargs):
        # type: (str, TokenCredential, Dict[str, Any]) -> None
        """Create a ContainerRegistryClient from an ACR endpoint and a credential

        :param endpoint: An ACR endpoint
        :type endpoint: str
        :param credential: The credential with which to authenticate
        :type credential: TokenCredential
        :returns: None
        :raises: None
        """
        if not endpoint.startswith("https://"):
            endpoint = "https://" + endpoint
        self._endpoint = endpoint
        self._credential = credential
        super(ContainerRegistryClient, self).__init__(endpoint=endpoint, credential=credential, **kwargs)

    def delete_repository(self, repository, **kwargs):
        # type: (str, Dict[str, Any]) -> DeletedRepositoryResult
        """Delete a repository

        :param repository: The repository to delete
        :type repository: str
        :returns: None
        :raises: :class:~azure.core.exceptions.ResourceNotFoundError
        """
        # NOTE: DELETE `/acr/v1/{name}`
        deleted_repository = self._client.container_registry.delete_repository(repository, **kwargs)
        return DeletedRepositoryResult._from_generated(deleted_repository)  # pylint: disable=protected-access

    def list_repositories(self, **kwargs):
        # type: (Dict[str, Any]) -> ItemPaged[str]
        """List all repositories

        :keyword max: Maximum number of repositories to return
        :type max: int
        :keyword last: Query parameter for the last item in previous query
        :type last: str
        :returns: ~azure.core.paging.ItemPaged[str]
        :raises: None
        """
        return self._client.container_registry.get_repositories(
            last=kwargs.pop("last", None), n=kwargs.pop("max", None), **kwargs
        )

    def get_repository_client(self, repository, **kwargs):
        # type: (str, Dict[str, Any]) -> ContainerRepositoryClient
        """Get a repository client

        :param repository: The repository to create a client for
        :type repository: str
        :returns: :class:~azure.containerregistry.ContainerRepositoryClient
        """
        return ContainerRepositoryClient(self._endpoint, repository, credential=self._credential, **kwargs)
