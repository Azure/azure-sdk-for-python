# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.purview.catalog import PurviewCatalogClient


class PurviewCatalogTest(AzureTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(PurviewCatalogClient)
        return self.create_client_from_credential(
            PurviewCatalogClient,
            credential=credential,
            endpoint=endpoint,
        )


PurviewCatalogPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "purviewcatalog",
    purviewcatalog_endpoint="https://fake_account.purview.azure.com"
)
