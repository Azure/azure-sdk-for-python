# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os

from devtools_testutils import AzureTestCase, PowerShellPreparer

from azure.containerregistry import ContainerRepositoryClient, ContainerRegistryUserCredential
from azure.identity import DefaultAzureCredential


acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
)


class TestContainerRepositoryClient(AzureTestCase):
    def set_up(self, endpoint):
        return ContainerRepositoryClient(
            endpoint=endpoint,
            repository="hello-world",
            credential=ContainerRegistryUserCredential(
                username=os.environ["CONTAINERREGISTRY_USERNAME"],
                password=os.environ["CONTAINERREGISTRY_PASSWORD"]
            )
        )

    @acr_preparer()
    def test_list_tags(self, containerregistry_baseurl):
        client = self.set_up(containerregistry_baseurl)

        repos = client.list_tags()
        count = 0
        # for repo in repos._repositories:
        #     count += 1
        print(repos)

        # assert count > 0

    @acr_preparer()
    def test_get_attributes(self, containerregistry_baseurl):
        client = self.set_up(containerregistry_baseurl)

        repo_attribs = client.get_properties()

        assert repo_attribs is not None
        assert repo_attribs.content_permissions is not None

    @acr_preparer()
    def test_list_registry_artifacts(self, containerregistry_baseurl):
        client = self.set_up(containerregistry_baseurl)

        repo_attribs = client.list_registry_artifacts()

        print(repo_attribs)


