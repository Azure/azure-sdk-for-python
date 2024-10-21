# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.purview.datamap import DataMapClient


class DataMapTest(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(DataMapClient)
        return self.create_client_from_credential(
            DataMapClient,
            credential=credential,
            endpoint=endpoint,
        )


DataMapPowerShellPreparer = functools.partial(
    PowerShellPreparer, "purviewdatamap", purviewdatamap_endpoint="https://fakeaccount.purview.azure.com"
)
