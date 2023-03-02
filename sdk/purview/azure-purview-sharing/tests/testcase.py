# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.purview.sharing import PurviewSharing

class TestPurviewSharing(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(PurviewSharing)
        return self.create_client_from_credential(
            PurviewSharing,
            credential=credential,
            endpoint=endpoint,
        )
    
    def prepare_sent_share(self):
        artifact = {
            "properties": {
                "paths": [
                    {
                        "containerName": "container1",
                        "receiverPath": "t1/dbtGen2Pqt.parquet",
                        "senderPath": "t1/dbtGen2Pqt.parquet"
                    }
                ]
            },
            "storeKind": "AdlsGen2Account",
            "storeReference": {
                "referenceName": "/subscriptions/0f3dcfc3-18f8-4099-b381-8353e19d43a7/resourceGroups/faisalaltell/providers/Microsoft.Storage/storageAccounts/ftsharersan",
                "type": "ArmResourceReference"
            }
        }

        sent_share = {
            "properties": {
                "artifact": artifact,
                "displayName": "sentShare-Test",
                "description": "A sample share"
            },
            "shareKind": "InPlace"
        }

        return sent_share

PurviewSharingPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "purviewsharing",
    purviewsharing_endpoint="https://fake_account.share.purview.azure.com"
)