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
from azure.identity import DefaultAzureCredential

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
    def test_get_refresh_token(self, containerregistry_baseurl):
        client = self.create_repository_client(containerregistry_baseurl, self.repository)

        service = "seankane.azurecr.io"
        scope = "repository:hello-world:metadata_read"

        d = DefaultAzureCredential()

        token = d.get_token("https://management.core.windows.net/.default").token
        print(token)

        m = Paths108HwamOauth2ExchangePostRequestbodyContentApplicationXWwwFormUrlencodedSchema(
            service=service,
            aad_accesstoken=token,
        )

        refresh = client._client.authentication.exchange_aad_access_token_for_acr_refresh_token(m)

        m = PathsV3R3RxOauth2TokenPostRequestbodyContentApplicationXWwwFormUrlencodedSchema(
            service=service,
            scope=scope,
            acr_refresh_token=refresh.refresh_token,
        )

        assert m.access_token