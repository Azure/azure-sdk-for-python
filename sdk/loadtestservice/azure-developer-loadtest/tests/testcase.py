# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.developer.loadtesting import LoadTestingClient


LoadtestservicePowerShellPreparer = functools.partial(
    PowerShellPreparer, "loadtesting", loadtesting_endpoint="https://fake.loadtesting.azure.com"
)


class LoadtestserviceTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(LoadtestserviceTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint):
        credential = self.get_credential(LoadTestClient)
        return self.create_client_from_credential(
            LoadTestingClient,
            credential=credential,
            endpoint=endpoint,
        )
