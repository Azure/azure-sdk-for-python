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
    ContainerRegistryClient,
    ContainerRegistryUserCredential,
    DeletedRepositoryResult,
    ACRExchangeClient
)
from azure.core.exceptions import ResourceNotFoundError
from azure.core.paging import ItemPaged
from azure.identity import DefaultAzureCredential

from testcase import ContainerRegistryTestClass


acr_preparer = functools.partial(
    PowerShellPreparer,
    "containerregistry",
    containerregistry_baseurl="fake_url.azurecr.io",
)


class TestContainerRegistryClient(AzureTestCase, ContainerRegistryTestClass):

    def create_exchange_client(self, endpoint):
        return self.create_client_from_credential(
            ACRExchangeClient,
            credential=self.get_credential(ACRExchangeClient),
            endpoint=endpoint,
        )

    @pytest.mark.live_test_only
    @acr_preparer()
    def test_exchange_client(self, containerregistry_baseurl):
        client = self.create_exchange_client(containerregistry_baseurl)

        service = "seankane.azurecr.io"
        scope = "repository:hello-world:metadata_read"

        refresh = client.get_refresh_token(service, os.environ["AZURE_TENANT_ID"])

        assert refresh is not None
        print(refresh)
