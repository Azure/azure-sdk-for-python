# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import pytest

from devtools_testutils import AzureTestCase

from azure.containerregistry import (
    DeletedRepositoryResult,
    RepositoryProperties,
    ContentPermissions,
    RegistryArtifactOrderBy,
    RegistryArtifactProperties,
    TagOrderBy,
)
from azure.containerregistry.aio import ContainerRegistryClient, ContainerRepositoryClient
from azure.core.exceptions import ResourceNotFoundError
from azure.core.async_paging import AsyncItemPaged

from asynctestcase import AsyncContainerRegistryTestClass
from preparer import acr_preparer
from constants import TO_BE_DELETED


class TestContainerRepositoryClient(AsyncContainerRegistryTestClass):
    @acr_preparer()
    async def test_list_registry_artifacts(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        async for artifact in client.list_registry_artifacts():
            assert artifact is not None
            assert isinstance(artifact, RegistryArtifactProperties)
            assert artifact.created_on is not None
            assert isinstance(artifact.created_on, datetime)
            assert artifact.last_updated_on is not None
            assert isinstance(artifact.last_updated_on, datetime)

    @acr_preparer()
    async def test_list_registry_artifacts_by_page(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)
        results_per_page = 2

        pages = client.list_registry_artifacts(results_per_page=results_per_page)
        page_count = 0
        async for page in pages.by_page():
            reg_count = 0
            async for tag in page:
                reg_count += 1
            assert reg_count <= results_per_page
            page_count += 1

        assert page_count >= 1

    @acr_preparer()
    async def test_list_tags(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        tags = client.list_tags()
        assert isinstance(tags, AsyncItemPaged)
        count = 0
        async for tag in tags:
            count += 1

        assert count > 0

    @acr_preparer()
    async def test_list_tags_by_page(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        results_per_page = 2

        pages = client.list_tags(results_per_page=results_per_page)
        page_count = 0
        async for page in pages.by_page():
            tag_count = 0
            async for tag in page:
                tag_count += 1
            assert tag_count <= results_per_page
            page_count += 1

        assert page_count >= 1

    @acr_preparer()
    async def test_delete_tag(self, containerregistry_endpoint, containerregistry_resource_group):
        repo = self.get_resource_name("repo")
        self.import_repo(
            containerregistry_endpoint,
            resource_group=containerregistry_resource_group,
            repository=repo,
            tag=TO_BE_DELETED,
        )

        client = self.create_repository_client(containerregistry_endpoint, repo)

        tag = await client.get_tag_properties(TO_BE_DELETED)
        assert tag is not None

        await client.delete_tag(TO_BE_DELETED)
        self.sleep(5)

        with pytest.raises(ResourceNotFoundError):
            await client.get_tag_properties(TO_BE_DELETED)

    @acr_preparer()
    async def test_delete_tag_does_not_exist(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, "hello-world")

        with pytest.raises(ResourceNotFoundError):
            await client.delete_tag(TO_BE_DELETED)

    @acr_preparer()
    async def test_delete_repository(self, containerregistry_endpoint, containerregistry_resource_group):
        self.import_repo(
            containerregistry_endpoint, resource_group=containerregistry_resource_group, repository=TO_BE_DELETED
        )

        reg_client = self.create_registry_client(containerregistry_endpoint)
        existing_repos = []
        async for repo in reg_client.list_repositories():
            existing_repos.append(repo)
        assert TO_BE_DELETED in existing_repos

        repo_client = self.create_repository_client(containerregistry_endpoint, TO_BE_DELETED)
        result = await repo_client.delete()
        assert isinstance(result, DeletedRepositoryResult)
        assert result.deleted_registry_artifact_digests is not None
        assert result.deleted_tags is not None

        existing_repos = []
        async for repo in reg_client.list_repositories():
            existing_repos.append(repo)
        assert TO_BE_DELETED not in existing_repos

    @acr_preparer()
    async def test_delete_repository_doesnt_exist(self, containerregistry_endpoint):
        DOES_NOT_EXIST = "does_not_exist"

        repo_client = self.create_repository_client(containerregistry_endpoint, DOES_NOT_EXIST)
        with pytest.raises(ResourceNotFoundError):
            await repo_client.delete()

    @acr_preparer()
    async def test_delete_registry_artifact(self, containerregistry_endpoint, containerregistry_resource_group):
        repository = self.get_resource_name("repo")
        self.import_repo(
            containerregistry_endpoint, resource_group=containerregistry_resource_group, repository=repository
        )

        repo_client = self.create_repository_client(containerregistry_endpoint, repository)

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

    @acr_preparer()
    async def test_set_tag_properties(self, containerregistry_endpoint, containerregistry_resource_group):
        repository = self.get_resource_name("repo")
        tag_identifier = self.get_resource_name("tag")
        self.import_repo(
            containerregistry_endpoint,
            resource_group=containerregistry_resource_group,
            tag=tag_identifier,
            repository=repository,
        )

        client = self.create_repository_client(containerregistry_endpoint, repository)

        tag_props = await client.get_tag_properties(tag_identifier)
        permissions = tag_props.content_permissions

        received = await client.set_tag_properties(
            tag_identifier,
            ContentPermissions(
                can_delete=False,
                can_list=False,
                can_read=False,
                can_write=False,
            ),
        )

        assert not received.content_permissions.can_write
        assert not received.content_permissions.can_read
        assert not received.content_permissions.can_list
        assert not received.content_permissions.can_delete

    @acr_preparer()
    async def test_set_tag_properties_does_not_exist(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.get_resource_name("repo"))

        with pytest.raises(ResourceNotFoundError):
            await client.set_tag_properties("does_not_exist", ContentPermissions(can_delete=False))

    @acr_preparer()
    async def test_set_manifest_properties(self, containerregistry_endpoint, containerregistry_resource_group):
        repository = self.get_resource_name("reposet")
        tag_identifier = self.get_resource_name("tag")
        self.import_repo(
            containerregistry_endpoint,
            resource_group=containerregistry_resource_group,
            tag=tag_identifier,
            repository=repository,
        )

        client = self.create_repository_client(containerregistry_endpoint, repository)

        async for artifact in client.list_registry_artifacts():
            permissions = artifact.content_permissions

            received_permissions = await client.set_manifest_properties(
                artifact.digest,
                ContentPermissions(
                    can_delete=False,
                    can_list=False,
                    can_read=False,
                    can_write=False,
                ),
            )
            assert not received_permissions.content_permissions.can_delete
            assert not received_permissions.content_permissions.can_read
            assert not received_permissions.content_permissions.can_list
            assert not received_permissions.content_permissions.can_write

            # Reset and delete
            await client.set_manifest_properties(
                artifact.digest,
                ContentPermissions(
                    can_delete=True,
                    can_list=True,
                    can_read=True,
                    can_write=True,
                ),
            )
            await client.delete()

            break

    @acr_preparer()
    async def test_set_manifest_properties_does_not_exist(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.get_resource_name("repo"))

        with pytest.raises(ResourceNotFoundError):
            await client.set_manifest_properties("sha256:abcdef", ContentPermissions(can_delete=False))

    @acr_preparer()
    async def test_list_tags_descending(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        prev_last_updated_on = None
        count = 0
        async for tag in client.list_tags(order_by=TagOrderBy.LAST_UPDATE_TIME_DESCENDING):
            if prev_last_updated_on:
                assert tag.last_updated_on < prev_last_updated_on
            prev_last_updated_on = tag.last_updated_on
            count += 1

        assert count > 0

    @acr_preparer()
    async def test_list_tags_ascending(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        prev_last_updated_on = None
        count = 0
        async for tag in client.list_tags(order_by=TagOrderBy.LAST_UPDATE_TIME_ASCENDING):
            if prev_last_updated_on:
                assert tag.last_updated_on > prev_last_updated_on
            prev_last_updated_on = tag.last_updated_on
            count += 1

        assert count > 0

    @acr_preparer()
    async def test_list_registry_artifacts(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        count = 0
        async for artifact in client.list_registry_artifacts():
            assert artifact is not None
            assert isinstance(artifact, RegistryArtifactProperties)
            assert artifact.created_on is not None
            assert isinstance(artifact.created_on, datetime)
            assert artifact.last_updated_on is not None
            assert isinstance(artifact.last_updated_on, datetime)
            count += 1

        assert count > 0

    @acr_preparer()
    async def test_list_registry_artifacts_descending(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        prev_last_updated_on = None
        count = 0
        async for artifact in client.list_registry_artifacts(
            order_by=RegistryArtifactOrderBy.LAST_UPDATE_TIME_DESCENDING
        ):
            if prev_last_updated_on:
                assert artifact.last_updated_on < prev_last_updated_on
            prev_last_updated_on = artifact.last_updated_on
            count += 1

        assert count > 0

    @acr_preparer()
    async def test_list_registry_artifacts_ascending(self, containerregistry_endpoint):
        client = self.create_repository_client(containerregistry_endpoint, self.repository)

        prev_last_updated_on = None
        count = 0
        async for artifact in client.list_registry_artifacts(
            order_by=RegistryArtifactOrderBy.LAST_UPDATE_TIME_ASCENDING
        ):
            if prev_last_updated_on:
                assert artifact.last_updated_on > prev_last_updated_on
            prev_last_updated_on = artifact.last_updated_on
            count += 1

        assert count > 0
