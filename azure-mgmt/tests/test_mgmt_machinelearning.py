# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest
raise unittest.SkipTest("Skipping all tests")

import azure.mgmt.machinelearning
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import (
    StorageAccountCreateParameters,
    StorageAccountUpdateParameters,
    Sku,
    SkuName,
    Kind
)
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtMachineLearningTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMachineLearningTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.machinelearning.AzureMLWebServicesManagementClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_ml(self):
        region = 'southcentralus'

        # Create a storage account and get keys
        storage_name = self.get_resource_name('pystorage')
        storage_client = azure.mgmt.storage.StorageManagementClient(
            credentials=self.settings.get_credentials(),
            subscription_id=self.settings.SUBSCRIPTION_ID
        )
        storage_async_operation = storage_client.storage_accounts.create(
            self.group_name,
            storage_name,
            StorageAccountCreateParameters(
                sku=Sku(SkuName.standard_ragrs),
                kind=Kind.storage,
                location=region
            )
        )
        storage_async_operation.wait()
        storage_key = storage_client.storage_accounts.list_keys(
            self.group_name,
            storage_name
        ).keys[0].value

        # Create Commitment plan
        commitplan_name = self.get_resource_name('pycommit')
        commitplan = self.resource_client.resources.create_or_update(
            resource_group_name=self.group_name,
            resource_provider_namespace="Microsoft.MachineLearning",
            parent_resource_path="",
            resource_type="commitmentPlans",
            resource_name=commitplan_name,
            api_version="2016-05-01-preview",
            parameters={
                'location': region,
                'sku': {
                    'name': "DevTest",
                    'tier': 'Standard',
                    'capacity': '1'
                }
            }
        )

        # Create WebService
        ws_name = self.get_resource_name('pyws')
        self.client.web_services.create_or_update({
                'location': region,
                'properties': {
                    'storage_account': {
                        'name': storage_name,
                        'key': storage_key
                    },
                    'machine_learning_workspace': {
                        'id': commitplan.id
                    },
                    'packageType': 'Graph'
                }
            },
            self.group_name,
            ws_name
        )
            


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
