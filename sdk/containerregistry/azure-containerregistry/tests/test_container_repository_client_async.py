# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from devtools_testutils import AzureTestCase

from azure.containerregistry import (
    DeletedRepositoryResult,
    RepositoryProperties,
)
from azure.containerregistry.aio import ContainerRegistryClient, ContainerRepositoryClient
from azure.core.exceptions import ResourceNotFoundError
from azure.core.paging import ItemPaged

from asynctestcase import AsyncContainerRegistryTestClass
from preparer import acr_preparer
from constants import TO_BE_DELETED


class TestContainerRegistryClient(AsyncContainerRegistryTestClass):
    @acr_preparer()
    async def test_delete_tag(self, containerregistry_baseurl, containerregistry_resource_group):
        repo = self.get_resource_name("repo")
        self._import_tag_to_be_deleted(containerregistry_baseurl, resource_group=containerregistry_resource_group, repository=repo, tag=TO_BE_DELETED)

        client = self.create_repository_client(containerregistry_baseurl, repo)

        tag = await client.get_tag_properties(TO_BE_DELETED)
        assert tag is not None

        await client.delete_tag(TO_BE_DELETED)
        self.sleep(5)

        with pytest.raises(ResourceNotFoundError):
            await client.get_tag_properties(TO_BE_DELETED)

    @acr_preparer()
    async def test_delete_repository(self, containerregistry_baseurl, containerregistry_resource_group):
        self.import_repo_to_be_deleted(containerregistry_baseurl, resource_group=containerregistry_resource_group)

        reg_client = self.create_registry_client(containerregistry_baseurl)
        existing_repos = []
        async for repo in reg_client.list_repositories():
            existing_repos.append(repo)
        assert TO_BE_DELETED in existing_repos

        repo_client = self.create_repository_client(containerregistry_baseurl, TO_BE_DELETED)
        await repo_client.delete()
        self.sleep(5)

        existing_repos = []
        async for repo in reg_client.list_repositories():
            existing_repos.append(repo)
        assert TO_BE_DELETED not in existing_repos

    @acr_preparer()
    async def test_delete_repository_doesnt_exist(self, containerregistry_baseurl):
        DOES_NOT_EXIST = "does_not_exist"

        repo_client = self.create_repository_client(containerregistry_baseurl, DOES_NOT_EXIST)
        with pytest.raises(ResourceNotFoundError):
            await repo_client.delete()

    @acr_preparer()
    async def test_delete_registry_artifact(self, containerregistry_baseurl, containerregistry_resource_group):
        self.import_repo_to_be_deleted(containerregistry_baseurl, resource_group=containerregistry_resource_group)

        repo_client = self.create_repository_client(containerregistry_baseurl, TO_BE_DELETED)

        count = 0
        async for artifact in repo_client.list_registry_artifacts():
            if count == 0:
                await repo_client.delete_registry_artifact(artifact.digest)
            count += 1
        assert count > 0

        artifacts = []
        async for a in repo_client.list_registry_artifacts():
            artifacts.append(a)

        assert len(artifacts) > 0
        assert len(artifacts) == count - 1
