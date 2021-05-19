# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import pytest
import six

from azure.containerregistry import (
    RepositoryProperties,
    ArtifactManifestProperties,
    ManifestOrder,
    ArtifactTagProperties,
)
from azure.core.exceptions import ResourceNotFoundError
from azure.core.async_paging import AsyncItemPaged

from asynctestcase import AsyncContainerRegistryTestClass
from constants import TO_BE_DELETED, HELLO_WORLD, ALPINE, BUSYBOX, DOES_NOT_EXIST
from preparer import acr_preparer


class TestContainerRegistryClient(AsyncContainerRegistryTestClass):
    @acr_preparer()
    async def test_list_repository_names(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        repositories = client.list_repository_names()
        assert isinstance(repositories, AsyncItemPaged)

        count = 0
        prev = None
        async for repo in repositories:
            count += 1
            assert isinstance(repo, six.string_types)
            assert prev != repo
            prev = repo

        assert count > 0

    @acr_preparer()
    async def test_list_repository_names_by_page(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)
        results_per_page = 2
        total_pages = 0

        repository_pages = client.list_repository_names(results_per_page=results_per_page)

        prev = None
        async for page in repository_pages.by_page():
            page_count = 0
            async for repo in page:
                assert isinstance(repo, six.string_types)
                assert prev != repo
                prev = repo
                page_count += 1
            assert page_count <= results_per_page
            total_pages += 1

        assert total_pages > 1

    @acr_preparer()
    async def test_delete_repository(self, containerregistry_endpoint, containerregistry_resource_group):
        self.import_image(HELLO_WORLD, [TO_BE_DELETED])
        client = self.create_registry_client(containerregistry_endpoint)

        await client.delete_repository(TO_BE_DELETED)

        async for repo in client.list_repository_names():
            if repo == TO_BE_DELETED:
                raise ValueError("Repository not deleted")

    @acr_preparer()
    async def test_delete_repository_does_not_exist(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        await client.delete_repository("not_real_repo")

    @acr_preparer()
    async def test_get_repository_properties(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_repository_properties(ALPINE)
        assert isinstance(properties, RepositoryProperties)
        assert properties.name == ALPINE

    @acr_preparer()
    async def test_set_properties(self, containerregistry_endpoint):
        repository = self.get_resource_name("repo")
        tag_identifier = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repository, tag_identifier)])
        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_repository_properties(repository)

        properties.can_delete = False
        properties.can_read = False
        properties.can_list = False
        properties.can_write = False

        new_properties = await client.set_repository_properties(repository, properties)

        assert properties.can_delete == new_properties.can_delete
        assert properties.can_read == new_properties.can_read
        assert properties.can_list == new_properties.can_list
        assert properties.can_write == new_properties.can_write

        new_properties.can_delete = True
        new_properties.can_read = True
        new_properties.can_list = True
        new_properties.can_write = True

        new_properties = await client.set_repository_properties(repository, new_properties)

        assert new_properties.can_delete == True
        assert new_properties.can_read == True
        assert new_properties.can_list == True
        assert new_properties.can_write == True

    @acr_preparer()
    async def test_list_registry_artifacts(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        count = 0
        async for artifact in client.list_manifests(BUSYBOX):
            assert artifact is not None
            assert isinstance(artifact, ArtifactManifestProperties)
            assert artifact.created_on is not None
            assert isinstance(artifact.created_on, datetime)
            assert artifact.last_updated_on is not None
            assert isinstance(artifact.last_updated_on, datetime)
            assert artifact.repository_name == BUSYBOX
            count += 1

        assert count > 0

    @acr_preparer()
    async def test_list_registry_artifacts_by_page(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)
        results_per_page = 2

        pages = client.list_manifests(BUSYBOX, results_per_page=results_per_page)
        page_count = 0
        async for page in pages.by_page():
            reg_count = 0
            async for tag in page:
                reg_count += 1
            assert reg_count <= results_per_page
            page_count += 1

        assert page_count >= 1

    @acr_preparer()
    async def test_list_registry_artifacts_descending(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        prev_last_updated_on = None
        count = 0
        async for artifact in client.list_manifests(BUSYBOX, order_by=ManifestOrder.LAST_UPDATE_TIME_DESCENDING):
            if prev_last_updated_on:
                assert artifact.last_updated_on < prev_last_updated_on
            prev_last_updated_on = artifact.last_updated_on
            count += 1

        assert count > 0

    @acr_preparer()
    async def test_list_registry_artifacts_ascending(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        prev_last_updated_on = None
        count = 0
        async for artifact in client.list_manifests(BUSYBOX, order_by=ManifestOrder.LAST_UPDATE_TIME_ASCENDING):
            if prev_last_updated_on:
                assert artifact.last_updated_on > prev_last_updated_on
            prev_last_updated_on = artifact.last_updated_on
            count += 1

        assert count > 0

    @acr_preparer()
    async def test_get_manifest_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_manifest_properties(repo, tag)

        assert isinstance(properties, ArtifactManifestProperties)
        assert properties.repository_name == repo

    @acr_preparer()
    async def test_get_manifest_properties_does_not_exist(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        with pytest.raises(ResourceNotFoundError):
            properties = await client.get_manifest_properties("DOESNOTEXIST", "DOESNOTEXIST")

    @acr_preparer()
    async def test_set_manifest_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_manifest_properties(repo, tag)
        properties.can_delete = False
        properties.can_read = False
        properties.can_write = False
        properties.can_list = False

        received = await client.set_manifest_properties(repo, tag, properties)

        assert received.can_delete == properties.can_delete
        assert received.can_read == properties.can_read
        assert received.can_write == properties.can_write
        assert received.can_list == properties.can_list

        properties.can_delete = True
        properties.can_read = True
        properties.can_write = True
        properties.can_list = True

        received = await client.set_manifest_properties(repo, tag, properties)

        assert received.can_delete == True
        assert received.can_read == True
        assert received.can_write == True
        assert received.can_list == True

    @acr_preparer()
    async def test_get_tag_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_tag_properties(repo, tag)

        assert isinstance(properties, ArtifactTagProperties)
        assert properties.name == tag

    @acr_preparer()
    async def test_get_tag_properties_does_not_exist(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        with pytest.raises(ResourceNotFoundError):
            await client.get_tag_properties("Nonexistent", "Nonexistent")

    @acr_preparer()
    async def test_set_tag_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)

        properties = await client.get_tag_properties(repo, tag)
        properties.can_delete = False
        properties.can_read = False
        properties.can_write = False
        properties.can_list = False
        received = await client.set_tag_properties(repo, tag, properties)

        assert received.can_delete == properties.can_delete
        assert received.can_read == properties.can_read
        assert received.can_write == properties.can_write
        assert received.can_list == properties.can_list

        properties.can_delete = True
        properties.can_read = True
        properties.can_write = True
        properties.can_list = True

        received = await client.set_tag_properties(repo, tag, properties)

        assert received.can_delete == True
        assert received.can_read == True
        assert received.can_write == True
        assert received.can_list == True

    @acr_preparer()
    async def test_list_tags(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        tags = ["{}:{}".format(repo, tag + str(i)) for i in range(4)]
        self.import_image(HELLO_WORLD, tags)

        client = self.create_registry_client(containerregistry_endpoint)

        count = 0
        async for tag in client.list_tags(repo):
            assert "{}:{}".format(repo, tag.name) in tags
            count += 1
        assert count == 4

    @acr_preparer()
    async def test_delete_tag(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        tags = ["{}:{}".format(repo, tag + str(i)) for i in range(4)]
        self.import_image(HELLO_WORLD, tags)

        client = self.create_registry_client(containerregistry_endpoint)

        await client.delete_tag(repo, tag + str(0))

        count = 0
        async for tag in client.list_tags(repo):
            assert "{}:{}".format(repo, tag.name) in tags[1:]
            count += 1
        assert count == 3

    @acr_preparer()
    async def test_delete_tag_does_not_exist(self, containerregistry_endpoint):
        client = self.create_registry_client(containerregistry_endpoint)

        await client.delete_tag(DOES_NOT_EXIST, DOES_NOT_EXIST)

    @acr_preparer()
    async def test_delete_manifest(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repo, tag)])

        client = self.create_registry_client(containerregistry_endpoint)
        client.delete_manifest(repo, tag)

        self.sleep(10)

        await client.get_manifest_properties(repo, tag)

    @acr_preparer()
    async def test_delete_manifest_does_not_exist(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")

        client = self.create_registry_client(containerregistry_endpoint)

        client.delete_manifest(repo, DOES_NOT_EXIST)
