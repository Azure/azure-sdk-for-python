# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
import pytest
import six
import subprocess
import time

from devtools_testutils import AzureTestCase, PowerShellPreparer

from azure.containerregistry import (
    DeletedRepositoryResult,
    RepositoryProperties,
)
from azure.containerregistry.aio import ContainerRegistryClient, ContainerRepositoryClient
from azure.core.exceptions import ResourceNotFoundError
from azure.core.paging import ItemPaged

from asynctestcase import AsyncContainerRegistryTestClass
from testcase import AcrBodyReplacer


acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
    containerregistry_resource_group="fake_rg",
)


class TestContainerRegistryClient(AsyncContainerRegistryTestClass):

    def __init__(self, method_name):
        super(TestContainerRegistryClient, self).__init__(method_name)
        self.vcr.match_on = ["path", "method", "query"]
        self.recording_processors.append(AcrBodyReplacer())
        self.repository = "hello-world"

    @acr_preparer()
    async def test_delete_tag(self, containerregistry_baseurl, containerregistry_resource_group):
        self._import_tag_to_be_deleted(containerregistry_baseurl, resource_group=containerregistry_resource_group)

        client = self.create_repository_client(containerregistry_baseurl, "hello-world")

        tag = await client.get_tag_properties("to_be_deleted")
        assert tag is not None

        await client.delete_tag("to_be_deleted")
        self.sleep(10)

        with pytest.raises(ResourceNotFoundError):
            await client.get_tag_properties("to_be_deleted")