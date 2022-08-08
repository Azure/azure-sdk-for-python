# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.purview.administration.account import PurviewAccountClient
from azure.purview.administration.metadatapolicies import PurviewMetadataPoliciesClient


class PurviewAccountTest(AzureRecordedTestCase):

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


class PurviewMetaPolicyTest(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(PurviewMetadataPoliciesClient)
        return self.create_client_from_credential(
            PurviewMetadataPoliciesClient,
            credential=credential,
            endpoint=endpoint,
        )


PurviewMetaPolicyPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "purviewmetapolicy",
    purviewmetapolicy_endpoint="https://fake_account.account.purview.azure.com"
)
