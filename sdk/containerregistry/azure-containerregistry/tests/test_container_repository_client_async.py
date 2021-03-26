# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
import pytest
import six

from devtools_testutils import AzureTestCase, PowerShellPreparer

from azure.containerregistry import (
    DeletedRepositoryResult,
    RepositoryProperties,
)
from azure.containerregistry.aio import ContainerRegistryClient, ContainerRepositoryClient
from azure.core.exceptions import ResourceNotFoundError
from azure.core.paging import ItemPaged
from azure.identity.aio import DefaultAzureCredential

from asynctestcase import AsyncContainerRegistryTestClass


acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
)


class TestContainerRegistryClient(AsyncContainerRegistryTestClass):

    @acr_preparer()
    async def test_delete_tag(self, containerregistry_baseurl):
        pass