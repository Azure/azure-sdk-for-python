# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureTestCase

from azure.developer.loadtesting.aio import LoadTestingClient
from testcase import TEST_ID, FILE_ID, TEST_RUN_ID, APP_COMPONENT, SUBSCRIPTION_ID


class LoadtestingAsyncTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(LoadtestingAsyncTest, self).__init__(method_name, **kwargs)

        if self.is_live:
            self.scrubber.register_name_pair(TEST_ID, "TEST_ID")
            self.scrubber.register_name_pair(FILE_ID, "FILE_ID")
            self.scrubber.register_name_pair(TEST_RUN_ID, "TEST_RUN_ID")
            self.scrubber.register_name_pair(APP_COMPONENT, "APP_COMPONENT")
            self.scrubber.register_name_pair(SUBSCRIPTION_ID, "SUBSCRIPTION_ID")

    def create_client(self, endpoint):
        credential = self.get_credential(LoadTestingClient, is_async=True)
        return self.create_client_from_credential(
            LoadTestingClient,
            credential=credential,
            endpoint=endpoint,
        )
