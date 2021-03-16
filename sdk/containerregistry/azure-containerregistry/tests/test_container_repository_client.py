# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os

from devtools_testutils import AzureTestCase, PowerShellPreparer

from azure.containerregistry import (
    ContainerRepositoryClient,
    ContainerRegistryClient,
)
from azure.identity import DefaultAzureCredential

from _shared.testcase import ContainerRegistryTestClass

acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
)


class TestContainerRepositoryClient(AzureTestCase, ContainerRegistryTestClass):

    repository = "hello-world"

    @acr_preparer()
    def test_delete_repository(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)
        client.delete()

        reg_client = self.create_registry_client(containerregistry_baseurl)

        repo_count = 0
        for repo in reg_client.list_repositories():
            repo_count += 1

        assert repo_count == 0

    @acr_preparer()
    def test_list_tags(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        repos = client.list_tags()
        count = 0
        # for repo in repos._repositories:
        #     count += 1
        print(repos)

        # assert count > 0

    @acr_preparer()
    def test_get_attributes(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        repo_attribs = client.get_properties()

        assert repo_attribs is not None
        assert repo_attribs.content_permissions is not None

    @acr_preparer()
    def test_list_registry_artifacts(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        repo_attribs = client.list_registry_artifacts()

        print(repo_attribs)

    @acr_preparer()
    def test_get_tag(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        repos = client.list_tags()

        tag = client.get_tag_properties()
