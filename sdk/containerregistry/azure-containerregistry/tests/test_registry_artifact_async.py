# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.containerregistry import (
    ArtifactArchitecture,
    ArtifactManifestProperties,
    ArtifactOperatingSystem,
    ContentProperties,
    ArtifactTagProperties,
)
from azure.core.exceptions import ResourceNotFoundError

from asynctestcase import AsyncContainerRegistryTestClass
from constants import DOES_NOT_EXIST, HELLO_WORLD
from preparer import acr_preparer


class TestContainerRepository(AsyncContainerRegistryTestClass):
    async def set_up(self, endpoint, name):
        repo_client = self.create_container_repository(endpoint, name)

        async for artifact in repo_client.list_manifests():
            return repo_client.get_artifact(artifact.digest)

    @acr_preparer()
    async def test_get_manifest_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repo, tag)])

        reg_artifact = await self.set_up(containerregistry_endpoint, name=repo)

        properties = await reg_artifact.get_manifest_properties()

        assert isinstance(properties, ArtifactManifestProperties)
        assert isinstance(properties.writeable_properties, ContentProperties)
        assert isinstance(properties.writeable_properties, ContentProperties)
        assert isinstance(properties.architecture, ArtifactArchitecture)
        assert isinstance(properties.operating_system, ArtifactOperatingSystem)

    @acr_preparer()
    async def test_get_manifest_properties_does_not_exist(self, containerregistry_endpoint):
        repo_client = self.create_container_repository(containerregistry_endpoint, "hello-world")

        reg_artifact = repo_client.get_artifact("sha256:abcdefghijkl")

        with pytest.raises(ResourceNotFoundError):
            await reg_artifact.get_manifest_properties()

    @acr_preparer()
    async def test_set_manifest_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repo, tag)])

        reg_artifact = await self.set_up(containerregistry_endpoint, name=repo)

        properties = await reg_artifact.get_manifest_properties()
        c = ContentProperties(can_delete=False, can_read=False, can_write=False, can_list=False)

        received = await reg_artifact.set_manifest_properties(c)

        assert received.writeable_properties.can_delete == c.can_delete
        assert received.writeable_properties.can_read == c.can_read
        assert received.writeable_properties.can_write == c.can_write
        assert received.writeable_properties.can_list == c.can_list

        c = ContentProperties(can_delete=True, can_read=True, can_write=True, can_list=True)
        received = await reg_artifact.set_manifest_properties(c)

        assert received.writeable_properties.can_delete == c.can_delete
        assert received.writeable_properties.can_read == c.can_read
        assert received.writeable_properties.can_write == c.can_write
        assert received.writeable_properties.can_list == c.can_list

    @acr_preparer()
    async def test_get_tag_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repo, tag)])

        reg_artifact = await self.set_up(containerregistry_endpoint, name=repo)

        properties = await reg_artifact.get_tag_properties(tag)

        assert isinstance(properties, ArtifactTagProperties)
        assert properties.name == tag

    @acr_preparer()
    async def test_get_tag_properties_does_not_exist(self, containerregistry_endpoint):
        repo_client = self.create_container_repository(containerregistry_endpoint, "hello-world")

        reg_artifact = repo_client.get_artifact("sha256:abcdefghijkl")

        with pytest.raises(ResourceNotFoundError):
            await reg_artifact.get_tag_properties("doesnotexist")

    @acr_preparer()
    async def test_set_tag_properties(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repo, tag)])

        reg_artifact = await self.set_up(containerregistry_endpoint, name=repo)

        properties = await reg_artifact.get_tag_properties(tag)
        c = ContentProperties(can_delete=False, can_read=False, can_write=False, can_list=False)

        received = await reg_artifact.set_tag_properties(tag, c)

        assert received.writeable_properties.can_delete == c.can_delete
        assert received.writeable_properties.can_read == c.can_read
        assert received.writeable_properties.can_write == c.can_write
        assert received.writeable_properties.can_list == c.can_list

        c = ContentProperties(can_delete=True, can_read=True, can_write=True, can_list=True)
        received = await reg_artifact.set_tag_properties(tag, c)

        assert received.writeable_properties.can_delete == c.can_delete
        assert received.writeable_properties.can_read == c.can_read
        assert received.writeable_properties.can_write == c.can_write
        assert received.writeable_properties.can_list == c.can_list

    @acr_preparer()
    async def test_list_tags(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        tags = ["{}:{}".format(repo, tag + str(i)) for i in range(4)]
        self.import_image(HELLO_WORLD, tags)
        reg_artifact = await self.set_up(containerregistry_endpoint, name=repo)

        count = 0
        async for tag in reg_artifact.list_tags():
            assert "{}:{}".format(repo, tag.name) in tags
            count += 1
        assert count == 4

    @acr_preparer()
    async def test_delete_tag(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        tags = ["{}:{}".format(repo, tag + str(i)) for i in range(4)]
        self.import_image(HELLO_WORLD, tags)
        container_repo = self.create_container_repository(containerregistry_endpoint, repo)
        reg_artifact = container_repo.get_artifact(tag + str(0))

        await reg_artifact.delete_tag(tag + str(0))

        count = 0
        async for tag in reg_artifact.list_tags():
            assert "{}:{}".format(repo, tag.name) in tags[1:]
            count += 1
        assert count == 3

    @acr_preparer()
    async def test_delete_tag_does_not_exist(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        container_repo = self.create_container_repository(containerregistry_endpoint, repo)
        reg_artifact = container_repo.get_artifact(DOES_NOT_EXIST)

        with pytest.raises(ResourceNotFoundError):
            await reg_artifact.delete_tag(DOES_NOT_EXIST)

    @acr_preparer()
    async def test_delete_registry_artifact(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        tag = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repo, tag)])
        reg_artifact = await self.set_up(containerregistry_endpoint, name=repo)

        await reg_artifact.delete()
        self.sleep(10)

        with pytest.raises(ResourceNotFoundError):
            await reg_artifact.get_manifest_properties()

    @acr_preparer()
    async def test_delete_registry_artifact_does_not_exist(self, containerregistry_endpoint):
        repo = self.get_resource_name("repo")
        container_repo = self.create_container_repository(containerregistry_endpoint, repo)
        reg_artifact = container_repo.get_artifact(DOES_NOT_EXIST)

        with pytest.raises(ResourceNotFoundError):
            await reg_artifact.delete()
