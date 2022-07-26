# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.developer.loadtesting import LoadTestingClient

TEST_ID = os.getenv("TEST_ID")  # ID to be assigned to a test
FILE_ID = os.getenv("FILE_ID")  # ID to be assigned to file uploaded
TEST_RUN_ID = os.getenv("TEST_RUN_ID")  # ID to be assigned to a test run
APP_COMPONENT = os.getenv("APP_COMPONENT")  # ID of the APP Component
SUBSCRIPTION_ID = os.getenv("SUBSCRIPTION_ID")

class LoadtestingTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(LoadtestingTest, self).__init__(method_name, **kwargs)
        if self.is_live:
            self.scrubber.register_name_pair(TEST_ID, "TEST_ID")
            self.scrubber.register_name_pair(FILE_ID, "FILE_ID")
            self.scrubber.register_name_pair(TEST_RUN_ID, "TEST_RUN_ID")
            self.scrubber.register_name_pair(APP_COMPONENT, "APP_COMPONENT")
            self.scrubber.register_name_pair(SUBSCRIPTION_ID, "SUBSCRIPTION_ID")

    def create_client(self, endpoint):
        credential = self.get_credential(LoadTestingClient)
        return self.create_client_from_credential(
            LoadTestingClient,
            credential=credential,
            endpoint=endpoint,
        )


LoadtestingPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "loadtesting",
    loadtesting_endpoint="https://myservice.azure.com"
)
