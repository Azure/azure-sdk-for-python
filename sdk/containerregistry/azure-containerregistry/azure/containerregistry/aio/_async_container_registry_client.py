# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.async_paging import AsyncItemPaged

from .._container_registry_client import ContainerRegistryClient as SyncContainerRegistryClient
from .._models import RepositoryProperties

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential


class ContainerRegistryClient(object):
    def __init__(
        self, base_url: str, credential: "AsyncTokenCredential", **kwargs
    ):  # pylint: disable=client-method-missing-type-annotations
        pass

    def delete_repository(self, name: str, **kwargs) -> None:
        pass

    def list_repositories(self, **kwargs) -> AsyncItemPaged[str]:
        pass

    def get_repository_client(self, name: str, **kwargs) -> SyncContainerRegistryClient:
        pass

    def get_repository_attributes(self, name: str, **kwargs) -> RepositoryProperties:
        pass
