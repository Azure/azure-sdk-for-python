# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from _aio_testcase import AzureRecordedAsyncTestCase
from azure.purview.administration.account.aio import PurviewAccountClient as AsyncPurviewAccountClient
from azure.purview.administration.metadatapolicies.aio import PurviewMetadataPoliciesClient as AsyncPurviewMetadataPoliciesClient


class PurviewAccountTestAsync(AzureRecordedAsyncTestCase):
    def create_async_client(self, endpoint):
        credential = self.get_credential(AsyncPurviewAccountClient, is_async=True)
        return self.create_aio_client(
            AsyncPurviewAccountClient,
            credential=credential,
            endpoint=endpoint,
        )


class PurviewMetaPolicyTestAsync(AzureRecordedAsyncTestCase):
    def create_async_client(self, endpoint):
        credential = self.get_credential(AsyncPurviewMetadataPoliciesClient, is_async=True)
        return self.create_aio_client(
            AsyncPurviewMetadataPoliciesClient,
            credential=credential,
            endpoint=endpoint,
        )
