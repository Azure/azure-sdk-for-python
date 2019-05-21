# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.redis
from devtools_testutils import AzureMgmtTestCase, ResourceGroupPreparer

class MgmtRedisTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtRedisTest, self).setUp()
        self.redis_client = self.create_mgmt_client(
            azure.mgmt.redis.RedisManagementClient
        )

    @ResourceGroupPreparer()
    def test_redis(self, resource_group, location):
        account_name = self.get_resource_name('pyarmredis')

        cache_name = 'mycachename'
        redis_async_create = self.redis_client.redis.create(
            resource_group.name,
            cache_name,
            azure.mgmt.redis.models.RedisCreateParameters( 
                sku = azure.mgmt.redis.models.Sku(name = 'Basic', family = 'C', capacity = '1'),
                location = location
            )
        ) 
        redis_cache = redis_async_create.result()
        self.assertEqual(redis_cache.name, cache_name)

        result = self.redis_client.redis.get(
            resource_group.name,
            cache_name,
        )
        self.assertEqual(result.name, cache_name)



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
