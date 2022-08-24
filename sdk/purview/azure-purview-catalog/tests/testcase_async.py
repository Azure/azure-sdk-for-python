# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase
from azure.purview.catalog import PurviewCatalogClient
from azure.purview.catalog.aio import PurviewCatalogClient as AsyncPurviewCatalogClient

class PurviewCatalogTestAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(PurviewCatalogClient, is_async=True)
        return self.create_client_from_credential(
            AsyncPurviewCatalogClient,
            credential=credential,
            endpoint=endpoint,
        )