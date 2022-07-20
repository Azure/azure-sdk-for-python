# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.developer.loadtesting import LoadTestingClient


LoadtestingPowerShellPreparer = functools.partial(
    PowerShellPreparer, "loadtesting", loadtesting_endpoint="https://fake.loadtesting.azure.com"
)


class LoadtestingTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(LoadtestingTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint):
        credential = self.get_credential(LoadTestingClient)
        return self.create_client_from_credential(
            LoadTestingClient,
            credential=credential,
            endpoint=endpoint,
        )
