# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.redis
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtRedisTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtRedisTest, self).setUp()
        self.redis_client = self.create_mgmt_client(
            azure.mgmt.redis.RedisManagementClientConfiguration,
            azure.mgmt.redis.RedisManagementClient
        )

    @record
    def test_redis(self):
        self.create_resource_group()

        account_name = self.get_resource_name('pyarmredis')

        cache_name = 'mycachename'
        redis_cache = self.redis_client.redis.create_or_update(
            self.group_name, 
            cache_name,
            azure.mgmt.redis.models.RedisCreateOrUpdateParameters( 
                sku = azure.mgmt.redis.models.Sku(name = 'Basic', family = 'C', capacity = '1'),
                location = "West US"
            )
        ) 

        result = self.redis_client.redis.get(
            self.group_name, 
            cache_name,
        )
        self.assertEquals(result.name, cache_name)



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
