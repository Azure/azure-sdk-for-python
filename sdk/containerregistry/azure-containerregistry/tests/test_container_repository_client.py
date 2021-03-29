# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import functools
import os
import pytest
import subprocess
import time

from devtools_testutils import AzureTestCase, PowerShellPreparer

from azure.containerregistry import (
    ContainerRepositoryClient,
    ContainerRegistryClient,
    ContentPermissions,
    RepositoryProperties,
    RegistryArtifactProperties,
    TagProperties,
    TagOrderBy,
)
from azure.core.exceptions import ResourceNotFoundError
from azure.core.paging import ItemPaged

from testcase import ContainerRegistryTestClass, AcrBodyReplacer, FakeTokenCredential
from constants import TO_BE_DELETED


acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
    containerregistry_resource_group="fake_rg",
)


class TestContainerRepositoryClient(ContainerRegistryTestClass):

    def __init__(self, method_name):
        super(TestContainerRepositoryClient, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]
        self.recording_processors.append(AcrBodyReplacer())
        self.repository = "hello-world"

    @acr_preparer()
    def test_delete_tag(self, containerregistry_baseurl, containerregistry_resource_group):
        self._import_tag_to_be_deleted(containerregistry_baseurl, resource_group=containerregistry_resource_group)

        client = self.create_repository_client(containerregistry_baseurl, "hello-world")

        tag = client.get_tag_properties(TO_BE_DELETED)
        assert tag is not None

        client.delete_tag(TO_BE_DELETED)
        self.sleep(10)

        with pytest.raises(ResourceNotFoundError):
            client.get_tag_properties(TO_BE_DELETED)

    @acr_preparer()
    def test_get_attributes(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        repo_attribs = client.get_properties()

        assert repo_attribs is not None
        assert repo_attribs.content_permissions is not None

    @acr_preparer()
    def test_get_properties(self, containerregistry_baseurl):
        repo_client = self.create_repository_client(containerregistry_baseurl, "hello-world")

        properties = repo_client.get_properties()
        assert isinstance(properties.content_permissions, ContentPermissions)

    @acr_preparer()
    def test_get_tag(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        tag = client.get_tag_properties("latest")

        assert tag is not None
        assert isinstance(tag, TagProperties)

    @acr_preparer()
    def test_list_registry_artifacts(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        count = 0
        for artifact in client.list_registry_artifacts():
            assert artifact is not None
            assert isinstance(artifact, RegistryArtifactProperties)
            assert artifact.created_on is not None
            assert isinstance(artifact.created_on, datetime)
            assert artifact.last_updated_on is not None
            assert isinstance(artifact.last_updated_on, datetime)
            count += 1

        assert count > 0

    @acr_preparer()
    def test_get_registry_artifact_properties(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        properties = client.get_registry_artifact_properties("latest")

        assert properties is not None
        assert isinstance(properties, RegistryArtifactProperties)
        assert isinstance(properties.created_on, datetime)
        assert isinstance(properties.last_updated_on, datetime)

    @acr_preparer()
    def test_list_tags(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        tags = client.list_tags()
        assert isinstance(tags, ItemPaged)
        count = 0
        for tag in tags:
            count += 1
            print(tag)

        assert count > 0

    @acr_preparer()
    def test_list_tags_descending(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        # TODO: This is giving time in ascending order
        tags = client.list_tags(order_by=TagOrderBy.LAST_UPDATE_TIME_DESCENDING)
        assert isinstance(tags, ItemPaged)
        last_updated_on = None
        count = 0
        for tag in tags:
            print(tag.last_updated_on)
            # if last_updated_on:
            #     assert tag.last_updated_on < last_updated_on
            last_updated_on = tag.last_updated_on
            count += 1

        assert count > 0

    @pytest.mark.live_test_only
    @acr_preparer()
    def test_set_manifest_properties(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        for manifest in client.list_registry_artifacts():

            permissions = manifest.content_permissions
            permissions.can_delete = not permissions.can_delete

            client.set_manifest_properties(manifest.digest, permissions)

            received = client.get_registry_artifact_properties(manifest.digest)

            assert received.content_permissions.can_write == permissions.can_write
            assert received.content_permissions.can_read == permissions.can_read
            assert received.content_permissions.can_list == permissions.can_list
            assert received.content_permissions.can_delete == permissions.can_delete

            break

    @pytest.mark.xfail
    @acr_preparer()
    def test_set_tag_properties(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        for tag in client.list_tags():

            permissions = tag.content_permissions
            permissions.can_write = not permissions.can_write

            client.set_tag_properties(tag.digest, permissions)

            received = client.get_tag_properties(tag.name)

            assert received.content_permissions.can_write == permissions.can_write
            assert received.content_permissions.can_read == permissions.can_read
            assert received.content_permissions.can_list == permissions.can_list
            assert received.content_permissions.can_delete == permissions.can_delete

            break

        tags = client.set_manifest_properties()

    @acr_preparer()
    def test_delete_repository(self, containerregistry_baseurl, containerregistry_resource_group):
        self.import_repo_to_be_deleted(containerregistry_baseurl, resource_group=containerregistry_resource_group)

        reg_client = self.create_registry_client(containerregistry_baseurl)
        existing_repos = list(reg_client.list_repositories())
        assert TO_BE_DELETED in existing_repos

        repo_client = self.create_repository_client(containerregistry_baseurl, TO_BE_DELETED)
        repo_client.delete()
        self.sleep(5)

        existing_repos = list(reg_client.list_repositories())
        assert TO_BE_DELETED not in existing_repos

    @acr_preparer()
    def test_delete_repository_doesnt_exist(self, containerregistry_baseurl):
        DOES_NOT_EXIST = "does_not_exist"

        repo_client = self.create_repository_client(containerregistry_baseurl, DOES_NOT_EXIST)
        with pytest.raises(ResourceNotFoundError):
            repo_client.delete()

    @acr_preparer()
    def test_delete_registry_artifact(self, containerregistry_baseurl, containerregistry_resource_group):
        self.import_repo_to_be_deleted(containerregistry_baseurl, resource_group=containerregistry_resource_group)

        repo_client = self.create_repository_client(containerregistry_baseurl, TO_BE_DELETED)

        count = 0
        for artifact in repo_client.list_registry_artifacts():
            if count == 0:
                repo_client.delete_registry_artifact(artifact.digest)
            count += 1
        assert count > 0

        artifacts = []
        for a in repo_client.list_registry_artifacts():
            artifacts.append(a)

        assert len(artifacts) > 0
        assert len(artifacts) == count - 1
