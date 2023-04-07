
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer, recorded_by_proxy
from azure.agrifood.farming import FarmBeatsClient

class FarmBeatsTestCase(AzureRecordedTestCase):

    def create_client(self, agrifood_endpoint):
        credential = self.get_credential(FarmBeatsClient)
        return self.create_client_from_credential(
            FarmBeatsClient,
            endpoint=agrifood_endpoint,
            credential=credential,
        )

FarmBeatsPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "agrifood",
    agrifood_endpoint="https://fakeaccount.farmbeats.azure.net"
)
