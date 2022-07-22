# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureTestCase

from azure.developer.loadtesting.aio import LoadTestingClient


class LoadtestingAsyncTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(LoadtestingAsyncTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint):
        credential = self.get_credential(LoadTestingClient, is_async=True)
        return self.create_client_from_credential(
            LoadTestingClient,
            credential=credential,
            endpoint=endpoint,
        )
