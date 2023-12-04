# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase
from azure.purview.datamap import PurviewDataMapClient
from azure.purview.datamap.aio import PurviewDataMapClient as AsyncPurviewDataMapClient

class PurviewDataMapTestAsync(AzureRecordedTestCase):

    def create_async_client(self, endpoint):
        credential = self.get_credential(PurviewDataMapClient, is_async=True)
        return self.create_client_from_credential(
            AsyncPurviewDataMapClient,
            credential=credential,
            endpoint=endpoint,
        )