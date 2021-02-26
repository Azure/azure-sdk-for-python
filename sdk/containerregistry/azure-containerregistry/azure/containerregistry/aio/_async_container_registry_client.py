# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import TYPE_CHECKING

from azure.core.async_paging import AsyncItemPaged
from .._container_repository_client import ContainerRepositoryClient
from .._models import (
    RepositoryAttributes
)

if TYPE_CHECKING:
    from azure.core.async_credentials import AsyncTokenCredential

class ContainerRegistryClient(object):
    def __init__(self, base_url: str, credential: "AsyncTokenCredential", **kwargs):
        pass

    def delete_repository(self, name: str, **kwargs) -> None:
        pass

    def list_repositories(self, **kwargs) -> AsyncItemPaged[str]:
        pass

    def get_repository_client(self, name: str, **kwargs) -> ContainerRepositoryClient:
        pass

    def get_repository_attributes(self, name: str, **kwargs) -> RepositoryAttributes:
        pass
