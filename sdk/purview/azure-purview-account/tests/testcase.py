# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.purview.account import PurviewAccountClient


class PurviewAccountTest(AzureTestCase):
    def __init__(self, method_name, **kwargs):
        super(PurviewAccountTest, self).__init__(method_name, **kwargs)

    def create_client(self, endpoint):
        credential = self.get_credential(PurviewAccountClient)
        return self.create_client_from_credential(
            PurviewAccountClient,
            credential=credential,
            endpoint=endpoint,
        )


PurviewAccountPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "purviewaccount",
    purviewaccount_endpoint="https://fake_account.account.purview.azure.com"
)
