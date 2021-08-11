# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.purview.account import PurviewAccountClient
from _util import PurviewAccountRecordingProcessor


class PurviewAccountTest(AzureTestCase):

    def create_client(self, endpoint):
        self.recording_processors.append(PurviewAccountRecordingProcessor())
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
