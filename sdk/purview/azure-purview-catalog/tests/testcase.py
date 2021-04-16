# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.purview.catalog import AzurePurviewCatalogClient
from azure.purview.catalog.aio import AzurePurviewCatalogClient as AsyncAzurePurviewCatalogClient


class PurviewCatalogTest(AzureTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(AzurePurviewCatalogClient)
        return self.create_client_from_credential(
            AzurePurviewCatalogClient,
            credential=credential,
            endpoint=endpoint,
        )

    def create_async_client(self, endpoint):
        credential = self.get_credential(AzurePurviewCatalogClient, is_async=True)
        return self.create_client_from_credential(
            AsyncAzurePurviewCatalogClient,
            credential=credential,
            endpoint=endpoint,
        )

PurviewCatalogPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "purviewcatalog",
    purviewcatalog_endpoint="https://fake_account.catalog.purview.azure.com"
)
