# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.media
import azure.mgmt.storage

from devtools_testutils import (
    AzureMgmtTestCase, ResourceGroupPreparer,
    StorageAccountPreparer, FakeStorageAccount,
)


PLAYBACK_STORAGE_ID = (
    '/subscriptions/00000000-0000-0000-0000-000000000000/'
    'resourceGroups/test_mgmt_media_test_media8fdd0a81/'
    'providers/Microsoft.Storage/storageAccounts/msmediapttest'
)

FAKE_STORAGE = FakeStorageAccount(
    name='msmediapttest',
    id=PLAYBACK_STORAGE_ID,
)


class MgmtMediaTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtMediaTest, self).setUp()
        self.client = self.create_mgmt_client(
            azure.mgmt.media.MediaServicesManagementClient
        )

    @ResourceGroupPreparer()
    @StorageAccountPreparer(name_prefix='msmediapttest', playback_fake_resource=FAKE_STORAGE)
    def test_media(self, resource_group, location, storage_account):
        media_name = self.get_resource_name('pymedia')

        available = self.client.media_service.check_name_availability(
            name=media_name
        )
        self.assertTrue(available.name_available)

        media_obj = self.client.media_service.create(
            resource_group.name,
            media_name,
            {
                'location': location,
                'storage_accounts': [{
                    'id': storage_account.id,
                    'is_primary': True,
                }]
            }
        )

        media_obj = self.client.media_service.get(
            resource_group.name,
            media_name
        )
        self.assertEqual(media_obj.name, media_name)

        medias = list(self.client.media_service.list_by_resource_group(resource_group.name))
        self.assertEqual(len(medias), 1)
        self.assertEqual(medias[0].name, media_name)

        # why is keys assigned to here?
        keys = self.client.media_service.list_keys(
            resource_group.name,
            media_name
        )

        keys = self.client.media_service.regenerate_key(
            resource_group.name,
            media_name,
            "Primary"
        )

        self.client.media_service.sync_storage_keys(
            resource_group.name,
            media_name,
            storage_account.id
        )

        media_obj = self.client.media_service.delete(
            resource_group.name,
            media_name
        )




#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
