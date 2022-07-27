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

class LoadtestingTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(LoadtestingTest, self).__init__(method_name, **kwargs)

        self.test_id = "TEST_ID"  # ID to be assigned to a test
        self.file_id = "FILE_ID"  # ID to be assigned to file uploaded
        self.test_run_id = "TEST_RUN_ID"  # ID to be assigned to a test run
        self.app_component = "APP_COMPONENT"  # ID of the APP Component
        self.subscription_id = "SUBSCRIPTION_ID"

        if self.is_live:
            self.test_id = os.getenv("TEST_ID")
            self.file_id = os.getenv("FILE_ID")
            self.test_run_id = os.getenv("TEST_RUN_ID")
            self.app_component = os.getenv("APP_COMPONENT")
            self.subscription_id = os.getenv("SUBSCRIPTION_ID")

            self.scrubber.register_name_pair(self.test_id, "TEST_ID")
            self.scrubber.register_name_pair(self.file_id, "FILE_ID")
            self.scrubber.register_name_pair(self.test_run_id, "TEST_RUN_ID")
            self.scrubber.register_name_pair(self.app_component, "APP_COMPONENT")
            self.scrubber.register_name_pair(self.subscription_id, "SUBSCRIPTION_ID")

    def create_client(self, endpoint):
        credential = self.get_credential(LoadTestingClient)
        return self.create_client_from_credential(
            LoadTestingClient,
            credential=credential,
            endpoint=endpoint,
        )


LoadtestingPowerShellPreparer = functools.partial(
    PowerShellPreparer, "loadtesting", loadtesting_endpoint="https://myservice.azure.com"
)
