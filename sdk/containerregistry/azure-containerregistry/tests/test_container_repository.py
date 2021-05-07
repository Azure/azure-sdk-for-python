# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import pytest

from azure.containerregistry import (
    ContentProperties,
    DeleteRepositoryResult,
    RepositoryProperties,
    ManifestOrder,
    ArtifactManifestProperties,
)
from azure.core.exceptions import ResourceNotFoundError

from testcase import ContainerRegistryTestClass
from constants import TO_BE_DELETED, DOES_NOT_EXIST, HELLO_WORLD
from preparer import acr_preparer


class TestContainerRepository(ContainerRegistryTestClass):
    @acr_preparer()
    def test_get_properties(self, containerregistry_endpoint):
        repo_client = self.create_container_repository(containerregistry_endpoint, HELLO_WORLD)

        properties = repo_client.get_properties()
        assert isinstance(properties, RepositoryProperties)
        assert isinstance(properties.writeable_properties, ContentProperties)
        assert properties.name == u"library/hello-world"

    @acr_preparer()
    def test_set_properties(self, containerregistry_endpoint):
        repository = self.get_resource_name("repo")
        tag_identifier = self.get_resource_name("tag")
        self.import_image(HELLO_WORLD, ["{}:{}".format(repository, tag_identifier)])
        repo_client = self.create_container_repository(containerregistry_endpoint, repository)

        properties = repo_client.get_properties()
        assert isinstance(properties.writeable_properties, ContentProperties)

        c = ContentProperties(can_delete=False, can_read=False, can_list=False, can_write=False)
        properties.writeable_properties = c
        new_properties = repo_client.set_properties(c)

        assert c.can_delete == new_properties.writeable_properties.can_delete
        assert c.can_read == new_properties.writeable_properties.can_read
        assert c.can_list == new_properties.writeable_properties.can_list
        assert c.can_write == new_properties.writeable_properties.can_write

        c = ContentProperties(can_delete=True, can_read=True, can_list=True, can_write=True)
        properties.writeable_properties = c
        new_properties = repo_client.set_properties(c)

        assert c.can_delete == new_properties.writeable_properties.can_delete
        assert c.can_read == new_properties.writeable_properties.can_read
        assert c.can_list == new_properties.writeable_properties.can_list
        assert c.can_write == new_properties.writeable_properties.can_write

    @acr_preparer()
    def test_list_registry_artifacts(self, containerregistry_endpoint):
        client = self.create_container_repository(containerregistry_endpoint, "library/busybox")

        count = 0
        for artifact in client.list_manifests():
            assert artifact is not None
            assert isinstance(artifact, ArtifactManifestProperties)
            assert artifact.created_on is not None
            assert isinstance(artifact.created_on, datetime)
            assert artifact.last_updated_on is not None
            assert isinstance(artifact.last_updated_on, datetime)
            assert artifact.repository_name == "library/busybox"
            count += 1

        assert count > 0

    @acr_preparer()
    def test_list_registry_artifacts_by_page(self, containerregistry_endpoint):
        client = self.create_container_repository(containerregistry_endpoint, "library/busybox")
        results_per_page = 2

        pages = client.list_manifests(results_per_page=results_per_page)
        page_count = 0
        for page in pages.by_page():
            reg_count = 0
            for tag in page:
                reg_count += 1
            assert reg_count <= results_per_page
            page_count += 1

        assert page_count >= 1

    @acr_preparer()
    def test_list_registry_artifacts_descending(self, containerregistry_endpoint):
        client = self.create_container_repository(containerregistry_endpoint, "library/busybox")

        prev_last_updated_on = None
        count = 0
        for artifact in client.list_manifests(order_by=ManifestOrder.LAST_UPDATE_TIME_DESCENDING):
            if prev_last_updated_on:
                assert artifact.last_updated_on < prev_last_updated_on
            prev_last_updated_on = artifact.last_updated_on
            count += 1

        assert count > 0

    @acr_preparer()
    def test_list_registry_artifacts_ascending(self, containerregistry_endpoint):
        client = self.create_container_repository(containerregistry_endpoint, "library/busybox")

        prev_last_updated_on = None
        count = 0
        for artifact in client.list_manifests(order_by=ManifestOrder.LAST_UPDATE_TIME_ASCENDING):
            if prev_last_updated_on:
                assert artifact.last_updated_on > prev_last_updated_on
            prev_last_updated_on = artifact.last_updated_on
            count += 1

        assert count > 0

    @acr_preparer()
    def test_delete_repository(self, containerregistry_endpoint, containerregistry_resource_group):
        self.import_image(HELLO_WORLD, [TO_BE_DELETED])

        reg_client = self.create_registry_client(containerregistry_endpoint)
        existing_repos = list(reg_client.list_repository_names())
        assert TO_BE_DELETED in existing_repos

        repo_client = self.create_container_repository(containerregistry_endpoint, TO_BE_DELETED)
        result = repo_client.delete()
        assert isinstance(result, DeleteRepositoryResult)
        assert result.deleted_manifests is not None
        assert result.deleted_tags is not None

        existing_repos = list(reg_client.list_repository_names())
        assert TO_BE_DELETED not in existing_repos

    @acr_preparer()
    def test_delete_repository_doesnt_exist(self, containerregistry_endpoint):
        repo_client = self.create_container_repository(containerregistry_endpoint, DOES_NOT_EXIST)
        with pytest.raises(ResourceNotFoundError):
            repo_client.delete()
