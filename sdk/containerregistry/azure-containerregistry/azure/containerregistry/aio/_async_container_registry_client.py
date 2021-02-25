# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


class ContainerRegistryClient(object):
    def __init__(self, base_url: str, credential: TokenCredential, **kwargs):
        pass

    def delete_repository(self, name: str, **kwargs) -> None:
        pass

    def list_repositories(self, **kwargs) -> Pageable[str]:
        pass

    def get_repository_client(self, name: str, **kwargs) -> ContainerRepositoryClient:
        pass

    def get_repository_attributes(self, name: str, **kwargs) -> RepositoryAttributes:
        pass
