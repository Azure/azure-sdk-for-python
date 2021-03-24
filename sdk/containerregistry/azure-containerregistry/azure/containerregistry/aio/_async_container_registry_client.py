# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.async_paging import AsyncItemPaged

from ._async_base_client import ContainerRegistryBaseClient
from .._container_registry_client import ContainerRegistryClient as SyncContainerRegistryClient
from .._models import RepositoryProperties

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


    def delete_repository(self, name: str, **kwargs) -> None:
        pass

    def list_repositories(self, **kwargs) -> AsyncItemPaged[str]:

        return self._client.container_registry.get_repositories(
            last=kwargs.pop("last", None), n=kwargs.pop("max", None), **kwargs
        )


    def get_repository_client(self, name: str, **kwargs) -> SyncContainerRegistryClient:
        pass