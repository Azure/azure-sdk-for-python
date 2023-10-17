# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.purview.sharing import PurviewSharingClient

class TestPurviewSharing(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(PurviewSharingClient)
        return self.create_client_from_credential(
            PurviewSharingClient,
            credential=credential,
            endpoint=endpoint,
        )
    
    def prepare_sent_share(self):
        artifact = {
            "properties": {
                "paths": [
                    {
                        "containerName": "container1",
                        "receiverPath": "folder1",
                        "senderPath": "folder1"
                    }
                ]
            },
            "storeKind": "AdlsGen2Account",
            "storeReference": {
                # cspell:disable-next-line
                "referenceName": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/fakeResourceGroup/providers/Microsoft.Storage/storageAccounts/fakeStorageAccount",
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