# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from _aio_testcase import AzureRecordedAsyncTestCase
from devtools_testutils import AzureRecordedTestCase
from azure.purview.administration.account.aio import PurviewAccountClient as AsyncPurviewAccountClient
from azure.purview.administration.metadatapolicies.aio import PurviewMetadataPoliciesClient as AsyncPurviewMetadataPoliciesClient


class PurviewAccountTestAsync(AzureRecordedTestCase):
    def create_async_client(self, endpoint):
        credential = self.get_credential(AsyncPurviewAccountClient, is_async=True)
        return self.create_client_from_credential(
            AsyncPurviewAccountClient,
            credential=credential,
            endpoint=endpoint,
        )


class PurviewMetaPolicyTestAsync(AzureRecordedTestCase):
    def create_async_client(self, endpoint):
        credential = self.get_credential(AsyncPurviewMetadataPoliciesClient, is_async=True)
        return self.create_client_from_credential(
            AsyncPurviewMetadataPoliciesClient,
            credential=credential,
            endpoint=endpoint,
        )
