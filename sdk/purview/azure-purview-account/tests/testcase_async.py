# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureTestCase
from azure.purview.account.aio import PurviewAccountClient as AsyncPurviewAccountClient


class PurviewAccountTestAsync(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(PurviewAccountTestAsync, self).__init__(method_name, **kwargs)

    def create_async_client(self, endpoint):
        credential = self.get_credential(AsyncPurviewAccountClient, is_async=True)
        return self.create_client_from_credential(
            AsyncPurviewAccountClient,
            credential=credential,
            endpoint=endpoint,
        )
