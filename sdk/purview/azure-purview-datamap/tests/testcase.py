# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.purview.datamap import PurviewDataMapClient


class PurviewDataMapTest(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(PurviewDataMapClient)
        return self.create_client_from_credential(
            PurviewDataMapClient,
            credential=credential,
            endpoint=endpoint,
        )


PurviewDataMapPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "purviewdatamap",
    purviewdatamap_endpoint="https://metamodelBugBash.purview.azure.com/datamap"
)
