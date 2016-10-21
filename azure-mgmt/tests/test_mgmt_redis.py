# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.redis
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtRedisTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtRedisTest, self).setUp()
        self.redis_client = self.create_mgmt_client(
            azure.mgmt.redis.RedisManagementClient
        )
        if not self.is_playback():
            self.create_resource_group()

    @record
    def test_redis(self):
        account_name = self.get_resource_name('pyarmredis')

        cache_name = 'mycachename'
        redis_async_create = self.redis_client.redis.create(
            self.group_name, 
            cache_name,
            azure.mgmt.redis.models.RedisCreateParameters( 
                sku = azure.mgmt.redis.models.Sku(name = 'Basic', family = 'C', capacity = '1'),
                location = self.region
            )
        ) 
        redis_cache =redis_async_create.result()
        self.assertEqual(redis_cache.name, cache_name)

        result = self.redis_client.redis.get(
            self.group_name, 
            cache_name,
        )
        self.assertEqual(result.name, cache_name)



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
