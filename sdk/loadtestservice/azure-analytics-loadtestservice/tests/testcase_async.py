# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureTestCase
from azure.analytics.loadtestservice.aio import LoadTestClient


class LoadtestserviceAsyncTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(LoadtestserviceAsyncTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint):
        credential = self.get_credential(LoadTestClient, is_async=True)
        return self.create_client_from_credential(
            LoadTestClient,
            credential=credential,
            endpoint=endpoint,
        )
