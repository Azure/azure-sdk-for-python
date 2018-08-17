# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import asyncio
import unittest

import azure.mgmt.storage.models

from msrest.universal_http.async_requests import AsyncRequestsHTTPSender
from msrest.pipeline import AsyncPipeline
from msrest.pipeline.universal import RawDeserializer, HTTPLogger, UserAgentPolicy, HeadersPolicy
from msrest.pipeline.async_requests import AsyncRequestsCredentialsPolicy, AsyncPipelineRequestsHTTPSender

from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer


class MgmtStorageTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtStorageTest, self).setUp()
        self.storage_client = self.create_mgmt_client(
            azure.mgmt.storage.StorageManagementClient
        )
        self.loop = asyncio.get_event_loop()

    def test_storage_usage_async(self):
        self.loop.run_until_complete(self._test_storage_usage())

    async def _test_storage_usage(self):
        usages = [usage async for usage in self.storage_client.usage.list()]
        self.assertGreater(len(usages), 0)

    @ResourceGroupPreparer()
    def test_storage_accounts_async(self, resource_group, location):
        self.loop.run_until_complete(self._test_storage_accounts(resource_group, location))

    async def _test_storage_accounts(self, resource_group, location):

        # Change the pipeline of the current client as example
        # Add a header x-ms-testing: true to all query
        self.storage_client.config.async_pipeline = AsyncPipeline(
            [
                # This is the msrest default UserAgent, that will inject the msrest/version, etc UA
                # You could replace this line with a new "UserAgentPolicy()", but the one pre-declared
                # in the config is already filled with the name of this specific package azure-mgmt-storage
                self.storage_client.config.user_agent_policy,
                # This adds the header x-ms-testing: true as POC of the pipeline architecture
                HeadersPolicy({
                    "x-ms-testing": "true"
                }),
                # This signs the query. It works for "requests" only for now, the sender has to be requests
                AsyncRequestsCredentialsPolicy(self.storage_client.config.credentials),
                # This is the raw deserializer, that reads all the bytes and create JSON/XML. Autorest model are built outside of the pipeline for now.
                RawDeserializer(),
                # This is the default HTTP logging policy
                HTTPLogger()
            ],
            # This is a pipeline wrapper to any requests based universal HTTP driver
            AsyncPipelineRequestsHTTPSender(
                # This creates a Universal HTTP driver based on requests and default msrest configuration
                AsyncRequestsHTTPSender()
            )
        )

        account_name = self.get_resource_name('pyarmstorage')

        result_check = await self.storage_client.storage_accounts.check_name_availability_async(
            account_name
        )
        self.assertTrue(result_check.name_available)
        self.assertFalse(result_check.reason)
        self.assertFalse(result_check.message)

        params_create = azure.mgmt.storage.models.StorageAccountCreateParameters(
            sku=azure.mgmt.storage.models.Sku(
                name=azure.mgmt.storage.models.SkuName.standard_lrs),
            kind=azure.mgmt.storage.models.Kind.storage,
            location=location,
        )
        storage_account = await self.storage_client.storage_accounts.create_async(
            resource_group.name,
            account_name,
            params_create,
        )
        self.assertEqual(storage_account.name, account_name)

        storage_account = await self.storage_client.storage_accounts.get_properties_async(
            resource_group.name,
            account_name,
        )
        self.assertEqual(storage_account.name, account_name)

        result_list_keys = await self.storage_client.storage_accounts.list_keys_async(
            resource_group.name,
            account_name,
        )
        keys = {v.key_name: (v.value, v.permissions) for v in result_list_keys.keys}
        self.assertEqual(len(keys), 2)
        self.assertGreater(len(keys['key1'][0]), 0)
        self.assertGreater(len(keys['key1'][0]), 0)

        result_regen_keys = await self.storage_client.storage_accounts.regenerate_key_async(
            resource_group.name,
            account_name,
            "key1"
        )
        new_keys = {v.key_name: (v.value, v.permissions) for v in result_regen_keys.keys}
        self.assertEqual(len(new_keys), 2)
        self.assertNotEqual(
            new_keys['key1'][0],
            keys['key1'][0],
        )
        self.assertEqual(
            new_keys['key2'][0],
            keys['key2'][0],
        )

        result_list = self.storage_client.storage_accounts.list_by_resource_group(
            resource_group.name,
        )
        result_list = [account async for account in result_list]
        self.assertGreater(len(result_list), 0)

        result_list = self.storage_client.storage_accounts.list()
        result_list = [account async for account in result_list]
        self.assertGreater(len(result_list), 0)

        storage_account = await self.storage_client.storage_accounts.update_async(
            resource_group.name,
            account_name,
            azure.mgmt.storage.models.StorageAccountUpdateParameters(
                sku=azure.mgmt.storage.models.Sku(name=azure.mgmt.storage.models.SkuName.standard_grs)
            )
        )

        # should there be a test of the update operation?

        await self.storage_client.storage_accounts.delete_async(
            resource_group.name,
            account_name,
        )

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
