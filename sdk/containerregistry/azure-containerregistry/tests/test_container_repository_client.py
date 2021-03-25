# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
import pytest

from devtools_testutils import AzureTestCase, PowerShellPreparer

from azure.containerregistry import (
    ContainerRepositoryClient,
    ContainerRegistryClient,
    RepositoryProperties,
    ContentPermissions,
    TagProperties,
    TagOrderBy,
)
from azure.core.paging import ItemPaged

from testcase import ContainerRegistryTestClass

acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
)


class TestContainerRepositoryClient(AzureTestCase, ContainerRegistryTestClass):

    repository = "hello-world"

    @pytest.mark.live_test_only
    @acr_preparer()
    def test_get_attributes(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        repo_attribs = client.get_properties()

        assert repo_attribs is not None
        assert repo_attribs.content_permissions is not None

    @pytest.mark.live_test_only
    @acr_preparer()
    def test_get_properties(self, containerregistry_baseurl):
        reg_client = self.create_repository_client(containerregistry_baseurl, "hello-world")

        properties = reg_client.get_properties()

        assert isinstance(properties, RepositoryProperties)
        assert properties.name == "hello-world"
        assert properties.registry == containerregistry_baseurl
        assert properties.content_permissions is not None
        assert isinstance(properties.content_permissions, ContentPermissions)

    @pytest.mark.skip("Pending")
    @acr_preparer()
    def test_get_registry_artifact_properties(self, containerregistry_baseurl):
        reg_client = self.create_repository_client(containerregistry_baseurl, "hello-world")

        digest = "sha256:90659bf80b44ce6be8234e6ff90a1ac34acbeb826903b02cfa0da11c82cbc042"
        tag = "first"

        properties = reg_client.get_registry_artifact_properties(digest)
        first_properties = reg_client.get_registry_artifact_properties(tag)

        self.assert_registry_artifact(properties, digest)
        self.assert_registry_artifact(first_properties, tag)

    @pytest.mark.live_test_only
    @acr_preparer()
    def test_get_tag(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        tag = client.get_tag_properties("latest")

        self.assert_tag(tag)

    @pytest.mark.live_test_only
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

    @pytest.mark.live_test_only
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
            # print(tag)

        assert count > 0

    @pytest.mark.skip("List pending")
    @acr_preparer()
    def test_list_registry_artifacts(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        repo_attribs = client.list_registry_artifacts()

        print(repo_attribs)

    @pytest.mark.skip("Don't want to delete right now")
    @acr_preparer()
    def test_delete_repository(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)
        client.delete()

        reg_client = self.create_registry_client(containerregistry_baseurl)

        repo_count = 0
        for repo in reg_client.list_repositories():
            repo_count += 1

        assert repo_count == 0
