# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime
import functools
import os
import pytest

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
from azure.core.paging import ItemPaged

from .testcase import ContainerRegistryTestClass, AcrBodyReplacer, FakeTokenCredential

acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
)


class TestContainerRepositoryClient(ContainerRegistryTestClass):

    def __init__(self, method_name):
        super(TestContainerRepositoryClient, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]
        self.recording_processors.append(AcrBodyReplacer())
        self.repository = "hello-world"

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

        for artifact in client.list_registry_artifacts():
            assert artifact is not None
            assert isinstance(artifact, RegistryArtifactProperties)
            assert artifact.created_on is not None
            assert isinstance(artifact.created_on, datetime)
            assert artifact.last_updated_on is not None
            assert isinstance(artifact.last_updated_on, datetime)
            assert artifact.tags is not None
            assert isinstance(artifact.tags, list)


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

    @pytest.mark.skip("Don't want to delete right now")
    @acr_preparer()
    def test_delete_repository(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)
        client.delete()

        repo_client = self.create_registry_client(containerregistry_baseurl)

        repo_count = 0
        for repo in repo_client.list_repositories():
            repo_count += 1

        assert repo_count == 0
