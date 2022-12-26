# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.purview.scanning import PurviewScanningClient


class PurviewScanningTest(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(PurviewScanningClient)
        return self.create_client_from_credential(
            PurviewScanningClient,
            credential=credential,
            endpoint=endpoint,
        )


PurviewScanningPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "purviewscanning",
    purviewscanning_endpoint="https://fake_account.scan.purview.azure.com"
)
