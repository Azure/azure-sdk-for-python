# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.media
import azure.mgmt.storage
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtMediaTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMediaTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.media.MediaServicesManagementClient
        )
        if not self.is_playback():
            self.create_resource_group()

            self.storage_client = self.create_mgmt_client(
                azure.mgmt.storage.StorageManagementClient
            )

            params_create = azure.mgmt.storage.models.StorageAccountCreateParameters(
                sku=azure.mgmt.storage.models.Sku(azure.mgmt.storage.models.SkuName.standard_lrs),
                kind=azure.mgmt.storage.models.Kind.storage,
                location=self.region
            )
            result_create = self.storage_client.storage_accounts.create(
                self.group_name,
                'msmediapttest',
                params_create,
            )
            self.storage_account = result_create.result()
            self.storage_id = self.storage_account.id
        else:
            self.storage_id = ('/subscriptions/00000000-0000-0000-0000-000000000000/'
                                'resourceGroups/test_mgmt_media_test_media8fdd0a81/'
                                'providers/Microsoft.Storage/storageAccounts/msmediapttest')


    @record
    def test_media(self):
        media_name = self.get_resource_name('pymedia')

        available = self.client.media_service.check_name_availability(
            name=media_name
        )
        self.assertTrue(available.name_available)

        media_obj = self.client.media_service.create(
            self.group_name,
            media_name,
            {
                'location': self.region,
                'storage_accounts': [{
                      'id': self.storage_id,
                      'is_primary': True
                }]
            }
        )

        media_obj = self.client.media_service.get(
            self.group_name,
            media_name
        )
        self.assertEqual(media_obj.name, media_name)
        
            
        medias = list(self.client.media_service.list_by_resource_group(self.group_name))
        self.assertEqual(len(medias), 1)
        self.assertEqual(medias[0].name, media_name)

        keys = self.client.media_service.list_keys(
            self.group_name,
            media_name
        )

        keys = self.client.media_service.regenerate_key(
            self.group_name,
            media_name,
            "Primary"
        )

        self.client.media_service.sync_storage_keys(
            self.group_name,
            media_name,
            self.storage_id
        )

        media_obj = self.client.media_service.delete(
            self.group_name,
            media_name
        )




#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
